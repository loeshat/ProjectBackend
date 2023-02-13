from src.config import url
import pytest
import requests
import src.other as other
import tests.helper_functions as helper_functions


@pytest.fixture
def clear_store():
    requests.delete(other.CLEAR_URL, json={})


@pytest.fixture
def create_user():
    user_input = {'email': "z432324@unsw.edu.au",
                  'password': "password", 'name_first': "Name", 'name_last': "Lastname"}
    request_data = requests.post(other.REGISTER_URL, json=user_input)
    user_info = request_data.json()
    return user_info


@pytest.fixture
def create_user2():
    user_input = {'email': "z432325@unsw.edu.au", 'password': "password1",
                  'name_first': "Name1", 'name_last': "Lastname1"}
    request_data = requests.post(other.REGISTER_URL, json=user_input)
    user_info = request_data.json()
    return user_info


@pytest.fixture
def create_user3():
    user_input = {'email': "z432326@unsw.edu.au",
                  'password': "password2", 'name_first': "Name2", 'name_last': "Lastname2"}
    request_data = requests.post(other.REGISTER_URL, json=user_input)
    user_info = request_data.json()
    return user_info


def test_private_channel(clear_store, create_user, create_user2):
    user_token_1 = create_user['token']
    user_token_2 = create_user2['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={
                               'token': user_token_1, 'name': 'My Channel!', 'is_public': False}).json()['channel_id']
    response = requests.post(other.CHANNEL_JOIN_URL, json={
                             'token': user_token_2, 'channel_id': channel_id})
    assert response.status_code == 403


def test_successfully_joined_channel(clear_store, create_user, create_user2):
    user_token_1 = create_user['token']
    user_token_2 = create_user2['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={
                               'token': user_token_1, 'name': 'test', 'is_public': True}).json()['channel_id']
    response = requests.post(other.CHANNEL_JOIN_URL, json={
                             'token': user_token_2, 'channel_id': channel_id})
    assert response.status_code == 200
    channel_details = requests.get(other.CHANNEL_DETAILS_URL, params={'channel_id': channel_id, 'token': user_token_2}).json()
    assert channel_details['name'] == 'test'
    assert channel_details['is_public'] == True
    assert helper_functions.strip_array_url_image(channel_details['owner_members']) == [
            {
                'u_id': create_user['auth_user_id'],
                'email': 'z432324@unsw.edu.au',
                'name_first': 'Name',
                'name_last': 'Lastname',
                'handle_str': 'namelastname',
            }
        ]
    assert helper_functions.strip_array_url_image(channel_details['all_members']) == [
            {
                'u_id': create_user['auth_user_id'],
                'email': 'z432324@unsw.edu.au',
                'name_first': 'Name',
                'name_last': 'Lastname',
                'handle_str': 'namelastname',
            },
            {
                'u_id': create_user2['auth_user_id'],
                'email': 'z432325@unsw.edu.au',
                'name_first': 'Name1',
                'name_last': 'Lastname1',
                'handle_str': 'name1lastname1',
            },
        ]


def test_successfully_joined_channel2(clear_store, create_user, create_user2, create_user3):
    user_token_1 = create_user['token']
    user_token_2 = create_user2['token']
    user_token_3 = create_user3['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={
                               'token': user_token_1, 'name': 'test2', 'is_public': True}).json()['channel_id']
    response_1 = requests.post(other.CHANNEL_JOIN_URL, json={
                               'token': user_token_2, 'channel_id': channel_id})
    assert response_1.status_code == 200
    response_2 = requests.post(other.CHANNEL_JOIN_URL, json={
                               'token': user_token_3, 'channel_id': channel_id})
    assert response_2.status_code == 200
    channel_details = requests.get(other.CHANNEL_DETAILS_URL, params={'channel_id': channel_id, 'token': user_token_3}).json()
    assert channel_details['name'] == 'test2'
    assert channel_details['is_public'] == True
    assert helper_functions.strip_array_url_image(channel_details['owner_members']) == [
            {
                'u_id': create_user['auth_user_id'],
                'email': 'z432324@unsw.edu.au',
                'name_first': 'Name',
                'name_last': 'Lastname',
                'handle_str': 'namelastname',
            }
        ]
    assert helper_functions.strip_array_url_image(channel_details['all_members']) == [
            {
                'u_id': create_user['auth_user_id'],
                'email': 'z432324@unsw.edu.au',
                'name_first': 'Name',
                'name_last': 'Lastname',
                'handle_str': 'namelastname',
            },
            {
                'u_id': create_user2['auth_user_id'],
                'email': 'z432325@unsw.edu.au',
                'name_first': 'Name1',
                'name_last': 'Lastname1',
                'handle_str': 'name1lastname1',
            },
            {
                'u_id': create_user3['auth_user_id'],
                'email': 'z432326@unsw.edu.au',
                'name_first': 'Name2',
                'name_last': 'Lastname2',
                'handle_str': 'name2lastname2',
            },
        ]

def test_channel_doesnt_exist(clear_store, create_user):
    user_token_1 = create_user['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={
                               'token': user_token_1, 'name': 'test2', 'is_public': True}).json()['channel_id']
    response = requests.post(other.CHANNEL_JOIN_URL, json={
                             'token': user_token_1, 'channel_id': channel_id + 1})
    assert response.status_code == 400


def test_user_already_in_channel(clear_store, create_user):
    user_token_1 = create_user['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={
                               'token': user_token_1, 'name': 'My Channel!', 'is_public': True}).json()['channel_id']
    response = requests.post(other.CHANNEL_JOIN_URL, json={
                             'token': user_token_1, 'channel_id': channel_id})
    assert response.status_code == 400


def test_list_and_join(clear_store, create_user, create_user2):
    user_token_1 = create_user['token']
    user_token_2 = create_user2['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={
                               'token': user_token_1, 'name': 'test2', 'is_public': True}).json()['channel_id']

    assert requests.get(other.CHANNELS_LIST_URL, params={'token': user_token_1}).json() == {'channels': [{'channel_id': channel_id,'name': 'test2'}]}
    assert requests.get(other.CHANNELS_LISTALL_URL, params={'token': user_token_2}).json() == requests.get(other.CHANNELS_LIST_URL, params={'token': user_token_1}).json()
    assert requests.get(other.CHANNELS_LIST_URL, params={'token': user_token_2}).json() == {'channels': []}
    response = requests.post(other.CHANNEL_JOIN_URL, json={
                             'token': user_token_2, 'channel_id': channel_id})
    assert response.status_code == 200
    assert requests.get(other.CHANNELS_LIST_URL, params={'token': user_token_2}).json() == {'channels': [{'channel_id': channel_id,'name': 'test2'}]}

def test_global_owner_join_private(clear_store, create_user, create_user2, create_user3):
    user_token_1 = create_user['token']
    user_token_2 = create_user2['token']
    user_token_3 = create_user3['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={
                               'token': user_token_2, 'name': 'secret', 'is_public': False}).json()['channel_id']
    response = requests.post(other.CHANNEL_JOIN_URL, json={
                             'token': user_token_3, 'channel_id': channel_id})
    assert response.status_code == 403
    assert requests.get(other.CHANNELS_LIST_URL, params={'token': user_token_1}).json() == {'channels': []}
    response = requests.post(other.CHANNEL_JOIN_URL, json={
                             'token': user_token_1, 'channel_id': channel_id})
    assert response.status_code == 200
    assert requests.get(other.CHANNELS_LIST_URL, params={'token': user_token_1}).json() == {'channels': [{'channel_id': channel_id,'name': 'secret'}]}


def test_fake_id(clear_store, create_user, create_user2):
    user_token_1 = create_user['token']
    user_token_2 = create_user2['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={
                               'token': user_token_1, 'name': 'test2', 'is_public': True}).json()['channel_id']
    requests.post(other.LOGOUT_URL, json={'token': user_token_2})
    response = requests.post(other.CHANNEL_JOIN_URL, json={
                             'token': user_token_2, 'channel_id': channel_id})
    assert response.status_code == 403
