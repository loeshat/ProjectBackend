"""
Search
Filename: search.py

Author: Jacqueline Chen (z5360310)
Created: 22.04.2022

Description: Allows the user to search for messages.
"""
from src.data_store import data_store
from src.error import InputError, AccessError
import src.other as other

def search_v1(auth_user_id:int, query_string:str)->dict:
    """
    Searches for the query string within all the messages that the user has access to

    Exceptions:
        InputError          - Occurs when the query_string is less 
                              than 1 character or greater than 1000 characters long

    Arguments:
        auth_user_id (int)  - The id of the user
        query_stirng (str)  - The string that the user is searching for

    Return Value:
        Returns { 'messages' } on successful creation
    """
    store = data_store.get()
    channels = store['channels']
    dms = store['dms']
    messages = store['messages']

    if len(query_string) > 1000 or len(query_string) < 1:
        raise InputError("The query's character count is out of bounds")

    query_messages = list()
    user_channels = list()
    user_dms = list()
    for channel_id, channel_info in channels.items():
        if other.check_user_in_channel(auth_user_id, channel_info):
            user_channels.append(channel_id)
    for dm_id, dm_info in dms.items():
        if other.check_user_in_dm(auth_user_id, dm_info):
            user_dms.append(dm_id)
    
    for message in messages.values():
        if message['is_channel'] and message['id'] in user_channels and query_string in message['message']:
            message = {k:v for k, v in message.items() if k not in ['is_channel', 'id']}
            query_messages.append(message)
        elif message['id'] in user_dms and query_string in message['message']:
            message = {k:v for k, v in message.items() if k not in ['is_channel', 'id']}
            query_messages.append(message)

    return {'messages': query_messages}
    
    
    