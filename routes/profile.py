from flask import Blueprint, render_template, session, redirect, url_for, flash
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
