
import pytest
import requests
from .helper_functions import is_valid_dictionary_output
from src.config import url
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


def test_basic_message_send(clear_store, create_user):
    user_token_1 = create_user['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={
                               'token': user_token_1, 'name': 'My Channel!', 'is_public': True}).json()['channel_id']
                               
    response = requests.post(other.MESSAGE_SEND_URL, json={'token': user_token_1, 'channel_id': channel_id, 'message': "Hello World"})
    assert response.status_code == 200
    message_id = response.json()['message_id']
    assert is_valid_dictionary_output(response.json(), {'message_id': int})
    response = requests.get(other.CHANNEL_MESSAGES_URL, params={'channel_id': channel_id, 'start': 0, 'token': user_token_1})                                                        
    assert response.status_code == 200
    list_msg_ids = [message['message_id'] for message in response.json()['messages']]
    assert message_id in list_msg_ids
    msg_index = list_msg_ids.index(message_id)
    assert response.json()['messages'][msg_index]['message_id'] == message_id
    assert response.json()['messages'][msg_index]['u_id'] == create_user['auth_user_id']
    assert response.json()['messages'][msg_index]['message'] == "Hello World"
    assert response.json()['start'] == 0
    assert response.json()['end'] == -1    
    

def test_basic_message_send_v2(clear_store, create_user, create_user2):
    user_token_1 = create_user['token']
    user_token_2 = create_user2['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={
                               'token': user_token_1, 'name': 'My Channel!', 'is_public': True}).json()['channel_id']
    response = requests.post(other.CHANNEL_JOIN_URL, json={
                             'token': user_token_2, 'channel_id': channel_id})  
    response = requests.post(other.MESSAGE_SEND_URL, json={'token': user_token_1, 'channel_id': channel_id, 'message': "Hello World"})
    message_id1 = response.json()['message_id']
    assert response.status_code == 200 
    assert is_valid_dictionary_output(response.json(), {'message_id': int})
    response = requests.post(other.MESSAGE_SEND_URL, json={'token': user_token_2, 'channel_id': channel_id, 'message': "Hello World2"})
    message_id2 = response.json()['message_id']
    assert response.status_code == 200
    assert is_valid_dictionary_output(response.json(), {'message_id': int})
    response = requests.get(other.CHANNEL_MESSAGES_URL, params={'channel_id': channel_id, 'start': 0, 'token': user_token_1})
    assert response.status_code == 200
    assert response.json()['start'] == 0
    assert response.json()['end'] == -1
    for message in response.json()['messages']:
        if message['message_id'] == message_id1:
            assert message['message'] == "Hello World"
            assert message['u_id'] == create_user['auth_user_id']
        if message['message_id'] == message_id2:
            assert message['message'] == "Hello World2"
            assert message['u_id'] == create_user2['auth_user_id']    

def test_check_accessibility_of_messages_across_channels(clear_store, create_user, create_user2):
    user_token_1 = create_user['token']
    user_token_2 = create_user2['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={
                               'token': user_token_1, 'name': 'My Channel!', 'is_public': True}).json()['channel_id']
    channel_id2 = requests.post(other.CHANNELS_CREATE_URL, json={
                               'token': user_token_2, 'name': 'My Channel2!', 'is_public': True}).json()['channel_id'] 
    response = requests.post(other.MESSAGE_SEND_URL, json={'token': user_token_1, 'channel_id': channel_id, 'message': "Hello World"})
    assert response.status_code == 200 
    assert is_valid_dictionary_output(response.json(), {'message_id': int})
    response = requests.get(other.CHANNEL_MESSAGES_URL, params={'channel_id': channel_id2, 'start': 0, 'token': user_token_2})
    assert response.status_code == 200
    assert response.json() == {'messages': [], 'start': 0, 'end': -1}

def test_invalid_message(clear_store, create_user):
    user_token_1 = create_user['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={
                               'token': user_token_1, 'name': 'My Channel!', 'is_public': True}).json()['channel_id']
    response = requests.post(other.MESSAGE_SEND_URL, json={'token': user_token_1, 'channel_id': channel_id, 'message': ""})
    assert response.status_code == 400

def test_user_not_part_of_channel(clear_store, create_user, create_user2):
    user_token_1 = create_user['token']
    user_token_2 = create_user2['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={
                               'token': user_token_1, 'name': 'My Channel!', 'is_public': True}).json()['channel_id']
    response = requests.post(other.MESSAGE_SEND_URL, json={'token': user_token_2, 'channel_id': channel_id, 'message': "Hello World"})
    assert response.status_code == 403

def test_channel_not_valid(clear_store, create_user):
    user_token_1 = create_user['token']
    response = requests.post(other.MESSAGE_SEND_URL, json={'token': user_token_1, 'channel_id': "100", 'message': "Hello World"})
    assert response.status_code == 400
