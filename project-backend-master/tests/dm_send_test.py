from src.config import url
import requests
import pytest
import src.other as other

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

def test_basic_dm_send(clear_store, register_user_1, register_user_2):
    user_1 = register_user_1
    user_2 = register_user_2
    dm_id = requests.post(other.DM_CREATE_URL, json={"token": user_1['token'], "u_ids": [user_2['auth_user_id']]}).json()['dm_id']
    response = requests.post(other.MESSAGE_SENDDM_URL, json={'token': user_1['token'], "dm_id": dm_id, 'message': 'HELLO THERE'})
    assert response.status_code == 200
    message_id = response.json()['message_id']
    response = requests.get(other.DM_MESSAGES_URL, params = {"token": user_1['token'], 'dm_id': dm_id, 'start': 0})
    assert response.status_code == 200
    list_msg_ids = [message['message_id'] for message in response.json()['messages']]
    assert message_id in list_msg_ids
    msg_index = list_msg_ids.index(message_id)
    assert response.json()['messages'][msg_index]['message_id'] == message_id
    assert response.json()['messages'][msg_index]['u_id'] == user_1['auth_user_id']
    assert response.json()['messages'][msg_index]['message'] == "HELLO THERE"
    assert response.json()['start'] == 0
    assert response.json()['end'] == -1    

def test_short_message(clear_store, register_user_1, register_user_2):
    user_1 = register_user_1
    user_2 = register_user_2
    dm_id = requests.post(other.DM_CREATE_URL, json={"token": user_1['token'], "u_ids": [user_2['auth_user_id']]}).json()['dm_id']
    response = requests.post(other.MESSAGE_SENDDM_URL, json={'token': user_1['token'], "dm_id": dm_id, 'message': ''})
    assert response.status_code == 400

def test_long_message(clear_store, register_user_1, register_user_2):
    user_1 = register_user_1
    user_2 = register_user_2
    dm_id = requests.post(other.DM_CREATE_URL, json={"token": user_1['token'], "u_ids": [user_2['auth_user_id']]}).json()['dm_id']
    long_msg = ""
    for num in range(1000):
        long_msg += str(num)
    response = requests.post(other.MESSAGE_SENDDM_URL, json={'token': user_1['token'], "dm_id": dm_id, 'message': long_msg})
    assert response.status_code == 400

def test_invalid_dm_id(clear_store, register_user_1, register_user_2):
    user_1 = register_user_1
    user_2 = register_user_2
    dm_id = requests.post(other.DM_CREATE_URL, json={"token": user_1['token'], "u_ids": [user_2['auth_user_id']]}).json()['dm_id']
    response = requests.post(other.MESSAGE_SENDDM_URL, json={'token': user_1['token'], "dm_id": dm_id + 400, 'message': '1234567890'})
    assert response.status_code == 400

def test_user_not_in_channel(clear_store, register_user_1, register_user_2):
    user_1 = register_user_1
    user_2 = register_user_2
    dm_id = requests.post(other.DM_CREATE_URL, json={"token": user_1['token'], "u_ids": []}).json()['dm_id']
    response = requests.post(other.MESSAGE_SENDDM_URL, json={'token': user_2['token'], "dm_id": dm_id, 'message': '1234567890'})
    assert response.status_code == 403
    
    