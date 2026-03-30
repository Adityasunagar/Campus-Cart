from models.item import Item


def get_listing(item_id):
    return Item.get(item_id)


def list_available_items(**filters):
    return Item.list_all(**filters)
