from src.config import url
import requests
import pytest
import src.other as other

@pytest.fixture
def clear_store():
    requests.delete(other.CLEAR_URL, json={})

@pytest.fixture
def create_user():
    user_input = {'email': "z4323234@unsw.edu.au", 'password': "Password1", 'name_first': "Name1", 'name_last': "LastName1"}
    request_data = requests.post(other.REGISTER_URL, json=user_input)
    user_info = request_data.json()
    return user_info

@pytest.fixture
def create_user2():
    user_input = {'email': "z546326@unsw.edu.au", 'password': "Password2", 'name_first': "Name2", 'name_last': "LastName2"}
    request_data = requests.post(other.REGISTER_URL, json=user_input)
    user_info = request_data.json()
    return user_info

@pytest.fixture
def create_user3():
    user_input = {'email': "z5362601@unsw.edu.au", 'password': "Password3", 'name_first': "Name3", 'name_last': "LastName3"}
    request_data = requests.post(other.REGISTER_URL, json=user_input)
    user_info = request_data.json()
    return user_info

def check_user_left(user_token, user_id, dm_id):
    dm_details = requests.get(other.DM_DETAILS_URL, params={'dm_id': dm_id, 'token': user_token}).json()
    user_has_left = True

    list_members = dm_details['members']
    for member in list_members:
            if member['u_id'] == user_id:
                return False
    return user_has_left

def test_owner_leaves(clear_store, create_user, create_user2):
    user_token_1 = create_user['token']
    user_id_1 = create_user['auth_user_id']
    user_token_2 = create_user2['token']
    user_id_2 = create_user2['auth_user_id']
    dm_id = requests.post(other.DM_CREATE_URL, json={'token': user_token_1, 'u_ids': [user_id_2]}).json()['dm_id']
    
    response = requests.post(other.DM_LEAVE_URL, json={'token': user_token_1, 'dm_id': dm_id})
    assert response.status_code == 200
    assert check_user_left(user_token_2, user_id_1, dm_id)
    

def test_member_leaves(clear_store, create_user, create_user2):
    user_token_1 = create_user['token']
    user_token_2 = create_user2['token']
    user_id_2 = create_user2['auth_user_id']
    dm_id = requests.post(other.DM_CREATE_URL, json={'token': user_token_1, 'u_ids': [user_id_2]}).json()['dm_id']
    
    response = requests.post(other.DM_LEAVE_URL, json={'token': user_token_2, 'dm_id': dm_id})
    assert response.status_code == 200
    assert check_user_left(user_token_1, user_id_2, dm_id)

def test_not_a_member(clear_store, create_user, create_user2, create_user3):
    user_token_1 = create_user['token']
    user_id_2 = create_user2['auth_user_id']
    user_token_3 = create_user3['token']
    
    dm_id = requests.post(other.DM_CREATE_URL, json={'token': user_token_1, 'u_ids': [user_id_2]}).json()['dm_id']
    
    response = requests.post(other.DM_LEAVE_URL, json={'token': user_token_3, 'dm_id': dm_id})
    assert response.status_code == 403
    

def test_invalid_dm_id(clear_store, create_user):
    user_token_1 = create_user['token']
    dm_id = 0
    response = requests.post(other.DM_LEAVE_URL, json={'token': user_token_1, 'dm_id': dm_id})
    assert response.status_code == 400