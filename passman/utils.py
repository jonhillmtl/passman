from termcolor import colored
import sys
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import time

def error_exit(message):
    print(colored(message, "red"))
    sys.exit(1)


def get_rotation_time():
    t = int(time.time())
    return t - (t % 300)


def smart_choice(choices):
    for index, choice in enumerate(choices):
        print("{}: {}".format(index, choice['description']))
    print("q: quit")

    while True:
        print("choose: ", end='')
        choice = input()
        if choice.lower().strip() == 'q':
            return -1
        else:
            try:
                choice = int(choice)
            except TypeError:
                continue

            if choice < len(choices):
                return choices[choice]['choice_data']


def get_cache_password():
    return None

def get_encryption_key(salt, password):
    if type(password) == str:
        password = password.encode('utf-8')

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )

    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key
