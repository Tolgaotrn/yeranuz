# core/console.py

#todo: rajouter un autocompleteur commandes + paths


from modules.valid_user_no_pass.no_pass import ValidUser
from modules.no_cred.no_cred import NoCred
from modules.valid_creds.valid_creds import ValidCreds 
from modules.quick_compromise.quick_compromise import Quick_compromise as CommonVulns
from modules.bloodhound.bloodhound import BloodHound

from colorama import Fore, Style, init
# import readline
from core.basicautomation import basicAutomation
from core.authanticated_enum import AuthenticatedEnum
init()
from utils.ui import show_main_banner
import readline
import rlcompleter
from core.context import Context
from core.engine import engine


#init()

MODULES = {
    "valid_user": ValidUser,
    "no_cred": NoCred,
    "valid_creds": ValidCreds,
    "common_vulns": CommonVulns,
    "basicAutomation": basicAutomation,
    "engine": engine,
    "bloodhound": BloodHound,  
    "authanticated_enum": AuthenticatedEnum,
}

MODULES_COLORS = {
    "valid_user" : Fore.BLUE,
    "no_cred" : Fore.MAGENTA,
    "valid_creds" : Fore.GREEN,
}




class Shell:
    def __init__(self):
        self.current_module = None
        self.module_instance = None
        self.context = Context()




    def run(self):
        while True:
            color = MODULES_COLORS.get(self.current_module, Fore.CYAN)

            prompt = (
                f"[yeranuz/[\001{color}\002{self.current_module}\001{Style.RESET_ALL}\002] > "
                if self.current_module
                else "[yeranuz] > "
            )



            cmd = input(prompt).strip()

            if cmd in ["exit", "quit"]:
                print("👋 Bye!")
                break

            elif cmd == "modules":
                print(f"{Fore.MAGENTA}Available modules:\n")
                print(Fore.LIGHTBLACK_EX + "╭" + "─" * 44 + "╮")
                for module in MODULES:
                    print(f"{Fore.LIGHTBLACK_EX}│ {Fore.YELLOW}🟡 {module:<40}{Fore.LIGHTBLACK_EX}│")
                print(Fore.LIGHTBLACK_EX + "╰" + "─" * 44 + "╯")

            elif cmd == "help":
                print("\nAvailable commands:")
                print("  modules         - Show available modules")
                print("  use <module>    - Load a module")
                print("  options         - Show module options and actions (if module is loaded)")
                print("  set <opt> <val> - Set a module option")
                print("  run <action>    - Run a specific action from the loaded module")
                print("  run all         - Run all actions from the loaded module")
                print("  back            - Unload current module")
                print("  exit, quit      - Exit the framework\n")


            elif cmd.startswith("use "):
                name = cmd.split(" ", 1)[1]
                if name in MODULES:
                    self.module_instance = MODULES[name]()
                    if self.context.active_ip:
                        self.module_instance.options["ip"] = self.context.active_ip
                    if self.context.active_user:
                        self.module_instance.options["user"] = self.context.active_user
                    if self.context.domains:
                        self.module_instance.options["domain"] = next(iter(self.context.domains))

                    self.current_module = name
                    self.module_instance.banner()
                    self.module_instance.show_actions()
                    self.module_instance.context = self.context
            

                    
                else:
                    print("[-] Unknown module.")

            elif cmd == "context":
                self.context.show()

            elif cmd == "back":
                self.current_module = None
                self.module_instance = None
                show_main_banner(MODULES)



            elif cmd.startswith("pick "):
                parts = cmd.split(maxsplit=2)
                cat = parts[1]               
                val_given = len(parts) == 3

                
                if cat == "user":
                    if val_given:
                        login = parts[2]
                        if login in self.context.users:
                            self.context.active_user = login
                            print(f"[+] active user : {login}")
                        else:
                            print("[-] User inconnu.")
                    else:
                        self.context.select_user()

                    if self.module_instance and self.context.active_user:
                        self.module_instance.options["user"] = self.context.active_user

                
                elif cat == "ip":
                    if val_given:
                        addr = parts[2]
                        if addr in self.context.ips:
                            self.context.active_ip = addr
                            print(f"[+] active ip : {addr}")
                        else:
                            print("[-] IP inconnue.")
                    else:
                        self.context.select_ip()

                    if self.module_instance and self.context.active_ip:
                        self.module_instance.options["ip"] = self.context.active_ip

                elif cat == "cred":
                    if val_given and ":" in parts[2]:
                        u, p = parts[2].split(":", 1)
                        entry = {"user": u, "password": p}
                        if entry in self.context.creds:
                            self.context.active_cred = entry
                            print(f"[+] active credentials : {u}:{p}")
                        else:
                            print(f"[-] unknown creds")
                    else:
                        self.context.select_cred()
                    
                    if self.module_instance and self.context.active_cred:
                        self.module_instance.options["user"] = self.context.active_cred["user"]
                        self.module_instance.options["password"] = self.context.active_cred["password"]

                else:
                    print("Usage : pick user|ip [valeur]")




            #ajouter au data store
            elif cmd.startswith("add "):
                parts = cmd.split(maxsplit=2)
                if len(parts) < 3:
                    print("Usage: add user|ip|domain <value>")
                    continue
                cat, val = parts[1], parts[2].strip()

                if cat == "user":
                    self.context.users.add(val)
                    self.context.active_user = val                      
                    print(f"[+] User ajouté & sélectionné : {val}")

                    if self.module_instance:
                        self.module_instance.options["user"] = val

                elif cat == "ip":
                    self.context.ips.add(val)
                    self.context.active_ip = val                        
                    print(f"[+] IP ajoutée & sélectionnée : {val}")

                    if self.module_instance:
                        self.module_instance.options["ip"] = val


                elif cat == "domain":
                    self.context.domains.add(val)
                    print(f"[+] Added domain : {val}")

                    if self.module_instance:
                        self.module_instance.options["domain"] = val

                elif cat == "cred":
                    if ":" not in val:
                        print("usage : add cred user:password")
                        continue
                    u, p = val.split(":", 1)
                    entry = {"user": u, "password": p}
                    if entry not in self.context.creds:
                        self.context.creds.append(entry)
                    self.context.active_cred = entry
                    print(f"[+] creds added : {u}:{p}")

                else:
                    print("uknown user, ip, domain")
                    continue


            #supprimer du data store
            elif cmd.startswith("remove "):
                parts = cmd.split(maxsplit=2)
                if len(parts) < 3:
                    print("Usage: remove user|ip|domain|cred <valeur>")
                    continue
                cat, val = parts[1], parts[2].strip()

                if cat == "user" and val in self.context.users:
                    self.context.users.remove(val)
                    if self.context.active_user == val:
                        self.context.active_user = None
                    print(f"[–] User supprimé : {val}")

                elif cat == "ip" and val in self.context.ips:
                    self.context.ips.remove(val)
                    if self.context.active_ip == val:
                        self.context.active_ip = None
                    print(f"[–] IP supprimée : {val}")

                elif cat == "domain" and val in self.context.domains:
                    self.context.domains.remove(val)
                    print(f"[–] Domaine supprimé : {val}")

                elif cat == "cred" and ":" in val:
                    u, p = val.split(":", 1)
                    entry = {"user": u, "password": p}
                    if entry in self.context.creds:
                        self.context.creds.remove(entry)
                        if self.context.active_cred == entry:
                            self.context.active_cred = None
                        print(f"[–] Credential supprimé : {u}:{p}")
                    else:
                        print("[-] Credential introuvable.")
                else:
                    print("[-] Catégorie / valeur inconnue.")
                continue




            elif self.module_instance:
                if cmd == "options":
                    self.module_instance.show_options()
                    self.module_instance.show_actions()
                #elif cmd == "show actions":
                #    self.module_instance.show_actions()
                elif cmd.startswith("set "):
                    try:
                        _, key, value = cmd.split(" ", 2)
                        self.module_instance.set_option(key, value)
                    except:
                        print("Usage: set <option> <value>")
                elif cmd.startswith("run ") or cmd.startswith("use "):
                    action = cmd.split(" ", 1)[1]
                    self.module_instance.run_action(action)
                elif cmd == "run all":
                    self.module_instance.run_all()
                else:
                    print("Unknown command in module. Try: show actions, run <action>, set <opt> <val>, back")
            else:
                print("Unknown command. Try: show modules, use <module>, exit.")
