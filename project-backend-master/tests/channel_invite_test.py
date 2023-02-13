from src.config import url
import requests
import pytest
import src.other as other

@pytest.fixture
def clear_store():
    requests.delete(other.CLEAR_URL, json={})

@pytest.fixture
def create_user():
    user_input = {'email': "z4323234@unsw.edu.au", 'password': "Password1", 'name_first': "Name1", 'name_last': "LastName1"}
    request_data = requests.post(other.REGISTER_URL, json=user_input)
    user_info = request_data.json()
    return user_info

@pytest.fixture
def create_user2():
    user_input = {'email': "z546326@unsw.edu.au", 'password': "Password2", 'name_first': "Name2", 'name_last': "LastName2"}
    request_data = requests.post(other.REGISTER_URL, json=user_input)
    user_info = request_data.json()
    return user_info

@pytest.fixture
def create_user3():
    user_input = {'email': "z5362601@unsw.edu.au", 'password': "Password3", 'name_first': "Name3", 'name_last': "LastName3"}
    request_data = requests.post(other.REGISTER_URL, json=user_input)
    user_info = request_data.json()
    return user_info


def check_user(user_token, u_id, channel_id):
    details = requests.get(other.CHANNEL_DETAILS_URL, params={'channel_id': channel_id, 'token': user_token}).json()
    user_was_added = False
    members = details['all_members']
    for member in members:
        if member['u_id'] == u_id:
            user_was_added = True

    return user_was_added


def test_invite_public(clear_store, create_user, create_user2):
    user_token_1 = create_user['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token_1, 'name': 'Channel1', 'is_public': True}).json()['channel_id']

    u_id = create_user2['auth_user_id']
    response = requests.post(other.CHANNEL_INVITE_URL, json={'token': user_token_1, 'channel_id': channel_id, 'u_id': u_id})
    assert response.status_code == 200
    
    assert check_user(user_token_1, u_id, channel_id)

def test_invite_private(clear_store, create_user, create_user2):
    user_token_1 = create_user['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token_1, 'name': 'Channel1', 'is_public': False}).json()['channel_id']

    u_id = create_user2['auth_user_id']
    response = requests.post(other.CHANNEL_INVITE_URL, json={'token': user_token_1, 'channel_id': channel_id, 'u_id': u_id})
    assert response.status_code == 200
    
    assert check_user(user_token_1, u_id, channel_id)

def test_invite_multiple(clear_store, create_user, create_user2, create_user3):
    user_token_1 = create_user['token']
    channel_id_1 = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token_1, 'name': 'Channel1', 'is_public': False}).json()['channel_id']
    channel_id_2 = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token_1, 'name': 'Channel2', 'is_public': True}).json()['channel_id']

    u_id_1 = create_user2['auth_user_id']
    user_token_2 = create_user2['token']
    u_id_2 = create_user3['auth_user_id']
    
    response_1 = requests.post(other.CHANNEL_INVITE_URL, json={'token': user_token_1, 'channel_id': channel_id_1, 'u_id': u_id_1})
    assert response_1.status_code == 200
    assert check_user(user_token_1, u_id_1, channel_id_1)
    
    response_2 = requests.post(other.CHANNEL_INVITE_URL, json={'token': user_token_2, 'channel_id': channel_id_1, 'u_id': u_id_2})
    response_3 = requests.post(other.CHANNEL_INVITE_URL, json={'token': user_token_1, 'channel_id': channel_id_2, 'u_id': u_id_2})
    assert response_2.status_code == 200
    assert response_3.status_code == 200
    
    assert check_user(user_token_1, u_id_2, channel_id_1)
    assert check_user(user_token_1, u_id_2, channel_id_2)

def test_invite_auth_user_id_invalid(clear_store, create_user, create_user2):
    user_token_1 = create_user['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token_1, 'name': 'Channel1', 'is_public': True}).json()['channel_id']
    requests.post(other.LOGOUT_URL, json={'token': user_token_1})

    u_id = create_user2['auth_user_id']
    response = requests.post(other.CHANNEL_INVITE_URL, json={'token': user_token_1, 'channel_id': channel_id, 'u_id': u_id})
    assert response.status_code == 403

def test_invite_error_invalid_channel(clear_store, create_user, create_user2):
    user_token_1 = create_user['token']
    u_id = create_user2['auth_user_id']
    response = requests.post(other.CHANNEL_INVITE_URL, json={'token': user_token_1, 'channel_id': None, 'u_id': u_id})
    assert response.status_code == 400

def test_invite_error_invalid_user(clear_store, create_user):
    user_token_1 = create_user['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token_1, 'name': 'Channel1', 'is_public': False}).json()['channel_id']
    response = requests.post(other.CHANNEL_INVITE_URL, json={'token': user_token_1, 'channel_id': channel_id, 'u_id': create_user['auth_user_id'] + 1})
    assert response.status_code == 400

def test_invite_error_already_joined(clear_store, create_user, create_user2):
    user_token_1 = create_user['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token_1, 'name': 'Channel1', 'is_public': True}).json()['channel_id']
    
    u_id = create_user2['auth_user_id']
    u_id_token = create_user2['token']
    requests.post(other.CHANNEL_JOIN_URL, json={'token': u_id_token, 'channel_id': channel_id})
    response = requests.post(other.CHANNEL_INVITE_URL, json={'token': user_token_1, 'channel_id': channel_id, 'u_id': u_id})
    assert response.status_code == 400   

def test_invite_error_not_member(clear_store, create_user, create_user2, create_user3):
    user_token_1 = create_user['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token_1, 'name': 'Channel1', 'is_public': True}).json()['channel_id']

    user_token_2 = create_user2['token']
    u_id = create_user3['auth_user_id']
    response = requests.post(other.CHANNEL_INVITE_URL, json={'token': user_token_2, 'channel_id': channel_id, 'u_id': u_id})
    assert response.status_code == 403
    
