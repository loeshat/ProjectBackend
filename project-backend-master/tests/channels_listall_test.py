from src.config import url
import requests
import pytest
import src.other as other

@pytest.fixture
def clear_store():
    requests.delete(other.CLEAR_URL, json={})

@pytest.fixture
def create_user():
    user_input = {'email': "z2537530@unsw.edu.au", 'password': "badpassword123", 'name_first': "Twix", 'name_last': "Chocolate"}
    request_data = requests.post(other.REGISTER_URL, json=user_input)
    user_info = request_data.json()
    return user_info

@pytest.fixture
def create_user2():
    user_input = {'email': "z934183@unsw.edu.au", 'password': "Password", 'name_first': "Snickers", 'name_last': "Lickers"}
    request_data = requests.post(other.REGISTER_URL, json=user_input)
    user_info = request_data.json()
    return user_info

def test_listall_v2_no_channels(clear_store, create_user):
    user_token = create_user['token']
    response = requests.get(other.CHANNELS_LISTALL_URL, params={'token': user_token})
    response_data = response.json()
    assert response.status_code == 200
    assert response_data == {'channels': []} 

def test_listall_v2_one_public(clear_store, create_user):
    user_token = create_user['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token, 'name': 'Channel1', 'is_public': True}).json()['channel_id']
    
    response = requests.get(other.CHANNELS_LISTALL_URL, params= {'token': user_token})
    response_data = response.json()
    assert response.status_code == 200
    assert response_data == {'channels': [{'channel_id': channel_id, 'name': 'Channel1'}]}

def test_listall_v2_mul_privacy(clear_store, create_user):
    user_token = create_user['token']
    channel_id1 = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token, 'name': 'Channel1', 'is_public': True}).json()['channel_id']
    channel_id2 = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token, 'name': 'Channel2', 'is_public': False}).json()['channel_id']
    channel_id3 = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token, 'name': 'Channel3', 'is_public': True}).json()['channel_id']
    channel_id4 = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token, 'name': 'Channel4', 'is_public': False}).json()['channel_id']

    response = requests.get(other.CHANNELS_LISTALL_URL, params={'token': user_token})
    response_data = response.json()
    assert response.status_code == 200

    expected = {'channels': [{'channel_id': channel_id1, 'name': 'Channel1'}, {'channel_id': channel_id2, 'name': 'Channel2'}, {'channel_id': channel_id3, 'name': 'Channel3'}, {'channel_id': channel_id4, 'name': 'Channel4'}]}
    assert response_data == expected

def test_listall_v2_not_in_bothprivacy(clear_store, create_user, create_user2):
    user_token_1 = create_user['token']
    user_token_2 = create_user2['token']

    channel_id1 = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token_1, 'name': 'Channel1', 'is_public': True}).json()['channel_id']
    channel_id2 = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token_1, 'name': 'Channel2', 'is_public': False}).json()['channel_id']
    channel_id3 = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token_2, 'name': 'Channel3', 'is_public': True}).json()['channel_id']
    channel_id4 = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token_2, 'name': 'Channel4', 'is_public': False}).json()['channel_id']

    response_1 = requests.get(other.CHANNELS_LISTALL_URL, params={'token': user_token_1})
    response_data_1 = response_1.json()
    assert response_1.status_code == 200

    expected = {'channels': [{'channel_id': channel_id1, 'name': 'Channel1'}, {'channel_id': channel_id2, 'name': 'Channel2'}, {'channel_id':  channel_id3, 'name': 'Channel3'}, {'channel_id': channel_id4, 'name': 'Channel4'}]}
    assert response_data_1 == expected

    response_2 = requests.get(other.CHANNELS_LISTALL_URL, params={'token': user_token_2})
    response_data_2 = response_1.json()
    assert response_2.status_code == 200
    assert response_data_2 == expected

def test_invalid_user_token(clear_store, create_user):
    user_token = create_user['token']
    requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token, 'name': 'Channel!', 'is_public': True}).json()['channel_id']
    requests.post(other.LOGOUT_URL, json={'token': user_token})
    response = requests.get(other.CHANNELS_LISTALL_URL, params={'token': user_token})
    assert response.status_code == 403




