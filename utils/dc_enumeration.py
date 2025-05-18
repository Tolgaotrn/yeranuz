import subprocess


def find_dc_ip():

    target_domain = input("Please provide a domain address: ")
    if target_domain:
        command = f'nslookup -type=SRV _ldap._tcp.dc._msdcs.{target_domain}'
    else:
        exit(1)



    print(f'\n[+] Running command: {command}')

    try :
        result = subprocess.run(command, shell=True,  text=True)
        print(result.stdout)

        if result.returncode == 0:
            print("\n[+] DC IP address found successfully!")
        else:
            print(f"\n[-] Error: {result.stderr}")

    except Exception as e:
        print(f"\n[-] Exception: {e}")
