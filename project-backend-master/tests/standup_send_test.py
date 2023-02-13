from src.config import url
import requests
import pytest
from time import time, sleep
import src.other as other

@pytest.fixture
def clear_store():
    requests.delete(other.CLEAR_URL, json={})

@pytest.fixture
def create_user():
    user_input = {'email': "z432324@unsw.edu.au", 'password': "badpassword123", 'name_first': "Twix", 'name_last': "Fix"}
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
    user_input = {'email': "z902136@unsw.edu.au", 'password': "Password1", 'name_first': "Name1", 'name_last': "Lastname1"}
    request_data = requests.post(other.REGISTER_URL, json=user_input)
    user_info = request_data.json()
    return user_info

@pytest.fixture
def long_string():
    string = ''
    for i in range(1,1000):
        string += str(i)
    return string

def test_send_one_message(clear_store, create_user):
    user_token = create_user['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token, 'name': 'Channel!', 'is_public': True}).json()['channel_id']
    requests.post(other.STANDUP_START_URL, json={'token': user_token, 'channel_id': channel_id, 'length': 2})

    response = requests.post(other.STANDUP_SEND_URL, json={'token': user_token, 'channel_id': channel_id, 'message': 'Hello World'})
    assert response.status_code == 200
    assert response.json() == {}

    sleep(2)
    response2 = requests.get(other.CHANNEL_MESSAGES_URL, params={'channel_id': channel_id, 'start': 0, 'token': user_token})
    for message in response2.json()['messages']:
        message_id = message['message_id'] 
   
    assert response2.json()['messages'][message_id]['message'] == "twixfix: Hello World\n"

def test_send_multiple_message(clear_store, create_user, create_user2, create_user3):
    user_token_1 = create_user['token']
    user_token_2 = create_user2['token']
    user_token_3 = create_user3['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token_1, 'name': 'Channel!', 'is_public': True}).json()['channel_id']
    requests.post(other.CHANNEL_JOIN_URL, json={'token': user_token_2, 'channel_id': channel_id})
    requests.post(other.CHANNEL_JOIN_URL, json={'token': user_token_3, 'channel_id': channel_id})
    requests.post(other.STANDUP_START_URL, json={'token': user_token_1, 'channel_id': channel_id, 'length': 2})

    response1 = requests.post(other.STANDUP_SEND_URL, json={'token': user_token_1, 'channel_id': channel_id, 'message': 'I ate a catfish'})
    response2 = requests.post(other.STANDUP_SEND_URL, json={'token': user_token_2, 'channel_id': channel_id, 'message': 'I went to kmart'})
    response3 = requests.post(other.STANDUP_SEND_URL, json={'token': user_token_3, 'channel_id': channel_id, 'message': 'I ate a toaster'})
    
    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response3.status_code == 200
    sleep(2)
    response = requests.get(other.CHANNEL_MESSAGES_URL, params={'channel_id': channel_id, 'start': 0, 'token': user_token_1})
    for message in response.json()['messages']:
        message_id = message['message_id'] 
   
    assert response.json()['messages'][message_id]['message'] == "twixfix: I ate a catfish\nname2lastname2: I went to kmart\nname1lastname1: I ate a toaster\n"

def test_length_over_1000(clear_store, create_user, long_string):
    user_token = create_user['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token, 'name': 'My Channel!', 'is_public': True}).json()['channel_id']
    requests.post(other.STANDUP_START_URL, json={'token': user_token, 'channel_id': channel_id, 'length': 2})
    
    response = requests.post(other.STANDUP_SEND_URL, json={'token': user_token, 'channel_id': channel_id, 'message': long_string})
    assert response.status_code == 400

def test_standup_not_running(clear_store, create_user):
    user_token = create_user['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token, 'name': 'My Channel!', 'is_public': True}).json()['channel_id']

    response = requests.post(other.STANDUP_SEND_URL, json={'token': user_token, 'channel_id': channel_id, 'message': 'Hello World'})
    assert response.status_code == 400
    
def test_invalid_channel(clear_store, create_user):
    user_token = create_user['token']
    response = requests.post(other.STANDUP_SEND_URL, json={'token': user_token, 'channel_id': 0, 'message': 'Hello World'})
    assert response.status_code == 400

def test_unauthorised_member(clear_store, create_user, create_user2):
    user_token = create_user['token']
    user_token_2 = create_user2['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token, 'name': 'My Channel!', 'is_public': True}).json()['channel_id']
    requests.post(other.STANDUP_START_URL, json={'token': user_token, 'channel_id': channel_id, 'length': 10})

    response = requests.post(other.STANDUP_SEND_URL, json={'token': user_token_2, 'channel_id': channel_id, 'message': 'Hello World'})
    assert response.status_code == 403