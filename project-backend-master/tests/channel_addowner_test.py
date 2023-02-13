from src.error import AccessError
from src.config import port, url
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
    user_info = requests.post(other.REGISTER_URL, json = user_input).json()
    return user_info

@pytest.fixture
def create_user2():
    user_input = {'email': "z54626@unsw.edu.au", 'password': "Password", 'name_first': "Snickers", 'name_last': "Lickers"}
    user_info = requests.post(other.REGISTER_URL, json = user_input).json()
    return user_info

@pytest.fixture
def create_user3():
    user_input = {'email': "z536601@unsw.edu.au", 'password': "1243Bops", 'name_first': "Mars", 'name_last': "Bars"}
    user_info = requests.post(other.REGISTER_URL, json = user_input).json()
    return user_info

def test_owner_addowner(clear_store, create_user, create_user2):
    user_token_1 = create_user['token']
    user_token_2 = create_user2['token']
    channel_id_1 = requests.post(other.CHANNELS_CREATE_URL, json = {'token': user_token_1, 'name': 'My Channel!', 'is_public': True}).json()['channel_id']
    channel_id_2 = requests.post(other.CHANNELS_CREATE_URL, json = {'token': user_token_2, 'name': 'kitchen', 'is_public': True}).json()['channel_id']
    requests.post(other.CHANNEL_JOIN_URL, json = {'token': user_token_2, 'channel_id': channel_id_1})
    requests.post(other.CHANNEL_JOIN_URL, json = {'token': user_token_1, 'channel_id': channel_id_2})
    request_data_1 = requests.post(other.CHANNEL_ADDOWNER_URL, json = {'token': user_token_1, 'channel_id': channel_id_1, 'u_id': create_user2['auth_user_id']})
    request_data_2 = requests.post(other.CHANNEL_ADDOWNER_URL, json = {'token': user_token_2, 'channel_id': channel_id_2, 'u_id': create_user['auth_user_id']})
    channel_details_1 = requests.get(other.CHANNEL_DETAILS_URL, params = {'token': user_token_1, 'channel_id': channel_id_2}).json()
    channel_details_2 = requests.get(other.CHANNEL_DETAILS_URL, params = {'token': user_token_2, 'channel_id': channel_id_1}).json()

    assert request_data_1.json() == {}
    assert request_data_1.status_code == 200
    assert request_data_2.json() == {}
    assert request_data_2.status_code == 200
    assert helper_functions.strip_array_url_image(channel_details_1['owner_members']) == [
                                                    {
                                                        'u_id': create_user2['auth_user_id'],
                                                        'email': "z54626@unsw.edu.au",
                                                        'name_first': "Snickers",
                                                        'name_last': "Lickers",
                                                        'handle_str': "snickerslickers",
                                                    },
                                                    {
                                                        'u_id': create_user['auth_user_id'],
                                                        'email': "z432324@unsw.edu.au",
                                                        'name_first': "Twix",
                                                        'name_last': "Chocolate",
                                                        'handle_str': "twixchocolate",
                                                    },   
                                                 ]
    assert helper_functions.strip_array_url_image(channel_details_2['owner_members']) == [
                                                    {
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

def test_global_owner_add_themselves(clear_store, create_user, create_user2):
    user_token_1 = create_user['token']
    user_token_2 = create_user2['token']
    user_id = create_user['auth_user_id']
    channel_id_2 = requests.post(other.CHANNELS_CREATE_URL, json = {'token': user_token_2, 'name': 'kitchen', 'is_public': True}).json()['channel_id']
    join_request = requests.post(other.CHANNEL_JOIN_URL, json = {'token': user_token_1, 'channel_id': channel_id_2})
    response = requests.post(other.CHANNEL_ADDOWNER_URL, json = {'token': user_token_1, 'channel_id': channel_id_2, 'u_id': user_id})
    channel_details = requests.get(other.CHANNEL_DETAILS_URL, params = {'token': user_token_1, 'channel_id': channel_id_2}).json()
   
    assert join_request.status_code == 200
    assert response.json() == {}
    assert response.status_code == 200

    assert helper_functions.strip_array_url_image(channel_details['owner_members']) ==  [
                                                    {
                                                        'u_id': create_user2['auth_user_id'],
                                                        'email': "z54626@unsw.edu.au",
                                                        'name_first': "Snickers",
                                                        'name_last': "Lickers",
                                                        'handle_str': "snickerslickers",
                                                    },
                                                    {
                                                        'u_id': create_user['auth_user_id'],
                                                        'email': "z432324@unsw.edu.au",
                                                        'name_first': "Twix",
                                                        'name_last': "Chocolate",
                                                        'handle_str': "twixchocolate",
                                                    },   
                                                ]

def test_global_owner_add_others(clear_store, create_user, create_user2, create_user3):
    user_token_1 = create_user['token']
    user_token_2 = create_user2['token']
    user_token_3 = create_user3['token']
    user_id_3 = create_user3['auth_user_id']
    channel_id_1 = requests.post(other.CHANNELS_CREATE_URL, json = {'token': user_token_2, 'name': 'kitchen', 'is_public': True}).json()['channel_id']
    channel_id_2 = requests.post(other.CHANNELS_CREATE_URL, json = {'token': user_token_2, 'name': 'priv kitchen', 'is_public': False}).json()['channel_id']
    requests.post(other.CHANNEL_JOIN_URL, json = {'token': user_token_3, 'channel_id': channel_id_2})
    response_1 = requests.post(other.CHANNEL_ADDOWNER_URL, json = {'token': user_token_1, 'channel_id': channel_id_1, 'u_id': user_id_3})
    response_2 = requests.post(other.CHANNEL_ADDOWNER_URL, json = {'token': user_token_1, 'channel_id': channel_id_2, 'u_id': user_id_3})
    assert response_1.status_code == 403
    assert response_2.status_code == 403

def test_member_addowner(clear_store, create_user, create_user2, create_user3):
    user_token_1 = create_user['token']
    user_token_2 = create_user2['token']
    channel_id_1 = requests.post(other.CHANNELS_CREATE_URL, json = {'token': user_token_1, 'name': 'Channel!', 'is_public': True}).json()['channel_id']
    join_response1 = requests.post(other.CHANNEL_JOIN_URL, json = {'token': user_token_2, 'channel_id': channel_id_1})
    response_1 = requests.post(other.CHANNEL_ADDOWNER_URL, json = {'token': user_token_2, 'channel_id': channel_id_1, 'u_id': create_user3['auth_user_id']})
    assert join_response1.status_code == 200
    assert response_1.status_code == 403

def test_non_member_addowner(clear_store, create_user, create_user2, create_user3):
    user_token_1 = create_user['token']
    user_token_2 = create_user2['token']
    user_token_3 = create_user3['token']
    channel_id_1 = requests.post(other.CHANNELS_CREATE_URL, json = {'token': user_token_1, 'name': 'Channel!', 'is_public': True}).json()['channel_id']
    join_response1 = requests.post(other.CHANNEL_JOIN_URL, json = {'token': user_token_2, 'channel_id': channel_id_1})
    response_1 = requests.post(other.CHANNEL_ADDOWNER_URL, json = {'token': user_token_3, 'channel_id': channel_id_1, 'u_id': create_user2['auth_user_id']})
    assert join_response1.status_code == 200
    assert response_1.status_code == 403

def test_invalid_user_token(clear_store, create_user, create_user2):
    user_token = create_user['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json = {'token': user_token, 'name': 'Channel!', 'is_public': True}).json()['channel_id']
    requests.post(other.LOGOUT_URL, json = {'token': user_token})
    request_data = requests.post(other.CHANNEL_ADDOWNER_URL, json = {'token': user_token, 'channel_id': channel_id, 'u_id': create_user2['auth_user_id']})
    assert request_data.status_code == 403

def test_invalid_u_id(clear_store, create_user):
    user_token = create_user['token']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json = {'token': user_token, 'name': 'Channel!', 'is_public': True}).json()['channel_id']
    response = requests.post(other.CHANNEL_ADDOWNER_URL, json = {'token': user_token, 'channel_id': channel_id, 'u_id': 24})
    assert response.status_code == 400

def test_unauthorised_member(clear_store, create_user, create_user2, create_user3):
    user_token_1 = create_user['token']
    channel_id_1 = requests.post(other.CHANNELS_CREATE_URL, json = {'token': user_token_1, 'name': 'My Channel!', 'is_public': True}).json()['channel_id']
    request_data_1 = requests.post(other.CHANNEL_ADDOWNER_URL, json = {'token': user_token_1, 'channel_id': channel_id_1, 'u_id': create_user3['auth_user_id']})
    assert request_data_1.status_code == 400

def test_already_owner(clear_store, create_user):
    user_token = create_user['token']
    u_id = create_user['auth_user_id']
    channel_id = requests.post(other.CHANNELS_CREATE_URL, json = {'token': user_token, 'name': 'My Channel!', 'is_public': True}).json()['channel_id']
    request_data = requests.post(other.CHANNEL_ADDOWNER_URL, json = {'token': user_token, 'channel_id': channel_id, 'u_id': u_id})
    assert request_data.status_code == 400

def test_invalid_channel_id(clear_store, create_user):
    user_token_1 = create_user['token']
    u_id_1 = create_user['auth_user_id']
    channel_id = 15
    request_data_1 = requests.post(other.CHANNEL_ADDOWNER_URL, json = {'token': user_token_1, 'channel_id': channel_id, 'u_id': u_id_1})
    assert request_data_1.status_code == 400
