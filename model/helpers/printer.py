from colorama import Fore


def print_info(self, *messages):
    print(Fore.BLUE + 'INFO: ', *messages, Fore.RESET)


def print_error(self, *messages):
    print(Fore.RED + 'ERROR: ', *messages, Fore.RESET)


def print_warning(self, *messages):
    print(Fore.YELLOW + 'WARNING: ', *messages, Fore.RESET)
