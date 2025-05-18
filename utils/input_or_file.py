import os

def read_file(file_path):
    try:
        with open(file_path, "r") as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []

def get_input_or_file(input_value):
    if os.path.isfile(input_value):
        print(f"[+] Loading from file: {input_value}")
        return read_file(input_value)
    elif os.path.exists(input_value):
        print(f"{input_value} not a file.")
        return []
    else:
        return [input_value]
