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
    dm_id = requests.post(other.DM_CREATE_URL, json={'token': user_token, 'u_ids': []}).json()['dm_id']
    response = requests.post(other.MESSAGE_SENDLATERDM_URL, json={'token': user_token, 'dm_id': dm_id, 'message': "Test message", 'time_sent': time.time() + 10})
    dm_messages = requests.get(other.DM_MESSAGES_URL, params={'token': user_token, 'dm_id': dm_id, 'start': 0})
    assert response.status_code == 200
    assert dm_messages.json()['messages'] == []

# WHITE BOX TEST DELETE OR MOVE LATER
def test_whitebox_sendlater_success(clear_store, create_user1):
    user_token = create_user1['token']
    user_id = create_user1['auth_user_id']
    dm_id = requests.post(other.DM_CREATE_URL, json={'token': user_token, 'u_ids': []}).json()['dm_id']
    timestamp = time.time() + 2
    response = requests.post(other.MESSAGE_SENDLATERDM_URL, json={'token': user_token, 'dm_id': dm_id, 'message': "Whitebox!", 'time_sent': timestamp})
    initial_message_response = requests.get(other.DM_MESSAGES_URL, params={'token': user_token, 'dm_id': dm_id, 'start': 0})
    time.sleep(3)
    message_response = requests.get(other.DM_MESSAGES_URL, params={'token': user_token, 'dm_id': dm_id, 'start': 0})
    expected_message = [{'message_id': response.json()['message_id'], 'message': "Whitebox!",
                        'u_id': user_id,'time_sent': timestamp,
                        'reacts': [{'react_id': 1, 'u_ids': [], 'is_this_user_reacted': False}], 'is_pinned': False}]
    assert response.status_code == 200
    assert initial_message_response.json()['messages'] == []
    assert message_response.status_code == 200
    assert message_response.json()['messages'] == expected_message

def test_invalid_dm_id(clear_store, create_user1):
    user_token = create_user1['token']
    response = requests.post(other.MESSAGE_SENDLATERDM_URL, json={'token': user_token, 'dm_id': 1, 'message': "Test message", 'time_sent': time.time() + 10})
    assert response.status_code == 400

def test_message_too_long(clear_store, create_user1, long_string):
    user_token = create_user1['token']
    dm_id = requests.post(other.DM_CREATE_URL, json={'token': user_token, 'u_ids': []}).json()['dm_id']
    response = requests.post(other.MESSAGE_SENDLATERDM_URL, json={'token': user_token, 'dm_id': dm_id, 'message': long_string, 'time_sent': time.time() + 10})
    assert response.status_code == 400

def test_time_in_past(clear_store, create_user1):
    user_token = create_user1['token']
    dm_id = requests.post(other.DM_CREATE_URL, json={'token': user_token, 'u_ids': []}).json()['dm_id']
    response = requests.post(other.MESSAGE_SENDLATERDM_URL, json={'token': user_token, 'dm_id': dm_id, 'message': "Hello!", 'time_sent': time.time() - 10})
    assert response.status_code == 400

def test_sender_not_member(clear_store, create_user1, create_user2):
    user_token_1 = create_user1['token']
    user_token_2 = create_user2['token']
    dm_id = requests.post(other.DM_CREATE_URL, json={'token': user_token_1, 'u_ids': []}).json()['dm_id']
    response = requests.post(other.MESSAGE_SENDLATERDM_URL, json={'token': user_token_2, 'dm_id': dm_id, 'message': "I'm not a member!", 'time_sent': time.time() + 10})
    assert response.status_code == 403

def test_sender_invalid(clear_store, create_user1):
    user_token = create_user1['token']
    dm_id = requests.post(other.DM_CREATE_URL, json={'token': user_token, 'u_ids': []}).json()['dm_id']
    requests.post(other.LOGOUT_URL, json={'token': user_token})
    response = requests.post(other.MESSAGE_SENDLATERDM_URL, json={'token': user_token, 'dm_id': dm_id, 'message': "My token has expired!", 'time_sent': time.time() + 10})
    assert response.status_code == 403