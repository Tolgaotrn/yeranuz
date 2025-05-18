from colorama import Fore, Style, init
from core.module_base import ModuleBase
from gvm.connections import TLSConnection
from gvm.protocols.gmp import Gmp
from datetime import datetime
import time
import socket
import subprocess

init()

class BloodHound(ModuleBase):
    def __init__(self):
        super().__init__()
        self.name = "bloodhound"
        self.options = {
            "ad_ip": None,
            "openvas_host": "127.0.0.1",
            "openvas_port": "9392",
            "openvas_username": "admin",
            "openvas_password": "admin",
            "bypass_openvas": "false"
        }
        self.actions = {
            "fetch_openvas": self.fetch_openvas_data,
            "process_data": self.process_data,
            "cornershot_analysis": "analysis",
            "test_connection": self.test_openvas_connection,
            "all": self.run_all,
            "check_openvas": self.check_openvas_status
        }
        self.color = Fore.GREEN
        self.context = None
        self.gmp = None

    def banner(self):
        print(f"""
{Fore.GREEN}
╔══════════════════════════════════════╗
║         BloodHound Module            ║
║    Active Directory Reconnaissance   ║
╚══════════════════════════════════════╝{Style.RESET_ALL}
        """)

    def check_openvas_status(self):
        host = self.options["openvas_host"]
        port = int(self.options["openvas_port"])
        print(f"{Fore.CYAN}[*] Checking if OpenVAS is running at {host}:{port}...{Style.RESET_ALL}")

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        sock.close()

        if result == 0:
            print(f"{Fore.GREEN}[+] OpenVAS appears to be running at {host}:{port}{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}[-] Cannot connect to OpenVAS at {host}:{port}{Style.RESET_ALL}")
            if host == "127.0.0.1" or host == "localhost":
                print(f"{Fore.CYAN}[*] Would you like to try starting OpenVAS? (y/n){Style.RESET_ALL}")
                choice = input()
                if choice.lower() in ['y', 'yes']:
                    self.try_start_openvas()
            return False

    def try_start_openvas(self):
        print(f"{Fore.CYAN}[*] Attempting to start OpenVAS services...{Style.RESET_ALL}")
        try:
            subprocess.run(["sudo", "systemctl", "start", "openvas"],
                           stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            subprocess.run(["sudo", "gvm-start"],
                           stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            print(f"{Fore.GREEN}[+] Commands sent to start OpenVAS. Waiting 5 seconds...{Style.RESET_ALL}")
            time.sleep(5)
            self.check_openvas_status()
        except:
            print(f"{Fore.RED}[-] Failed to start OpenVAS automatically.{Style.RESET_ALL}")

    def test_openvas_connection(self):
        if not self.check_openvas_status():
            return False
        try:
            connection = TLSConnection(
                hostname=self.options["openvas_host"],
                port=int(self.options["openvas_port"])
            )
            with Gmp(connection=connection) as gmp:
                version = gmp.get_version()
                print(f"{Fore.GREEN}[+] Connected to OpenVAS - Version info received{Style.RESET_ALL}")
                return True
        except Exception as e:
            print(f"{Fore.RED}[-] Failed to connect to OpenVAS GMP: {str(e)}{Style.RESET_ALL}")
            return False

    def connect_gmp(self):
        if not self.check_openvas_status():
            return False
        try:
            connection = TLSConnection(
                hostname=self.options["openvas_host"],
                port=int(self.options["openvas_port"]),
            )
            self.gmp = Gmp(connection=connection)
            print(f"{Fore.GREEN}[+] Connected to OpenVAS GMP{Style.RESET_ALL}")
            return True
        except Exception as e:
            print(f"{Fore.RED}[-] GMP connection error: {str(e)}{Style.RESET_ALL}")
            return False

    def fetch_openvas_data(self):
        if not self.options["ad_ip"]:
            print(f"{Fore.RED}[-] Active Directory IP must be set.{Style.RESET_ALL}")
            return

        if self.options["bypass_openvas"].lower() == "true":
            print(f"{Fore.YELLOW}[!] Bypassing OpenVAS - using alternative scanning method...{Style.RESET_ALL}")
            self.run_basic_scan()
            return

        if not self.connect_gmp():
            print(f"{Fore.YELLOW}[!] Using alternative scanning method due to OpenVAS connection issues...{Style.RESET_ALL}")
            self.run_basic_scan()
            return

        print(f"{Fore.CYAN}[*] Setting up scan for {self.options['ad_ip']}...{Style.RESET_ALL}")
        try:
            response = self.gmp.send_command('get_scanners')
            scanner = response.find('.//scanner')
            scanner_id = scanner.get('id')

            create_target_resp = self.gmp.send_command('create_target', {
                'name': f'Target-{self.options["ad_ip"]}',
                'hosts': self.options['ad_ip'],
                'port_list_id': '33d0cd82-57c6-11e1-8ed1-406186ea4fc5'
            })
            target_id = create_target_resp.get('id')

            create_task_resp = self.gmp.send_command('create_task', {
                'name': f'Scan-{self.options["ad_ip"]}',
                'target_id': target_id,
                'scanner_id': scanner_id,
                'config_id': 'daba56c8-73ec-11df-a475-002264764cea'
            })
            task_id = create_task_resp.get('id')

            self.gmp.send_command('start_task', {'task_id': task_id})

            print(f"{Fore.GREEN}[+] Scan started successfully!{Style.RESET_ALL}")
            print(f"{Fore.CYAN}[*] Waiting for scan to complete...{Style.RESET_ALL}")

            scan_finished = False
            while not scan_finished:
                task_status_resp = self.gmp.send_command('get_task', {'task_id': task_id})
                status = task_status_resp.find('.//status').text
                if status == 'Done':
                    scan_finished = True
                else:
                    print(f"{Fore.YELLOW}[!] Scan still running... waiting 10 seconds{Style.RESET_ALL}")
                    time.sleep(10)

            print(f"{Fore.GREEN}[+] Scan completed! Fetching report...{Style.RESET_ALL}")

            task_data = self.gmp.send_command('get_task', {'task_id': task_id})
            report_id = task_data.find('.//last_report/report').get('id')

            report_resp = self.gmp.send_command('get_report', {
                'report_id': report_id,
                'details': '1'
            })

            results = report_resp.findall('.//result')
            print(f"{Fore.CYAN}[*] Found {len(results)} vulnerabilities in total.{Style.RESET_ALL}")

            critical_findings = []

            for result in results:
                try:
                    name = result.find('name').text
                    severity = float(result.find('severity').text)
                    description = result.find('description').text if result.find('description') is not None else "No description"
                    nvt = result.find('nvt')
                    cve = None
                    if nvt is not None:
                        cve_elem = nvt.find('cve')
                        if cve_elem is not None:
                            cve = cve_elem.text

                    if severity >= 2.0:
                        finding = {
                            "name": name,
                            "severity": severity,
                            "description": description,
                            "cve": cve
                        }
                        critical_findings.append(finding)
                        break
                except Exception as e:
                    continue

            if critical_findings:
                print(f"{Fore.RED}[!] Found a critical vulnerability!{Style.RESET_ALL}")
                for finding in critical_findings:
                    print(f"{Fore.YELLOW}- {finding['name']} (Severity: {finding['severity']}){Style.RESET_ALL}")
                    if finding['cve']:
                        print(f"    CVE: {finding['cve']}")
                    print(f"    Description: {finding['description']}\n")
            else:
                print(f"{Fore.GREEN}[+] No critical vulnerabilities found!{Style.RESET_ALL}")

        except Exception as e:
            print(f"{Fore.RED}[-] Error during scan creation or fetching report: {str(e)}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}[!] Falling back to basic scanning...{Style.RESET_ALL}")
            self.run_basic_scan()

    def run_basic_scan(self):
        print(f"{Fore.CYAN}[*] Running basic scan against {self.options['ad_ip']}...{Style.RESET_ALL}")
        try:
            print(f"{Fore.CYAN}[*] Checking for nmap availability...{Style.RESET_ALL}")
            subprocess.run(["which", "nmap"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            print(f"{Fore.GREEN}[+] Nmap found, running basic scan...{Style.RESET_ALL}")
            scan_output = subprocess.run(
                ["nmap", "-sV", "-p389,445,3389,5985,88,636", self.options["ad_ip"]],
                capture_output=True,
                text=True
            ).stdout

            print(f"{Fore.GREEN}[+] Basic scan completed. Results:{Style.RESET_ALL}")
            print(scan_output)

        except subprocess.CalledProcessError:
            print(f"{Fore.RED}[-] Nmap not found. Cannot perform basic scan.{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[-] Error during basic scan: {str(e)}{Style.RESET_ALL}")

    def process_data(self):
        if self.options["bypass_openvas"].lower() == "true":
            print(f"{Fore.YELLOW}[!] OpenVAS bypassed - no scan data to process{Style.RESET_ALL}")
            return

        if not self.connect_gmp():
            print(f"{Fore.YELLOW}[!] Cannot process data - OpenVAS connection issues{Style.RESET_ALL}")
            return

        print(f"{Fore.CYAN}[*] Processing scan results...{Style.RESET_ALL}")
