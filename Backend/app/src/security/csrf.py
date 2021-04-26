'''
This file is for functions related to CSRF features. Pretty minimal.
'''


def validate_request(payload, target: str) -> bool:
    '''
    Used to validate that a POST, PUT, PATCH, DELETE, etc request has a valid
    CSRF token to avoid getting 0wned.
    '''
    token = payload.get('token', '')
    return token == target
