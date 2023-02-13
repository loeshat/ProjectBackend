import signal
from json import dumps
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from src.error import AccessError
from src import config
from src.other import clear_v1, user_id_from_JWT, is_valid_JWT
from src.channel import channel_invite_v2, channel_details_v2, channel_join_v2, channel_leave_v1, channel_messages_v2, channel_addowner_v1, channel_removeowner_v1, standup_start_v1, standup_active_v1, standup_send_v1
from src.channels import channels_create_v2, channels_list_v2, channels_listall_v2
from src.auth import auth_login_v2, auth_logout_v1, auth_register_v2, change_global_permission, password_reset_request_v1, reset_user_password_v1
from src.search import search_v1
from src.user import user_profile_v1, user_set_handle_v1, user_setemail_v1, user_setname_v1, users_all_v1, user_uploadphoto_v1
from src.user import user_profile_v1, user_setemail_v1, user_setname_v1, users_all_v1, user_remove_v1, users_stats_v1, user_stats_v1
from src.message import message_send_v1, message_remove_v1, message_edit_v1, message_pin_v1, message_unpin_v1, message_react_v1, message_sendlater_v1, message_share_v1, message_sendlaterdm_v1, message_unreact_v1
from src.dm import dm_create_v1, dm_list_v1, dm_remove_v1, dm_details_v1,  dm_leave_v1, dm_send_v1, dm_messages_v1
from src.notifications import notifications_get_v1
from src.search import search_v1


def quit_gracefully(*args):
    '''For coverage'''
    exit(0)


def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response


APP = Flask(__name__, static_folder="../static", static_url_path='/static/')
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)


@APP.route('/static/<path:path>')
def serve_static_path(path):
    return send_from_directory('', path)


@APP.route("/clear/v1", methods=['DELETE'])
def handle_clear():
    clear_v1()
    return {}


@APP.route("/auth/register/v2", methods=['POST'])
def handle_register_v2():
    request_data = request.get_json()
    email = request_data['email']
    password = request_data['password']
    name_first = request_data['name_first']
    name_last = request_data['name_last']
    return auth_register_v2(email, password, name_first, name_last)


@APP.route("/auth/login/v2", methods=['POST'])
def handle_login_v2():
    request_data = request.get_json()
    email = request_data['email']
    password = request_data['password']
    return auth_login_v2(email, password)


@APP.route("/auth/logout/v1", methods=['POST'])
def handle_logout_v1():
    request_data = request.get_json()
    token = request_data['token']
    return auth_logout_v1(token)


@APP.route("/auth/passwordreset/request/v1", methods=['POST'])
def handle_reset_request_v1():
    request_data = request.get_json()
    email = request_data['email']
    return password_reset_request_v1(email)


@APP.route("/auth/passwordreset/reset/v1", methods=['POST'])
def handle_reset_v1():
    request_data = request.get_json()
    reset_code = str(request_data['reset_code'])
    new_password = str(request_data['new_password'])
    return reset_user_password_v1(reset_code, new_password)


@APP.route("/user/profile/v1", methods=['GET'])
def handle_profile_v1():
    token = request.args.get('token')
    u_id = int(request.args.get('u_id'))
    return user_profile_v1(token, u_id)


@APP.route("/user/profile/setname/v1", methods=['PUT'])
def handle_setname_v1():
    request_data = request.get_json()
    token = request_data['token']
    name_first = request_data['name_first']
    name_last = request_data['name_last']
    return user_setname_v1(token, name_first, name_last)


@APP.route("/user/profile/setemail/v1", methods=['PUT'])
def handle_setemail_v1():
    request_data = request.get_json()
    token = request_data['token']
    email = request_data['email']
    return user_setemail_v1(token, email)


@APP.route("/user/profile/uploadphoto/v1", methods=['POST'])
def handle_uploadphoto_v1():
    request_data = request.get_json()
    token = request_data['token']
    img_url = request_data['img_url']
    x_start = int(request_data['x_start'])
    x_end = int(request_data['x_end'])
    y_start = int(request_data['y_start'])
    y_end = int(request_data['y_end'])
    return user_uploadphoto_v1(token, img_url, x_start, y_start, x_end, y_end)


@APP.route("/user/profile/sethandle/v1", methods=['PUT'])
def handle_sethandle_v1():
    request_data = request.get_json()
    token = request_data['token']
    handle_str = request_data['handle_str']
    return user_set_handle_v1(token, handle_str)


@APP.route("/users/all/v1", methods=['GET'])
def handle_users_all_v1():
    user_token = request.args.get('token')
    if not is_valid_JWT(user_token):
        raise AccessError(description="JWT no longer valid")
    user_id = user_id_from_JWT(user_token)
    return users_all_v1(user_id)


@APP.route("/channels/create/v2", methods=["POST"])
def handle_channels_create_v2():
    request_data = request.get_json()
    user_token = request_data['token']
    channel_name = request_data['name']
    is_public = request_data['is_public']
    if not is_valid_JWT(user_token):
        raise AccessError(description="JWT no longer valid")
    user_id = user_id_from_JWT(user_token)
    return channels_create_v2(user_id, channel_name, is_public)


@APP.route("/channels/list/v2", methods=["GET"])
def handle_channels_list_v2():
    user_token = request.args.get('token')
    if not is_valid_JWT(user_token):
        raise AccessError(description="JWT no longer valid")
    user_id = user_id_from_JWT(user_token)
    return channels_list_v2(user_id)


@APP.route("/channels/listall/v2", methods=['GET'])
def handle_channels_listall_v2():
    user_token = request.args.get('token')
    if not is_valid_JWT(user_token):
        raise AccessError(description="JWT no longer valid")
    user_id = user_id_from_JWT(user_token)
    return channels_listall_v2(user_id)


@APP.route("/channel/details/v2", methods=["GET"])
def handle_channel_details():
    user_token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    if not is_valid_JWT(user_token):
        raise AccessError(description="JWT no longer valid")
    user_id = user_id_from_JWT(user_token)
    return channel_details_v2(user_id, channel_id)


@APP.route("/channel/join/v2", methods=["POST"])
def handle_channel_join():
    request_data = request.get_json()
    user_token = request_data['token']
    channel_id = request_data['channel_id']
    if not is_valid_JWT(user_token):
        raise AccessError(description="JWT no longer valid")
    user_id = user_id_from_JWT(user_token)
    channel_join_v2(user_id, channel_id)
    return {}


@APP.route("/channel/invite/v2", methods=['POST'])
def handle_channel_invite():
    request_data = request.get_json()
    user_token = request_data['token']
    channel_id = request_data['channel_id']
    u_id = int(request_data['u_id'])
    if not is_valid_JWT(user_token):
        raise AccessError(description="JWT no longer valid")
    user_id = user_id_from_JWT(user_token)
    channel_invite_v2(user_id, channel_id, u_id)
    return {}


@APP.route("/channel/leave/v1", methods=['POST'])
def handle_channel_leave():
    request_data = request.get_json()
    user_token = request_data['token']
    channel_id = int(request_data['channel_id'])
    if not is_valid_JWT(user_token):
        raise AccessError(description="JWT no longer valid")
    user_id = user_id_from_JWT(user_token)
    channel_leave_v1(user_id, channel_id)
    return {}


@APP.route("/channel/addowner/v1", methods=["POST"])
def handle_channel_addowner():
    request_data = request.get_json()
    user_token = request_data['token']
    channel_id = int(request_data['channel_id'])
    u_id = int(request_data['u_id'])
    if not is_valid_JWT(user_token):
        raise AccessError(description="JWT no longer valid")
    user_id = user_id_from_JWT(user_token)
    channel_addowner_v1(user_id, channel_id, u_id)
    return {}


@APP.route("/channel/messages/v2", methods=['GET'])
def handle_channel_messages():
    user_token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    start = int(request.args.get('start'))
    if not is_valid_JWT(user_token):
        raise AccessError(description="JWT no longer valid")
    user_id = user_id_from_JWT(user_token)
    return channel_messages_v2(user_id, channel_id, start)


@APP.route("/channel/removeowner/v1", methods=["POST"])
def handle_channel_removeowner():
    request_data = request.get_json()
    user_token = request_data['token']
    channel_id = int(request_data['channel_id'])
    u_id = int(request_data['u_id'])
    if not is_valid_JWT(user_token):
        raise AccessError(description="JWT no longer valid")
    user_id = user_id_from_JWT(user_token)
    channel_removeowner_v1(user_id, channel_id, u_id)
    return {}


@APP.route("/message/send/v1", methods=['POST'])
def handle_message_send():
    request_data = request.get_json()
    user_token = request_data['token']
    channel_id = int(request_data['channel_id'])
    message = request_data['message']
    if not is_valid_JWT(user_token):
        raise AccessError(description="JWT no longer valid")
    user_id = user_id_from_JWT(user_token)
    return message_send_v1(user_id, channel_id, message)


@APP.route("/message/remove/v1", methods=['DELETE'])
def handle_message_remove():
    request_data = request.get_json()
    user_token = request_data['token']
    message_id = int(request_data['message_id'])
    if not is_valid_JWT(user_token):
        raise AccessError(description="JWT no longer valid")
    user_id = user_id_from_JWT(user_token)
    message_remove_v1(user_id, message_id)
    return {}


@APP.route("/message/edit/v1", methods=['PUT'])
def handle_message_edit():
    request_data = request.get_json()
    user_token = request_data['token']
    message_id = request_data['message_id']
    message = request_data['message']
    if not is_valid_JWT(user_token):
        raise AccessError(description="JWT no longer valid")
    user_id = user_id_from_JWT(user_token)
    message_edit_v1(user_id, int(message_id), message)
    return {}


@APP.route("/message/react/v1", methods=['POST'])
def handle_message_react():
    request_data = request.get_json()
    user_token = request_data['token']
    message_id = request_data['message_id']
    react_id = request_data['react_id']
    if not is_valid_JWT(user_token):
        raise AccessError(description="JWT no longer valid")
    user_id = user_id_from_JWT(user_token)
    message_react_v1(user_id, int(message_id), react_id)
    return {}


@APP.route("/message/unreact/v1", methods=['POST'])
def handle_message_unreact():
    request_data = request.get_json()
    user_token = request_data['token']
    message_id = request_data['message_id']
    react_id = request_data['react_id']
    if not is_valid_JWT(user_token):
        raise AccessError(description="JWT no longer valid")
    user_id = user_id_from_JWT(user_token)
    message_unreact_v1(user_id, int(message_id), react_id)
    return {}


@APP.route("/message/pin/v1", methods=['POST'])
def handle_message_pin():
    request_data = request.get_json()
    user_token = request_data['token']
    message_id = request_data['message_id']
    if not is_valid_JWT(user_token):
        raise AccessError(description="JWT no longer valid")
    user_id = user_id_from_JWT(user_token)
    message_pin_v1(user_id, int(message_id))
    return {}


@APP.route("/message/unpin/v1", methods=['POST'])
def handle_message_unpin():
    request_data = request.get_json()
    user_token = request_data['token']
    message_id = request_data['message_id']
    if not is_valid_JWT(user_token):
        raise AccessError(description="JWT no longer valid")
    user_id = user_id_from_JWT(user_token)
    message_unpin_v1(user_id, int(message_id))
    return {}


@APP.route("/dm/create/v1", methods=["POST"])
def handle_dm_create():
    request_data = request.get_json()
    user_token = request_data['token']
    u_ids = request_data['u_ids']
    if not is_valid_JWT(user_token):
        raise AccessError(description="JWT no longer valid")
    user_id = user_id_from_JWT(user_token)
    return dm_create_v1(user_id, u_ids)


@APP.route("/dm/list/v1", methods=["GET"])
def handle_dm_list():
    user_token = request.args.get('token')
    if not is_valid_JWT(user_token):
        raise AccessError(description="JWT no longer valid")
    user_id = user_id_from_JWT(user_token)
    return dm_list_v1(user_id)


@APP.route("/dm/remove/v1", methods=["DELETE"])
def handle_dm_remove():
    request_data = request.get_json()
    user_token = request_data['token']
    dm_id = int(request_data['dm_id'])
    if not is_valid_JWT(user_token):
        raise AccessError(description="JWT no longer valid")
    user_id = user_id_from_JWT(user_token)
    dm_remove_v1(user_id, dm_id)
    return {}


@APP.route("/dm/details/v1", methods=["GET"])
def handle_dm_details():
    user_token = request.args.get('token')
    dm_id = int(request.args.get('dm_id'))
    if not is_valid_JWT(user_token):
        raise AccessError(description="JWT no longer valid")
    user_id = user_id_from_JWT(user_token)
    return dm_details_v1(user_id, dm_id)


@APP.route("/dm/leave/v1", methods=["POST"])
def handle_dm_leave():
    request_data = request.get_json()
    user_token = request_data['token']
    dm_id = int(request_data['dm_id'])
    if not is_valid_JWT(user_token):
        raise AccessError(description="JWT no longer valid")
    user_id = user_id_from_JWT(user_token)
    dm_leave_v1(user_id, dm_id)
    return {}


@APP.route("/admin/userpermission/change/v1", methods=["POST"])
def handle_userperm_change():
    request_data = request.get_json()
    if not is_valid_JWT(request_data['token']):
        raise AccessError(description="JWT no longer valid")
    change_global_permission(user_id_from_JWT(
        request_data['token']), request_data['u_id'], request_data['permission_id'])
    return {}


@APP.route("/admin/user/remove/v1", methods=["DELETE"])
def handle_user_remove():
    request_data = request.get_json()
    if not is_valid_JWT(request_data['token']):
        raise AccessError(description="JWT no longer valid")
    return user_remove_v1(request_data['token'], request_data['u_id'])


@APP.route("/message/senddm/v1", methods=["POST"])
def handle_dm_send():
    request_data = request.get_json()
    if not is_valid_JWT(request_data['token']):
        raise AccessError(description="JWT no longer valid")
    return dm_send_v1(user_id_from_JWT(request_data['token']), request_data['message'], request_data['dm_id'])


@APP.route("/dm/messages/v1", methods=["GET"])
def handle_dm_messages():
    if not is_valid_JWT(request.args.get('token')):
        raise AccessError(description="JWT no longer valid")
    return dm_messages_v1(user_id_from_JWT(request.args.get('token')), int(request.args.get('dm_id')), int(request.args.get('start')))


@APP.route("/user/stats/v1", methods=["GET"])
def handle_user_stats():
    if not is_valid_JWT(request.args.get('token')):
        raise AccessError(description="JWT no longer valid")
    return {"user_stats": user_stats_v1(user_id_from_JWT(request.args.get('token')))}

@APP.route("/users/stats/v1", methods=["GET"])
def handle_users_stats():
    if not is_valid_JWT(request.args.get('token')):
        raise AccessError(description="JWT no longer valid")
    return {"workspace_stats": users_stats_v1()}
   

@APP.route("/message/sendlater/v1", methods=["POST"])
def handle_message_sendlater():
    request_data = request.get_json()
    if not is_valid_JWT(request_data['token']):
        raise AccessError(description="JWT no longer valid")
    user_id = user_id_from_JWT(request_data['token'])
    return message_sendlater_v1(user_id, request_data['channel_id'], request_data['message'], request_data['time_sent'])


@APP.route("/search/v1", methods=["GET"])
def handle_search():
    user_token = request.args.get('token')
    query_string = request.args.get('query_str')
    if not is_valid_JWT(user_token):
        raise AccessError(description="JWT no longer valid")
    user_id = user_id_from_JWT(user_token)
    return search_v1(user_id, query_string)


@APP.route("/message/share/v1", methods=['POST'])
def handle_message_share():
    request_data = request.get_json()
    if not is_valid_JWT(request_data['token']):
        raise AccessError(description="JWT no longer valid")
    return message_share_v1(user_id_from_JWT(request_data['token']), int(request_data['og_message_id']), request_data['message'], int(request_data['channel_id']), int(request_data['dm_id']))

@APP.route("/standup/start/v1", methods=["POST"])
def handle_standup_start():
    request_data = request.get_json()
    if not is_valid_JWT(request_data['token']):
        raise AccessError(description="JWT no longer valid")
    user_id = user_id_from_JWT(request_data['token'])
    return standup_start_v1(user_id, int(request_data['channel_id']), int(request_data['length']))

@APP.route("/standup/active/v1", methods=["GET"])
def handle_standup_active():
    user_token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    if not is_valid_JWT(user_token):
        raise AccessError(description="JWT no longer valid")
    user_id = user_id_from_JWT(user_token)
    return standup_active_v1(user_id, channel_id)

@APP.route("/standup/send/v1", methods=["POST"])
def handle_standup_send():
    request_data = request.get_json()
    if not is_valid_JWT(request_data['token']):
        raise AccessError(description="JWT no longer valid")
    user_id = user_id_from_JWT(request_data['token'])
    standup_send_v1(user_id, int(request_data['channel_id']), request_data['message'])
    return {}
     
@APP.route("/message/sendlaterdm/v1", methods=["POST"])
def handle_message_sendlaterdm():
    request_data = request.get_json()
    if not is_valid_JWT(request_data['token']):
        raise AccessError(description="JWT no longer valid")
    user_id = user_id_from_JWT(request_data['token'])
    return message_sendlaterdm_v1(user_id, request_data['dm_id'], request_data['message'], request_data['time_sent'])


@APP.route("/notifications/get/v1", methods=["GET"])
def handle_get_notifications():
    if not is_valid_JWT(request.args.get('token')):
        raise AccessError(description="JWT no longer valid")
    return notifications_get_v1(user_id_from_JWT(request.args.get('token')))


# NO NEED TO MODIFY BELOW THIS POINT


if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully)  # For coverage
    APP.run(port=config.port)  # Do not edit this port
