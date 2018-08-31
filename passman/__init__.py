from termcolor import colored
from str2bool import str2bool
from argparse import RawTextHelpFormatter

import argparse
import os
import sys
import getpass

from .repo import Repo, RepoAlreadyExistsError
from .vault import Vault, VaultWrongPasswordError

# TODO JHILL: one at a time
from .commands import *

COMMANDS = [
    'init',                     # implemented
    'list_vaults',              # implemented

    'create_vault',             # implemented
    'dump_vault',               # implemented

    'add_vault_entry',          # implemented
    'delete_vault_entry',       # implemented
    'update_vault_entry',
    'change_vault_password',    # implemented

    'merge_vaults',             # implemented

    # 'resalt',                   # hmmm... they'd have to provide password for every vault
    'security_audit',           # implemented,

    'password'                        # implemented,

    # 'clear_cache'               # go for it
]


COMMAND_ALIASES = dict(
    lv='list_vaults',
    sa='security_audit',
    cv='create_vault',
    dv='dump_vault',
    ave='add_vault_entry',
    dve='delete_vault_entry',
    uve='update_vault_entry',
    mv='merge_vaults',
    cvp='change_vault_password',
    cc='clear_cache',
    pw='password'
)


def prepare_command_help_string():
    return "can be any one of:\n\n{}\n\nabbreviations are available:\n\n{}".format(
        "\n".join(COMMANDS),
        "\n".join(["{} == {}".format(k, v) for k, v in COMMAND_ALIASES.items()])
    )

argparser = argparse.ArgumentParser(description='passman - an inconvenient way to store your passwords', formatter_class=RawTextHelpFormatter)
argparser.add_argument(
    "command",
    help=prepare_command_help_string(),
    choices=COMMANDS + [k for k in COMMAND_ALIASES.keys()]
)

# need to parse_known_args because the other arguments are added on
# a per command basis
args, unknown = argparser.parse_known_args()

def prepare_args(command):
    """ touch up the args with separate requirements for each command """

    # TODO JHILL: unglobalize this
    # TODO JHILL: use vault_name and vault_password everywhere, even though it's longer
    # TODO JHILL: add tagging
    # TODO JHILL: use subsparser, for real

    global args
    interactive_password = False

    if command == 'create_vault':
        argparser.add_argument("--vault_name", required=False, default='default')
        args = argparser.parse_args()

        vault = Vault(args.vault_name, None)
        if vault.exists:
            error_exit('vault already exists')

        password = getpass.getpass("enter password: ")
        confirm_password = getpass.getpass("confirm password: ")

        if password != confirm_password:
            error_exit("passwords do not match")

        sys.argv.extend(['--vault_password', password])
        argparser.add_argument("--vault_password", required=True)

        # then reparse them to grab any --vault_password that might have been added
        args = argparser.parse_args()

    elif command == 'dump_vault':
        argparser.add_argument("--vault_name", required=False, default='default')

        interactive_password = True

    elif command == 'list_vaults':
        pass

    elif command == 'add_vault_entry':
        argparser.add_argument("--vault_name", required=False, default='default')
        argparser.add_argument("--name", required=True)
        argparser.add_argument("--username", required=True)
        argparser.add_argument("--password", required=True)
        argparser.add_argument("--tags", required=False)

        interactive_password = True

    elif command == 'resalt':
        pass

    elif command == 'merge_vaults':
        argparser.add_argument("--v1", required=True)
        argparser.add_argument("--v2", required=True)
        
        # TODO JHILL: hmmmmm..... how do we get these interactively?
        # just do it right here I guess?
        argparser.add_argument("--v1pw", required=True)
        argparser.add_argument("--v2pw", required=True)

    elif command =='change_vault_password':
        argparser.add_argument("--vault_name", required=False, default='default')

        # TODO JHILL: hmmmmm..... how do we get these interactively?
        # just do it right here I guess?
        argparser.add_argument("--old_password", required=True)
        argparser.add_argument("--new_password", required=True)

    elif command == 'delete_vault_entry':
        argparser.add_argument("--vault_name", required=False, default='default')

        interactive_password = True

    elif command == 'update_vault_entry':
        argparser.add_argument("--vault_name", required=False, default='default')
        argparser.add_argument("--name", required=True)
        argparser.add_argument("--username", required=True)
        argparser.add_argument("--password", required=True)

        interactive_password = True

    elif command == 'security_audit':
        argparser.add_argument("--vault_name", required=False, default='default')

        interactive_password = True
    
    elif command == 'password':
        argparser.add_argument("--vault_name", required=False, default='default')
        argparser.add_argument("--search", required=False, default='')

        interactive_password = True

    # then reparse them to enforce the required-ness of them
    args = argparser.parse_args()

    if interactive_password is True:
        # password = Repo.get_cached_password(args.vault_name)
        # if password is None:
            # password = getpass.getpass("enter password: ")
        password = getpass.getpass("enter password: ")
        
        # neat trick to put something on the command line and then 
        # you can parse it like it was always there
        sys.argv.extend(['--vault_password', password])
        argparser.add_argument("--vault_password", required=True)

        # then reparse them to grab any --vault_password that might have been added
        args = argparser.parse_args()

        vault = Vault(args.vault_name, args.vault_password)
        try:
            vault.read()
            # Repo.write_cached_password(args.vault_name, password)
        except VaultWrongPasswordError:
            error_exit("password is wrong")
        except VaultNotFoundError:
            error_exit("vault not found")


def call_command(command):
    if command not in globals():
        error_exit("{} is unimplemented".format(command))
    globals()[command](args)


def main():
    command = args.command

    if command not in COMMANDS:
        if command not in COMMAND_ALIASES:
            error_exit("{} not in ({})".format(args.command, ", ".join(COMMANDS)))
        else:
            command = COMMAND_ALIASES[command]

    prepare_args(command)
    call_command(command)


if __name__ == '__main__':
    main()