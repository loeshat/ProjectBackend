import pytest
import requests
from .helper_functions import is_valid_dictionary_output
from src.config import url
import src.other as other
import tests.helper_functions as helper_functions

@pytest.fixture
def clear_store():
    requests.delete(other.CLEAR_URL, json={})

def test_user_registration(clear_store):
    response = requests.post(other.REGISTER_URL, json={"email":"z55555@unsw.edu.au", "password":"passwordlong", "name_first":"Jake", "name_last":"Renzella"})
    assert response.status_code == 200
    assert is_valid_dictionary_output(response.json(), {'token': str, 'auth_user_id': int})

def test_auth_register_handle_generate(clear_store):
    response_0 = requests.post(other.REGISTER_URL, json={"email":"z55555@unsw.edu.au", "password":"passwordlong", "name_first":"abcdefghi", "name_last":"jklmnopqrst"})
    response_1 = requests.post(other.REGISTER_URL, json={"email":"z55556@unsw.edu.au", "password":"passwordlong", "name_first":" **(&(abcdefghi__  ", "name_last":"jklmnopqrst&**uv"})
    response_2 = requests.post(other.REGISTER_URL, json={"email":"z55557@unsw.edu.au", "password":"passwordlong", "name_first":"ABCDEFGHI", "name_last":"JKLMNOPQRSTUVWXYZ"})

    token = response_0.json()['token']
    id_0 = response_0.json()['auth_user_id']
    id_1 = response_1.json()['auth_user_id']
    id_2 = response_2.json()['auth_user_id']
    profile_response_0 = requests.get(other.USER_PROFILE_URL, params={"u_id": id_0, "token": token})
    assert helper_functions.strip_url_image_profile(profile_response_0.json()['user']) == {"u_id": id_0, "email":"z55555@unsw.edu.au", "name_first": "abcdefghi", "name_last": "jklmnopqrst", "handle_str": "abcdefghijklmnopqrst"}
    profile_response_1 = requests.get(other.USER_PROFILE_URL, params={"u_id": id_1, "token": token})
    assert helper_functions.strip_url_image_profile(profile_response_1.json()['user']) == {"u_id": id_1, "email":"z55556@unsw.edu.au", "name_first": " **(&(abcdefghi__  ", "name_last": "jklmnopqrst&**uv", "handle_str": "abcdefghijklmnopqrst0"}
    profile_response_2 = requests.get(other.USER_PROFILE_URL, params={"u_id": id_2, "token": token})
    assert helper_functions.strip_url_image_profile(profile_response_2.json()['user']) == {"u_id": id_2, "email":"z55557@unsw.edu.au", "name_first": "ABCDEFGHI", "name_last": "JKLMNOPQRSTUVWXYZ", "handle_str": "abcdefghijklmnopqrst1"}

def test_error_email_not_valid(clear_store):
    response = requests.post(other.REGISTER_URL, json={"email":"tsgyd", "password":"34rd^hds)", "name_first": "Johnny", "name_last":"Smith"})
    assert response.status_code == 400

def test_error_password_short(clear_store):
    response = requests.post(other.REGISTER_URL, json={"email":"z55555@unsw.edu.au", "password":"pa33", "name_first":"Marc", "name_last":"Chee"})
    assert response.status_code == 400

def test_error_email_used(clear_store):
    response = requests.post(other.REGISTER_URL, json={"email":"z123456789@unsw.edu.au", "password":"thi3isn0t@pa33wor&", "name_first":"Steve", "name_last":"Jobs"})
    assert response.status_code == 200
    assert is_valid_dictionary_output(response.json(), {"token": str, "auth_user_id": int})
    response2 = requests.post(other.REGISTER_URL, json={"email":"z123456789@unsw.edu.au", "password":"newpassword", "name_first":"Steve", "name_last":"Wozniak"})
    assert response2.status_code == 400


def test_error_first_name_short(clear_store):
    response = requests.post(other.REGISTER_URL, json={"email":"z123456789@unsw.edu.au", "password":"longpassword", "name_first":"", "name_last":"Li"})
    assert response.status_code == 400

def test_error_first_name_long(clear_store):
    response = requests.post(other.REGISTER_URL, json={"email":"z123456789@unsw.edu.au", "password":"longpassword", "name_first":"THISISIAREALLYALONGNAMEWHICHISOUTOFBOUNDSDEFINITIELY", "name_last":"Li"})
    assert response.status_code == 400
        

def test_error_last_name_short(clear_store):
    response = requests.post(other.REGISTER_URL, json={"email":"z123456789@unsw.edu.au", "password":"goodpass", "name_first":"Simon", "name_last":""})
    assert response.status_code == 400


def test_error_last_name_long(clear_store):
    response = requests.post(other.REGISTER_URL, json={"email":"z123456789@unsw.edu.au", "password":"goodpass", "name_first":"Simon", "name_last":"THISISIAREALLYALONGNAMEWHICHISOUTOFBOUNDSDEFINITIELY"})
    assert response.status_code == 400
