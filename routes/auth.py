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
        is_admin = False

        if not username or not email or not password:
            flash('Please fill all fields.', 'warning')
        elif password != confirm:
            flash('Passwords do not match.', 'warning')
        else:
            try:
                User.create(username, email, password, is_admin=is_admin)
                flash('Account created successfully. Please log in.', 'success')
                return redirect(url_for('auth.login'))
            except psycopg2.IntegrityError:
                flash('Username or email already exists.', 'danger')

    return render_template('register.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))
