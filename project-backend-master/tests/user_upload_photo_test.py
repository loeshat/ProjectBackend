import pytest
import requests
from src.config import url
import src.other as other

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

def test_photo_upload_first(clear_store, create_user):
    u_id = create_user['auth_user_id']
    token = create_user['token']
    profile_repsonse = requests.get(other.USER_PROFILE_URL, params={"u_id": u_id, "token": token})
    assert profile_repsonse.json()['user']['profile_img_url'] != ""
    old_url = profile_repsonse.json()['user']['profile_img_url']
    img_url = "http://www.cse.unsw.edu.au/~tw/Toby2062.jpg"
    upload_image_response = requests.post(other.USER_UPLOADPHOTO_URL, json={"token": token, "img_url": img_url, "x_start": 0, "y_start": 0, "x_end": 100, "y_end": 100})
    assert upload_image_response.status_code == 200
    assert upload_image_response.json() == {}

    profile_repsonse_1 = requests.get(other.USER_PROFILE_URL, params={"u_id": u_id, "token": token})
    assert profile_repsonse_1.json()['user']['profile_img_url'] != ""
    assert profile_repsonse_1.json()['user']['profile_img_url'] != old_url

def test_invalid_token(clear_store, create_user):
    token = create_user['token']
    requests.post(other.LOGOUT_URL, json={"token": token})
    img_url = "http://www.cse.unsw.edu.au/~tw/Toby2062.jpg"
    upload_image_response = requests.post(other.USER_UPLOADPHOTO_URL, json={"token": token, "img_url": img_url, "x_start": 0, "y_start": 0, "x_end": 100, "y_end": 100})
    assert upload_image_response.status_code == 403

def test_invalid_url(clear_store, create_user):
    token = create_user['token']
    img_url = "http://www.teaching.unsw.edu.au/sites/deflt/files/inline-images/Professor%20Richard%20Buckland.jpg"
    upload_image_response = requests.post(other.USER_UPLOADPHOTO_URL, json={"token": token, "img_url": img_url, "x_start": 0, "y_start": 0, "x_end": 100, "y_end": 100})
    assert upload_image_response.status_code == 400

def test_image_not_jpeg(clear_store, create_user):
    token = create_user['token']
    img_url = "http://www.cse.unsw.edu.au/~richardb/index_files/RichardBuckland-200.png"
    upload_image_response = requests.post(other.USER_UPLOADPHOTO_URL, json={"token": token, "img_url": img_url, "x_start": 0, "y_start": 0, "x_end": 100, "y_end": 100})
    assert upload_image_response.status_code == 400

def test_x_end_less(clear_store, create_user):
    token = create_user['token']
    img_url = "http://www.cse.unsw.edu.au/~tw/Toby2062.jpg"
    upload_image_response = requests.post(other.USER_UPLOADPHOTO_URL, json={"token": token, "img_url": img_url, "x_start": 34, "y_start": 0, "x_end": 10, "y_end": 100})
    assert upload_image_response.status_code == 400

def test_y_end_less(clear_store, create_user):
    token = create_user['token']
    img_url = "http://www.cse.unsw.edu.au/~tw/Toby2062.jpg"
    upload_image_response = requests.post(other.USER_UPLOADPHOTO_URL, json={"token": token, "img_url": img_url, "x_start": 0, "y_start": 65, "x_end": 10, "y_end": 1})
    assert upload_image_response.status_code == 400

def test_x_start_not_in_image(clear_store, create_user):
    token = create_user['token']
    img_url = "http://www.cse.unsw.edu.au/~tw/Toby2062.jpg"
    upload_image_response = requests.post(other.USER_UPLOADPHOTO_URL, json={"token": token, "img_url": img_url, "x_start": 9000, "y_start": 0, "x_end": 9002, "y_end": 2})
    assert upload_image_response.status_code == 400

def test_y_start_not_in_image(clear_store, create_user):
    token = create_user['token']
    img_url = "http://www.cse.unsw.edu.au/~tw/Toby2062.jpg"
    upload_image_response = requests.post(other.USER_UPLOADPHOTO_URL, json={"token": token, "img_url": img_url, "x_start": 0, "y_start": 9090, "x_end": 2, "y_end": 9092})
    assert upload_image_response.status_code == 400

def test_x_end_not_in_image(clear_store, create_user):
    token = create_user['token']
    img_url = "http://www.cse.unsw.edu.au/~tw/Toby2062.jpg"
    upload_image_response = requests.post(other.USER_UPLOADPHOTO_URL, json={"token": token, "img_url": img_url, "x_start": 0, "y_start": 0, "x_end": 9001, "y_end": 2})
    assert upload_image_response.status_code == 400

def test_y_end_not_in_image(clear_store, create_user):
    token = create_user['token']
    img_url = "http://www.cse.unsw.edu.au/~tw/Toby2062.jpg"
    upload_image_response = requests.post(other.USER_UPLOADPHOTO_URL, json={"token": token, "img_url": img_url, "x_start": 0, "y_start": 0, "x_end": 2, "y_end": 9001})
    assert upload_image_response.status_code == 400