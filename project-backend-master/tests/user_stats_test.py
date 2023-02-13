from src.config import url
import pytest
import requests
import src.other as other
import time


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


def test_basic_stats(clear_store, create_user):
    user = create_user
    response = requests.get(other.USER_STATS_URL, params = {'token': user['token']})
    assert response.status_code == 200
    assert response.json()['user_stats']['involvement_rate'] == 0
    requests.post(other.CHANNELS_CREATE_URL, json = {'token': user['token'], 'name': 'Happy', 'is_public': True})
    response = requests.get(other.USER_STATS_URL, params = {'token': user['token']})
    assert response.json()['user_stats']['involvement_rate'] == 1
    channels_join = response.json()['user_stats']['channels_joined']
    assert channels_join[0]['num_channels_joined'] == 0
    assert channels_join[1]['num_channels_joined'] == 1
    assert channels_join[0]['time_stamp'] < channels_join[1]['time_stamp']

def test_multi_user_stats(clear_store, create_user, create_user2):
    user1 = create_user
    user2 = create_user2
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json = {'token': user1['token'], 'name': 'Happy', 'is_public': True}).json()['channel_id']
    requests.post(other.MESSAGE_SEND_URL, json = {'token': user1['token'], 'message': 'hey', 'channel_id': channel_id})
    requests.post(other.CHANNEL_JOIN_URL, json = {'token': user2['token'], 'channel_id': channel_id})
    requests.post(other.MESSAGE_SEND_URL, json = {'token': user1['token'], 'message': 'hey', 'channel_id': channel_id})
    requests.post(other.MESSAGE_SEND_URL, json = {'token': user2['token'], 'message': 'hey back', 'channel_id': channel_id})
    response1 = requests.get(other.USER_STATS_URL, params = {'token': user1['token']})
    response2 = requests.get(other.USER_STATS_URL, params = {'token': user2['token']})
    assert response1.json()['user_stats']['involvement_rate'] == 3/4
    assert response2.json()['user_stats']['involvement_rate'] == 1/2

def test_deprecating_stats(clear_store, create_user, create_user2):
    user1 = create_user
    user2 = create_user2
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json = {'token': user1['token'], 'name': 'Happy', 'is_public': True}).json()['channel_id']
    requests.post(other.MESSAGE_SEND_URL, json = {'token': user1['token'], 'message': 'hey', 'channel_id': channel_id})
    requests.post(other.CHANNEL_JOIN_URL, json = {'token': user2['token'], 'channel_id': channel_id})
    requests.post(other.MESSAGE_SEND_URL, json = {'token': user1['token'], 'message': 'hey', 'channel_id': channel_id})
    requests.post(other.MESSAGE_SEND_URL, json = {'token': user2['token'], 'message': 'hey back', 'channel_id': channel_id})
    requests.post(other.CHANNEL_LEAVE_URL, json = {'token': user2['token'], 'channel_id': channel_id})
    response2 = requests.get(other.USER_STATS_URL, params = {'token': user2['token']})
    assert response2.json()['user_stats']['involvement_rate'] == 1/4

def test_involvement_greater_1(clear_store, create_user):
    user1 = create_user
    dm_id = requests.post(other.DM_CREATE_URL, json = {'token': user1['token'], 'u_ids': []}).json()['dm_id']
    requests.post(other.MESSAGE_SENDDM_URL, json = {'token': user1['token'], 'message': 'hey', 'dm_id': dm_id})
    requests.post(other.CHANNELS_CREATE_URL, json = {'token': user1['token'], 'name': 'Happy', 'is_public': True}).json()['channel_id']
    response1 = requests.get(other.USER_STATS_URL, params = {'token': user1['token']})
    assert response1.json()['user_stats']['involvement_rate'] == 1
    requests.delete(other.DM_REMOVE_URL, json = {'token': user1['token'], 'dm_id': dm_id})
    response = requests.get(other.USER_STATS_URL, params = {'token': user1['token']})
    assert response.json()['user_stats']['involvement_rate'] == 1

def test_complex_many_operations(clear_store, create_user, create_user2):
    user1 = create_user
    user2 = create_user2
    dm_id1 = requests.post(other.DM_CREATE_URL, json = {'token': user1['token'], 'u_ids': []}).json()['dm_id']
    dm_id2 = requests.post(other.DM_CREATE_URL, json = {'token': user1['token'], 'u_ids': [user2['auth_user_id']]}).json()['dm_id']
    requests.post(other.MESSAGE_SENDDM_URL, json = {'token': user1['token'], 'message': 'hey', 'dm_id': dm_id1})
    requests.post(other.MESSAGE_SENDDM_URL, json = {'token': user2['token'], 'message': 'hey', 'dm_id': dm_id2})
    requests.post(other.MESSAGE_SENDDM_URL, json = {'token': user1['token'], 'message': 'hey', 'dm_id': dm_id2})
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json = {'token': user1['token'], 'name': 'Happy', 'is_public': True}).json()['channel_id']
    requests.post(other.MESSAGE_SEND_URL, json = {'token': user1['token'], 'message': 'hey', 'channel_id': channel_id})
    requests.post(other.CHANNEL_JOIN_URL, json = {'token': user2['token'], 'channel_id': channel_id})
    requests.post(other.MESSAGE_SEND_URL, json = {'token': user2['token'], 'message': 'hey', 'channel_id': channel_id})
    requests.delete(other.DM_REMOVE_URL, json = {'token': user1['token'], 'dm_id': dm_id1})
    response1 = requests.get(other.USER_STATS_URL, params = {'token': user1['token']})
    response2 = requests.get(other.USER_STATS_URL, params = {'token': user2['token']})
    assert response1.json()['user_stats']['involvement_rate'] == 5/6
    assert response2.json()['user_stats']['involvement_rate'] == 4/6    
    
