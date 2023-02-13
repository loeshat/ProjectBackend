from src.config import url
import pytest
import requests
import src.other as other
from src.config import url

@pytest.fixture
def clear_store():
    requests.delete(other.CLEAR_URL, json={})
    
@pytest.fixture
def register_user_1():
    response = requests.post(other.REGISTER_URL, json={"email":"z55555@unsw.edu.au", "password":"passwordlong", "name_first":"Jake", "name_last":"Renzella"}).json()
    return response

@pytest.fixture
def register_user_2():
    response = requests.post(other.REGISTER_URL, json={"email":"z12345@unsw.edu.au", "password": "epicpassword", "name_first": "FirstName", "name_last": "LastName"}).json()
    return response

def test_changing_permission_success(clear_store, register_user_1, register_user_2):
    admin = register_user_1
    user = register_user_2
    requests.post(other.CHANGE_PERM_URL, json={"token": admin['token'], "u_id": user['auth_user_id'], "permission_id": other.GLOBAL_PERMISSION_OWNER})
    response = requests.post(other.CHANGE_PERM_URL, json={"token": user['token'], "u_id": admin['auth_user_id'], "permission_id": other.GLOBAL_PERMISSION_USER})
    assert response.status_code == 200
    
def test_only_one_owner(clear_store, register_user_1):
    admin = register_user_1
    response = requests.post(other.CHANGE_PERM_URL, json={"token": admin['token'], "u_id": admin['auth_user_id'], "permission_id": other.GLOBAL_PERMISSION_USER})
    assert response.status_code == 400


def test_invalid_u_id(clear_store, register_user_1, register_user_2):
    admin = register_user_1
    user = register_user_2
    response = requests.post(other.CHANGE_PERM_URL, json={"token": admin['token'], "u_id": user['auth_user_id'] + 1, "permission_id": other.GLOBAL_PERMISSION_OWNER})
    assert response.status_code == 400


def test_invalid_permission_id(clear_store, register_user_1, register_user_2):
    admin = register_user_1
    user = register_user_2
    response = requests.post(other.CHANGE_PERM_URL, json={"token": admin['token'], "u_id": user['auth_user_id'], "permission_id": other.GLOBAL_PERMISSION_REMOVED})
    assert response.status_code == 400


def test_same_permission_id(clear_store, register_user_1, register_user_2):
    admin = register_user_1
    user = register_user_2
    response = requests.post(other.CHANGE_PERM_URL, json={"token": admin['token'], "u_id": user['auth_user_id'], "permission_id": other.GLOBAL_PERMISSION_USER})
    assert response.status_code == 400


def test_unauthorised_attempt(clear_store, register_user_1, register_user_2):
    user = register_user_2
    response = requests.post(other.CHANGE_PERM_URL, json={"token": user['token'], "u_id": user['auth_user_id'], "permission_id": other.GLOBAL_PERMISSION_OWNER})
    assert response.status_code == 403
