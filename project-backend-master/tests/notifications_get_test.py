from src.config import url
import pytest
import requests
import src.other as other
from time import time, sleep

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

def test_channel_tagged_message_notification(clear_store, create_user1):
    user_token = create_user1['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token, 'name': 'Cool Channel', 'is_public': True}).json()['channel_id']
    requests.post(other.MESSAGE_SEND_URL, json={'token': user_token, 'channel_id': channel_id, 'message': 'Tagged @twixfix'})
    response = requests.get(other.NOTIFICATIONS_GET_URL, params={'token': user_token})
    expected_output = [{'channel_id': channel_id, 'dm_id': -1, 'notification_message': 'twixfix tagged you in Cool Channel: Tagged @twixfix'}]
    assert response.json()['notifications'] == expected_output
    assert response.status_code == 200

def test_channel_react_message_notification(clear_store, create_user1):
    user_token = create_user1['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token, 'name': 'Cool Channel', 'is_public': True}).json()['channel_id']
    message_id = requests.post(other.MESSAGE_SEND_URL, json={'token': user_token, 'channel_id': channel_id, 'message': 'React message'}).json()['message_id']
    requests.post(other.MESSAGE_REACT_URL, json={'token': user_token, 'message_id': message_id, 'react_id': 1})
    response = requests.get(other.NOTIFICATIONS_GET_URL, params={'token': user_token})
    expected_output = [{'channel_id': channel_id, 'dm_id': -1, 'notification_message': 'twixfix reacted to your message in Cool Channel'}]
    assert response.json()['notifications'] == expected_output
    assert response.status_code == 200

def test_dm_tagged_message_notification(clear_store, create_user1):
    user_token = create_user1['token']
    dm_id = requests.post(other.DM_CREATE_URL, json={'token': user_token, 'u_ids': []}).json()['dm_id']
    requests.post(other.MESSAGE_SENDDM_URL, json={'token': user_token, 'dm_id': dm_id, 'message': 'Tagged @twixfix'})
    response = requests.get(other.NOTIFICATIONS_GET_URL, params={'token': user_token})
    expected_output = [{'channel_id': -1, 'dm_id': dm_id, 'notification_message': 'twixfix tagged you in twixfix: Tagged @twixfix'}]
    assert response.json()['notifications'] == expected_output
    assert response.status_code == 200

def test_dm_react_message_notification(clear_store, create_user1):
    user_token = create_user1['token']
    dm_id = requests.post(other.DM_CREATE_URL, json={'token': user_token, 'u_ids': []}).json()['dm_id']
    message_id = requests.post(other.MESSAGE_SENDDM_URL, json={'token': user_token, 'dm_id': dm_id, 'message': 'React message'}).json()['message_id']
    requests.post(other.MESSAGE_REACT_URL, json={'token': user_token, 'message_id': message_id, 'react_id': 1})
    response = requests.get(other.NOTIFICATIONS_GET_URL, params={'token': user_token})
    expected_output = {'notifications': [{'channel_id': -1, 'dm_id': dm_id, 'notification_message': 'twixfix reacted to your message in twixfix'}]}
    assert response.json() == expected_output
    assert response.status_code == 200

def test_message_edit_to_include_tag(clear_store, create_user1):
    user_token = create_user1['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token, 'name': 'Cool Channel', 'is_public': True}).json()['channel_id']
    message_id = requests.post(other.MESSAGE_SEND_URL, json={'token': user_token, 'channel_id': channel_id, 'message': 'Tagged nobody!'}).json()['message_id']
    initial_response = requests.get(other.NOTIFICATIONS_GET_URL, params={'token': user_token})
    requests.put(other.MESSAGE_EDIT_URL, json={'token': user_token, 'message_id': message_id, 'message': 'Tagged @twixfix'})
    response = requests.get(other.NOTIFICATIONS_GET_URL, params={'token': user_token})
    expected_output = [{'channel_id': channel_id, 'dm_id': -1, 'notification_message': 'twixfix tagged you in Cool Channel: Tagged @twixfix'}]
    assert initial_response.json()['notifications'] == []
    assert response.json()['notifications'] == expected_output
    assert response.status_code == 200

def test_sendlater_tag(clear_store, create_user1):
    user_token = create_user1['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token, 'name': 'Cool Channel', 'is_public': True}).json()['channel_id']
    requests.post(other.MESSAGE_SENDLATER_URL, json={'token': user_token, 'channel_id': channel_id, 'message': "Tag you later @twixfix", 'time_sent': time() + 1})
    sleep(2)
    response = requests.get(other.NOTIFICATIONS_GET_URL, params={'token': user_token})
    expected_output = [{'channel_id': channel_id, 'dm_id': -1, 'notification_message': 'twixfix tagged you in Cool Channel: Tag you later @twixf'}]
    assert response.json()['notifications'] == expected_output
    assert response.status_code == 200

def test_sendlaterdm_tag(clear_store, create_user1):
    user_token = create_user1['token']
    dm_id = requests.post(other.DM_CREATE_URL, json={'token': user_token, 'u_ids': []}).json()['dm_id']
    requests.post(other.MESSAGE_SENDLATERDM_URL, json={'token': user_token, 'dm_id': dm_id, 'message': "Tag you later @twixfix", 'time_sent': time() + 1})
    sleep(2)
    response = requests.get(other.NOTIFICATIONS_GET_URL, params={'token': user_token})
    expected_output = [{'channel_id': -1, 'dm_id': dm_id, 'notification_message': 'twixfix tagged you in twixfix: Tag you later @twixf'}]
    assert response.json()['notifications'] == expected_output
    assert response.status_code == 200

def test_user_is_added_channel(clear_store, create_user1, create_user2):
    user_token = create_user1['token']
    user_token_2 = create_user2['token']
    user_id_2 = create_user2['auth_user_id']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token, 'name': 'Cool Channel', 'is_public': True}).json()['channel_id']
    requests.post(other.CHANNEL_INVITE_URL, json={'token': user_token, 'channel_id': channel_id, 'u_id': user_id_2})
    response = requests.get(other.NOTIFICATIONS_GET_URL, params={'token': user_token_2})
    expected_output = {'notifications': [{'channel_id': channel_id, 'dm_id': -1, 'notification_message': 'twixfix has added you to Cool Channel'}]}
    assert response.json() == expected_output
    assert response.status_code == 200

def test_user_is_added_dm(clear_store, create_user1, create_user2):
    user_token = create_user1['token']
    user_token_2 = create_user2['token']
    user_id_2 = create_user2['auth_user_id']
    dm_id = requests.post(other.DM_CREATE_URL, json={'token': user_token, 'u_ids': [user_id_2]}).json()['dm_id']
    response = requests.get(other.NOTIFICATIONS_GET_URL, params={'token': user_token_2})
    expected_output = {'notifications': [{'channel_id': -1, 'dm_id': dm_id, 'notification_message': 'twixfix has added you to snickerslickers, twixfix'}]}
    assert response.json() == expected_output
    assert response.status_code == 200

def test_no_notifications(clear_store, create_user1):
    user_token = create_user1['token']
    requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token, 'name': 'Cool Channel', 'is_public': True}).json()['channel_id']
    requests.post(other.DM_CREATE_URL, json={'token': user_token, 'u_ids': []}).json()
    response = requests.get(other.NOTIFICATIONS_GET_URL, params={'token': user_token})
    assert response.json() == {'notifications': []}
    assert response.status_code == 200

def test_more_than_20_notifications_channel(clear_store, create_user1):
    user_token = create_user1['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token, 'name': 'Cool Channel', 'is_public': True}).json()['channel_id']
    for _ in range(21):
        requests.post(other.MESSAGE_SEND_URL, json={'token': user_token, 'channel_id': channel_id, 'message': 'Tagged myself @twixfix!!!'}).json()['message_id']
    response = requests.get(other.NOTIFICATIONS_GET_URL, params={'token': user_token})
    assert len(response.json()['notifications']) == 20
    assert response.status_code == 200

def test_non_handle_tags(clear_store, create_user1):
    user_token = create_user1['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token, 'name': 'Cool Channel', 'is_public': True}).json()['channel_id']
    requests.post(other.MESSAGE_SEND_URL, json={'token': user_token, 'channel_id': channel_id, 'message': 'Tagged @nobody!@@@random @nontag! @'}).json()['message_id']
    response = requests.get(other.NOTIFICATIONS_GET_URL, params={'token': user_token})
    assert response.status_code == 200
    assert response.json()['notifications'] == []

def test_invalid_user_token(clear_store, create_user1):
    user_token = create_user1['token']
    requests.post(other.LOGOUT_URL, json={'token': user_token})
    response = requests.get(other.NOTIFICATIONS_GET_URL, params={'token': user_token})
    assert response.status_code == 403

def test_user_has_left_channel(clear_store, create_user1, create_user2):
    user_token = create_user1['token']
    user_token_2 = create_user2['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token, 'name': 'Cool Channel', 'is_public': True}).json()['channel_id']
    requests.post(other.CHANNEL_JOIN_URL, json={'token': user_token_2, 'channel_id': channel_id})
    message_id = requests.post(other.MESSAGE_SEND_URL, json={'token': user_token_2, 'channel_id': channel_id, 'message': 'Test Message'}).json()['message_id']
    requests.post(other.CHANNEL_LEAVE_URL, json={'token': user_token_2, 'channel_id': channel_id})
    requests.post(other.MESSAGE_SEND_URL, json={'token': user_token, 'channel_id': channel_id, 'message': 'Tag after leave @snickerslickers'})
    requests.post(other.MESSAGE_REACT_URL, json={'token': user_token, 'message_id': message_id, 'react_id': 1})
    response = requests.get(other.NOTIFICATIONS_GET_URL, params={'token': user_token_2})
    expected_output = {'notifications': []}
    assert response.json() == expected_output
    assert response.status_code == 200

def test_user_has_left_dm(clear_store, create_user1, create_user2):
    user_token = create_user1['token']
    user_token_2 = create_user2['token']
    user_id_2 = create_user2['auth_user_id']
    dm_id = requests.post(other.DM_CREATE_URL, json={'token': user_token, 'u_ids': [user_id_2]}).json()['dm_id']
    message_id = requests.post(other.MESSAGE_SENDDM_URL, json={'token': user_token_2, 'dm_id': dm_id, 'message': 'Test Message'}).json()['message_id']
    requests.post(other.DM_LEAVE_URL, json={'token': user_token_2, 'dm_id': dm_id})
    requests.post(other.MESSAGE_SENDDM_URL, json={'token': user_token, 'dm_id': dm_id, 'message': 'Tag after leave @snickerslickers'})
    requests.post(other.MESSAGE_REACT_URL, json={'token': user_token, 'message_id': message_id, 'react_id': 1})
    response = requests.get(other.NOTIFICATIONS_GET_URL, params={'token': user_token_2})
    expected_output = {'notifications': [{'channel_id': -1, 'dm_id': dm_id, 'notification_message': 'twixfix has added you to snickerslickers, twixfix'}]}
    assert response.json() == expected_output
    assert response.status_code == 200
