import requests
import pytest
import src.other as other
from tests.helper_functions import is_valid_dictionary_output, strip_url_image_profile

@pytest.fixture
def clear_store():
    requests.delete(other.CLEAR_URL, json={})

def test_normal_profile(clear_store):
    response = requests.post(other.REGISTER_URL, json={"email":"z55555@unsw.edu.au", "password":"passwordlong", "name_first":"Jake", "name_last":"Renzella"})
    user_0_token = response.json()['token']
    user_0_id = response.json()['auth_user_id']
    profile_repsonse = requests.get(other.USER_PROFILE_URL, params={"u_id": user_0_id, "token": user_0_token})
    assert is_valid_dictionary_output(profile_repsonse.json()['user'], {"u_id": int, "email": str, "name_first": str, "name_last": str, "handle_str": str, "profile_img_url": str})
    assert strip_url_image_profile(profile_repsonse.json()['user']) == {"u_id": user_0_id, "email":"z55555@unsw.edu.au", "name_first": "Jake", "name_last": "Renzella", "handle_str": "jakerenzella"}

def test_invalid_token(clear_store):
    response = requests.post(other.REGISTER_URL, json={"email":"z55555@unsw.edu.au", "password":"passwordlong", "name_first":"Jake", "name_last":"Renzella"})
    user_0_token = response.json()['token']
    user_0_id = response.json()['auth_user_id']
    requests.post(other.LOGOUT_URL, json={"token": user_0_token})
    profile_repsonse = requests.get(other.USER_PROFILE_URL, params={"u_id": user_0_id, "token": user_0_token})
    assert profile_repsonse.status_code == 403    

def test_invalid_user_id(clear_store):
    response = requests.post(other.REGISTER_URL, json={"email":"z55555@unsw.edu.au", "password":"passwordlong", "name_first":"Jake", "name_last":"Renzella"})
    user_0_token = response.json()['token']
    user_0_id = response.json()['auth_user_id']
    profile_repsonse = requests.get(other.USER_PROFILE_URL, params={"u_id": user_0_id + 1, "token": user_0_token})
    assert profile_repsonse.status_code == 400