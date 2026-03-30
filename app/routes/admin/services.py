from models.user import User
from models.item import Item


def get_admin_dashboard():
    return {
        'users': User.list_all(),
        'items': Item.list_all_admin(),
    }
