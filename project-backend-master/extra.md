## Automated Testing of Email Code
Given that we cannot assume that all the tests are not run concurrently, this is a further test file (whitebox)
which can automatically send and retrive the email for the codes. It is not included as if another email is sent (from another test)
while it is waiting for the reset code in this test it may input the wrong code (if there are multiple server instances etc).

```python
import requests
import pytest
import src.other as other
from time import sleep
from imapclient import IMAPClient
import email

@pytest.fixture
def clear_store():
    requests.delete(other.CLEAR_URL, json={})

@pytest.fixture
def create_user():
    user_input = {'email': TEST_USER_EMAIL, 'password': OLD_PASSWORD, 'name_first': "Ji", 'name_last': "Sun"}
    request_data = requests.post(other.REGISTER_URL, json=user_input)
    user_info = request_data.json()
    return user_info

MAIL_USERNAME = "comp1531h13a.camel@gmail.com"
MAIL_PASSWORD = "hapless_history_h13a_camel"
TEST_USER_EMAIL = "comp1531h13acamel@gmail.com"
OLD_PASSWORD = "badpassword123"


def send_and_get_reset_code(email):
    # Login to the server to get messages before request is sent
    server = IMAPClient('imap.gmail.com', use_uid=True)
    server.login(MAIL_USERNAME, MAIL_PASSWORD)
    select_info = server.select_folder('INBOX')
    before = int(select_info\[b'EXISTS'\])
    # Clean out any old messages from before
    messages = server.search(['FROM', other.SENDER_ADDRESS, 'UNSEEN'])
    for msgid, data in server.fetch(messages, ['ENVELOPE', 'BODY\[TEXT\]']).items():
        print(msgid)
    # Send request
    requests.post(other.AUTH_PASSWORDRESET_REQUEST_URL, json={"email": TEST_USER_EMAIL})

    code = ""
    # Wait until a new message is recived
    while(int(select_info[b'EXISTS']) == before):
        server.logout()
        sleep(5)
        server = IMAPClient('imap.gmail.com', use_uid=True)
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        select_info = server.select_folder('INBOX')

    # Grab the newest message which is unread from the known sender address
    messages = server.search(['FROM', other.SENDER_ADDRESS, 'UNSEEN'])
    for msgid, data in server.fetch(messages, ['ENVELOPE', 'BODY[TEXT]']).items():
        body_text = data[b'BODY[TEXT]']
        msg = email.message_from_bytes(body_text)
        # Extract code from message
        message = msg.get_payload()
        for charcter in message:
            if charcter.isnumeric():
                code += charcter
    server.logout()
    return code


def test_reset_code_is_valid(clear_store, create_user):

    token = create_user['token']
    u_id = create_user['auth_user_id']
    new_password = "anewpassword"

    code = send_and_get_reset_code(TEST_USER_EMAIL)

    profile_request = requests.get(other.USER_PROFILE_URL, params={"token": token, "u_id": u_id})
    assert profile_request.status_code == 403
    
    reset_password_request = requests.post(other.AUTH_PASSWORDRESET_RESET_URL, json={"reset_code": code, "new_password": new_password})
    assert reset_password_request.status_code == 200
    assert reset_password_request.json() == {}

    login_1_request = requests.post(other.LOGIN_URL, json={"email": TEST_USER_EMAIL, "password": OLD_PASSWORD})
    assert login_1_request.status_code == 400

    login_2_request = requests.post(other.LOGIN_URL, json={"email": TEST_USER_EMAIL, "password": new_password})
    assert login_2_request.status_code == 200`