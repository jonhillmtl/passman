import os
from .utils import get_encryption_key, get_rotation_time
from cryptography.fernet import Fernet, InvalidToken
import datetime
import json

class RepoAlreadyExistsError(Exception):
    pass


class RepoNotFoundError(Exception):
    pass


class Repo():
    path = os.path.expanduser("~/passman_vaults/")

    def init(self):
        if not self.exists:
            os.makedirs(self.path)
            salt_filename = os.path.join(self.path, '.salt')
            with open(salt_filename, "wb") as f:
                salt = os.urandom(32)
                f.write(salt)
        else:
            raise RepoAlreadyExistsError()


    @staticmethod
    def get_cached_password(vault_name):

        key = get_encryption_key(Repo.salt(), get_rotation_time())
        fernet = Fernet(key)
        path = os.path.join(Repo.path, '.cached_passwords')

        with open(path, "rb") as f:
            try:
                data = json.loads(fernet.decrypt(f.read()))
                return data[vault_name]['password']
            except InvalidToken:
                return None
            except KeyError:
                return None
        return None


    @staticmethod
    def write_cached_password(vault_name, password):
        key = get_encryption_key(Repo.salt(), get_rotation_time())
        fernet = Fernet(key)
        path = os.path.join(Repo.path, '.cached_passwords')

        # TODO JHILL: lots needs to be done here, need to merge in data
        data = dict()
        data[vault_name] =dict(
            password=password,
            timestamp=datetime.datetime.now().isoformat()
        )

        with open(path, "wb") as f:
            f.write(fernet.encrypt(json.dumps(data).encode('utf-8')))


    @staticmethod
    def salt():
        salt_filename = os.path.expanduser("~/passman_vaults/.salt")
        with open(salt_filename, "rb") as f:
            return f.read()


    @property
    def vaults(self):
        # TODO JHILL: this should return vault objects, not just string
        assert self.exists is True
        
        vs = []
        for d, sds, files in os.walk(self.path):
            for sd in sds:
                vs.append(os.path.join(d, sd))
        return vs


    @property
    def exists(self):
        return os.path.exists(self.path)
    