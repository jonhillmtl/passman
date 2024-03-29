from .repo import Repo, RepoAlreadyExistsError, RepoNotFoundError
from .vault import (Vault, VaultNotFoundError, VaultAlreadyExistsError, 
    VaultWrongPasswordError, VaultEntryAlreadyExistsError, VaultWeakPasswordError)
from .utils import error_exit, smart_choice
from termcolor import colored
import pprint
import pyperclip

def add_vault_entry(args):
    vault = Vault(args.vault_name, args.vault_password)

    try:
        entry = vault.add_entry(name=args.name, username=args.username, password=args.password)
        entry['password'] = '<sensitive>'
        vault.add_history_entry('add_entry', entry, entry['timestamp'])
    except VaultEntryAlreadyExistsError:
        error_exit("entry for {} ({}) already exists. try update_vault_entry instead".format(
            args.name,
            args.username
        ))


def change_vault_password(args):
    vault = Vault(args.name, args.old_password)

    try:
        vault.change_password(args.new_password)
    except VaultWeakPasswordError as e:
        error_exit("the password is too weak: {}".format(e.error))


def create_vault(args):
    vault = Vault(args.vault_name, args.vault_password)

    try:
        vault.create()
        vault.add_history_entry('create_vault', None, None)

        # TODO JHILL: write cached password to cache file
    except VaultAlreadyExistsError as e:
        error_exit("vault already exists")
    except RepoNotFoundError as e:
        error_exit("repo does not exist")
    except VaultWeakPasswordError as e:
        error_exit("the password is too weak: {}".format(e.error))


def delete_vault_entry(args):
    vault = Vault(args.vault_name, args.vault_password)

    vault_data = vault.read()

    entry_id = smart_choice(
        [
            dict(
                choice_data=entry['id'],
                description="{}: {} {} {}".format(
                    entry['id'],
                    entry['name'],
                    entry['username'],
                    entry['password']
                )
            ) for entry in vault_data['entries']]
    )

    if entry_id != -1:
        vault.delete_entry(entry_id)

        vault.add_history_entry('delete_vault_entry', entry_id, None)


def dump_vault(args):
    vault = Vault(args.vault_name, args.vault_password)

    vault.add_history_entry('dump_vault', None, None)
    pprint.pprint(vault.read())


def init(args):
    repo = Repo()

    try:
        repo.init()
        print(colored("created repo", "green"))
    except RepoAlreadyExistsError as e:
        error_exit("repo already exists")


def list_vaults(args):
    repo = Repo()
    if repo.exists:
        print(repo.vaults)
    else:
        error_exit("no repo exists")


def merge_vaults(args):
    target = Vault(args.v1, args.v1pw)
    source = Vault(args.v2, args.v2pw)

    target.merge_vault(source)

    # TODO JHILL: add_history_entry


def password(args):
    vault = Vault(args.vault_name, args.vault_password)
    vault_data = vault.read()

    matches = []
    if args.search == '':
        matches= vault_data['entries']
    else:
        for entry in vault_data['entries']:
            if args.search.lower() in entry['name'].lower():
                matches.append(entry)

    if len(matches) == 0:
        error_exit("no matches found for {}".format(args.search))

    entry_id = smart_choice(
        [
            dict(
                choice_data=index,
                description="{} {}".format(
                    entry['name'],
                    entry['username']
                )
            ) for (index, entry) in enumerate(matches)
        ]
    )

    if entry_id != -1:
        pyperclip.copy(matches[entry_id]['password'])
        print(colored("copied to clipboard", "green"))

        vault.add_history_entry(
            'password',
            dict(
                entry_id=matches[entry_id]['id'],
                search=args.search
            )
        )

def security_audit(args):
    vault = Vault(args.vault_name, args.vault_password)

    # TODO JHILL: use entry audits
    password_audits, entry_audits = vault.security_audit()
    secure = True

    for password, data in password_audits.items():
        if len(data['entries']) > 1:
            secure = False
            print("{} accounts have the same password: {}".format(
                len(data['entries']),
                ", ".join("{} ({})".format(e['name'], e['username']) for e in data['entries'])
            ))

        if data['password_secure'] is False:
            secure = False
            print("{} accounts have weak passwords: {}".format(
                len(data['entries']),
                ", ".join("{} ({})".format(e['name'], e['username']) for e in data['entries'])
            ))

    # TODO JHILL: check the age of the password by their timestamp!!!

    if secure is True:
        print(colored("secure", "green"))

    vault.add_history_entry('security_audit', None, None)


def update_vault_entry(args):
    vault = Vault(args.vault_name, args.vault_password)

    vault_data = vault.read()
    entry_id = smart_choice([
        dict(
            choice_data=entry['id'],
            description="{}: {} {} {}".format(
                entry['id'],
                entry['name'],
                entry['username'],
                entry['password']
            )
        ) for entry in vault_data['entries']
    ])

    if entry_id != -1:
        entry = vault.update_entry(entry_id, name=args.name, username=args.username, password=args.password)
        entry['password'] = '<sensitive>'
        vault.add_history_entry('update_vault_entry', entry, None)

