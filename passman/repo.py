import os

class RepoAlreadyExistsError(Exception):
    pass


class RepoNotFoundError(Exception):
    pass


class Repo():
    def init(self):
        if not self.exists:
            os.makedirs(self.path)
            salt_filename = os.path.join(self.path, '.salt')
            with open(salt_filename, "wb") as f:
                salt = os.urandom(32)
                f.write(salt)
        else:
            raise RepoAlreadyExistsError()

    @property
    def path(self):
        return os.path.expanduser("~/passman_vaults/")


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
    