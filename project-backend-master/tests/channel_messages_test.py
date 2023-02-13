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

def test_basic_get_messages_success(clear_store, create_user):
    user_token_1 = create_user['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={
                               'token': user_token_1, 'name': 'My Channel!', 'is_public': True}).json()['channel_id']
    response = requests.get(other.CHANNEL_MESSAGES_URL, params= {'channel_id': channel_id, 'start':0, 'token': user_token_1})
    assert response.json() == {'messages': [], 'start': 0, 'end': -1}         
    message_id = requests.post(other.MESSAGE_SEND_URL, json={'token': user_token_1, 'channel_id': channel_id, 'message': "Leo loves tests!"}).json()['message_id']      
    response = requests.get(other.CHANNEL_MESSAGES_URL, params={'channel_id': channel_id, 'start':0, 'token': user_token_1})
    assert response.json()['start'] == 0
    assert response.json()['end'] == -1
    list_msg_id = [message['message_id'] for message in response.json()['messages']]
    assert message_id in list_msg_id
    message_index = list_msg_id.index(message_id)
    assert response.json()['messages'][message_index]['message'] == "Leo loves tests!"
    assert response.json()['messages'][message_index]['message_id'] == 0
    assert response.json()['messages'][message_index]['u_id'] == 0

def test_pagination_functionality(clear_store, create_user):
    user_1_token = create_user['token']

    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={"token": user_1_token, "name": "My Paginated Channel", "is_public": False}).json()['channel_id']

    for i in range(0, 124):
        requests.post(other.MESSAGE_SEND_URL, json={"token": user_1_token, "channel_id": channel_id, "message": str(i)})

    request_messages = requests.get(other.CHANNEL_MESSAGES_URL, params={'token': user_1_token, 'channel_id': channel_id, 'start': 0})
    counter = 123
    current_start = 0
    while request_messages.json()['end'] != -1:
        assert request_messages.json()['start'] == current_start
        assert request_messages.json()['end'] == current_start + 50
        assert len(request_messages.json()['messages']) == 50
        for message in request_messages.json()['messages']:
            assert message['message'] == str(counter)
            counter -= 1
        current_start += 50
        request_messages = requests.get(other.CHANNEL_MESSAGES_URL, params={'token': user_1_token, 'channel_id': channel_id, 'start': current_start})
    for message in request_messages.json()['messages']:
        assert message['message'] == str(counter)
        counter -= 1
    assert counter == -1


def test_invalid_channel_id(clear_store, create_user):
    user_token_1 = create_user['token']
    response = requests.get(other.CHANNEL_MESSAGES_URL, params= {'channel_id': 1, 'start':0, 'token': user_token_1})
    assert response.status_code == 400


def test_user_not_in_channel(clear_store, create_user, create_user2):
    user_token_1 = create_user['token']
    user_token_2 = create_user2['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={
                               'token': user_token_1, 'name': 'My Channel!', 'is_public': True}).json()['channel_id']
    response = requests.get(other.CHANNEL_MESSAGES_URL, params= {'channel_id': channel_id, 'start':0, 'token': user_token_2})
    assert response.status_code == 403


def test_channel_messages_with_no_messages(clear_store, create_user):
    user_token_1 = create_user['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={
                               'token': user_token_1, 'name': 'My Channel!', 'is_public': True}).json()['channel_id']
    response = requests.get(other.CHANNEL_MESSAGES_URL, params={'channel_id': channel_id, 'start': 0, 'token': user_token_1})
    expected_output = {'messages': [], 'start': 0, 'end': -1}
    assert response.json() == expected_output
    assert response.status_code == 200


def test_channel_messages_start_exceeds(clear_store, create_user):
    user_token_1 = create_user['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={
                               'token': user_token_1, 'name': 'My Channel!', 'is_public': True}).json()['channel_id']
    current = 0
    response = requests.get(other.CHANNEL_MESSAGES_URL, params={'channel_id': channel_id, 'start': current, 'token': user_token_1})
    # Spew through the messages until we reach the end
    while response.json()['end'] != -1:
        current += 50
        response = requests.get(other.CHANNEL_MESSAGES_URL, params={'channel_id': channel_id, 'start': current, 'token': user_token_1})
    response = requests.get(other.CHANNEL_MESSAGES_URL, params={'channel_id': channel_id, 'start': current + 100, 'token': user_token_1})
    assert response.status_code == 400


def test_invalid_auth_id(clear_store, create_user):
    user_token_1 = create_user['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={
                               'token': user_token_1, 'name': 'My Channel!', 'is_public': True}).json()['channel_id']
    requests.post(other.LOGOUT_URL, json={'token': user_token_1})
    response = requests.get(other.CHANNEL_MESSAGES_URL, params={'channel_id': channel_id, 'start': 0, 
                            'token': user_token_1})
    assert response.status_code == 403
