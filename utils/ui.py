from colorama import Fore, Style

def show_main_banner(MODULES):
    print(Fore.GREEN + r"""
 __    _   ______  ______   ______   ______   _    _   ______ 
 \ \  | | | |     | |  | \ | |  | | | |  \ \ | |  | |     / / 
  \_\_| | | |---- | |__| | | |__| | | |  | | | |  | |  .---'  
  ____|_| |_|____ |_|  \_\ |_|  |_| |_|  |_| \_|__|_| /_/___  
                                                             
    """ + Style.RESET_ALL)

    print(f"{Fore.CYAN}🔰 ACTIVE DIRECTORY FRAMEWORK 🔰")
    print("    Based on Orange Cyberdefense Mind Map\n")

    print(f"{Fore.MAGENTA}Available modules:")
    print(Fore.LIGHTBLACK_EX + "╭" + "─" * 44 + "╮")
    for module in MODULES:
        print(f"{Fore.LIGHTBLACK_EX}│ {Fore.YELLOW}🟡 {module:<40}{Fore.LIGHTBLACK_EX}│")
    print(Fore.LIGHTBLACK_EX + "╰" + "─" * 44 + "╯")

    print(f"\n{Fore.CYAN}💡 Type '{Fore.YELLOW}use <module>{Fore.CYAN}' to start or '{Fore.YELLOW}help{Fore.CYAN}' for a list of commands\n")


def show_help():
    print("\n📌 Available commands:")
    print("  modules         - Show available modules")
    print("  use <module>    - Load a module")
    print("  options         - Show module options and actions (if module is loaded)")
    print("  set <opt> <val> - Set a module option")
    print("  run <action>    - Run a specific action from the loaded module")
    print("  run all         - Run all actions from the loaded module")
    print("  back            - Unload current module")
    print("  exit, quit      - Exit the framework\n")