from .helper_functions import is_valid_dictionary_output
from src.config import url
import pytest
import requests
import src.other as other

@pytest.fixture
def clear_store():
    requests.delete(other.CLEAR_URL, json={})

def test_single_user_login_success(clear_store):
    register_request = requests.post(other.REGISTER_URL, json={"email":"z55555@unsw.edu.au", "password":"passwordlong", "name_first":"Jake", "name_last":"Renzella"})
    assert register_request.status_code == 200
    assert is_valid_dictionary_output(register_request.json(), {"token": str, "auth_user_id": int})

    login_request = requests.post(other.LOGIN_URL, json={"email":"z55555@unsw.edu.au", "password":"passwordlong"})
    assert login_request.status_code == 200
    assert is_valid_dictionary_output(login_request.json(), {"token": str, "auth_user_id": int})

def test_incorrect_password(clear_store):
    requests.post(other.REGISTER_URL, json={"email":"z55555@unsw.edu.au", "password":"passwordlong", "name_first":"Jake", "name_last":"Renzella"})
    login_request = requests.post(other.LOGIN_URL, json={"email":"z55555@unsw.edu.au", "password":"passWRONG"})
    assert login_request.status_code == 400

def test_invalid_email(clear_store):
    requests.post(other.REGISTER_URL, json={"email":"z09328373@unsw.edu.au", "password":"passwordlong", "name_first":"Hayden", "name_last":"Jacobs"})
    login_request = requests.post(other.LOGIN_URL, json={"email":"z1234@unsw.edu.au", "password":"passWRONG"})
    assert login_request.status_code == 400

def test_complex_success(clear_store):
    requests.post(other.REGISTER_URL, json={"email":"z55555@unsw.edu.au", "password":"passwordlong", "name_first":"Jake", "name_last":"Renzella"})
    requests.post(other.REGISTER_URL, json={"email":"z09328373@unsw.edu.au", "password":"passwordlong", "name_first":"Hayden", "name_last":"Jacobs"})
    requests.post(other.REGISTER_URL, json={"email":"z123@unsw.edu.au", "password":"apples123", "name_first":"Jakob", "name_last":"Renzellid"})
    requests.post(other.REGISTER_URL, json={"email":"z12345@unsw.edu.au", "password":"bananas&apricots", "name_first":"Apricot", "name_last":"IsNotAFirstName"})

    login_request_0 = requests.post(other.LOGIN_URL, json={"email": "z55555@unsw.edu.au", "password": "passwordlong"})
    assert is_valid_dictionary_output(login_request_0.json(), {"token": str, "auth_user_id": int})
    login_request_1 = requests.post(other.LOGIN_URL, json={"email": "z12345@unsw.edu.au", "password": "bananas&apricots"})
    assert is_valid_dictionary_output(login_request_1.json(), {"token": str, "auth_user_id": int})

    login_request_2 = requests.post(other.LOGIN_URL, json={"email": "z123@unsw.edu.au", "password": "wrongpasswordboi"})
    assert login_request_2.status_code == 400


