import os
import uuid
from flask import Blueprint, render_template, session, redirect, url_for, flash, request, current_app
from werkzeug.utils import secure_filename
from models.user import User
from models.item import Item
from models.wishlist import Wishlist

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile')
def index():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to view your profile.', 'warning')
        return redirect(url_for('auth.login'))
        
    user = User.find_by_id(user_id)
    all_listed = Item.list_by_owner(user_id)
    listed_items = [item for item in all_listed if item['status'] == 'available']
    sold_items = [item for item in all_listed if item['status'] == 'sold']
    purchased_items = Item.list_purchased(user_id)
    wishlist_items = Wishlist.list_for_user(user_id)
    
    return render_template('profile.html', user=user, listed_items=listed_items, sold_items=sold_items, purchased_items=purchased_items, wishlist_items=wishlist_items)

@profile_bp.route('/profile/upload_photo', methods=['POST'])
def upload_photo():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))
        
    file = request.files.get('profile_photo')
    if file and file.filename:
        ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
            filename = f"user_{user_id}_{uuid.uuid4().hex}.{ext}"
            upload_dir = os.path.join(current_app.static_folder, 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            filepath = os.path.join(upload_dir, filename)
            file.save(filepath)
            
            User.update_profile_photo(user_id, f"uploads/{filename}")
            flash('Profile photo updated successfully!', 'success')
        else:
            flash('Invalid file format. Please upload an image.', 'danger')
            
    return redirect(url_for('profile.index'))

@profile_bp.route('/profile/update_details', methods=['POST'])
def update_details():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))
        
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip().lower()
    phone_number = request.form.get('phone_number', '').strip()
    
    if not username or not email:
        flash('Username and email are required.', 'danger')
        return redirect(url_for('profile.index'))
        
    try:
        User.update_details(user_id, username, email, phone_number)
        flash('Profile details updated successfully!', 'success')
        session['username'] = username # optionally update session cache if stored
    except Exception as e:
        flash('Failed to update details. Username or email might already be taken.', 'danger')
        
    return redirect(url_for('profile.index'))
