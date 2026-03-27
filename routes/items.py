from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.item import Item, CATEGORIES
from models.wishlist import Wishlist
from models.report import Report
from utils.helpers import login_required

BANNED_KEYWORDS = ['spam', 'fake', 'scam', 'fraud', 'cheat', 'illegal', 'stolen']


main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    query = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    min_price = request.args.get('min_price', '').strip()
    max_price = request.args.get('max_price', '').strip()
    sort = request.args.get('sort', 'newest').strip()

    min_p = float(min_price) if min_price else None
    max_p = float(max_price) if max_price else None

    items = Item.list_all(
        category=category if category else None,
        min_price=min_p,
        max_price=max_p,
        sort=sort,
        search=query if query else None,
    )
    category_counts = Item.get_category_counts()

    return render_template(
        'index.html',
        items=items,
        query=query,
        active_category=category,
        min_price=min_price,
        max_price=max_price,
        active_sort=sort,
        categories=CATEGORIES,
        category_counts=category_counts,
    )


@main_bp.route('/item/<int:item_id>')
def item_detail(item_id):
    item = Item.get(item_id)
    if not item:
        flash('Item not found.', 'warning')
        return redirect(url_for('main.index'))

    in_wishlist = False
    if session.get('user_id'):
        in_wishlist = Wishlist.exists(session['user_id'], item_id)

    return render_template('detail.html', item=item, in_wishlist=in_wishlist)


@main_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_item():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        price = request.form.get('price', '').strip()
        category = request.form.get('category', 'Other').strip()

        if not title or not description or not price:
            flash('All fields are required.', 'warning')
        else:
            try:
                price_value = float(price)

                # Content moderation: block banned keywords
                combined = (title + ' ' + description).lower()
                for kw in BANNED_KEYWORDS:
                    if kw in combined:
                        flash(f'Your listing was blocked: contains flagged keyword "{kw}". Please revise your content.', 'danger')
                        return render_template('add.html', item=None, categories=CATEGORIES)

                
                # Handle image uploads
                base64_images = request.form.getlist('images')
                image_paths = []
                import os
                import base64
                import uuid
                from flask import current_app
                
                upload_dir = os.path.join(current_app.static_folder, 'uploads')
                os.makedirs(upload_dir, exist_ok=True)
                
                for b64 in base64_images:
                    if b64.startswith('data:image'):
                        header, data = b64.split(',', 1)
                        ext = header.split('/')[1].split(';')[0]
                        filename = f"{uuid.uuid4().hex}.{ext}"
                        filepath = os.path.join(upload_dir, filename)
                        with open(filepath, 'wb') as f:
                            f.write(base64.b64decode(data))
                        image_paths.append(f"uploads/{filename}")
                        
                Item.create(title, description, price_value, session['user_id'], image_paths, category)
                flash('Listing created successfully.', 'success')
                return redirect(url_for('main.index'))
            except ValueError:
                flash('Please enter a valid price.', 'warning')

    return render_template('add.html', item=None, categories=CATEGORIES)


@main_bp.route('/item/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    item = Item.get(item_id)
    if not item:
        flash('Item not found.', 'warning')
        return redirect(url_for('main.index'))

    if item['owner_id'] != session['user_id'] and not session.get('is_admin'):
        flash('You do not have permission to edit this item.', 'danger')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        price = request.form.get('price', '').strip()
        category = request.form.get('category', 'Other').strip()

        if not title or not description or not price:
            flash('All fields are required.', 'warning')
        else:
            try:
                price_value = float(price)
                Item.update(item_id, title, description, price_value, category)
                flash('Listing updated successfully.', 'success')
                return redirect(url_for('main.item_detail', item_id=item_id))
            except ValueError:
                flash('Please enter a valid price.', 'warning')

    return render_template('add.html', item=item, categories=CATEGORIES)


@main_bp.route('/item/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_item(item_id):
    item = Item.get(item_id)
    if not item:
        flash('Item not found.', 'warning')
        return redirect(url_for('main.index'))

    if item['owner_id'] != session['user_id'] and not session.get('is_admin'):
        flash('You do not have permission to delete this item.', 'danger')
        return redirect(url_for('main.index'))

    Item.delete(item_id)
    flash('Listing removed successfully.', 'success')
    return redirect(url_for('main.index'))


@main_bp.route('/item/<int:item_id>/buy', methods=['POST'])
@login_required
def buy_item(item_id):
    item = Item.get(item_id)
    if not item or item['status'] != 'available':
        flash('Item is no longer available.', 'danger')
        return redirect(url_for('main.index'))
        
    if item['owner_id'] == session['user_id']:
        flash('You cannot buy your own item.', 'warning')
        return redirect(url_for('main.item_detail', item_id=item_id))
        
    Item.mark_sold(item_id, session['user_id'])
    flash('Congratulations! You have purchased this item.', 'success')
    return redirect(url_for('profile.index'))


@main_bp.route('/wishlist')
@login_required
def wishlist():
    items = Wishlist.list_for_user(session['user_id'])
    return render_template('wishlist.html', items=items)


@main_bp.route('/wishlist/add/<int:item_id>', methods=['POST'])
@login_required
def add_wishlist(item_id):
    Wishlist.add(session['user_id'], item_id)
    flash('Added to your wishlist.', 'success')
    return redirect(url_for('main.item_detail', item_id=item_id))


@main_bp.route('/wishlist/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_wishlist(item_id):
    Wishlist.remove(session['user_id'], item_id)
    flash('Item removed from wishlist.', 'info')
    return redirect(request.referrer or url_for('main.wishlist'))


@main_bp.route('/report/item/<int:item_id>', methods=['POST'])
@login_required
def report_item(item_id):
    reason = request.form.get('reason', '').strip()
    if not reason:
        flash('Please provide a reason for the report.', 'warning')
        return redirect(request.referrer or url_for('main.index'))
    Report.create(reporter_id=session['user_id'], reason=reason, reported_item_id=item_id)
    flash('Report submitted. Our team will review it shortly.', 'success')
    return redirect(request.referrer or url_for('main.index'))


@main_bp.route('/report/user/<int:user_id>', methods=['POST'])
@login_required
def report_user(user_id):
    reason = request.form.get('reason', '').strip()
    if not reason:
        flash('Please provide a reason for the report.', 'warning')
        return redirect(request.referrer or url_for('main.index'))
    Report.create(reporter_id=session['user_id'], reason=reason, reported_user_id=user_id)
    flash('Report submitted. Our team will review it shortly.', 'success')
    return redirect(request.referrer or url_for('main.index'))
