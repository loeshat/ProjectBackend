from venv import create
from src.config import url
from time import time
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
    user_input = {'email': "z4321321@unsw.edu.au", 'password': "123LLLpass", 'name_first': "Snickers", 'name_last': "Lickers"}
    request_data = requests.post(other.REGISTER_URL, json=user_input)
    user_info = request_data.json()
    return user_info

@pytest.fixture
def long_string():
    string = ''
    for i in range(1,1000):
        string += str(i)
    return string

def test_channel_messages_contains_query(clear_store, create_user1):
    user_token = create_user1['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token, 'name': 'Channel!', 'is_public': True}).json()['channel_id']
    requests.post(other.MESSAGE_SEND_URL, json={'token': user_token, 'channel_id': channel_id, 'message': "Query word hello"})
    channel_messages = requests.get(other.CHANNEL_MESSAGES_URL, params={'token': user_token, 'channel_id': channel_id, 'start': 0}).json()
    response = requests.get(other.SEARCH_URL, params={'token': user_token, 'query_str': "hello"})
    expected_output = channel_messages['messages']
    assert response.json()['messages'] == expected_output
    assert response.status_code == 200

def test_dm_messages_contains_query(clear_store, create_user1):
    user_token = create_user1['token']
    dm_id = requests.post(other.DM_CREATE_URL, json={'token': user_token, 'u_ids': []}).json()['dm_id']
    requests.post(other.MESSAGE_SENDDM_URL, json={'token': user_token, 'dm_id': dm_id, 'message': "Query word hello"})
    dm_messages = requests.get(other.DM_MESSAGES_URL, params={'token': user_token, 'dm_id': dm_id, 'start': 0}).json()
    response = requests.get(other.SEARCH_URL, params={'token': user_token, 'query_str': "hello"})
    expected_output = dm_messages['messages']
    assert response.json()['messages'] == expected_output
    assert response.status_code == 200

def test_messages_do_not_contain_query(clear_store, create_user1):
    user_token = create_user1['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token, 'name': 'Channel!', 'is_public': True}).json()['channel_id']
    requests.post(other.MESSAGE_SEND_URL, json={'token': user_token, 'channel_id': channel_id, 'message': "hello"})
    response = requests.get(other.SEARCH_URL, params={'token': user_token, 'query_str': "word"})
    expected_output = {'messages': []}
    assert response.json() == expected_output
    assert response.status_code == 200

def test_channel_non_member_query(clear_store, create_user1, create_user2):
    user_token_1 = create_user1['token']
    user_token_2 = create_user2['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token_1, 'name': 'Channel!', 'is_public': True}).json()['channel_id']
    requests.post(other.MESSAGE_SEND_URL, json={'token': user_token_1, 'channel_id': channel_id, 'message': "hello"})
    response = requests.get(other.SEARCH_URL, params={'token': user_token_2, 'query_str': "word"})
    expected_output = {'messages': []}
    assert response.json() == expected_output
    assert response.status_code == 200

def test_dm_non_member_query(clear_store, create_user1, create_user2):
    user_token_1 = create_user1['token']
    user_token_2 = create_user2['token']
    dm_id = requests.post(other.DM_CREATE_URL, json={'token': user_token_1, 'u_ids': []}).json()['dm_id']
    requests.post(other.MESSAGE_SENDDM_URL, json={'token': user_token_1, 'dm_id': dm_id, 'message': "hello"})
    response = requests.get(other.SEARCH_URL, params={'token': user_token_2, 'query_str': "word"})
    expected_output = {'messages': []}
    assert response.json() == expected_output
    assert response.status_code == 200

def test_query_too_long(clear_store, create_user1, long_string):
    user_token = create_user1['token']
    create_user1['auth_user_id']
    requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token, 'name': 'Channel!', 'is_public': True}).json()['channel_id']
    response = requests.get(other.SEARCH_URL, params={'token': user_token, 'query_str': long_string})
    assert response.status_code == 400

def test_invalid_user(clear_store, create_user1):
    user_token = create_user1['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token, 'name': 'Channel!', 'is_public': True}).json()['channel_id']
    requests.post(other.MESSAGE_SEND_URL, json={'token': user_token, 'channel_id': channel_id, 'message': "Hello"})
    requests.post(other.LOGOUT_URL, json={'token': user_token})
    request_data = requests.get(other.SEARCH_URL, params={'token': user_token, 'query_str': "Hello"})
    assert request_data.status_code == 403
