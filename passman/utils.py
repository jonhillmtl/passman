from termcolor import colored
import sys


def error_exit(message):
    print(colored(message, "red"))
    sys.exit(1)


def smart_choice(choices):
    for index, choice in enumerate(choices):
        print("{}: {}".format(index, choice['description']))
    print("q: quit")

    while True:
        print("choose: ")
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