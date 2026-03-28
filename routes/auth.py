from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.user import User
import psycopg2

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id'):
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = User.authenticate(email, password)

        if user == 'banned':
            flash('Your account has been banned. Contact admin for support.', 'danger')
            return redirect(url_for('auth.login'))

        if user:
            is_admin = bool(user['is_admin'])
            if is_admin:
                flash('Admins must log in via the admin portal.', 'warning')
                return redirect(url_for('auth.login'))

            session.clear()
            session['user_id'] = user['id']
            session['is_admin'] = False
            User.set_online(user['id'], True)
            flash(f"Welcome back, {user['username']}!", 'success')
            return redirect(url_for('main.index'))

        flash('Invalid email or password.', 'danger')

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('user_id'):
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')
        phone_number = request.form.get('phone_number', '').strip()
        is_admin = False

        if not username or not email or not password:
            flash('Please fill all fields.', 'warning')
        elif password != confirm:
            flash('Passwords do not match.', 'warning')
        else:
            try:
                User.create(username, email, password, phone_number=phone_number, is_admin=is_admin)
                flash('Account created successfully. Please log in.', 'success')
                return redirect(url_for('auth.login'))
            except psycopg2.IntegrityError:
                flash('Username or email already exists.', 'danger')

    return render_template('register.html')


@auth_bp.route('/logout')
def logout():
    user_id = session.get('user_id')
    if user_id:
        User.set_online(user_id, False)
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user = User.find_by_email(email)

        if user:
            # Generate a secure time-limited token
            from itsdangerous import URLSafeTimedSerializer
            from flask import current_app
            s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
            token = s.dumps(email, salt='password-reset-salt')
            reset_url = url_for('auth.reset_password', token=token, _external=True)

            # ── DEV MODE: Flash link on screen (replace with email in production) ──
            import logging
            logging.getLogger('werkzeug').warning(f'PASSWORD RESET LINK: {reset_url}')
            flash(f'Reset link generated! Click here to reset: <a href="{reset_url}" style="color:#ff007f;font-weight:700;">{reset_url}</a>', 'reset_link')
        else:
            # Don't reveal if email exists (security best practice)
            flash('If that email is registered, a reset link will appear below.', 'info')

        return redirect(url_for('auth.forgot_password'))

    return render_template('forgot_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
    from flask import current_app
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

    try:
        email = s.loads(token, salt='password-reset-salt', max_age=3600)  # 1 hour expiry
    except SignatureExpired:
        flash('This reset link has expired. Please request a new one.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    except BadSignature:
        flash('Invalid reset link. Please request a new one.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')

        if not password or len(password) < 6:
            flash('Password must be at least 6 characters.', 'warning')
            return render_template('reset_password.html', token=token)

        if password != confirm:
            flash('Passwords do not match.', 'warning')
            return render_template('reset_password.html', token=token)

        user = User.find_by_email(email)
        if user:
            User.update_password(user['id'], password)
            flash('Password updated successfully! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Account not found.', 'danger')
            return redirect(url_for('auth.forgot_password'))

    return render_template('reset_password.html', token=token)
