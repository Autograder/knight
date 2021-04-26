'''
This class provides a places to put custom exceptions, if we so desire that
level of flexibility.
'''


class SingletonAccessException(Exception):
    '''
    This exception is triggered when the Logger/Mailer is instantianted
    when an instance already exists.
    '''
    def __init__(self, message):
        super().__init__(message)
