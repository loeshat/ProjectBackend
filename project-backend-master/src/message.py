"""
Message
Filename: message.py

Author: Tetian Madfouni (z5361722), Jacqueline Chen (z5360310), Leo Shi (z5364321),
Samuel Bell (z5362604), Jerry Li (z5362290)
Created: 19.03.2022

Description: Allows the user to send, edit and remove messages.
"""
from time import time
from src.data_store import data_store
from src.error import InputError, AccessError
import src.other as other
import threading
from src.dm import dm_send_v1


def message_send_v1(user_id, channel_id, message):
    """
    Send a message from the authorised user to the channel specified by channel_id

    Exceptions:
        AccessError     - Occurs when channel_id is valid and the user is not a member of the channel
        InputError      - Occurs when channel_id is invalid
        InputError      - Occurs when the length of a message is < 1 or > 1000 characters

    Arguments:
        user_id (int)       - The token of the user
        channel_id (int)    - The id of the channel
        message (string)    - The message

    Return Value:
        Returns { message_id } when successful
    """
    store = data_store.get()
    channels = store['channels']

    if channel_id in channels.keys():
        message_channel = channels[channel_id]
    else:
        raise InputError(
            description="channel_id does not refer to a valid channel")

    if len(message) > 1000 or len(message) < 1:
        raise InputError(
            description="Length of message is less than 1 or over 1000 characters")
    if not other.check_user_in_channel(user_id, message_channel):
        raise AccessError(
            description="channel_id is valid and the user is not a member of the channel")
    messages = store['messages']
    new_message_id = len(messages)
    messages[new_message_id] = {'message_id': new_message_id, 'u_id': user_id,
                                'message': message, 'time_sent': time(), 'is_channel': True, 'id': channel_id, 'reacts': [], 'is_pinned': False}
    messages[new_message_id]['reacts'].append(
        {'react_id': 1, 'u_ids': [], 'is_this_user_reacted': False})

    if '@' in message:
        other.create_notification(channel_id, -1, user_id, None, message_channel['name'], message, 'tagged')
    other.user_stats_update(0, 0, 1, user_id)
    other.server_stats_update(0, 0, 1)
    data_store.set(store)
    return ({'message_id': new_message_id})


def message_edit_v1(user_id, message_id, message):
    """
    Given a message, update its text with new text. 
    If the new message is an empty string, the message is deleted.

    Exceptions:
        AccessError     - Occurs when the message_id is valid and the message was not sent by the user trying to edit
        AccessError     - Occurs when the message_id is valid and the user does not have owner permissions in the channel/DM
        InputError      - Occurs when the length of a message over 1000 characters
        InputError      - Occurs when message_id does not refer to a valid message within a channel

    Arguments:
        token (int)         - The token of the user
        message_id (int)    - The id of the message
        message (string)    - The message

    Return Value:
        Returns { } when successful
    """
    store = data_store.get()
    messages = store['messages']
    channels = store['channels']
    dms = store['dms']
    if message_id not in messages or messages[message_id] == "invalid":
        raise InputError(
            description="message_id does not refer to a valid message")
    else:
        curr_message = messages[message_id]
    if curr_message['is_channel'] == True:
        u_ids = [user['u_id']
                 for user in channels[curr_message['id']]['owner_members']]
        all_u_ids = [user['u_id']
                     for user in channels[curr_message['id']]['all_members']]
        if user_id not in u_ids and user_id not in all_u_ids:
            raise InputError(
                description="message_id is valid but user is not in channel")
        if curr_message['u_id'] != user_id and user_id not in u_ids:
            raise AccessError(
                description="message_id is valid but user does not have permissions to edit")
        channel_id = curr_message['id']
        dm_id = -1
        room_name = channels[channel_id]['name']
    else:
        u_ids = [user['u_id'] for user in dms[curr_message['id']]['members']]
        if user_id not in u_ids:
            raise InputError(
                description="message_id is valid but user is not in dm")
        channel_id = -1
        dm_id = curr_message['id']
        room_name = dms[dm_id]['name']
    if len(message) > 1000:
        raise InputError(description="message over 1000 characters")
    if message == '':
        message_remove_v1(user_id, message_id)
    else:
        curr_message['message'] = message
        messages['message'] = curr_message
        store['messages'] = messages
        if '@' in message:
            other.create_notification(channel_id, dm_id, user_id, None, room_name, message, 'tagged')
        data_store.set(store)
    
    return {}


def message_remove_v1(user_id, message_id):
    """
    Given a message_id for a message, this message is removed from the channel/DM

    Exceptions:
        AccessError     - Occurs when the message_id is valid and the message was not sent by the user trying to edit
        AccessError     - Occurs when the message_id is valid and the user does not have owner permissions in the channel/DM
        InputError      - Occurs when message_id does not refer to a valid message within a channel/DM  

    Arguments:
        token (int)         - The token of the user
        message_id (int)    - The id of the message

    Return Value:
        Returns {} when successful 
    """
    store = data_store.get()
    channels = store['channels']
    dms = store['dms']
    messages = store['messages']
    if message_id not in messages or messages[message_id] == "invalid":
        raise InputError(
            description="message_id does not refer to a valid message")
    else:
        message = messages[message_id]
    if message['is_channel'] == True:
        u_ids = [user['u_id']
                 for user in channels[message['id']]['owner_members']]
        all_u_ids = [user['u_id']
                     for user in channels[message['id']]['all_members']]
        if user_id not in u_ids and user_id not in all_u_ids:
            raise InputError(
                description="message_id is valid but user is not in channel")
        if message['u_id'] != user_id and user_id not in u_ids:
            raise AccessError(
                description="message_id is valid but user does not have permissions to remove")
    else:
        u_ids = [user['u_id'] for user in dms[message['id']]['members']]
        if user_id not in u_ids:
            raise InputError(
                description="message_id is valid but user is not in dm")
    messages.pop(message['message_id'])
    store['messages'] = messages
    other.server_stats_update(0, 0, -1)
    data_store.set(store)
    return {}


def message_pin_v1(user_id, message_id):
    """
    Given a message within a channel or DM, mark it as "pinned".

    Exceptions:
        AccessError     - Occurs when the message_id is valid and the user does not have owner permissions in the channel/DM
        InputError      - Occurs when the message_id is not a valid message within the channel/DM that the user has joined
        InputError      - Occurs when message is already pinned

    Arguments:
        token (int)         - The token of the user
        message_id (int)    - The id of the message

    Return Value:
        Returns {} when successful 
    """
    store = data_store.get()
    channels = store['channels']
    dms = store['dms']
    messages = store['messages']
    if message_id not in messages or messages[message_id] == "invalid":
        raise InputError(
            description="message_id does not refer to a valid message")
    else:
        message = messages[message_id]

    if message['is_channel'] == True:
        u_ids = [user['u_id']
                 for user in channels[message['id']]['owner_members']]
        all_u_ids = [user['u_id']
                     for user in channels[message['id']]['all_members']]
        if user_id not in u_ids and user_id not in all_u_ids:
            raise InputError(
                description="message and user are in different channels")
        if user_id not in u_ids:
            raise AccessError(
                description="message_id is valid but user does not have permissions to remove")
    else:
        u_ids = [user['u_id'] for user in dms[message['id']]['members']]
        if user_id not in u_ids:
            raise InputError(
                description="message and user are in different dms")

    if message['is_pinned'] == True:
        raise InputError(description="message is already pinned")
    else:
        message['is_pinned'] = True
    store['messages'] = messages
    data_store.set(store)
    return {}


def message_unpin_v1(user_id, message_id):
    """
    Given a message within a channel or DM, remove its mark it as "pinned".

    Exceptions:
        AccessError     - Occurs when the message_id is valid and the user does not have owner permissions in the channel/DM
        InputError      - Occurs when the message_id is not a valid message within the channel/DM that the user has joined
        InputError      - Occurs when message is not pinned

    Arguments:
        token (int)         - The token of the user
        message_id (int)    - The id of the message

    Return Value:
        Returns {} when successful 
    """
    store = data_store.get()
    channels = store['channels']
    dms = store['dms']
    messages = store['messages']
    if message_id not in messages:
        raise InputError(
            description="message_id does not refer to a valid message")
    else:
        message = messages[message_id]

    if message['is_channel'] == True:
        u_ids = [user['u_id']
                 for user in channels[message['id']]['owner_members']]
        all_u_ids = [user['u_id']
                     for user in channels[message['id']]['all_members']]
        if user_id not in u_ids and user_id not in all_u_ids:
            raise InputError(
                description="message and user are in different channels")
        if user_id not in u_ids:
            raise AccessError(
                description="message_id is valid but user does not have permissions to remove")
    else:
        u_ids = [user['u_id'] for user in dms[message['id']]['members']]
        if user_id not in u_ids:
            raise InputError(
                description="message and user are in different dms")

    if not message['is_pinned']:
        raise InputError(description="message is not pinned")
    else:
        message['is_pinned'] = False
    store['messages'] = messages
    data_store.set(store)
    return {}


def message_share_v1(u_id: int, og_message_id: int, message: str, channel_id: int, dm_id: int):
    store = data_store.get()
    if channel_id not in store['channels'] and dm_id not in store['dms']:
        raise InputError("No valid channel/dm id supplied")
    if channel_id == -1:
        is_channel = False
        destination = store['dms'][dm_id]
        all_u_ids = [user['u_id'] for user in destination['members']]
        all_u_ids.append(destination['owner_members'])
    else:
        is_channel = True
        destination = store['channels'][channel_id]
        all_u_ids = [user['u_id'] for user in destination['all_members']]
    messages = store['messages']
    if og_message_id not in messages:
        raise InputError("Invalid message id supplied")
    else:
        og_message = messages[og_message_id]
        if og_message['is_channel']:
            valid_users = [user['u_id']
                           for user in store['channels'][og_message['id']]['all_members']]
        else:
            valid_users = [user['u_id']
                           for user in store['dms'][og_message['id']]['members']]
            valid_users.append(store['dms'][og_message['id']]['owner_members'])
        if u_id not in valid_users:
            raise InputError(
                "User trying to share from channel/dm that they aren't part of")
    if u_id not in all_u_ids:
        raise AccessError(
            "User trying to share to channel/dm that they aren't part of")
    if len(message) > 1000:
        raise InputError("Message to be attached is too long")
    overall_message = "> " + og_message['message'] + "\n" + message
    if is_channel:
        message_id = message_send_v1(u_id, channel_id, overall_message)[
            'message_id']
    else:
        message_id = dm_send_v1(u_id, overall_message, dm_id)['message_id']
    data_store.set(store)
    return {"shared_message_id": message_id}


def message_react_v1(user_id, message_id, react_id):
    """
    Given a message within a channel or DM the authorised user is part of, remove a "react" to that particular message.

    Exceptions:
        InputError      - Occurs when the message_id is not a valid message within the channel
        InputError      - Occurs when the react_id is not a valid react ID, ie != 1
        InputError      - Occurs when the message already contains a react with ID react_id

    Arguments:
        token (int)         - The token of the user
        message_id (int)    - The id of the message
        react_id (int)      - The id of the react (1 == valid, 0 == invalid)

    Return Value:
        Returns {} when successful 
    """

    store = data_store.get()
    channels = store['channels']
    dms = store['dms']
    messages = store['messages']

    if message_id not in messages or messages[message_id] == "invalid":
        raise InputError(
            description="message_id does not refer to a valid message")
    else:
        message = messages[message_id]

    if message['is_channel'] == True:
        all_u_ids = [user['u_id']
                     for user in channels[message['id']]['all_members']]
        if user_id not in all_u_ids:
            raise InputError(
                description="user is not in the channel the message was sent from")
        channel_id = message['id']
        dm_id = -1
        room_name = channels[channel_id]['name']
    else:
        u_ids = [user['u_id'] for user in dms[message['id']]['members']]
        if user_id not in u_ids:
            raise InputError(
                description="user is not in the dm the message was sent from")
        channel_id = -1
        dm_id = message['id']
        room_name = dms[dm_id]['name']
    for react in message['reacts']:
        if react['react_id'] == react_id:
            if user_id in react['u_ids']:
                raise InputError(
                    description="message already contains a react from this user")
            else:
                react['u_ids'].append(user_id)
        else:
            raise InputError(description="react_id is not valid")
    store['messages'] = messages

    other.create_notification(channel_id, dm_id, user_id, message['u_id'], room_name, message, 'reacted')

    data_store.set(store)
    return {}


def message_unreact_v1(user_id, message_id, react_id):
    """
    Given a message_id for a message, the authroised user adds a 'react' to the message from the channel/DM

    Exceptions:
        InputError      - Occurs when the message_id is not a valid message within the channel
        InputError      - Occurs when the react_id is not a valid react ID, ie != 1
        InputError      - Occurs when the message already contains a react with ID react_id

    Arguments:
        token (int)         - The token of the user
        message_id (int)    - The id of the message
        react_id (int)      - The id of the react (1 == valid, 0 == invalid)

    Return Value:
        Returns {} when successful 
    """

    store = data_store.get()
    channels = store['channels']
    dms = store['dms']
    messages = store['messages']

    if message_id not in messages or messages[message_id] == "invalid":
        raise InputError(
            description="message_id does not refer to a valid message")
    else:
        message = messages[message_id]

    if message['is_channel'] == True:
        all_u_ids = [user['u_id']
                     for user in channels[message['id']]['all_members']]
        if user_id not in all_u_ids:
            raise InputError(
                description="user is not in the channel the message was sent from")
    else:
        u_ids = [user['u_id'] for user in dms[message['id']]['members']]
        if user_id not in u_ids:
            raise InputError(
                description="user is not in the dm the message was sent from")

    for react in message['reacts']:
        if react['react_id'] == react_id:
            if user_id in react['u_ids']:
                react['u_ids'].remove(user_id)
            else:
                raise InputError(
                    description="the message does not contain a react with ID react_id from the authorised user")
        else:
            raise InputError(description="react_id is not valid")
    store['messages'] = messages
    data_store.set(store)
    return {}


def message_sendlater_v1(auth_user_id: int, channel_id: int, message: str, time_sent: int) -> dict:
    """
    Allows the user to send a message at a specified time in the future

    Exceptions:
        AccessError     - Occurs when auth_user_id is not a member of the channel
        InputError      - Occurs when the channel_id is invalid
        InputError      - Occurs when the length of the message is not within the bounds
        InputError      - Occurs when the time sent is in the past

    Arguments:
        auth_user_id (int)      - The id of the user
        channel_id (int)        - The id of the channel
        message (str)           - The message that will be sent
        time_sent (int)         - The time that the message should be sent

    Return Value:
        Returns { 'message_id' } upon successful creation
    """
    store = data_store.get()
    messages = store['messages']
    channels = store['channels']

    if time_sent < time():
        raise InputError(description="The specified time is in the past")
    if channel_id in channels.keys():
        message_channel = channels[channel_id]
    else:
        raise InputError(
            description="Channel_id does not refer to a valid channel")

    if len(message) > 1000 or len(message) < 1:
        raise InputError(
            description="Length of message is less than 1 or over 1000 characters")
    if not other.check_user_in_channel(auth_user_id, message_channel):
        raise AccessError(
            description="channel_id is valid and the user is not a member of the channel")

    message_id = len(messages)
    messages[message_id] = "invalid"
    message_thread = threading.Thread(target=other.sendlater_thread_function, args=(
        auth_user_id, message_id, channel_id, -1, time_sent, message), daemon=True)
    message_thread.start()

    data_store.set(store)
    return ({'message_id': message_id})

def message_sendlaterdm_v1(auth_user_id:int, dm_id:int, message:str, time_sent:int)->dict:
    """
    Allows the user to send a message at a specified time in the future

    Exceptions:
        AccessError     - Occurs when auth_user_id is not a member of the channel
        InputError      - Occurs when the channel_id is invalid
        InputError      - Occurs when the length of the message is not within the bounds
        InputError      - Occurs when the time sent is in the past

    Arguments:
        auth_user_id (int)      - The id of the user
        dm_id (int)             - The id of the channel
        message (str)           - The message that will be sent
        time_sent (int)         - The time that the message should be sent

    Return Value:
        Returns { 'message_id' } upon successful creation
    """
    store = data_store.get()
    messages = store['messages']
    dms = store['dms']

    if time_sent < time():
        raise InputError(description="The specified time is in the past")
    if dm_id in dms.keys():
        message_dm = dms[dm_id]
    else:
        raise InputError(description="Channel_id does not refer to a valid channel")

    if len(message) > 1000 or len(message) < 1:
        raise InputError(
            description="Length of message is less than 1 or over 1000 characters")
    if not other.check_user_in_dm(auth_user_id, message_dm):
        raise AccessError(
            description="channel_id is valid and the user is not a member of the channel")

    message_id = len(messages)
    messages[message_id] = "invalid"
    message_thread = threading.Thread(target = other.sendlater_thread_function, args = (auth_user_id, message_id, -1, dm_id, time_sent, message), daemon = True)
    message_thread.start()

    data_store.set(store)
    return ({'message_id': message_id})