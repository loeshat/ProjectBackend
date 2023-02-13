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

@pytest.fixture
def create_user3():
    user_input = {'email': "z43232455@unsw.edu.au",
                  'password': "password", 'name_first': "Name", 'name_last': "Lastname"}
    request_data = requests.post(other.REGISTER_URL, json=user_input)
    user_info = request_data.json()
    return user_info

@pytest.fixture
def create_user4():
    user_input = {'email': "z5362601@unsw.edu.au", 'password': "Password3", 'name_first': "Name3", 'name_last': "LastName3"}
    request_data = requests.post(other.REGISTER_URL, json=user_input)
    user_info = request_data.json()
    return user_info

def test_single_user_basic_actions(clear_store, create_user):
    user1 = create_user
    response = requests.get(other.USERS_STATS_URL, params = {'token': user1['token']})
    assert response.json()['workspace_stats']['utilization_rate'] == 0
    requests.post(other.CHANNELS_CREATE_URL, json = {'token': user1['token'], 'name': 'bob', 'is_public': True})
    response = requests.get(other.USERS_STATS_URL, params = {'token': user1['token']})
    assert response.json()['workspace_stats']['utilization_rate'] == 1
    assert response.json()['workspace_stats']['channels_exist'][0]['num_channels_exist'] == 0
    assert response.json()['workspace_stats']['channels_exist'][1]['num_channels_exist'] == 1

def test_many_users_util_rate(clear_store, create_user, create_user2, create_user3, create_user4):
    user1 = create_user
    user2 = create_user2
    user3 = create_user3
    user4 = create_user4
    response = requests.get(other.USERS_STATS_URL, params = {'token': user1['token']})
    assert response.json()['workspace_stats']['utilization_rate'] == 0
    requests.post(other.CHANNELS_CREATE_URL, json = {'token': user1['token'], 'name': 'bob', 'is_public': True})
    response = requests.get(other.USERS_STATS_URL, params = {'token': user1['token']})
    assert response.json()['workspace_stats']['utilization_rate'] == 1/4
    response = requests.get(other.USERS_STATS_URL, params = {'token': user2['token']})
    assert response.json()['workspace_stats']['utilization_rate'] == 1/4
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json = {'token': user2['token'], 'name': 'bob2', 'is_public': True}).json()['channel_id']
    response = requests.get(other.USERS_STATS_URL, params = {'token': user3['token']})
    assert response.json()['workspace_stats']['utilization_rate'] == 1/2
    requests.post(other.CHANNEL_JOIN_URL, json = {'token': user1['token'], 'channel_id': channel_id})
    response = requests.get(other.USERS_STATS_URL, params = {'token': user4['token']})
    assert response.json()['workspace_stats']['utilization_rate'] == 1/2
    requests.post(other.CHANNEL_JOIN_URL, json = {'token': user4['token'], 'channel_id': channel_id})
    response = requests.get(other.USERS_STATS_URL, params = {'token': user4['token']})
    assert response.json()['workspace_stats']['utilization_rate'] == 3/4
    requests.post(other.CHANNEL_JOIN_URL, json = {'token': user3['token'], 'channel_id': channel_id})
    response = requests.get(other.USERS_STATS_URL, params = {'token': user3['token']})
    assert response.json()['workspace_stats']['utilization_rate'] == 1
    
def test_complex_counts(clear_store, create_user, create_user2, create_user3, create_user4):
    user1 = create_user
    user2 = create_user2
    user3 = create_user3
    user4 = create_user4
    channel1 = requests.post(other.CHANNELS_CREATE_URL, json = {'token': user1['token'], 'name': 'hey', 'is_public': True}).json()['channel_id']
    channel2 = requests.post(other.CHANNELS_CREATE_URL, json = {'token': user2['token'], 'name': 'he2', 'is_public': True}).json()['channel_id']
    dm1 = requests.post(other.DM_CREATE_URL, json = {'token': user1['token'], 'u_ids': []}).json()['dm_id']
    dm2 = requests.post(other.DM_CREATE_URL, json = {'token': user2['token'], 'u_ids': [user3['auth_user_id'], user4['auth_user_id']]}).json()['dm_id']
    requests.post(other.MESSAGE_SEND_URL, json = {'token': user1['token'], 'message': 'hey', 'channel_id': channel1})
    requests.post(other.MESSAGE_SEND_URL, json = {'token': user1['token'], 'message': 'hey2', 'channel_id': channel1})
    requests.post(other.MESSAGE_SEND_URL, json = {'token': user2['token'], 'message': 'hey', 'channel_id': channel2})
    requests.post(other.MESSAGE_SENDDM_URL, json = {'token': user1['token'], 'message': 'hey54', 'dm_id': dm1})
    requests.post(other.MESSAGE_SENDDM_URL, json = {'token': user2['token'], 'message': 'hey3', 'dm_id': dm2})
    requests.post(other.MESSAGE_SENDDM_URL, json = {'token': user4['token'], 'message': 'hey2', 'dm_id': dm2})
    requests.delete(other.DM_REMOVE_URL, json = {'token': user2['token'], 'dm_id': dm2})
    response = requests.get(other.USERS_STATS_URL, params = {'token': user3['token']})
    channels_exist = [val['num_channels_exist'] for val in response.json()['workspace_stats']['channels_exist']]
    dms_exist = [val['num_dms_exist'] for val in response.json()['workspace_stats']['dms_exist']]
    messages_exist = [val['num_messages_exist'] for val in response.json()['workspace_stats']['messages_exist']]
    expected_channels = [0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
    expected_dms = [0, 0, 0, 1, 2, 2, 2, 2, 2, 2, 2, 1]
    expected_messages = [0, 0, 0, 0, 0, 1, 2, 3, 4, 5, 6, 4]
    assert channels_exist == expected_channels
    assert dms_exist == expected_dms
    assert messages_exist == expected_messages
    