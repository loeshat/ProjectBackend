import requests
import pytest
from src.config import url
import src.other as other
import tests.helper_functions as helper_functions

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

def test_one_user(clear_store, create_user):
    user_token = create_user['token']
    user_id = create_user['auth_user_id']
    response = requests.get(other.USERS_ALL_URL, params={'token': user_token})
    profile_response = requests.get(other.USER_PROFILE_URL, params={"u_id": user_id, "token": user_token})
    assert helper_functions.strip_url_image_profile(profile_response.json()['user']) == {"u_id": user_id, 'email': "z432324@unsw.edu.au", 'name_first': "Ji", 'name_last': "Sun", 'handle_str': "jisun"}
    assert response.json()['users'] == [profile_response.json()['user']]
    assert response.status_code == 200

def test_multiple_users(clear_store, create_user, create_user2):
    user_token = create_user['token']
    user_token2 = create_user2['token']
    user_id = create_user['auth_user_id']
    user_id2 = create_user2['auth_user_id']
    response = requests.get(other.USERS_ALL_URL, params={'token': user_token})
    profile_response1 = requests.get(other.USER_PROFILE_URL, params={"u_id": user_id, "token": user_token})
    profile_response2 = requests.get(other.USER_PROFILE_URL, params={"u_id": user_id2, "token": user_token2})
    assert [helper_functions.strip_url_image_profile(profile_response1.json()['user']), helper_functions.strip_url_image_profile(profile_response2.json()['user'])] == [   {"u_id": user_id, 'email': "z432324@unsw.edu.au", 'name_first': "Ji", 'name_last': "Sun", 'handle_str': "jisun"},
                                                                       {"u_id": user_id2, 'email': "z54626@unsw.edu.au", 'name_first': "Jane", 'name_last': "Gyuri", 'handle_str': "janegyuri"}
                                                                   ]
    assert response.json()['users'] == [profile_response1.json()['user'], profile_response2.json()['user']]
    assert response.status_code == 200
    requests.delete(other.USER_REMOVE_URL, json={'token': user_token, 'u_id': user_id2})
    response = requests.get(other.USERS_ALL_URL, params={'token': user_token})
    assert helper_functions.strip_array_url_image(response.json()['users']) == [{"u_id": user_id, 'email': "z432324@unsw.edu.au", 'name_first': "Ji", 'name_last': "Sun", 'handle_str': "jisun"}]

def test_invalid_token(clear_store, create_user):
    user_token = create_user['token']
    requests.post(other.LOGOUT_URL, json={"token": user_token})
    response = requests.get(other.USERS_ALL_URL, params={"token": user_token})
    assert response.status_code == 403
