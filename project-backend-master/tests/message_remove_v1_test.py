from src.config import url
import pytest
import requests
import src.other as other

@pytest.fixture
def clear_store():
    requests.delete(other.CLEAR_URL, json={})


@pytest.fixture
def create_user():
    user_input = {'email': "z432324@unsw.edu.au",
                  'password': "badpassword123", 'name_first': "Ji", 'name_last': "Sun"}
    request_data = requests.post(other.REGISTER_URL, json=user_input)
    user_info = request_data.json()
    return user_info


@pytest.fixture
def create_user2():
    user_input = {'email': "z54626@unsw.edu.au", 'password': "Password",
                  'name_first': "Jane", 'name_last': "Gyuri"}
    request_data = requests.post(other.REGISTER_URL, json=user_input)
    user_info = request_data.json()
    return user_info


def test_basic_message_removal(clear_store, create_user):
    user_token_1 = create_user['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={
                               'token': user_token_1, 'name': 'My Channel!', 'is_public': True}).json()['channel_id']

    message_id = requests.post(other.MESSAGE_SEND_URL, json={'token': user_token_1, 'channel_id': channel_id, 'message': "Hello World"}).json()['message_id']
    response = requests.get(other.CHANNEL_MESSAGES_URL, params={'channel_id': channel_id, 'start': 0, 'token': user_token_1})
    assert response.json() != {'messages': [], 'start': 0, 'end': -1}
    response = requests.delete(other.MESSAGE_REMOVE_URL, json={'token': user_token_1, 'message_id': message_id})
    assert response.status_code == 200
    response = requests.get(other.CHANNEL_MESSAGES_URL, params={'channel_id': channel_id, 'start': 0, 'token': user_token_1})
    assert response.status_code == 200
    assert response.json() == {'messages': [], 'start': 0, 'end': -1}


def test_message_already_removed(clear_store, create_user):
    user_token_1 = create_user['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={
                               'token': user_token_1, 'name': 'My Channel!', 'is_public': True}).json()['channel_id']

    message_id = requests.post(other.MESSAGE_SEND_URL, json={'token': user_token_1, 'channel_id': channel_id, 'message': "Hello World"}).json()['message_id']
    response = requests.get(other.CHANNEL_MESSAGES_URL, params={'channel_id': channel_id, 'start': 0, 'token': user_token_1})
    assert response.json() != {'messages': [], 'start': 0, 'end': -1}
    response = requests.delete(other.MESSAGE_REMOVE_URL, json={'token': user_token_1, 'message_id': message_id})
    assert response.status_code == 200
    response = requests.get(other.CHANNEL_MESSAGES_URL, params={'channel_id': channel_id, 'start': 0, 'token': user_token_1})
    assert response.status_code == 200
    assert response.json() == {'messages': [], 'start': 0, 'end': -1}
    response = requests.delete(other.MESSAGE_REMOVE_URL, json={'token': user_token_1, 'message_id': message_id})
    assert response.status_code == 400


def test_message_id_invalid(clear_store, create_user):
    user_token_1 = create_user['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={
                               'token': user_token_1, 'name': 'My Channel!', 'is_public': True}).json()['channel_id']
    message_id = requests.post(other.MESSAGE_SEND_URL, json={'token': user_token_1, 'channel_id': channel_id, 'message': "Hello World"}).json()['message_id']
    response = requests.delete(other.MESSAGE_REMOVE_URL, json={'token': user_token_1, 'message_id': message_id + 1})
    assert response.status_code == 400


def test_user_id_didnt_send_message(clear_store, create_user, create_user2):
    user_token_1 = create_user['token']
    user_token_2 = create_user2['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={
                               'token': user_token_1, 'name': 'My Channel!', 'is_public': True}).json()['channel_id']

    response = requests.post(other.CHANNEL_JOIN_URL, json={
                             'token': user_token_2, 'channel_id': channel_id})  
    assert response.status_code == 200
    message_id = requests.post(other.MESSAGE_SEND_URL, json={'token': user_token_1, 'channel_id': channel_id, 'message': "Hello World"}).json()['message_id']
    response = requests.delete(other.MESSAGE_REMOVE_URL, json={'token': user_token_2, 'message_id': message_id})
    assert response.status_code == 403

def test_user_without_permissions(clear_store, create_user, create_user2):
    user_token_1 = create_user['token']
    user_token_2 = create_user2['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={
                               'token': user_token_1, 'name': 'My Channel!', 'is_public': True}).json()['channel_id']

    response = requests.post(other.CHANNEL_JOIN_URL, json={
                             'token': user_token_2, 'channel_id': channel_id})  
    assert response.status_code == 200
    message_id = requests.post(other.MESSAGE_SEND_URL, json={'token': user_token_2, 'channel_id': channel_id, 'message': "Leo loves coding!"}).json()['message_id']
    response = requests.delete(other.MESSAGE_REMOVE_URL, json={'token': user_token_2, 'message_id': message_id})
    assert response.status_code == 200

def test_user_leaves_channel(clear_store, create_user):
    user_token_1 = create_user['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={
                               'token': user_token_1, 'name': 'My Channel!', 'is_public': True}).json()['channel_id']
    message_id = requests.post(other.MESSAGE_SEND_URL, json={'token': user_token_1, 'channel_id': channel_id, 'message': "Hello World"}).json()['message_id']
    response = requests.post(other.CHANNEL_LEAVE_URL, json={'token': user_token_1, 'channel_id': channel_id})
    response = requests.delete(other.MESSAGE_REMOVE_URL, json={'token': user_token_1, 'message_id': message_id})
    assert response.status_code == 400
    
def test_normal_dm(clear_store, create_user):
    user_1 = create_user
    dm_id = requests.post(other.DM_CREATE_URL, json={'token': user_1['token'], 'u_ids': []}).json()['dm_id']
    message_id = requests.post(other.MESSAGE_SENDDM_URL, json={'token': user_1['token'], 'dm_id': dm_id, 'message': 'hey there'}).json()['message_id']
    response = requests.delete(other.MESSAGE_REMOVE_URL, json={'token': user_1['token'], 'message_id': message_id})
    assert response.status_code == 200

def test_user_not_in_dm(clear_store, create_user, create_user2):
    user_1 = create_user
    dm_id = requests.post(other.DM_CREATE_URL, json={'token': user_1['token'], 'u_ids': []}).json()['dm_id']
    message_id = requests.post(other.MESSAGE_SENDDM_URL, json={'token': user_1['token'], 'dm_id': dm_id, 'message': 'hey there'}).json()['message_id']
    response = requests.delete(other.MESSAGE_REMOVE_URL, json={'token': create_user2['token'], 'message_id': message_id, 'message': 'i have edited this'})
    assert response.status_code == 400