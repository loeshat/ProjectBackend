"""
Notifications
Filename: notifications.py

Author: Jacqueline Chen (z5360310)
Created: 11.04.2022

Description: Allows the user to receive notifiations when they are tagged in a message,
when a user reacts to their message and when they are added to a channel or dm.
"""
from src.data_store import data_store
from src.error import InputError, AccessError
import src.other as other

def notifications_get_v1(auth_user_id: int) -> dict:
    """
    Gets the 20 most recent notifcations for the user

    Exceptions:
        None

    Arguments:
        auth_user_id (int)  - The id of the user

    Return Value:
        Returns { 'notifications' } on successful creation
    """
    notifications = list()
    store = data_store.get()
    notifications = store['notifications']
    user_notifications = list()
    if notifications.get(auth_user_id):
        user_notifications = notifications[auth_user_id]
    if len(user_notifications) > 20:
        reversed_list = user_notifications[-20:]
        reversed_list.reverse()
        return {'notifications': reversed_list}
    user_notifications.reverse()
    return {'notifications': user_notifications}
