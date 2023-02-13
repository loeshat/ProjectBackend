from src.config import url
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

def test_creator_of_dm(clear_store, create_user, create_user2):
    user_token_1 = create_user['token']
    user_token_2 = create_user2['token']
    dm_id_1 = requests.post(other.DM_CREATE_URL, json={'token': user_token_1, 'u_ids': []}).json()['dm_id']
    dm_id_2 = requests.post(other.DM_CREATE_URL, json={'token': user_token_2, 'u_ids': [create_user2['auth_user_id']]}).json()['dm_id']
    dm_details_1 = requests.get(other.DM_DETAILS_URL, params={'dm_id': dm_id_1, 'token': user_token_1})
    dm_details_2 = requests.get(other.DM_DETAILS_URL, params={'dm_id': dm_id_2, 'token': user_token_2})
    assert dm_details_1.json()['name'] == 'twixchocolate'
    assert helper_functions.strip_array_url_image(dm_details_1.json()['members']) == [{
                                'u_id': create_user['auth_user_id'],
                                'email': "z432324@unsw.edu.au",
                                'name_first': "Twix",
                                'name_last': "Chocolate",
                                'handle_str': "twixchocolate",
                            } ]
    assert dm_details_1.status_code == 200
    assert dm_details_2.status_code == 200

def test_member_of_dm(clear_store, create_user, create_user2):
    user_token_1 = create_user['token']
    user_token_2 = create_user2['token']
    user_id_2 = create_user2['auth_user_id']
    dm_id = requests.post(other.DM_CREATE_URL, json={'token': user_token_1, 'u_ids': [user_id_2]}).json()['dm_id']
    dm_details_1 = requests.get(other.DM_DETAILS_URL, params={'dm_id': dm_id, 'token': user_token_2})
    assert dm_details_1.json()['name'] == 'snickerslickers, twixchocolate'
    assert helper_functions.strip_array_url_image(dm_details_1.json()['members'])== [
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
                                }
                            ]
    assert dm_details_1.status_code == 200
    
def test_invalid_user(clear_store, create_user):
    user_token = create_user['token']
    dm_id = requests.post(other.DM_CREATE_URL, json={'token': user_token, 'u_ids': []}).json()['dm_id']
    requests.post(other.LOGOUT_URL, json={'token': user_token})
    request_data = requests.get(other.DM_DETAILS_URL, params={'dm_id': dm_id, 'token': user_token})
    assert request_data.status_code == 403

def test_unauthorised_user_id(clear_store, create_user, create_user2, create_user3):
    user_token_1 = create_user['token']
    user_token_2 = create_user2['token']
    user_token_3 = create_user3['token']
    dm_id_1 = requests.post(other.DM_CREATE_URL, json={'token': user_token_1, 'u_ids': []}).json()['dm_id']
    dm_id_2 = requests.post(other.DM_CREATE_URL, json={'token': user_token_2, 'u_ids': [create_user['auth_user_id']]}).json()['dm_id']
    request_data_1 = requests.get(other.DM_DETAILS_URL, params={'dm_id': dm_id_1, 'token': user_token_2})
    request_data_2 = requests.get(other.DM_DETAILS_URL, params={'dm_id': dm_id_2, 'token': user_token_3})
    assert request_data_1.status_code == 403
    assert request_data_2.status_code == 403

def test_invalid_dm_id(clear_store, create_user, create_user2):
    user_token_1 = create_user['token']
    user_token_2 = create_user2['token']
    dm_id = requests.post(other.DM_CREATE_URL, json={'token': user_token_1, 'u_ids': []}).json()['dm_id']
    request_data_1 = requests.get(other.DM_DETAILS_URL, params={'dm_id': dm_id + 1, 'token': user_token_1})
    request_data_2 = requests.get(other.DM_DETAILS_URL, params={'dm_id': dm_id + 2, 'token': user_token_2})
    assert request_data_1.status_code == 400
    assert request_data_2.status_code == 400

def test_from_stub_code(clear_store, create_stub_user):
    stub_token = create_stub_user['token']
    stub_uid = create_stub_user['auth_user_id']
    dm_id = requests.post(other.DM_CREATE_URL, json={'token': stub_token, 'u_ids': []}).json()['dm_id']
    dm_details = requests.get(other.DM_DETAILS_URL, params={'dm_id': dm_id, 'token': stub_token})
    
    assert dm_details.json()['name'] == "haydenjacobs"
    assert helper_functions.strip_array_url_image(dm_details.json()['members']) == [
            {
                'u_id': stub_uid,
                'email': 'example@gmail.com',
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
                'handle_str': 'haydenjacobs',
            }
        ]
