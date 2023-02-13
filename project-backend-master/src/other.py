import hashlib
import secrets
from src.data_store import data_store
from time import time, sleep
import jwt
import re
from src.config import url
from time import time

MAX_FIRST_NAME_LENGTH = 50
MAX_LAST_NAME_LENGTH = 50
MAX_CHANNEL_NAME_LENGTH = 20

GLOBAL_PERMISSION_OWNER = 1
GLOBAL_PERMISSION_USER = 2
GLOBAL_PERMISSION_REMOVED = 0

PAGE_THRESHOLD = 50



JWT_SECRET = "COMP1531_H13A_CAMEL"
SENDER_ADDRESS = "comp1531h13acamel@gmail.com"

LOGIN_URL = f"{url}/auth/login/v2"
REGISTER_URL = f"{url}/auth/register/v2"
CHANNELS_CREATE_URL = f"{url}/channels/create/v2"
CHANNELS_LISTALL_URL = f"{url}/channels/listall/v2"
CHANNEL_DETAILS_URL = f"{url}/channel/details/v2"
CHANNEL_JOIN_URL = f"{url}/channel/join/v2"
CHANNEL_INVITE_URL = f"{url}/channel/invite/v2"
CHANNEL_MESSAGES_URL = f"{url}/channel/messages/v2"
CHANNELS_LIST_URL = f"{url}/channels/list/v2"
CLEAR_URL = f"{url}/clear/v1"
LOGOUT_URL = f"{url}/auth/logout/v1"
CHANNEL_LEAVE_URL = f"{url}/channel/leave/v1"
CHANNEL_ADDOWNER_URL = f"{url}/channel/addowner/v1"
CHANNEL_REMOVEOWNER_URL = f"{url}/channel/removeowner/v1"
MESSAGE_SEND_URL = f"{url}/message/send/v1"
MESSAGE_EDIT_URL = f"{url}/message/edit/v1"
MESSAGE_REMOVE_URL = f"{url}/message/remove/v1"
DM_CREATE_URL = f"{url}/dm/create/v1"
DM_LIST_URL = f"{url}/dm/list/v1"
DM_REMOVE_URL = f"{url}/dm/remove/v1"
DM_DETAILS_URL = f"{url}/dm/details/v1"
DM_LEAVE_URL = f"{url}/dm/leave/v1"
DM_MESSAGES_URL = f"{url}/dm/messages/v1"
MESSAGE_SENDDM_URL = f"{url}/message/senddm/v1"
USERS_ALL_URL = f"{url}/users/all/v1"
USER_PROFILE_URL = f"{url}/user/profile/v1"
USER_SETNAME_URL = f"{url}/user/profile/setname/v1"
USER_SETEMAIL_URL = f"{url}/user/profile/setemail/v1"
USER_SETHANDLE_URL = f"{url}/user/profile/sethandle/v1"
USER_REMOVE_URL = f"{url}/admin/user/remove/v1"
CHANGE_PERM_URL = f"{url}/admin/userpermission/change/v1"
NOTIFICATIONS_GET_URL = f"{url}/notifications/get/v1"
SEARCH_URL = f"{url}/search/v1"
MESSAGE_SHARE_URL = f"{url}/message/share/v1"
MESSAGE_REACT_URL = f"{url}/message/react/v1"
MESSAGE_UNREACT_URL = f"{url}/message/unreact/v1"
MESSAGE_PIN_URL = f"{url}/message/pin/v1"
MESSAGE_UNPIN_URL = f"{url}/message/unpin/v1"
MESSAGE_SENDLATER_URL = f"{url}/message/sendlater/v1"
MESSAGE_SENDLATERDM_URL = f"{url}/message/sendlaterdm/v1"
STANDUP_START_URL = f"{url}/standup/start/v1"
STANDUP_ACTIVE_URL = f"{url}/standup/active/v1"
STANDUP_SEND_URL = f"{url}/standup/send/v1"
AUTH_PASSWORDRESET_REQUEST_URL = f"{url}/auth/passwordreset/request/v1"
AUTH_PASSWORDRESET_RESET_URL = f"{url}/auth/passwordreset/reset/v1"
USER_UPLOADPHOTO_URL = f"{url}/user/profile/uploadphoto/v1"
USER_STATS_URL = f"{url}/user/stats/v1"
USERS_STATS_URL = f"{url}/users/stats/v1"
RESET_PASSWORD_REQUEST_URL = f"{url}/auth/passwordreset/request/v1"
RESET_PASSWORD_URL = f"{url}/auth/passwordreset/reset/v1"

def clear_v1():
    """
    This function clears the data store environment for each test

    Arguments:
        None

    Return Value:
        None

    """
    print("Clearing store....")
    store = data_store.get()
    store['users'] = {}
    store['channels'] = {}
    store['dms'] = {}
    store['messages'] = {}
    store['notifications'] = {}
    store['user_stats'] = {}
    store['server_stats'] = {}
    store['reset_codes'] = {}
    data_store.set(store)

def verify_user(auth_user_id: int)->bool:
    """
    This function takes a user ID and validates that they are registered in the system

    Arguments:
        auth_user_id (int)    - The id to validate

    Return Value:
        Returns True if it is registered, False if not

    """
    users = data_store.get()['users']
    return bool(auth_user_id in users.keys())

def is_global_user(auth_user_id: int)->bool:
    """
    This function checks whether a user has global permissions

    Arguments:
        auth_user_id (int)  - id to check
    
    Return value:
        Returns True (Bool) is the user has global user permissions False if not
    
    """
    users = data_store.get()['users']
    return bool(users[auth_user_id]['global_permission'] == GLOBAL_PERMISSION_OWNER)

def user_id_from_JWT(token: str)->int:
    """
    This function extracts the user from a given token, assumes the token is valid

    Arguments:
        token (str) - the valid token from the user
    
    Return Value:
        The user id of the token
    """
    jwt_payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    return int(jwt_payload['auth_user_id'])

def non_password_global_permission_field(user: dict)->dict:
    """
    Removes all non-password fields from a user to print them

    Arguments:
        user (dict) - dictionary of all user details

    Returns:
        Dictionary with password field removed

    """
    user = {k: v for k, v in user.items() if k not in ['password', 'global_permission', 'sessions']}
    return user

def is_handle_taken(handle: str)->bool:
    """
    This function checks whether a handle is used before in the data store

    Arguments:
        handle (string)    - Handle to check

    Return Value:
        Returns True if the handle is taken
        Returns False if it is not taken

    """
    store = data_store.get()
    users = store['users']
    for user in users.values():
        if user['handle'] == handle:
            return True
    return False


def is_valid_email(email: str)->bool:
    """
    Verifies whether an email is valid or not

    Arguments:
        email (string)    - Email to check

    Return Value:
        Returns True if the email is valid and False if it is not
    """
    return bool(re.search(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$', email))


def remove_non_alphanumeric(string: str)->str:
    """
    Strips all alpha numeric characters from the input string

    Arguments:
        string (string)    - The string to have alphanumeric characters removed

    Return Value:
        Returns alnumString (string)
    """
    alnum_list = [char for char in string if char.isalnum()]
    return "".join(alnum_list)


def generate_handle(name_first:str, name_last:str)->str:
    """
    This function generates a handle for a user, the users first and last names
    are concatenated and turned lower case (if this is over 20 it is trimmed to 20).
    If that handle is taken a number is added to the end.

    Arguments:
        name_first (string)    - User's first name
        name_last (string)     - User's last name

    Return Value:
        Returns handle (string)

    """
    stripped_concatenated_name = remove_non_alphanumeric(name_first+name_last)
    stripped_concatenated_name = stripped_concatenated_name.lower()
    if len(stripped_concatenated_name) > 20:
        stripped_concatenated_name = stripped_concatenated_name[0:20]

    end_number = 0
    while is_handle_taken(stripped_concatenated_name):
        if end_number == 0:
            stripped_concatenated_name += str(end_number)
        else:
            stripped_concatenated_name = stripped_concatenated_name[:-1] + str(end_number)

        end_number += 1

    return stripped_concatenated_name

def is_email_taken(email: str)->bool:

    """
    Checks whether an email is used in the data store

    Arguments:
        email (string)    - The email to check

    Return Value:
        Returns True if it is taken
        Returns False if it is not taken

    """
    store = data_store.get()
    users = store['users']
    for user in users.values():
        if user['email'] == email:
            return True
    return False

def id_from_email(email: str)->int:
    """
    Converts an email to a user id

    Arguments:
        email (string)  - email to be converted
    
    Return Value:
        id (int) of the user on success
        None if the user is not founf
    
    """
    store = data_store.get()
    users = store['users']
    for id, user in users.items():
        if user['email'] == email:
            return int(id)
    return None

def is_valid_JWT(jwt_string: str)->bool:
    """
    Verifies whether a JWT is valid

    Arguments:
        jwt_string (str) - The string which needs to be verified

    Return Value:
        False if the JWT has been forged with a different secret, false if there is no session with the JWT,
        false if the user id does not exist. True if none of those conditions are met (a valid JWT).

    """
    try:
        jwt_payload = jwt.decode(jwt_string, JWT_SECRET, algorithms=['HS256'])
    except:
        return False
    store = data_store.get()
    users = store['users']
    if not verify_user(jwt_payload['auth_user_id']):
        return False
    if jwt_payload['user_session_id'] not in users[jwt_payload['auth_user_id']]['sessions']:
        return False
    return True

def create_JWT(auth_user_id: int)->str:
    """
    Creates a valid JWT from the auth user id, adds new session to user sessions

    Arguments:
        auth_user_id (int) - the user to get the JWT

    Return Value:
        The string of the new JWT, with the auth_user_id and session_id encoded
    """
    store = data_store.get()
    new_session = len(store['users'][auth_user_id]['sessions'])
    store['users'][auth_user_id]['sessions'].append(new_session)
    payload = {'auth_user_id': auth_user_id, 'user_session_id': new_session}
    data_store.set(store)
    new_jwt = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
    return new_jwt

def generate_reset_code(email: str)->int:
    """
    Generates a rest code for the given email

    Arguments:
        Email (str)     - Email for which the code will be generated for

    Return Value:
        An integer representing the code
    
    """
    payload = email + str(secrets.randbits(128))
    hash = hashlib.sha256(payload.encode()).hexdigest()
    return int(hash[0:6], 16)


def check_user_in_channel(auth_user_id:int, channel:dict)->bool:
    """
    Checks whether a user is in a channel or not

    Arguments:
        user_id (int)   - the id of the user
        channel (dict)  - the channel to check

    Returns:
        A boolean, true if the user is in the channel, false if not
    """
    ids = [user['u_id'] for user in channel['all_members']]
    return bool(auth_user_id in ids)

def check_user_in_dm(auth_user_id:int, dm:dict)->bool: 
    """
    Checks whether a user is in a dm or not

    Arguments:
        user_id (int)   - the id of the user
        dm (dict)       - the dm to check

    Returns:
        A boolean, true if the user is in the dm, false if not
    """
    ids = [user['u_id'] for user in dm['members']]
    return bool(auth_user_id in ids)

def check_user_is_member(auth_user_id:int, dm_id:int, channel_id:int)->bool:
    """
    Checks whether a user is in a dm or a channel

    Arguments:
        auth_user_id (int)      - the id of the user
        dm_id (int)             - the dm_id of the dm to check
        channel_id (int)        - the channel_id of the channel to check

    Returns:
        A boolean, true if the user is in the dm or channel, false if not
    """
    store = data_store.get()
    channels = store['channels']
    dms = store['dms']
    if dm_id < 0:
        is_member = check_user_in_channel(auth_user_id, channels[channel_id])
    else:
        is_member = check_user_in_dm(auth_user_id, dms[dm_id])
    return is_member

def id_to_handle(auth_user_id:int)->str:
    """
    Gets the handle from a user_id

    Arguments:
        auth_user_id (int)   - the id of the user

    Returns:
        A handle string corresponding to the user_id
    """
    store = data_store.get()
    users = store['users']
    return users[auth_user_id]['handle']

def handle_to_id(user_handle:str)->int:
    """
    Gets the user_id from a handle string

    Arguments:
        user_handle (str)   - the id of the user

    Returns:
        A user_id corresponding to the handle string
    """
    store = data_store.get()
    users = store['users']
    user_handles_id = {user_info['handle']:user_id for user_id, user_info in users.items()}
    return user_handles_id[user_handle]

def get_handles(message:str)->list:
    """
    Extracts the handles in a message

    Arguments:
        message (str)   - the message that may contain handles

    Returns:
        A list of all valid handles
    """
    store = data_store.get()
    users = store['users']
    letters = list(message)
    at_array = list()
    handles = list()
    counter = -1
    for index, letter in enumerate(letters):
        if (letter == '@'):
            at_array.append(index)

    for at_index in at_array:
        handles.append('')
        counter += 1
        # Should change later because of nesting but I'm not bothered right now sorry
        for letter in letters[at_index + 1:]:
            if letter.isalpha():
                handles[counter] += letter
            else:
                break

    valid_handles = list()
    user_handles = [user_info['handle'] for user_info in users.values()]
    for handle in handles:
        if handle in user_handles:
            valid_handles.append(handle)
    return list(set(valid_handles))

def create_notification(channel_id:int, dm_id:int, auth_user_id:int, u_id:int, room_name:str, message:str, type:str)->None:
    """
    Creates a notification

    Arguments:
        channel_id (int)    - The id of the channel if applicable
        dm_id (int)         - The id of the dm if applicable
        auth_user_id (int)  - The id of the user who triggered the action if applicable
        u_id (int)          - The id of the user who receives the notification if applicable
        room_name (str)     - The name of the channel/dm
        message (str)       - The message in which the notification may be for
        type (str)          - The notification type

    Returns:
        None
    """
    store = data_store.get()
    notifications = store['notifications']
    user_handle = id_to_handle(auth_user_id)

    if type == 'tagged':
        handles = get_handles(message)
        for handle in handles:
            u_id = handle_to_id(handle)
            is_member = check_user_is_member(u_id, dm_id, channel_id)
            if is_member and not notifications.get(u_id):
                notifications[u_id] = list()
                notifications[u_id].append({'channel_id': channel_id, 'dm_id': dm_id, 
                                        'notification_message': f"{user_handle} tagged you in {room_name}: {message[:20]}"})
            elif is_member:
                notifications[u_id].append({'channel_id': channel_id, 'dm_id': dm_id, 
                                        'notification_message': f"{user_handle} tagged you in {room_name}: {message[:20]}"})

    if type == 'reacted':
        is_member = check_user_is_member(u_id, dm_id, channel_id)
        if is_member and not notifications.get(u_id):
            notifications[u_id] = list()
            notifications[u_id].append({'channel_id': channel_id, 'dm_id': dm_id, 
                                        'notification_message': f"{user_handle} reacted to your message in {room_name}"})
        elif is_member:
            notifications[u_id].append({'channel_id': channel_id, 'dm_id': dm_id, 
                                        'notification_message': f"{user_handle} reacted to your message in {room_name}"})

    if type == 'added':
        if not notifications.get(u_id):
            notifications[u_id] = list()
        notifications[u_id].append({'channel_id': channel_id, 'dm_id': dm_id, 
                                        'notification_message': f"{user_handle} has added you to {room_name}"})

    data_store.set(store)

def user_stats_update(channels: int, dms: int, messages: int, u_id: int):
    store = data_store.get()
    user_stats = store['user_stats'][u_id]
    changes = user_stats['stats']
    current = changes[len(changes) - 1]
    new_stats = current.copy()
    new_stats['num_channels'] += channels
    new_stats['num_dms'] += dms
    new_stats['num_msg'] += messages
    new_stats['time'] = time()
    store['user_stats'][u_id]['stats'].append(new_stats)
    data_store.set(store)
    
def server_stats_update(channels: int, dms: int, messages: int):
    store = data_store.get()
    server_stats = store['server_stats']
    changes = server_stats['stats']
    current = changes[len(changes) - 1]
    new_stats = current.copy()
    new_stats['num_channels'] += channels
    new_stats['num_dms'] += dms
    new_stats['num_msg'] += messages
    new_stats['time'] = time()
    store['server_stats']['stats'].append(new_stats)
    data_store.set(store)
    
def sendlater_thread_function(auth_user_id:int, message_id:int, channel_id:int, 
                                dm_id:int, time_sent:int, message:str)->None:
    """
    Thread that sends the message at a specified time

    Arguments:
        auth_user_id (int)      - the id of the user
        message_id (int)        - the id of the message
        channel_id (int)        - the id of the channel
        dm_id (int)             - the id of the dm
        time_sent (int)         - the time that the message should be sent
        message (str)           - the message

    Returns:
        None
    """
    store = data_store.get()
    messages = store['messages']
    dms = store['dms']
    channels = store['channels']

    sleep(time_sent - time())
    server_stats_update(0,0,1)
    user_stats_update(0,0,1,auth_user_id)
    if channel_id < 0:
        messages[message_id] = {'message_id': message_id, 'u_id': auth_user_id,
                            'message': message, 'time_sent': time_sent, 'is_channel': False, 'id': dm_id, 
                            'reacts': [{'react_id': 1, 'u_ids': [], 'is_this_user_reacted': False}], 'is_pinned': False}
        room_name = dms[dm_id]['name']
    else: 
        messages[message_id] = {'message_id': message_id, 'u_id': auth_user_id,
                            'message': message, 'time_sent': time_sent, 'is_channel': True, 'id': channel_id, 
                            'reacts': [{'react_id': 1, 'u_ids': [], 'is_this_user_reacted': False}], 'is_pinned': False}
        room_name = channels[channel_id]['name']

    if '@' in message:
        create_notification(channel_id, dm_id, auth_user_id, None, room_name, message, 'tagged')


