import pytest
import requests
from src.config import url
import src.other as other

@pytest.fixture
def clear_store():
    requests.delete(other.CLEAR_URL, json={})

def test_normal_change(clear_store):
    registration_request = requests.post(other.REGISTER_URL, json={"email":"z55555@unsw.edu.au", "password":"passwordlong", "name_first":"Jake", "name_last":"Renzella"})
    user_id = registration_request.json()['auth_user_id']
    token = registration_request.json()['token']
    
    original_profile = requests.get(other.USER_PROFILE_URL, params={"u_id": user_id, "token": token})
    assert original_profile.json()['user']['email'] == "z55555@unsw.edu.au"
    set_email_request = requests.put(other.USER_SETEMAIL_URL, json={"token": token, "email": "mynewemail@gmail.com"})
    assert set_email_request.json() == {}
    new_profile = requests.get(other.USER_PROFILE_URL, params={"u_id": user_id, "token": token})
    assert new_profile.json()['user']['email'] == "mynewemail@gmail.com"

def test_invalid_token(clear_store):
    registration_request = requests.post(other.REGISTER_URL, json={"email":"z55555@unsw.edu.au", "password":"passwordlong", "name_first":"Jake", "name_last":"Renzella"})
    token = registration_request.json()['token']
    requests.post(other.LOGOUT_URL, json={"token": token})
    setemail_request = requests.put(other.USER_SETEMAIL_URL, json={"token": token, "email": "mynewemail@gmail.com"})
    assert setemail_request.status_code == 403

def test_email_already_in_use(clear_store):
    registration_request = requests.post(other.REGISTER_URL, json={"email":"z55555@unsw.edu.au", "password":"passwordlong", "name_first":"Jake", "name_last":"Renzella"})
    token = registration_request.json()['token']
    requests.post(other.REGISTER_URL, json={"email":"hello@unsw.edu.au", "password":"agreatpassword", "name_first":"Hayden", "name_last":"Poloto"})
    setemail_request = requests.put(other.USER_SETEMAIL_URL, json={"token": token, "email": "hello@unsw.edu.au"})
    assert setemail_request.status_code == 400


def test_email_not_valid(clear_store):
    registration_request = requests.post(other.REGISTER_URL, json={"email":"z55555@unsw.edu.au", "password":"passwordlong", "name_first":"Jake", "name_last":"Renzella"})
    token = registration_request.json()['token']
    setemail_request = requests.put(other.USER_SETEMAIL_URL, json={"token": token, "email": "mynsjis"})
    assert setemail_request.status_code == 400

def test_change_same_email(clear_store):
    registration_request = requests.post(other.REGISTER_URL, json={"email":"z55555@unsw.edu.au", "password":"passwordlong", "name_first":"Jake", "name_last":"Renzella"})
    user_id = registration_request.json()['auth_user_id']
    token = registration_request.json()['token']
    setemail_request = requests.put(other.USER_SETEMAIL_URL, json={"token": token, "email": "z55555@unsw.edu.au"})
    assert setemail_request.status_code == 200
    profile = requests.get(other.USER_PROFILE_URL, params={"u_id": user_id, "token": token})
    assert profile.json()['user']['email'] == "z55555@unsw.edu.au"