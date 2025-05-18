import subprocess

def run_command(command):
    try:
        result = subprocess.run(command, shell=False,capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"Erreur: {result.stderr.strip()}"
    except Exception as e:
        return f"Erreur : {e}"
        
