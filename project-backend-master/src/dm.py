"""
Dm
Filename: dm.py

Author: Jacqueline Chen (z5360310), Jerry Li (z5362290), Tetian Madfouni (z5361722)
Created: 22.03.2022

Description: Allows the user to create a dm, list dms, leave dms,
message in a dm, get details of a dm, and remove a dm.
"""
from time import time
from src.data_store import data_store
from src.error import InputError, AccessError
import src.other as other


def dm_create_v1(auth_user_id: int, u_ids: list) -> dict:
    """
    Creates a dm between the auth_user_id and the user(s) in the u_ids dict

    Exceptions:
        InputError          - Occurs when any u_id is invalid
        InputError          - Occurs when duplicate u_id occurs

    Arguments:
        auth_user_id (int)  - The id of the user
        u_ids (list)        - List of u_ids to add to the dm

    Return Value:
        Returns { 'dm_id' } on successful creation
    """
    store = data_store.get()
    dms = store['dms']
    users = store['users']

    for u_id in u_ids:
        if not other.verify_user(u_id):
            raise InputError(description="U_id not valid")

    user_set = set(u_ids)
    if len(user_set) < len(u_ids):
        raise InputError(description="Duplicate u_ids entered")
    if auth_user_id not in u_ids:
        u_ids.append(auth_user_id)

    members = []
    for id in u_ids:
        user = other.non_password_global_permission_field(users[id])
        user['u_id'] = id
        user['handle_str'] = user.pop('handle')
        members.append(user)
        other.user_stats_update(0,1,0,id)

    name = ''
    user_handles = []
    for id in u_ids:
        user_handles.append(users[id]['handle'])
    user_handles.sort()
    name = ', '.join(user_handles)

    dm_info = {}
    dm_id = len(dms)
    dm_info['owner_members'] = auth_user_id
    dm_info['name'] = name
    dm_info['members'] = members
    dm_info['messages'] = []
    dms[dm_id] = dm_info
    store['dms'] = dms

    for id in u_ids:
        if id != auth_user_id:
            other.create_notification(-1, dm_id, auth_user_id, id, name, None, 'added')
    other.server_stats_update(0,1,0)

    data_store.set(store)

    return {'dm_id': dm_id}


def dm_list_v1(auth_user_id: int) -> dict:
    """
    Lists all dms auth_user_id is apart of

    Exceptions:

    Arguments:
        auth_user_id (int)  - The id of the user

    Return Value:
        Returns { 'dms' } upon successful creation 
        in format {'dms': [{'dm_id': int, 'name': str}] } 
    """
    store = data_store.get()
    dms = store['dms']
    dm_list = []
    for key, value in dms.items():
        ids = [user['u_id'] for user in value['members']]
        if auth_user_id in ids:
            dm_list.append({'name': value['name'], 'dm_id': key})

    return {'dms': dm_list}


def dm_remove_v1(auth_user_id: int, dm_id: int) -> None:
    """
    Remove an existing DM, so all members are no longer in the DM. 
    This can only be done by the original creator of the DM.

    Exceptions:

    Arguments:
        auth_user_id (int)  - The id of the user
        dm_id (int)         - The id of the dm

    Return Value:
        None
    """

    store = data_store.get()
    dms = store['dms']
    users = store['users']
    if dm_id not in dms:
        raise InputError(description="dm_id is not valid")
    dm = dms[dm_id]
    msg_count = 0
    for msg in store['messages'].values():
        if msg['is_channel'] == False and msg['id'] == dm_id:
            msg_count += 1
    other.server_stats_update(0, -1, -msg_count)
    for user in dm['members']:
        other.user_stats_update(0,-1,0,user['u_id'])
    updated_messages = {msg_id: val for msg_id, val in store['messages'].items() if val['is_channel'] == True or val['id'] != dm_id}
    store['messages'] = updated_messages
    user = other.non_password_global_permission_field(users[auth_user_id])
    user['u_id'] = auth_user_id
    user['handle_str'] = user.pop('handle')
    if auth_user_id == dm['owner_members']:
        dms.pop(dm_id)
    elif user in dm['members']:
        raise AccessError(description="User is not the original DM creator")
    else:
        raise AccessError(description="User is not in DM")

    store['dms'] = dms
        
    data_store.set(store)
    return


def dm_details_v1(auth_user_id: int, dm_id: int) -> dict:
    """
    Returns details of the dm in a dict

    Exceptions:

    Arguments:
        auth_user_id (int)  - The id of the user
        dm_id (int)         - The id of the dm

    Return Value:
        Returns { 'name', 'members' } upon successful creation
    """
    store = data_store.get()
    dms = store['dms']

    if dm_id in dms.keys():
        dm = dms[dm_id]
    else:
        raise InputError(description="Dm_id not valid")

    dm_details = {}
    member_ids = [member['u_id'] for member in dm['members']]

    if auth_user_id in member_ids:
        dm_details['name'] = dm['name']
        dm_details['members'] = dm['members']
    else:
        raise AccessError(description="Auth_user_id not a member")

    data_store.set(store)
    return dm_details


def dm_leave_v1(auth_user_id: int, dm_id: int) -> None:
    """
    Removes auth_user_id from dm of dm_id

    Exceptions:

    Arguments:
        auth_user_id (int)      - The id of the user
        dm_id (int)             - The id of the dm

    Return Value:
        None
    """
    store = data_store.get()
    dms = store['dms']
    users = store['users']

    if dm_id in dms.keys():
        dm = dms[dm_id]
    else:
        raise InputError(description="Dm_id not valid")

    user = other.non_password_global_permission_field(users[auth_user_id])
    user['u_id'] = auth_user_id
    user['handle_str'] = user.pop('handle')
    if dm['owner_members'] == auth_user_id:
        dm['owner_members'] = None
        dm['members'].remove(user)
    elif user in dm['members']:
        dm['members'].remove(user)
    else:
        raise AccessError(description="User is not in DM")
    other.user_stats_update(0,-1,0, auth_user_id)
    store['dms'] = dms
    data_store.set(store)
    return None


def dm_send_v1(auth_user_id: int, message: str, dm_id: int) -> dict:
    """
    Allows a user to send a message in the specified DM

    Arguments:
        auth_user_id (int) - The user id of the sender
        message (str)      - The message to be sent
        dm_id (int)        - The id of the DM where the message will be sent to

    Errors
        AccessError        - Where the user does not belong to the specified DM
        InputError         - Where the DM id is invalid or the message is not between 1 and 1000 characters

    Return Value:
        Dictionary containing message_id, on success
    """
    store = data_store.get()
    dms = store['dms']
    if dm_id not in dms:
        raise InputError(description="dm_id is invalid")
    if len(message) > 1000 or len(message) < 1:
        raise InputError(description="Invalid message length")
    dm = dms[dm_id]
    u_ids = [user['u_id'] for user in dm['members']]
    if auth_user_id not in u_ids:
        raise AccessError(description="User is not part of DM")
    messages = store['messages']
    new_message_id = len(messages)
    messages[new_message_id] = {'message_id': new_message_id, 'u_id': auth_user_id, 'message': message,
                                'time_sent': time(), 'is_channel': False, 'id': dm_id, 'reacts': [], 'is_pinned': False}
    messages[new_message_id]['reacts'].append(
        {'react_id': 1, 'u_ids': [], 'is_this_user_reacted': False})

    if '@' in message:
        other.create_notification(-1, dm_id, auth_user_id, None, dm['name'], message, 'tagged')
    other.user_stats_update(0,0,1,auth_user_id)
    other.server_stats_update(0,0,1)

    data_store.set(store)
    return {'message_id': new_message_id}


def dm_messages_v1(auth_user_id: int, dm_id: int, start: int) -> dict:
    """
    Returns the messages of a dm from start index + 50

    Exceptions:

    Arguments:
        auth_user_id (int)      - The id of the user
        dm_id (int)             - The id of the dm
        start (int)             - The start index

    Return Value:
        Returns { 'messages', 'start', 'end' } upon successful creation
    """
    store = data_store.get()
    dms = store['dms']
    stored_messages = store['messages']
    if dm_id in dms:
        dm = dms[dm_id]
    else:
        raise InputError(description='dm_id does not refer to a valid channel')
    u_ids = [user['u_id'] for user in dm['members']]
    if auth_user_id not in u_ids:
        raise AccessError(
            description="dm_id is valid but user is not a member of the channel")
    dm_messages = []
    for message in stored_messages.values():
        if message != "invalid" and message['is_channel'] == False and message['id'] == dm_id:
            dm_messages.append({'message': message['message'], 'message_id': message['message_id'],
                               'u_id': message['u_id'], 'time_sent': message['time_sent'], 'reacts': message['reacts'], 'is_pinned': message['is_pinned']})
    if start > len(dm_messages):
        raise InputError(
            description="Start is greater than the total number of messages in channel")
    messages = []
    for message in dm_messages:
        message['reacts'][0]['is_this_user_reacted'] = auth_user_id in message['reacts'][0]['u_ids']
    not_displayed = list(reversed(dm_messages))[start:]
    messages.extend(
        not_displayed[:min(other.PAGE_THRESHOLD, len(not_displayed))])
    end = -1 if len(messages) == len(not_displayed) else start + \
        other.PAGE_THRESHOLD

    return {'messages': messages, 'start': start, 'end': end}
