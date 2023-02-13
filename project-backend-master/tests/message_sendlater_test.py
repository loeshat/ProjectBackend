from os import remove
from src.config import url
import time
import pytest
import requests
import src.other as other

@pytest.fixture
def clear_store():
    requests.delete(f"{url}/clear/v1", json={})

@pytest.fixture
def create_user1():
    user_input = {'email': "z432324@unsw.edu.au", 'password': "badpassword123", 'name_first': "Twix", 'name_last': "Fix"}
    request_data = requests.post(other.REGISTER_URL, json=user_input)
    user_info = request_data.json()
    return user_info

@pytest.fixture
def create_user2():
    user_input = {'email': "z54626@unsw.edu.au", 'password': "Password", 'name_first': "Snickers", 'name_last': "Lickers"}
    request_data = requests.post(other.REGISTER_URL, json=user_input)
    user_info = request_data.json()
    return user_info

@pytest.fixture
def long_string():
    string = ''
    for i in range(1,1000):
        string += str(i)
    return string

def test_sendlater_success(clear_store, create_user1):
    user_token = create_user1['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token, 'name': 'Channel!', 'is_public': True}).json()['channel_id']
    response = requests.post(other.MESSAGE_SENDLATER_URL, json={'token': user_token, 'channel_id': channel_id, 'message': "Test message", 'time_sent': time.time() + 10})
    channel_messages = requests.get(other.CHANNEL_MESSAGES_URL, params={'token':user_token, 'channel_id': channel_id, 'start': 0})
    assert response.status_code == 200
    assert channel_messages.json()['messages'] == []

def test_indepth_sendlater_success(clear_store, create_user1):
    user_token = create_user1['token']
    user_id = create_user1['auth_user_id']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token, 'name': 'Channel!', 'is_public': True}).json()['channel_id']
    timestamp = time.time() + 2
    response = requests.post(other.MESSAGE_SENDLATER_URL, json={'token': user_token, 'channel_id': channel_id, 'message': "Success!", 'time_sent': timestamp})
    time.sleep(3)
    message_response = requests.get(other.CHANNEL_MESSAGES_URL, params={'token': user_token, 'channel_id': channel_id, 'start': 0})    
    expected_message = [{'message_id': response.json()['message_id'], 'message': "Success!",
                        'u_id': user_id,'time_sent': timestamp,
                        'reacts': [{'react_id': 1, 'u_ids': [], 'is_this_user_reacted': False}], 'is_pinned': False}]
    assert response.status_code == 200
    assert message_response.status_code == 200
    assert message_response.json()['messages'] == expected_message

def test_functions_on_unsent_message(clear_store, create_user1):
    user_token = create_user1['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token, 'name': 'Channel!', 'is_public': True}).json()['channel_id']
    sendlater_response = requests.post(other.MESSAGE_SENDLATER_URL, json={'token': user_token, 'channel_id': channel_id, 'message': "Success!", 'time_sent': time.time() + 10})
    message_id = sendlater_response.json()['message_id']
    react_response = requests.post(other.MESSAGE_REACT_URL, json={'token': user_token, 'message_id': message_id, 'react_id': 1})
    edit_response = requests.put(other.MESSAGE_EDIT_URL, json={'token': user_token, 'message_id': message_id, 'message': "invalid edit"})
    remove_response = requests.delete(other.MESSAGE_REMOVE_URL, json={'token': user_token, 'message_id': message_id})
    assert sendlater_response.status_code == 200
    assert react_response.status_code == 400
    assert edit_response.status_code == 400
    assert remove_response.status_code == 400

def test_invalid_channel_id(clear_store, create_user1):
    user_token = create_user1['token']
    response = requests.post(other.MESSAGE_SENDLATER_URL, json={'token': user_token, 'channel_id': 1, 'message': "Test message", 'time_sent': time.time() + 2})
    assert response.status_code == 400

def test_message_too_long(clear_store, create_user1, long_string):
    user_token = create_user1['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token, 'name': 'Channel!', 'is_public': True}).json()['channel_id']
    response = requests.post(other.MESSAGE_SENDLATER_URL, json={'token': user_token, 'channel_id': channel_id, 'message': long_string, 'time_sent': time.time() + 2})
    assert response.status_code == 400

def test_time_in_past(clear_store, create_user1):
    user_token = create_user1['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token, 'name': 'Channel!', 'is_public': True}).json()['channel_id']
    response = requests.post(other.MESSAGE_SENDLATER_URL, json={'token': user_token, 'channel_id': channel_id, 'message': "Hello!", 'time_sent': time.time() - 2})
    assert response.status_code == 400

def test_sender_not_member(clear_store, create_user1, create_user2):
    user_token_1 = create_user1['token']
    user_token_2 = create_user2['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token_1, 'name': 'Channel!', 'is_public': True}).json()['channel_id']
    response = requests.post(other.MESSAGE_SENDLATER_URL, json={'token': user_token_2, 'channel_id': channel_id, 'message': "I'm not a member!", 'time_sent': time.time() + 2})
    assert response.status_code == 403

def test_sender_invalid(clear_store, create_user1):
    user_token = create_user1['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token, 'name': 'Channel!', 'is_public': True}).json()['channel_id']
    requests.post(other.LOGOUT_URL, json={'token': user_token})
    response = requests.post(other.MESSAGE_SENDLATER_URL, json={'token': user_token, 'channel_id': channel_id, 'message': "My token has expired!", 'time_sent': time.time() + 2})
    assert response.status_code == 403    
