from src.config import url
import requests
import pytest
from .helper_functions import is_valid_dictionary_output
import src.other as other

@pytest.fixture
def clear_store():
    requests.delete(other.CLEAR_URL, json={})

@pytest.fixture
def create_user():
    user_input = {'email': "z432324@unsw.edu.au", 'password': "badpassword123", 'name_first': "Twix", 'name_last': "Chocolate"}
    request_data = requests.post(other.REGISTER_URL, json=user_input)
    user_info = request_data.json()
    return user_info

@pytest.fixture
def create_user2():
    user_input = {'email': "z54626@unsw.edu.au", 'password': "Password", 'name_first': "Snickers", 'name_last': "Lickers"}
    request_data = requests.post(other.REGISTER_URL, json=user_input)
    user_info = request_data.json()
    return user_info

@pytest.fixture
def create_user3():
    user_input = {'email': "z536601@unsw.edu.au", 'password': "1243Bops", 'name_first': "Mars", 'name_last': "Bars"}
    request_data = requests.post(other.REGISTER_URL, json=user_input)
    user_info = request_data.json()
    return user_info

def test_success_create(clear_store, create_user, create_user2, create_user3): 
    user_token_1 = create_user['token']
    user_id_2 = create_user2['auth_user_id']
    user_id_3 = create_user3['auth_user_id']
    response = requests.post(other.DM_CREATE_URL, json={'token': user_token_1, 'u_ids': [user_id_2, user_id_3]})
    assert response.status_code == 200
    assert is_valid_dictionary_output(response.json(), {'dm_id': int})    

def test_empty_list(clear_store, create_user):
    user_token_1 = create_user['token']
    response = requests.post(other.DM_CREATE_URL, json={'token': user_token_1, 'u_ids': []})
    assert response.status_code == 200
    assert is_valid_dictionary_output(response.json(), {'dm_id': int})    

def test_invalid_token(clear_store, create_user):
    user_token = create_user['token']
    requests.post(other.LOGOUT_URL, json={'token': user_token})
    response = requests.post(other.DM_CREATE_URL, json={'token': user_token, 'u_ids': []})
    assert response.status_code == 403

def test_invalid_u_id(clear_store, create_user, create_user2):
    user_token = create_user['token']
    user_id_2 = create_user2['auth_user_id']
    response = requests.post(other.DM_CREATE_URL, json={'token': user_token, 'u_ids': [user_id_2, -1]})
    assert response.status_code == 400

def test_duplicate_u_id(clear_store, create_user, create_user2):
    user_token = create_user['token']
    user_id_2 = create_user2['auth_user_id']
    response = requests.post(other.DM_CREATE_URL, json={'token': user_token, 'u_ids': [user_id_2, user_id_2]})
    assert response.status_code == 400


