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


def test_basic_channel_message_pin(clear_store, create_user):
    user_token_1 = create_user['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={
                               'token': user_token_1, 'name': 'My Channel!', 'is_public': True}).json()['channel_id']

    message_id = requests.post(other.MESSAGE_SEND_URL, json={
                               'token': user_token_1, 'channel_id': channel_id, 'message': "yay pin works"}).json()['message_id']
    response = requests.post(other.MESSAGE_PIN_URL, json={
                             'token': user_token_1, 'message_id': message_id})
    assert response.status_code == 200
    response = requests.get(other.CHANNEL_MESSAGES_URL, params={
                            'channel_id': channel_id, 'start': 0, 'token': user_token_1})
    list_msg_id = [message['message_id']
                   for message in response.json()['messages']]
    assert message_id in list_msg_id
    message_index = list_msg_id.index(message_id)
    assert response.json()['messages'][message_index]['is_pinned'] == True


def test_message_id_is_invalid(clear_store, create_user):
    user_token_1 = create_user['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={
                               'token': user_token_1, 'name': 'My Channel!', 'is_public': True}).json()['channel_id']

    message_id = requests.post(other.MESSAGE_SEND_URL, json={
                               'token': user_token_1, 'channel_id': channel_id, 'message': "yay pin works"}).json()['message_id']
    response = requests.post(other.MESSAGE_PIN_URL, json={
                             'token': user_token_1, 'message_id': int(message_id) + 1})
    assert response.status_code == 400


def test_user_does_not_have_permissions(clear_store, create_user, create_user2):
    user_token_1 = create_user['token']
    user_token_2 = create_user2['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={
                               'token': user_token_1, 'name': 'My Channel!', 'is_public': True}).json()['channel_id']
    response = requests.post(other.CHANNEL_JOIN_URL, json={
                             'token': user_token_2, 'channel_id': channel_id})
    assert response.status_code == 200
    message_id = requests.post(other.MESSAGE_SEND_URL, json={
                               'token': user_token_2, 'channel_id': channel_id, 'message': "yay pin works"}).json()['message_id']

    response = requests.post(other.MESSAGE_PIN_URL, json={
                             'token': user_token_2, 'message_id': message_id})
    assert response.status_code == 403


def test_message_is_already_pinned_channel(clear_store, create_user):
    user_token_1 = create_user['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={
                               'token': user_token_1, 'name': 'My Channel!', 'is_public': True}).json()['channel_id']

    message_id = requests.post(other.MESSAGE_SEND_URL, json={
                               'token': user_token_1, 'channel_id': channel_id, 'message': "yay pin works"}).json()['message_id']
    response = requests.post(other.MESSAGE_PIN_URL, json={
                             'token': user_token_1, 'message_id': message_id})
    assert response.status_code == 200
    response = requests.post(other.MESSAGE_PIN_URL, json={
                             'token': user_token_1, 'message_id': message_id})
    assert response.status_code == 400


def test_user_is_not_in_channel(clear_store, create_user, create_user2):
    user_token_1 = create_user['token']
    user_token_2 = create_user2['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={
                               'token': user_token_1, 'name': 'My Channel!', 'is_public': True}).json()['channel_id']

    message_id = requests.post(other.MESSAGE_SEND_URL, json={
                               'token': user_token_1, 'channel_id': channel_id, 'message': "yay pin works"}).json()['message_id']
    response = requests.post(other.MESSAGE_PIN_URL, json={
                             'token': user_token_2, 'message_id': message_id})
    assert response.status_code == 400


def test_basic_dm_message_pin(clear_store, create_user):
    user_token_1 = create_user['token']
    dm_id = requests.post(other.DM_CREATE_URL, json={
                          'token': user_token_1, 'u_ids': []}).json()['dm_id']
    message_id = requests.post(other.MESSAGE_SENDDM_URL, json={
                               'token': user_token_1, 'dm_id': dm_id, 'message': 'hey there'}).json()['message_id']
    response = requests.post(other.MESSAGE_PIN_URL, json={
                             'token': user_token_1, 'message_id': message_id})
    assert response.status_code == 200
    response = requests.get(other.DM_MESSAGES_URL, params={
                            "token": user_token_1, 'dm_id': dm_id, 'start': 0})
    assert response.status_code == 200
    list_msg_ids = [message['message_id']
                    for message in response.json()['messages']]
    assert message_id in list_msg_ids
    message_index = list_msg_ids.index(message_id)
    assert response.json()['messages'][message_index]['is_pinned'] == True


def test_user_and_message_not_in_same_dm(clear_store, create_user, create_user2):
    user_token_1 = create_user['token']
    user_token_2 = create_user2['token']
    dm_id = requests.post(other.DM_CREATE_URL, json={
                          'token': user_token_1, 'u_ids': []}).json()['dm_id']
    message_id = requests.post(other.MESSAGE_SENDDM_URL, json={
                               'token': user_token_1, 'dm_id': dm_id, 'message': 'hey there'}).json()['message_id']
    response = requests.post(other.MESSAGE_PIN_URL, json={
        'token': user_token_2, 'message_id': message_id})
    assert response.status_code == 400


def test_message_is_already_pinned_dm(clear_store, create_user):
    user_token_1 = create_user['token']
    dm_id = requests.post(other.DM_CREATE_URL, json={
                          'token': user_token_1, 'u_ids': []}).json()['dm_id']
    message_id = requests.post(other.MESSAGE_SENDDM_URL, json={
                               'token': user_token_1, 'dm_id': dm_id, 'message': 'hey there'}).json()['message_id']
    response = requests.post(other.MESSAGE_PIN_URL, json={
                             'token': user_token_1, 'message_id': message_id})
    assert response.status_code == 200
    response = requests.post(other.MESSAGE_PIN_URL, json={
                             'token': user_token_1, 'message_id': message_id})
    assert response.status_code == 400
