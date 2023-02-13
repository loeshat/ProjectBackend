from src.config import url
from .helper_functions import is_valid_dictionary_output
import requests
import pytest
import src.other as other
import tests.helper_functions as helper_functions


@pytest.fixture
def clear_store():
    requests.delete(other.CLEAR_URL, json={})

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
def create_user3():
    user_input = {'email': "z536601@unsw.edu.au", 'password': "1243Bops", 'name_first': "Mars", 'name_last': "Bars"}
    user_info = requests.post(other.REGISTER_URL, json=user_input).json()
    return user_info

@pytest.fixture
def create_stub_user():
    user_input = {'email': "example@gmail.com", 'password': "hello123", 'name_first': "Hayden",'name_last': "Jacobs"}
    user_info = requests.post(other.REGISTER_URL, json=user_input).json()
    return user_info

def test_creator_of_channel(clear_store, create_user, create_user2):
    user_token_1 = create_user['token']
    user_token_2 = create_user2['token']
    channel_id_1 = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token_1, 'name': 'My Channel!', 'is_public': True}).json()['channel_id']
    channel_id_2 = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token_2, 'name': 'kitchen', 'is_public': False}).json()['channel_id']
    channel_details_1 = requests.get(other.CHANNEL_DETAILS_URL, params={'channel_id': channel_id_1, 'token': user_token_1}).json()
    channel_details_2 = requests.get(other.CHANNEL_DETAILS_URL, params={'channel_id': channel_id_2, 'token': user_token_2}).json()

    assert is_valid_dictionary_output(channel_details_1, {'name': str, 'is_public': bool, 'owner_members': list, 'all_members': list})
    for user in channel_details_1['owner_members']:
        assert is_valid_dictionary_output(user, {'name_first': str, 'name_last': str, 'email': str, 'handle_str': str, 'u_id': int, 'profile_img_url': str})

    for user in channel_details_1['all_members']:
        assert is_valid_dictionary_output(user, {'name_first': str, 'name_last': str, 'email': str, 'handle_str': str, 'u_id': int, 'profile_img_url': str})
    
    assert is_valid_dictionary_output(channel_details_2, {'name': str, 'is_public': bool, 'owner_members': list, 'all_members': list})
    for user in channel_details_2['owner_members']:
        assert is_valid_dictionary_output(user, {'name_first': str, 'name_last': str, 'email': str, 'handle_str': str, 'u_id': int, 'profile_img_url': str})

    for user in channel_details_2['all_members']:
        assert is_valid_dictionary_output(user, {'name_first': str, 'name_last': str, 'email': str, 'handle_str': str, 'u_id': int, 'profile_img_url': str})

def test_member_of_public_channel(clear_store, create_user, create_user2):
    user_token_1 = create_user['token']
    user_token_2 = create_user2['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token_1, 'name': 'My Channel!', 'is_public': True}).json()['channel_id']
    channel_join = requests.post(other.CHANNEL_JOIN_URL, json={'token': user_token_2, 'channel_id': channel_id}).json()
    channel_details_1 = requests.get(other.CHANNEL_DETAILS_URL, params={'channel_id': channel_id, 'token': user_token_1}).json()
    channel_details_2 = requests.get(other.CHANNEL_DETAILS_URL, params={'channel_id': channel_id, 'token': user_token_2}).json()
    assert channel_details_1['name'] == "My Channel!"
    assert channel_details_1['is_public'] == True
    assert helper_functions.strip_array_url_image(channel_details_1['owner_members']) == [
                                {
                                    'u_id': create_user['auth_user_id'],
                                    'email': "z432324@unsw.edu.au",
                                    'name_first': "Twix",
                                    'name_last': "Chocolate",
                                    'handle_str': "twixchocolate",
                                }
                            ]
    assert helper_functions.strip_array_url_image(channel_details_1['all_members']) == [{
                                    'u_id': create_user['auth_user_id'],
                                    'email': "z432324@unsw.edu.au",
                                    'name_first': "Twix",
                                    'name_last': "Chocolate",
                                    'handle_str': "twixchocolate",
                                },
                                {
                                    'u_id': create_user2['auth_user_id'],
                                    'email': "z54626@unsw.edu.au",
                                    'name_first': "Snickers",
                                    'name_last': "Lickers",
                                    'handle_str': "snickerslickers",
                                },
                            ]
    
    assert channel_join == {}
    

    assert channel_details_1 == channel_details_2

def test_invalid_user(clear_store, create_user):
    user_token = create_user['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token, 'name': 'Channel!', 'is_public': True}).json()['channel_id']
    requests.post(other.LOGOUT_URL, json={'token': user_token})
    request_data = requests.get(other.CHANNEL_DETAILS_URL, params={'channel_id': channel_id}, json={'token': user_token})
    assert request_data.status_code == 403

def test_unauthorised_user_id(clear_store, create_user, create_user2, create_user3):
    user_token_1 = create_user['token']
    user_token_2 = create_user2['token']
    user_token_3 = create_user3['token']
    channel_id_1 = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token_1, 'name': 'My Channel!', 'is_public': True}).json()['channel_id']
    channel_id_2 = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token_2, 'name': 'kitchen', 'is_public': False}).json()['channel_id']
    request_data_1 = requests.get(other.CHANNEL_DETAILS_URL, params={'channel_id': channel_id_1, 'token': user_token_2})
    request_data_2 = requests.get(other.CHANNEL_DETAILS_URL, params={'channel_id': channel_id_2, 'token': user_token_3})
    assert request_data_1.status_code == 403
    assert request_data_2.status_code == 403

def test_invalid_channel_id(clear_store, create_user, create_user2):
    user_token_1 = create_user['token']
    user_token_2 = create_user2['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={'token': user_token_1, 'name': 'My Channel', 'is_public': True}).json()['channel_id']
    request_data_1 = requests.get(other.CHANNEL_DETAILS_URL, params={'channel_id': channel_id + 1, 'token': user_token_1})
    request_data_2 = requests.get(other.CHANNEL_DETAILS_URL, params={'channel_id': channel_id + 2, 'token': user_token_2})
    assert request_data_1.status_code == 400
    assert request_data_2.status_code == 400

def test_from_stub_code(clear_store, create_stub_user):
    stub_token = create_stub_user['token']
    stub_uid = create_stub_user['auth_user_id']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json={'token': stub_token, 'name': "Hayden", 'is_public': False}).json()['channel_id']
    channel_details = requests.get(other.CHANNEL_DETAILS_URL, params={'channel_id': channel_id, 'token': stub_token})
    assert channel_details.json()['name'] == "Hayden"
    assert channel_details.json()['is_public'] == False
    assert helper_functions.strip_array_url_image(channel_details.json()['owner_members']) == [{'u_id': stub_uid, 'email': 'example@gmail.com', 'name_first': 'Hayden','name_last': 'Jacobs','handle_str': 'haydenjacobs'}]
    assert helper_functions.strip_array_url_image(channel_details.json()['all_members']) == [{'u_id': stub_uid, 'email': 'example@gmail.com', 'name_first': 'Hayden', 'name_last': 'Jacobs', 'handle_str': 'haydenjacobs'}]