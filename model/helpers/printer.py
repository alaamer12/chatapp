from colorama import Fore, init


init()

def print_info(*messages):
    print(Fore.BLUE + 'INFO: ', *messages, Fore.RESET)


def print_error(*messages):
    print(Fore.RED + 'ERROR: ', *messages, Fore.RESET)


def print_warning(*messages):
    print(Fore.YELLOW + 'WARNING: ', *messages, Fore.RESET)
