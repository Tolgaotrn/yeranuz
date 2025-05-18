#base pour les autres modules, ils héritent de cette  classe

from colorama import Fore, Style
from utils.run_command import run_command
from utils.parsers import PARSERS


class ModuleBase:
    def __init__(self):
        self.name = "unnamed_module"
        self.options = {}      
        self.actions = {}
        self.color = Fore.RED      

    def set_option(self, key, value):
        key = key.lower()
        if key in self.options:
            self.options[key] = value
            print(f"[+] {key} set to {value}")
        else:
            print(f"[-] Unknown option: {key}")

    def show_options(self):
        print("\nCurrent Options:")
        for key, val in self.options.items():
            print(f"  {key}: {val}")
        print()

    
    def show_actions(self):
        print(f"\n{self.color}Available Actions for module: {self.name.upper()}\n{Style.RESET_ALL}")
        for i, name in enumerate(self.actions.keys(), 1):
            print(f"{Fore.YELLOW}{i:2} {Fore.CYAN}{name}{Style.RESET_ALL}")


    def get_param(self, key, prompt=None, required=False):
        value = self.options.get(key)

        if not value and self.context:
            if key == "ip":
                value = self.context.active_ip
            elif key == "user":
                value = self.context.active_user
            elif key == "domain":
                value = next(iter(self.context.domains), None)

        if not value and prompt:
            value = input(prompt).strip()

        if required and not value:
            print(f"[-] {key} missing, User 'set {key} ...' or 'pick {key}'.")
        return value





    def run_action(self, action):
        actions_list = list(self.actions.keys())
        if action.isdigit():
            index = int(action) - 1
            if 0 <= index < len(actions_list):
                action_name = actions_list[index]
                print(f"\n[>] Running {action_name}...\n")
                self.actions[action_name]()
            else:
                print(f"[-] Invalid action number: {action}")
        elif action in self.actions:
            print(f"\n[>] Running {action}...\n")
            self.actions[action]()
        else:
            print(f"[-] Action '{action}' not found.")

    def banner(self):
        print(self.color + f"\n\t\t🔥 MODULE {self.name.upper()} 🔥 \n" + Style.RESET_ALL)
        print("\n See actions and set a target with 'options' or 'help'\n")


    def run_tool(self, cmd, key=None, category=None, source=None):
        """
        Exécute la commande `cmd`, puis si `key` est fourni :
         - appelle le parseur PARSERS[key](stdout, source)
         - stash chaque item via self.context.stash(category, item)
        Retourne la sortie brute (str).
        """
        out = run_command(cmd)
        if key and category and self.context:
            parser = PARSERS.get(key)
            if parser:
                for item in parser(out, source):
                    self.context.stash(category, item)
        return out

    def run_all(self):
        print("\n[🔥] Running all actions...\n")
        for action in self.actions:
            self.actions[action]()