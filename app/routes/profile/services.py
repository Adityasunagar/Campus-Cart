from models.user import User
from models.item import Item
from models.wishlist import Wishlist


def get_profile(user_id):
    user = User.find_by_id(user_id)
    listed_items = Item.list_by_owner(user_id)
    wishlist_items = Wishlist.list_for_user(user_id)
    purchased_items = Item.list_purchased(user_id)
    return {
        'user': user,
        'listed_items': listed_items,
        'wishlist_items': wishlist_items,
        'purchased_items': purchased_items,
    }
