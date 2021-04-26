import ssl
from os import getenv
import smtplib as slib
from threading import Lock


from .logger import LogLevels, Logger
from .exceptions import SingletonAccessException


class MailUtil(object):
    '''
    Utility class for sending emails.
    '''
    __instance = None

    @staticmethod
    def get_instance():
        if MailUtil.__instance is None:
            with Lock():
                if MailUtil.__instance is None:
                    MailUtil()
        return MailUtil.__instance

    def __init__(self):

        if MailUtil.__instance is not None:
            raise SingletonAccessException("This class is a singleton!")
        self.email = getenv('AG_EMAIL')
        self.passwd = getenv('AG_PASSWORD')
        self.host = 'smtp.gmail.com'
        self.port = 465
        MailUtil.__instance = self

    def send(self, to: [str], subject: str, body: str) -> bool:
        '''
        Util function for sending an email to any number of users
        @author shaeli and rahul
        Params:
            to      - email address to send to
            subject - subject of the email
            body    - message
        Return: True on successful send, false otherwise
        '''

        try:
            context = ssl.create_default_context()
            with slib.SMTP_SSL(self.host, self.port, context=context) as srvr:
                srvr.login(self.email, self.passwd)
                msglg = 'Login attempt for donotreply account successful'
                Logger.get_instance().custom_msg(msglg)

                message = f'Subject: {subject}\n\n{body}'
                srvr.sendmail(self.email, to, message)
                msglg = f'Successfully sent email to {to}'
                Logger.get_instance().custom_msg(msglg, LogLevels.INFO)

            return True

        except slib.SMTPAuthenticationError:
            msglg = 'Login attempt for donotreply account unsuccessful'
            Logger.get_instance().custom_msg(msglg, LogLevels.ERR)
            return False
