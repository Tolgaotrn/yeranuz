import os
import subprocess
from colorama import Fore, Style, init

from utils.nmap import run_nmap
from utils.dc_enumeration import find_dc_ip
from core.module_base import ModuleBase

init()


class NoCred(ModuleBase):
    def __init__(self):
        super().__init__()
        self.name = "no_creds"

        # options utilisables par get_param()
        self.options = {
            "ip": None,
            "domain": None,
        }

        # mapping action → méthode
        self.actions = {
            "nmap":              self.network_discovery,
            "find_dc_ip":        find_dc_ip,
            "anon_smb_share":    self.run_anonymous_access_on_smb_shares,
            "users_enumeration": self.enumerate_users,
            "bruteforcing_rid":  self.bruteforce_users,
            "smb_poisoning":     self.smb_poisoning,
            "zone_transfer":     self.zone_transfer,
            "all":               self.run_all,
        }

        self.color = Fore.MAGENTA

    # ──────────────────────────────────────────
    #  ACTIONS
    # ──────────────────────────────────────────
    def network_discovery(self):
        target = self.get_param("ip", required=True)
        if not target:
            return

        yn = input("\nSpecific nmap options ? (Y/N) : ").strip().upper()
        if yn == "Y":
            opts = input("Options (-Pn -sC …) : ").strip()
            run_nmap(target, options=opts or None)
        else:
            print("\n[+] Running with default options…")
            run_nmap(target)

    # -------------------------
    def run_anonymous_access_on_smb_shares(self):
        ip_range = self.get_param("ip", required=True)
        if not ip_range:
            return

        cmd = f"nxc smb {ip_range}"
        print(f"\n🟡 Running command: {cmd}")
        subprocess.run(cmd, shell=True, text=True)

    # -------------------------
    def run_normal_access_on_smb_shares(self, username, password):
        ip_range = self.get_param("ip", required=True)
        if not ip_range:
            return

        cmd = f"nxc smb {ip_range} -u {username} -p {password} --shares"
        print(f"\n🟡 Running command: {cmd}")
        subprocess.run(cmd, shell=True, text=True)

    # -------------------------
    def enumerate_users(self):
        ip = self.get_param("ip", required=True)
        if not ip:
            return

        cmd = ["nxc", "smb", ip, "--rid-brute", "10000"]
        self.run_tool(cmd,
                      key="users",
                      category="users",
                      source="rid_brute")

        if self.context:
            self.context.commit_pending()

    # -------------------------
    def bruteforce_users(self):
        domain     = self.get_param("domain", required=True)
        dc_address = self.get_param("ip",     required=True)
        userlist_path = input("User list file path : ").strip()

        if not (domain and dc_address and userlist_path):
            print("[-] Need domain, DC IP and wordlist path.")
            return
        if not os.path.isfile(userlist_path):
            print("[-] Wordlist not found.")
            return

        cmd = f"kerbrute userenum -d {domain} --dc {dc_address} {userlist_path}"
        print(f"\n[+] Running: {cmd}")
        subprocess.run(cmd, shell=True, text=True)

    # -------------------------
    def smb_poisoning(self):
        iface = input("Interface pour Responder : ").strip()
        if not iface:
            return
        subprocess.run(["sudo", "responder", "-I", iface])

    # -------------------------
    def zone_transfer(self):
        ip_range = input("IP range for zone-transfer scan : ").strip()
        if not ip_range:
            return
        subprocess.run(["nmap", "-p", "88", "--open", ip_range])

    # ──────────────────────────────────────────
    #  RUN ALL
    # ──────────────────────────────────────────
    def run_all(self):
        print("\n[🔥] Running all no_creds actions…\n")

        # vérifie les options de base
        self.options["ip"]     = self.get_param("ip", required=True)
        self.options["domain"] = self.get_param("domain")
        if not self.options["ip"]:
            return

        self.network_discovery()
        print("-" * 50)
        self.run_anonymous_access_on_smb_shares()
        print("-" * 50)
        self.enumerate_users()
        print("-" * 50)
        self.zone_transfer()
        print("-" * 50)
        self.bruteforce_users()
        print("-" * 50)
        self.smb_poisoning()
        print("-" * 50)

        if self.context:
            self.context.commit_pending()
