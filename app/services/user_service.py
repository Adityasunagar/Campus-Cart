from models.user import User


def get_user_by_id(user_id):
    return User.find_by_id(user_id)
