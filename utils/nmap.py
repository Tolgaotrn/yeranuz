import subprocess

def run_nmap(target, options= ''):
    """
    //TODO: add more options, and make it more dynamic for after using on other modules
    """

    command = f"nmap {options} {target}"
    if command:
        print(f"\n Running command: {command}")


    try:
        result = subprocess.run(command, shell=True,  text=True )
        if result.returncode == 0:
            print("\n[+] Command executed successfully!")
        else:
            print("\n[-] ERROR: Command executed unsuccessfully!")

    except Exception as e:
        print(f"\n[-] Exception: {e}")

def ports_scan(target, options= None):
    command = f"nmap {target} -p- {options}"
    if command:
        print(f"\n Running command: {command}")
    try:
        result = subprocess.run(command, shell=True, text=True)
        if result.returncode == 0:
            print("\n[+] Command executed successfully!")
        else:
            print("\n[-] ERROR: Command executed unsuccessfully!")

    except Exception as e:
        print(f"\n[-] Exception: {e}")

