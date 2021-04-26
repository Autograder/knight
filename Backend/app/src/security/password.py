from passlib.context import CryptContext

'''
Exporting our password checker to this area means that everyone can
import this global symbol into their code as needed, and we're able to
update the hash function we use with very little headache. Overall,
it's way better than doing it manually.
@author: npcompletenate
'''
pwd_context = CryptContext(schemes=['pbkdf2_sha256'], deprecated="auto")

# Save our master password as a hashed + salted string so that it's not
# readable
superpass = '$pbkdf2-sha256$29000$KmWM0RrDuNea817L2TuH8A$OCwFlfuiKRvoWAse2/\
Xt5BuHj9P6cp/VuSnT2VX2QcM'
