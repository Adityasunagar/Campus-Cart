from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.user import User
from models.item import Item
from models.report import Report
from models.message import Message
from utils.helpers import login_required, admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/secret-login', methods=['GET', 'POST'])
def admin_login():
    if session.get('user_id') and session.get('is_admin'):
        return redirect(url_for('admin.admin_dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = User.authenticate(email, password)

        if user and user != 'banned' and bool(user['is_admin']):
            session.clear()
            session['user_id'] = user['id']
            session['is_admin'] = True
            flash(f"Admin Access Granted: Welcome {user['username']}", 'success')
            return redirect(url_for('admin.admin_dashboard'))

        flash('Invalid admin credentials.', 'danger')

    return render_template('admin_login.html')


@admin_bp.route('/')
@login_required
@admin_required
def admin_dashboard():
    users = User.list_all()
    items = Item.list_all_admin()
    reports = Report.list_all()
    user_stats = User.get_stats()
    item_stats = Item.get_stats()
    pending_reports = Report.count_pending()

    # Message stats
    try:
        db_msg = Message
        from utils.db import get_db
        db = get_db()
        msg_count = db.execute("SELECT COUNT(*) AS c FROM messages").fetchone()['c']
    except Exception:
        msg_count = 0

    # Recent chats for admin monitoring
    try:
        from utils.db import get_db
        db = get_db()
        recent_chats = db.execute(
            "SELECT messages.*, s.username AS sender_name, r.username AS recipient_name "
            "FROM messages "
            "JOIN users AS s ON messages.sender_id = s.id "
            "JOIN users AS r ON messages.recipient_id = r.id "
            "ORDER BY messages.created_at DESC LIMIT 50"
        ).fetchall()
    except Exception:
        recent_chats = []

    # Popular wishlist items
    try:
        from utils.db import get_db
        db = get_db()
        wishlist_popular = db.execute(
            "SELECT items.id, items.title, COUNT(wishlist.id) AS wish_count "
            "FROM wishlist JOIN items ON wishlist.item_id = items.id "
            "GROUP BY items.id, items.title ORDER BY wish_count DESC LIMIT 10"
        ).fetchall()
    except Exception:
        wishlist_popular = []

    return render_template(
        'admin.html',
        users=users,
        items=items,
        reports=reports,
        user_stats=user_stats,
        item_stats=item_stats,
        pending_reports=pending_reports,
        msg_count=msg_count,
        recent_chats=recent_chats,
        wishlist_popular=wishlist_popular,
    )


# ── User Management ────────────────────────────────────────────────
@admin_bp.route('/user/<int:user_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_role(user_id):
    if user_id == session['user_id']:
        flash('You cannot change your own role.', 'warning')
    else:
        user = User.find_by_id(user_id)
        if user:
            User.update_role(user_id, not bool(user['is_admin']))
            flash('User role updated.', 'success')
    return redirect(url_for('admin.admin_dashboard') + '#users')


@admin_bp.route('/user/<int:user_id>/ban', methods=['POST'])
@login_required
@admin_required
def ban_user(user_id):
    if user_id == session['user_id']:
        flash('You cannot ban yourself.', 'warning')
    else:
        User.ban(user_id)
        flash('User has been banned.', 'success')
    return redirect(url_for('admin.admin_dashboard') + '#users')


@admin_bp.route('/user/<int:user_id>/unban', methods=['POST'])
@login_required
@admin_required
def unban_user(user_id):
    User.unban(user_id)
    flash('User has been unbanned.', 'success')
    return redirect(url_for('admin.admin_dashboard') + '#users')


@admin_bp.route('/user/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    if user_id == session['user_id']:
        flash('You cannot delete yourself.', 'danger')
    else:
        User.delete(user_id)
        flash('User and all their data have been deleted.', 'success')
    return redirect(url_for('admin.admin_dashboard') + '#users')


# ── Item Management ────────────────────────────────────────────────
@admin_bp.route('/item/<int:item_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_item(item_id):
    Item.delete(item_id)
    flash('Item removed from the marketplace.', 'success')
    return redirect(url_for('admin.admin_dashboard') + '#items')


@admin_bp.route('/item/<int:item_id>/flag', methods=['POST'])
@login_required
@admin_required
def flag_item(item_id):
    Item.flag_item(item_id)
    flash('Item has been flagged.', 'warning')
    return redirect(url_for('admin.admin_dashboard') + '#items')


@admin_bp.route('/item/<int:item_id>/mark-sold', methods=['POST'])
@login_required
@admin_required
def mark_sold(item_id):
    Item.mark_sold_admin(item_id)
    flash('Item marked as sold.', 'success')
    return redirect(url_for('admin.admin_dashboard') + '#items')


# ── Report Management ──────────────────────────────────────────────
@admin_bp.route('/report/<int:report_id>/resolve', methods=['POST'])
@login_required
@admin_required
def resolve_report(report_id):
    Report.resolve(report_id)
    flash('Report marked as resolved.', 'success')
    return redirect(url_for('admin.admin_dashboard') + '#reports')


@admin_bp.route('/report/<int:report_id>/ban-user', methods=['POST'])
@login_required
@admin_required
def report_ban_user(report_id):
    from utils.db import get_db
    db = get_db()
    row = db.execute("SELECT reported_user_id FROM reports WHERE id = %s", (report_id,)).fetchone()
    if row and row['reported_user_id']:
        User.ban(row['reported_user_id'])
        Report.resolve(report_id)
        flash('User banned and report resolved.', 'success')
    return redirect(url_for('admin.admin_dashboard') + '#reports')


@admin_bp.route('/report/<int:report_id>/delete-item', methods=['POST'])
@login_required
@admin_required
def report_delete_item(report_id):
    from utils.db import get_db
    db = get_db()
    row = db.execute("SELECT reported_item_id FROM reports WHERE id = %s", (report_id,)).fetchone()
    if row and row['reported_item_id']:
        Item.delete(row['reported_item_id'])
        Report.resolve(report_id)
        flash('Item deleted and report resolved.', 'success')
    return redirect(url_for('admin.admin_dashboard') + '#reports')
