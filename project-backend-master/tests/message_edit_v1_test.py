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


def test_basic_message_edit(clear_store, create_user):
    user_token_1 = create_user['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={
                               'token': user_token_1, 'name': 'My Channel!', 'is_public': True}).json()['channel_id']

    message_id = requests.post(other.MESSAGE_SEND_URL, json={'token': user_token_1, 'channel_id': channel_id, 'message': "Leo sucks"}).json()['message_id']
    response = requests.get(other.CHANNEL_MESSAGES_URL, params={'channel_id': channel_id, 'start': 0, 'token': user_token_1})
    list_msg_ids = [message['message_id'] for message in response.json()['messages']]
    assert message_id in list_msg_ids 
    response = requests.put(other.MESSAGE_EDIT_URL, json={'token': user_token_1, 'message_id': message_id, 'message': 'Leo is cool'})
    assert response.status_code == 200
    response = requests.get(other.CHANNEL_MESSAGES_URL, params={'channel_id': channel_id, 'start': 0, 'token': user_token_1})
    assert response.status_code == 200
    list_msg_ids = [message['message_id'] for message in response.json()['messages']]
    assert message_id in list_msg_ids
    msg_index = list_msg_ids.index(message_id)
    assert response.json()['messages'][msg_index]['u_id'] == create_user['auth_user_id']
    assert response.json()['messages'][msg_index]['message'] == "Leo is cool"



def test_message_over_1000_characters(clear_store, create_user):
    user_token_1 = create_user['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={
                               'token': user_token_1, 'name': 'My Channel!', 'is_public': True}).json()['channel_id']

    message_id = requests.post(other.MESSAGE_SEND_URL, json={'token': user_token_1, 'channel_id': channel_id, 'message': "Leo sucks"}).json()['message_id']
    response = requests.get(other.CHANNEL_MESSAGES_URL, params={'channel_id': channel_id, 'start': 0, 'token': user_token_1})
    assert response.json()['messages'][0]['message'] == "Leo sucks"
    long_message = ''
    for i in range(2000):
        long_message += str(i)
    response = requests.put(other.MESSAGE_EDIT_URL, json={'token': user_token_1, 'message_id': message_id, 'message': long_message})
    assert response.status_code == 400

def test_message_id_invalid(clear_store, create_user):
    user_token_1 = create_user['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={
                               'token': user_token_1, 'name': 'My Channel!', 'is_public': True}).json()['channel_id']
    message_id = requests.post(other.MESSAGE_SEND_URL, json={'token': user_token_1, 'channel_id': channel_id, 'message': "Leo sucks"}).json()['message_id']
    response = requests.put(other.MESSAGE_EDIT_URL, json={'token': user_token_1, 'message_id': message_id + 1, 'message': 'invalid message id'})
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
    response = requests.put(other.MESSAGE_EDIT_URL, json={'token': user_token_2, 'message_id': message_id, 'message': 'wrong user'})
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
    response = requests.put(other.MESSAGE_EDIT_URL, json={'token': user_token_2, 'message_id': message_id, 'message': 'no permissions'})
    assert response.status_code == 200

def test_message_is_nothing(clear_store, create_user):
    user_token_1 = create_user['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={
                               'token': user_token_1, 'name': 'My Channel!', 'is_public': True}).json()['channel_id']

    message_id = requests.post(other.MESSAGE_SEND_URL, json={'token': user_token_1, 'channel_id': channel_id, 'message': "Leo sucks"}).json()['message_id']
    response = requests.get(other.CHANNEL_MESSAGES_URL, params={'channel_id': channel_id, 'start': 0, 'token': user_token_1})
    assert response.json()['messages'][0]['message'] == "Leo sucks"
    response = requests.put(other.MESSAGE_EDIT_URL, json={'token': user_token_1, 'message_id': message_id, 'message': ''})
    assert response.status_code == 200
    response = requests.get(other.CHANNEL_MESSAGES_URL, params={'channel_id': channel_id, 'start': 0, 'token': user_token_1})
    assert response.json() == {'messages': [], 'start': 0, 'end': -1} 
    assert response.status_code == 200


def test_user_leaves_channel(clear_store, create_user, create_user2):
    user_token_1 = create_user['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={
                               'token': user_token_1, 'name': 'My Channel!', 'is_public': True}).json()['channel_id']
    message_id = requests.post(other.MESSAGE_SEND_URL, json={'token': user_token_1, 'channel_id': channel_id, 'message': "Hello World"}).json()['message_id']
    requests.post(other.CHANNEL_JOIN_URL, json={'token': create_user2['token'], 'channel_id': channel_id})
    response = requests.post(other.CHANNEL_LEAVE_URL, json={'token': user_token_1, 'channel_id': channel_id})
    response = requests.put(other.MESSAGE_EDIT_URL, json={'token': user_token_1, 'message_id': message_id, 'message': 'im not in channel'})
    assert response.status_code == 400


def test_normal_dm(clear_store, create_user):
    user_1 = create_user
    dm_id = requests.post(other.DM_CREATE_URL, json={'token': user_1['token'], 'u_ids': []}).json()['dm_id']
    message_id = requests.post(other.MESSAGE_SENDDM_URL, json={'token': user_1['token'], 'dm_id': dm_id, 'message': 'hey there'}).json()['message_id']
    response = requests.put(other.MESSAGE_EDIT_URL, json={'token': user_1['token'], 'message_id': message_id, 'message': 'i have edited this'})
    assert response.status_code == 200
    response = requests.get(other.DM_MESSAGES_URL, params={'dm_id': dm_id, 'token': user_1['token'], 'start': 0})
    assert response.json()['messages'][0]['message_id'] == message_id
    assert response.json()['messages'][0]['message'] == 'i have edited this'
    
def test_user_not_in_dm(clear_store, create_user, create_user2):
    user_1 = create_user
    dm_id = requests.post(other.DM_CREATE_URL, json={'token': user_1['token'], 'u_ids': []}).json()['dm_id']
    message_id = requests.post(other.MESSAGE_SENDDM_URL, json={'token': user_1['token'], 'dm_id': dm_id, 'message': 'hey there'}).json()['message_id']
    response = requests.put(other.MESSAGE_EDIT_URL, json={'token': create_user2['token'], 'message_id': message_id, 'message': 'i have edited this'})
    assert response.status_code == 400
    
def test_message_id_invalid_dm(clear_store, create_user):
    user_token_1 = create_user['token']
    dm_id = requests.post(other.DM_CREATE_URL, json={
                               'token': user_token_1, 'u_ids': []}).json()['dm_id']
    message_id = requests.post(other.MESSAGE_SENDDM_URL, json={'token': user_token_1, 'dm_id': dm_id, 'message': "Leo sucks"}).json()['message_id']
    response = requests.put(other.MESSAGE_EDIT_URL, json={'token': user_token_1, 'message_id': message_id + 1, 'message': 'invalid message id'})
    assert response.status_code == 400