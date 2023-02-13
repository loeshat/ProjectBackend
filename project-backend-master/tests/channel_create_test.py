from src.config import url
import pytest
import requests
import src.other as other


@pytest.fixture
def create_user():
    user_input = {'email': "z432324@unsw.edu.au", 'password': "badpassword123", 'name_first': "Twix", 'name_last': "Chocolate"}
    user_info = requests.post(other.REGISTER_URL, json=user_input).json()
    return user_info

@pytest.fixture
def create_user2():
    user_input = {'email': "z54626@unsw.edu.au", 'password': "Password", 'name_first': "Snickers", 'name_last': "Lickers"}
    user_info = requests.post(other.REGISTER_URL, json=user_input).json()
    return user_info

@pytest.fixture
def clear_store():
    requests.delete(other.CLEAR_URL, json={})

def test_add_public_channel(clear_store, create_user):
    user1 = create_user
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={'token': user1['token'], 'name': 'my house', 'is_public': True}).json()['channel_id']
    response = requests.get(other.CHANNELS_LIST_URL, params={'token': user1['token']})
    assert response.json() == { 'channels': [{'channel_id': channel_id, 'name': 'my house'}]}
    response = requests.get(other.CHANNEL_DETAILS_URL, params={'token': user1['token'], 'channel_id': channel_id})


def test_add_private_channel(clear_store, create_user):
    user1 = create_user
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={'token': user1['token'], 'name': 'my house', 'is_public': False}).json()['channel_id']
    response = requests.get(other.CHANNELS_LIST_URL, params={'token': user1['token']})
    assert response.json() == { 'channels': [{'channel_id': channel_id, 'name': 'my house'}]}
    

def test_null_name(clear_store, create_user):
    user1 = create_user
    response = requests.post(other.CHANNELS_CREATE_URL, json={'token': user1['token'], 'name': '', 'is_public': True})
    assert response.status_code == 400
    

def test_long_name(clear_store, create_user):
    user1 = create_user
    response = requests.post(other.CHANNELS_CREATE_URL, json={'token': user1['token'], 'name': 'sadoiasjdoiasjdoaisdjaoisdjaoisdjaoisjdadsjgfoiasjfgoiasjdfoiajsdofiajsdoifjaosdifjaoisdjf', 'is_public': True})
    assert response.status_code == 400

def test_invalid_JWT(clear_store, create_user):
    user1 = create_user
    requests.post(other.LOGOUT_URL, json={'token': user1['token']})
    response = requests.post(other.CHANNELS_CREATE_URL, json={'token': user1['token'], 'name': 'hello', 'is_public': True})
    assert response.status_code == 403


