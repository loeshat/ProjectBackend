import pytest
import requests
from src.config import url
import src.other as other


@pytest.fixture
def clear_store():
    requests.delete(other.CLEAR_URL, json={})

def test_set_name_success(clear_store):
    registration_request = requests.post(other.REGISTER_URL, json={"email":"z55555@unsw.edu.au", "password":"passwordlong", "name_first":"Jake", "name_last":"Renzella"})
    user_id = registration_request.json()['auth_user_id']
    token = registration_request.json()['token']
    setname_request = requests.put(other.USER_SETNAME_URL, json={"token": token, "name_first": "John", "name_last": "Smith"})
    assert setname_request.status_code == 200
    assert setname_request.json() == {}
    new_profile = requests.get(other.USER_PROFILE_URL, params={"u_id": user_id, "token": token})
    assert new_profile.json()['user']['name_first'] == "John"
    assert new_profile.json()['user']['name_last'] == "Smith"

def test_invalid_token(clear_store):
    registration_request = requests.post(other.REGISTER_URL, json={"email":"z55555@unsw.edu.au", "password":"passwordlong", "name_first":"Jake", "name_last":"Renzella"})
    token = registration_request.json()['token']
    requests.post(other.LOGOUT_URL, json={"token": token})
    setname_request = requests.put(other.USER_SETNAME_URL, json={"token": token, "name_first": "John", "name_last": "Smith"})
    assert setname_request.status_code == 403

def test_short_first_name(clear_store):
    registration_request = requests.post(other.REGISTER_URL, json={"email":"z55555@unsw.edu.au", "password":"passwordlong", "name_first":"Jake", "name_last":"Renzella"})
    token = registration_request.json()['token']
    setname_request = requests.put(other.USER_SETNAME_URL, json={"token": token, "name_first": "", "name_last": "Smith"})
    assert setname_request.status_code == 400

def test_short_last_name(clear_store):
    registration_request = requests.post(other.REGISTER_URL, json={"email":"z55555@unsw.edu.au", "password":"passwordlong", "name_first":"Jake", "name_last":"Renzella"})
    token = registration_request.json()['token']
    setname_request = requests.put(other.USER_SETNAME_URL, json={"token": token, "name_first": "John", "name_last": ""})
    assert setname_request.status_code == 400

def test_long_first_name(clear_store):
    registration_request = requests.post(other.REGISTER_URL, json={"email":"z55555@unsw.edu.au", "password":"passwordlong", "name_first":"Jake", "name_last":"Renzella"})
    token = registration_request.json()['token']
    setname_request = requests.put(other.USER_SETNAME_URL, json={"token": token, "name_first": "THISISAVERYLONGNAMEWHICHISCERTAINLYOUTOFTHERELEVANTBOUNDS", "name_last": "Smith"})
    assert setname_request.status_code == 400

def test_long_last_name(clear_store):
    registration_request = requests.post(other.REGISTER_URL, json={"email":"z55555@unsw.edu.au", "password":"passwordlong", "name_first":"Jake", "name_last":"Renzella"})
    token = registration_request.json()['token']
    setname_request = requests.put(other.USER_SETNAME_URL, json={"token": token, "name_first": "John", "name_last": "THISISAVERYLONGNAMEWHICHISCERTAINLYOUTOFTHERELEVANTBOUNDS"})
    assert setname_request.status_code == 400