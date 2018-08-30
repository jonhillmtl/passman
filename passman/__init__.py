from termcolor import colored
from str2bool import str2bool

import argparse
import os
import sys
import getpass

from .repo import Repo, RepoAlreadyExistsError
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

    'merge_vaults',             # implemented
    'change_vault_password',    # implemented

    'resalt',                   # hmmm... they'd have to provide password for every vault
    'security_audit'            # implemented
]


argparser = argparse.ArgumentParser()
argparser.add_argument("command")
argparser.add_argument("--interactive", default=False, type=str2bool, required=False)
args, unknown = argparser.parse_known_args()


def prepare_args(command):
    """ touch up the args with separate requirements for each command """
    
    # TODO JHILL: unglobalize this

    # TODO JHILL: use vault_name and vault_password everywhere, even though it's longer
    # TODO JHILL: make password interactive everywhere so it doesn't go in the history

    global args
    interactive_password = False
    confirm_password = False
    if command == 'create_vault':
        argparser.add_argument("--vault_name", required=True)
        interactive_password = True
        confirm_password = True

    elif command == 'dump_vault':
        argparser.add_argument("--vault_name", required=True)
        interactive_password = True

    elif command == 'list_vaults':
        pass

    elif command == 'add_vault_entry':
        argparser.add_argument("--vault_name", required=True)
        argparser.add_argument("--vault_password", required=True)
        argparser.add_argument("--name", required=True)
        argparser.add_argument("--username", required=True)
        argparser.add_argument("--password", required=True)
        argparser.add_argument("--tags", required=False)

    elif command == 'resalt':
        argparser.add_argument("--password", required=True)

    elif command == 'merge_vaults':
        argparser.add_argument("--v1", required=True)
        argparser.add_argument("--v2", required=True)
        argparser.add_argument("--v1pw", required=True)
        argparser.add_argument("--v2pw", required=True)

    elif command =='change_vault_password':
        argparser.add_argument("--name", required=True)
        argparser.add_argument("--old_password", required=True)
        argparser.add_argument("--new_password", required=True)
        
    elif command == 'delete_vault_entry':
        argparser.add_argument("--name", required=True)
        argparser.add_argument("--password", required=True)

    elif command == 'update_vault_entry':
        argparser.add_argument("--vault_name", required=True)
        argparser.add_argument("--vault_password", required=True)
        argparser.add_argument("--name", required=True)
        argparser.add_argument("--username", required=True)
        argparser.add_argument("--password", required=True)
        argparser.add_argument("--tags", required=False)

    elif command == 'security_audit':
        argparser.add_argument("--name", required=True)
        argparser.add_argument("--password", required=True)


    if interactive_password is True:
        if confirm_password is True:
            password = getpass.getpass("enter password: ")
            confirm_password = getpass.getpass("confirm password: ")
            if password != confirm_password:
                error_exit("passwords do not match")
        else:
            password = getpass.getpass("enter password: ")
        sys.argv.extend(['--vault_password', password])
        argparser.add_argument("--vault_password", required=True)

    # then reparse them to enforce the required-ness of them
    args = argparser.parse_args()
    

def call_command(command):
    if command not in globals():
        error_exit("{} is unimplemented".format(command))
    globals()[command](args)


def main():
    if args.command not in COMMANDS:
        error_exit("{} not in ({})".format(args.command, ", ".join(COMMANDS)))

    prepare_args(args.command)
    call_command(args.command)


if __name__ == '__main__':
    main()