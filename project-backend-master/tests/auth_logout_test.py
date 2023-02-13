import pytest
import requests
from src.config import url
import src.other as other

@pytest.fixture
def clear_store():
    requests.delete(other.CLEAR_URL, json={})


def test_single_logout_success(clear_store):
    response = requests.post(other.REGISTER_URL, json={"email":"z55555@unsw.edu.au", "password":"passwordlong", "name_first":"Jake", "name_last":"Renzella"})
    logout_request = requests.post(other.LOGOUT_URL, json={"token": response.json()['token']})
    assert logout_request.status_code == 200
    assert logout_request.json() == {}
    profile_response = requests.get(other.USER_PROFILE_URL, params={"token": response.json()['token'], "u_id": response.json()['auth_user_id']})
    assert profile_response.status_code == 403


def test_logout_invalid_token(clear_store):
    response = requests.post(other.REGISTER_URL, json={"email":"z55555@unsw.edu.au", "password":"passwordlong", "name_first":"Jake", "name_last":"Renzella"})
    requests.post(other.LOGOUT_URL, json={"token": response.json()['token']})
    logout_request_1 = requests.post(other.LOGOUT_URL, json={"token": response.json()['token']})
    assert logout_request_1.status_code == 403

def test_logout_multiple_sessions(clear_store):
    response = requests.post(other.REGISTER_URL, json={"email":"z55555@unsw.edu.au", "password":"passwordlong", "name_first":"Jake", "name_last":"Renzella"})
    token_0 = response.json()['token']
    u_id = response.json()['auth_user_id']
    login_response = requests.post(other.LOGIN_URL, json={"email":"z55555@unsw.edu.au", "password":"passwordlong"})
    token_1 = login_response.json()['token']
    requests.post(other.LOGOUT_URL, json={"token": token_0})
    profile_repsonse = requests.get(other.USER_PROFILE_URL, params={"u_id": u_id, 'token': token_1})
    assert profile_repsonse.status_code == 200
    profile_repsonse_1 = requests.get(other.USER_PROFILE_URL, params={"u_id": u_id, "token": token_0})
    assert profile_repsonse_1.status_code == 403