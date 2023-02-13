"""
Channels
Filename: channels.py

Author: Tetian Madfouni (z5361722), Jacqueline Chen (z5360310), Jerry Li (z5362290)
Created: 22.02.2022

Description: Allows the user to list channel info that they are apart of,
list channel info for all channels and create channels.
"""
from src.data_store import data_store
from src.error import InputError
import src.other as other


def channels_list_v2(auth_user_id: int)->dict:
    """
    Prints out the list of channels that the user is a member of
    In the format: { channels: [{}, {}, {}] }

    Arguments:
    auth_user_id (int)  - The id of the user
    Exceptions:
        AccessError     - Occurs when auth_user_id is invalid
    Return Value:
        Returns { channels } on successful creation
    """
    store = data_store.get()
    channels = store['channels']

    user_channels = []

    for channel_id, channel_details in channels.items():
        ids = [user['u_id'] for user in channel_details['all_members']]
        if auth_user_id in ids:
            user_channel = {'channel_id': channel_id, 'name': channel_details['name']}
            user_channels.append(user_channel)
    return {'channels': user_channels}


def channels_listall_v2(auth_user_id: int)->dict:
    """
    Allows a registered user to list all public and private channels

    Arguments:
       auth_user_id (int)   - The id of the user
    Exceptions:
        AccessError         - Occurs when auth_user_id is invalid
    Return Value:
        Returns { channels } on successful creation
    """

    store = data_store.get()
    channels = store['channels']
    return {'channels': [{'channel_id': key, 'name': channel['name']}
            for key, channel in channels.items()]}


def channels_create_v2(auth_user_id: int, name: str, is_public: bool)->dict:
    """
    Creates a new channel

    Arguments:
        auth_user_id (int)  - The id of the user
        name (string)       - Name of the channel
        is_public (bool)    - whether the channel is to be public or not

    Exceptions:
        InputError  - Occurs when channel name is too long or short
        AccessError - Occurs when user is not verified

    Return Value:
        Returns {channel_id} on successful creation

    Adds in format {'channel_id': int, 'name': str, 'public': bool, 'users': list(IDs)}
    """

    store = data_store.get()
    channels = store['channels']
    users = store['users']
    if len(name) > other.MAX_CHANNEL_NAME_LENGTH or len(name) < 1:
        raise InputError(description="Channel name too long or short")
    altered_users = {k: other.non_password_global_permission_field(v) for k,v in users.items()}
    for user_id, user in altered_users.items():
        user['u_id'] = user_id
        user['handle_str'] = user.pop('handle')
    new_channel_id = len(channels)
    channels[new_channel_id] = {'name': name, 'is_public': is_public,
                                'owner_members': [altered_users[auth_user_id]],
                                'all_members': [altered_users[auth_user_id]], 'messages': [],
                                'standup_active': False, 'standup_messages': '', 'standup_finish': ''}
    store['channels'] = channels
    other.user_stats_update(1,0,0,auth_user_id)
    other.server_stats_update(1,0,0)
    data_store.set(store)
    return(
        {'channel_id': new_channel_id}
    )
