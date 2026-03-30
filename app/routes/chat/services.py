from models.message import Message


def get_conversation(user_id, recipient_id):
    return Message.list_conversation(user_id, recipient_id)


def get_partners(user_id):
    return Message.list_partners(user_id)
