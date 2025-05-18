import sys
from colorama import Fore, Back, Style, init
from modules.no_cred.no_cred import NoCred
from modules.valid_user_no_pass.no_pass import ValidUser
from modules.valid_creds.valid_creds import ValidCreds
from core.console import Shell
from core.console import MODULES
from utils.ui import show_main_banner, show_help
from colorama import Fore,Style,init


init(autoreset=True)




if __name__ == "__main__":

    if "--help" in sys.argv or "-h" in sys.argv:
        show_help()
        sys.exit(0)



    show_main_banner(MODULES)

    Shell().run()


