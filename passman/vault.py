from .repo import Repo, RepoNotFoundError
from cryptography.fernet import Fernet, InvalidToken

from termcolor import colored
import datetime
import json
import os
import uuid

from .utils import get_encryption_key
from .repo import Repo


class VaultNotFoundError(Exception):
    pass


class VaultAlreadyExistsError(Exception):
    pass


class VaultWrongPasswordError(Exception):
    vault_name = None
    def __init__(self, vault_name):
        self.vault_name = vault_name


class VaultEntryAlreadyExistsError(Exception):
    pass


class VaultWeakPasswordError(Exception):
    error = None
    def __init__(self, error):
        self.error = error


class Vault():
    name = None
    password = None

    def __init__(self, name, password):
        self.name = name
        self.password = password


    # TODO JHILL: implement
    @staticmethod
    def validate_password(password):
        if len(password) < 8:
            return False, "password must be at least 8 characters long"
        return True, ""


    @property
    def exists(self):
        return os.path.exists(self.path) and os.path.exists(self.data_path)


    @property
    def path(self):
        repo = Repo()
        if not repo.exists:
            raise RepoNotFoundError()
        vault_path = os.path.join(repo.path, self.name)
        return vault_path


    @property
    def data_path(self):
        repo = Repo()
        if not repo.exists:
            raise RepoNotFoundError()
        vault_path = os.path.join(repo.path, self.name, 'data.passman')
        return vault_path


    def create(self):
        assert self.name is not None
        assert self.password is not None

        validate_password, pw_error = Vault.validate_password(self.password)
        if  validate_password is False:
            raise VaultWeakPasswordError(pw_error)

        repo = Repo()
        if not repo.exists:
            raise RepoNotFoundError()

        # TODO JHILL: validate the vault name
        vault_path = os.path.join(repo.path, self.name)

        if os.path.exists(vault_path):
            raise VaultAlreadyExistsError()
        else:
            os.makedirs(vault_path)

            vault_data = dict(
                entries=[],
                version='0.0.1',
                history=[]
            )

            self.write(vault_data)

            # TODO JHILL: don't print in here
            print(colored("created {}".format(vault_path), "green"))

        return True


    def add_entry(self, **kwargs):
        data = self.read()
        assert 'entries' in data

        kwargs = dict(**kwargs)
        for entry in data['entries']:
            if kwargs['name'].lower() == entry['name'].lower() and \
               kwargs['username'].lower() == entry['username'].lower():
                raise VaultEntryAlreadyExistsError()

        timestamp = datetime.datetime.now().isoformat()

        entry = dict(
            **kwargs,
            id=str(uuid.uuid4()),
            timestamp=timestamp
        )

        data['entries'].append(entry)

        self.write(data)

        return entry


    def add_history_entry(self, command_name, hint, timestamp=None):
        data = self.read()
        assert 'history' in data

        if timestamp is None:
            timestamp = datetime.datetime.now().isoformat()

        history_entry = dict(
            command_name=command_name,
            hint=hint,
            timestamp=timestamp,
            vault_name=self.name
        )
    
        data['history'].append(history_entry)
        self.write(data)

        return history_entry

    def merge_vault(self, source_vault):
        target_data = self.read()
        source_data = source_vault.read()

        target_data['entries'].extend(source_data['entries'])
        target_data['history'].extend(source_data['history'])

        # TODO JHILL: check to see if there would be duplicate entries as a result of the merge

        self.write(target_data)

        # TODO JHILL: dont add history entries in here
        self.add_history_entry('merge_vaults', dict(role='target', other_vault_name=source_vault.name))
        source_vault.add_history_entry('merge_vaults', dict(role='source', other_vault_name=self.name))

        return True


    def change_password(self, new_password):
        validate_password, pw_error = Vault.validate_password(new_password)
        if  validate_password is False:
            raise VaultWeakPasswordError(pw_error)

        vault_data = self.read()
        self.password = new_password
        self.write(vault_data)


    def delete_entry(self, entry_id):
        vault_data = self.read()
        for index, entry in enumerate(vault_data['entries']):
            if entry['id'] == entry_id:
                del vault_data['entries'][index]
        self.write(vault_data)


    def update_entry(self, entry_id, **kwargs):
        # TODO JHILL: check to see if it would conflict with an existing entry
        # that is NOT this entry.... raise VaultEntryAlreadyExistsError
        # and catch it in the calling command

        new_entry_data = dict(**kwargs)
        entry = None
        vault_data = self.read()
        for index, entry in enumerate(vault_data['entries']):
            if entry['id'] == entry_id:
                if entry['password'] == new_entry_data['password']:
                    # TODO JHILL: don't print in here
                    print(colored("password was the same as before, not updating timestamp", "yellow"))
                else:
                    new_entry_data['timestamp'] = datetime.datetime.now().isoformat()
                    vault_data['entries'][index].update(new_entry_data)
                    entry = vault_data['entries'][index]
        self.write(vault_data)

        return entry


    def security_audit(self):
        vault_data = self.read()

        passwords = dict()

        for entry in vault_data['entries']:
            if entry['password'] not in passwords:
                passwords[entry['password']] = dict()
                passwords[entry['password']]['entries'] = []

                validate_password, pw_error = Vault.validate_password(entry['password'])

                passwords[entry['password']]['password_secure'] = validate_password
                passwords[entry['password']]['pw_error'] = pw_error

            passwords[entry['password']]['entries'].append(entry)
        return passwords


    def write(self, data):
        assert type(data) == dict

        key = get_encryption_key(Repo.salt(), self.password)
        fernet = Fernet(key)

        with open(self.data_path, "wb") as f:
            f.write(fernet.encrypt(json.dumps(data).encode('utf-8')))

        return True


    def read(self):
        if not os.path.exists(self.data_path):
            raise VaultNotFoundError()
        else:
            with open(self.data_path, "rb") as f:
                key = get_encryption_key(Repo.salt(), self.password)
                fernet = Fernet(key)
                try:
                    return json.loads(fernet.decrypt(f.read()))
                except InvalidToken:
                    raise VaultWrongPasswordError(self.name)
            return True
