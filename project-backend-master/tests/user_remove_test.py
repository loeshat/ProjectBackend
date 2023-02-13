from src.config import url
import pytest
import requests
import src.other as other
import tests.helper_functions as helper_functions

@pytest.fixture
def clear_store():
    requests.delete(other.CLEAR_URL, json={})
    
@pytest.fixture
def register_user_1():
    response = requests.post(other.REGISTER_URL, json={"email":"z55555@unsw.edu.au", "password":"passwordlong", "name_first":"Jake", "name_last":"Renzella"}).json()
    return response

@pytest.fixture
def register_user_2():
    response = requests.post(other.REGISTER_URL, json={"email":"z12345@unsw.edu.au", "password": "epicpassword", "name_first": "FirstName", "name_last": "LastName"}).json()
    return response

def test_basic_user_remove(clear_store, register_user_1, register_user_2):
    user_1 = register_user_1
    user_2 = register_user_2
    assert 400 == requests.post(other.REGISTER_URL, json={"email":"z12345@unsw.edu.au", "password": "epicpassword", "name_first": "FirstName", "name_last": "LastName"}).status_code
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={"name": "MYCHANNEL", "token": user_2['token'], "is_public": True}).json()['channel_id']
    requests.post(other.CHANNEL_JOIN_URL, json={'channel_id': channel_id, "token": user_1['token']})
    requests.post(other.MESSAGE_SEND_URL, json={"token": user_2['token'], "channel_id": channel_id, "message": "HEY THERE GUYS"})
    response = requests.delete(other.USER_REMOVE_URL, json={'token': user_1['token'], 'u_id': user_2['auth_user_id']})
    channel_messages = requests.get(other.CHANNEL_MESSAGES_URL, params={'channel_id': channel_id, 'start': 0, "token": user_1['token']}).json()['messages']
    assert channel_messages[0]['message'] == 'Removed user'
    assert response.status_code == 200
    response = requests.get(other.USER_PROFILE_URL, params= {'u_id': user_2['auth_user_id'], 'token': user_1['token']})
    assert helper_functions.strip_url_image_profile(response.json()['user']) == {"u_id": user_2['auth_user_id'], "email":"", "name_first": "Removed", "name_last": "user", "handle_str": ""}
    assert 200 == requests.post(other.REGISTER_URL, json={"email":"z12345@unsw.edu.au", "password": "epicpassword", "name_first": "FirstName", "name_last": "LastName"}).status_code
    
def test_basic_user_remove_v2(clear_store, register_user_1, register_user_2):
    user_1 = register_user_1
    user_2 = register_user_2
    requests.post(other.CHANGE_PERM_URL, json={'token': user_1['token'], 'u_id': user_2['auth_user_id'], 'permission_id': other.GLOBAL_PERMISSION_OWNER})
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={"name": "MYCHANNEL", "token": user_1['token'], "is_public": True}).json()['channel_id']
    requests.post(other.DM_CREATE_URL, json={'token': user_1['token'], 'u_ids': [user_2['auth_user_id']]})
    requests.post(other.CHANNEL_JOIN_URL, json={'channel_id': channel_id, "token": user_2['token']})
    response = requests.delete(other.USER_REMOVE_URL, json={'token': user_1['token'], 'u_id': user_2['auth_user_id']})
    assert response.status_code == 200

def test_invalid_u_id(clear_store, register_user_1, register_user_2):
    response = requests.delete(other.USER_REMOVE_URL, json={'token': register_user_1['token'], 'u_id': register_user_2['auth_user_id'] + 1})
    assert response.status_code == 400

def test_invalid_only_user(clear_store, register_user_1):
     response = requests.delete(other.USER_REMOVE_URL, json={'token': register_user_1['token'], 'u_id': register_user_1['auth_user_id']})
     assert response.status_code == 400
     
def test_unauthorised_attempt(clear_store, register_user_1, register_user_2):
    response = requests.delete(other.USER_REMOVE_URL, json={'token': register_user_2['token'], 'u_id': register_user_1['auth_user_id']})
    assert response.status_code == 403

def test_remove_after_leave(clear_store, register_user_1, register_user_2):
    user_1 = register_user_1
    user_2 = register_user_2
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={"name": "MYCHANNEL", "token": user_1['token'], "is_public": True}).json()['channel_id']
    requests.post(other.CHANNEL_JOIN_URL, json={'channel_id': channel_id, "token": user_2['token']})   
    requests.post(other.MESSAGE_SEND_URL, json={"token": user_2['token'], "channel_id": channel_id, "message": "HEY THERE GUYS"})
    requests.post(other.MESSAGE_SEND_URL, json={"token": user_1['token'], "channel_id": channel_id, "message": "HEY THERE GUYS IM ALSO HERE"})
    requests.post(other.CHANNEL_LEAVE_URL, json={'token': user_2['token'], 'channel_id': channel_id})
    response = requests.delete(other.USER_REMOVE_URL, json={'token': user_1['token'], 'u_id': user_2['auth_user_id']})
    assert response.status_code == 200
    channel_messages = requests.get(other.CHANNEL_MESSAGES_URL, params={'channel_id': channel_id, 'start': 0, "token": user_1['token']}).json()['messages']
    removed_messages = [message['message_id'] for message in channel_messages if message['u_id'] == user_2['auth_user_id']]
    for message in channel_messages:
        if message['message_id'] in removed_messages:
            assert message['message'] == 'Removed user'
        else:
            assert message['message'] != 'Removed user'
            
def test_remove_after_leave_dm(clear_store, register_user_1, register_user_2):
    user_1 = register_user_1
    user_2 = register_user_2
    dm_id = requests.post(other.DM_CREATE_URL, json={"token": user_1['token'], "u_ids": [user_2['auth_user_id']]}).json()['dm_id']  
    requests.post(other.MESSAGE_SENDDM_URL, json={"token": user_2['token'], "dm_id": dm_id, "message": "HEY THERE GUYS"})
    requests.post(other.MESSAGE_SENDDM_URL, json={"token": user_1['token'], "dm_id": dm_id, "message": "HEY THERE GUYS IM ALSO HERE"})
    requests.post(other.DM_LEAVE_URL, json={'token': user_2['token'], 'dm_id': dm_id})
    response = requests.delete(other.USER_REMOVE_URL, json={'token': user_1['token'], 'u_id': user_2['auth_user_id']})
    assert response.status_code == 200
    dm_messages = requests.get(other.DM_MESSAGES_URL, params={'dm_id': dm_id, 'start': 0, "token": user_1['token']}).json()['messages']
    removed_messages = [message['message_id'] for message in dm_messages if message['u_id'] == user_2['auth_user_id']]
    for message in dm_messages:
        if message['message_id'] in removed_messages:
            assert message['message'] == 'Removed user'
        else:
            assert message['message'] != 'Removed user'
    
