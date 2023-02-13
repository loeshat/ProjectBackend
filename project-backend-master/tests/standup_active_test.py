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

def test_is_active(clear_store, create_user):
    user_token = create_user['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token, 'name': 'Channel!', 'is_public': True}).json()['channel_id']
    requests.post(other.STANDUP_START_URL, json={'token': user_token, 'channel_id': channel_id, 'length': 10})
    time_start = time()
    time_finish = int(time_start + 10)
    response = requests.get(other.STANDUP_ACTIVE_URL, params={'token': user_token, 'channel_id': channel_id})

    assert response.status_code == 200
    response_data = response.json()
    assert response_data == {'is_active': True, 'time_finish': time_finish}

def test_is_not_active(clear_store, create_user):
    user_token = create_user['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token, 'name': 'Channel!', 'is_public': True}).json()['channel_id']
    requests.post(other.STANDUP_START_URL, json={'token': user_token, 'channel_id': channel_id, 'length': 2})
    sleep(3)

    response = requests.get(other.STANDUP_ACTIVE_URL, params={'token': user_token, 'channel_id': channel_id})
    assert response.status_code == 200
    response_data = response.json()
    assert response_data == {'is_active': False, 'time_finish': None}
    
def test_invalid_channel(clear_store, create_user):
    user_token = create_user['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token, 'name': 'Channel!', 'is_public': True}).json()['channel_id']
    requests.post(other.STANDUP_START_URL, json={'token': user_token, 'channel_id': channel_id, 'length': 2})

    response = requests.get(other.STANDUP_ACTIVE_URL, params={'token': user_token, 'channel_id': 2})
    assert response.status_code == 400

def test_unauthorised_member(clear_store, create_user, create_user2):
    user_token = create_user['token']
    user_token_2 = create_user2['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token, 'name': 'My Channel!', 'is_public': True}).json()['channel_id']
    requests.post(other.STANDUP_START_URL, json={'token': user_token, 'channel_id': channel_id, 'length': 2})

    response = requests.get(other.STANDUP_ACTIVE_URL, params={'token': user_token_2, 'channel_id': channel_id})
    assert response.status_code == 403
    