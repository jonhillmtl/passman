import os
from .utils import get_encryption_key, get_rotation_time, get_cache_password
from cryptography.fernet import Fernet, InvalidToken
import datetime
import json
from uuid import getnode as get_mac

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
        return None
        """
        cache_password = "{}_{}".format(get_rotation_time(), get_mac())
        print(cache_password)

        key = get_encryption_key(Repo.salt(), cache_password)
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
        """

    @staticmethod
    def write_cached_password(vault_name, password):
        return False

        """
        cache_password = "{}_{}".format(get_rotation_time(), get_mac())
        print(cache_password)
        
        key = get_encryption_key(Repo.salt(), cache_password)
        fernet = Fernet(key)
        path = os.path.join(Repo.path, '.cached_passwords')

        data = dict()

        try:
            if os.path.exists(path):
                with open(path, "rb") as f:
                    data = json.loads(fernet.decrypt(f.read()))
        except InvalidToken:
            pass

        data[vault_name] = dict(
            password=password,
            timestamp=datetime.datetime.now().isoformat()
        )

        with open(path, "wb") as f:
            f.write(fernet.encrypt(json.dumps(data).encode('utf-8')))
        """

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
    