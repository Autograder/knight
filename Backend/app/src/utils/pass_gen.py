from random import choice
from string import ascii_letters, digits, punctuation


def gen_password(length: int = 10) -> str:
    '''
    Utility function for generating a random password made up of
    alphanumeric characters and punctuation.\n
    Params: `length`: int, length of generated string (defaults to 10).\n
    Returns: A `length` character long, randomly generated string.
    '''
    strs = ascii_letters + digits + punctuation
    return ''.join([choice(strs) for _ in range(length)])
