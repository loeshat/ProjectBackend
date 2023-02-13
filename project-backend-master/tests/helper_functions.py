def is_valid_dictionary_output(dictionary_output: dict, template_dictionary: dict) -> bool:
    """
    This function takes a dictionary output and determines whether it is structurally isomorphic
    to the template dictionary. This means that the keys must all be the same but the values can
    be anything as long as they are of the type specified in template dictionary.

    For example is_valid_dictionary({'auth_user_id': 2}, {'auth_user_id': int}) == True
                is_valid_dictionary({'auth_user_id': 787}, {'auth_user_id': int}) == True

                but

                is_valid_dictionary({'test': 'hello'}, {'auth_user_id': int}) == False

    Arguments:
        dictionary_output (dict)     - The dictionary which needs to be validated
        template_dictionary (dict)   - A dictionary with all the keys and types of values
                                       which the output will be checked against

    Exceptions:
        None

    Return Value:
        Returns a boolean value always
    """
    if not isinstance(dictionary_output,dict):
        return False
    if set(dictionary_output.keys()) != set(template_dictionary.keys()):
        return False
    for key in template_dictionary.keys():
        if not isinstance(dictionary_output[key], template_dictionary[key]):
            return False
    return True

def strip_url_image_profile(profile: dict):
    return {k: v for k, v in profile.items() if k not in ['profile_img_url']}

def strip_array_url_image(profiles: dict):
    output = []
    for profile in profiles:
        output.append(strip_url_image_profile(profile))
    return output