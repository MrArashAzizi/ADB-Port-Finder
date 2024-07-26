import subprocess
import socket
import logging
import threading
import time
import os
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Logging settings
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration variables
IP_ADDRESS = '192.168.1.5'  # IP address of the ADB-enabled device
TIMEOUT_DURATION = 1.5  # Timeout duration in seconds for checking open ports
PORT_RANGE = (33000, 48000)  # Port range for finding open ADB port

def clear_console():
    """Clear the console screen based on the operating system."""
    os.system('cls' if os.name == 'nt' else 'clear')

def run_adb_command(command):
    """Run ADB command and return the output."""
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing command: {e}")
        return ''

def is_port_open(ip_address, port):
    """Check if a specific port is open on the given IP address."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(TIMEOUT_DURATION)  # Timeout duration from config
        result = sock.connect_ex((ip_address, port))
        return result == 0

def connect_to_device(ip_address, port, result, lock):
    """Attempt to connect to the ADB device on the specified port."""
    if is_port_open(ip_address, port):
        adb_result = run_adb_command(['adb', 'connect', f'{ip_address}:{port}'])
        with lock:
            if "connected" in adb_result and result['port'] is None:
                result['port'] = port
                result['output'] = adb_result

def find_open_adb_port(ip_address, port_range=PORT_RANGE):
    """Find an open ADB port within the specified port range."""
    ports = list(range(port_range[0], port_range[1] + 1))
    total_ports = len(ports)
    result = {'port': None, 'output': None}
    lock = threading.Lock()

    def update_progress(progress):
        """Update the progress of port scanning."""
        percent = 100 * (progress / total_ports)
        print(f"Progress: {percent:.2f}%", end='\r')

    threads = []
    for i, port in enumerate(ports):
        if result['port']:
            break
        thread = threading.Thread(target=connect_to_device, args=(ip_address, port, result, lock))
        threads.append(thread)
        thread.start()

        if i % 50 == 0:
            update_progress(i)
            time.sleep(0.1)  # Short pause to show progress

    for thread in threads:
        thread.join()

    if result['port']:
        return result['port'], result['output']
    else:
        return None, "Could not find open port"

def install_apk(apk_path):
    """Install the APK file to the connected ADB device."""
    if os.path.exists(apk_path):
        logging.info(f"Installing APK from: {apk_path}")
        result = run_adb_command(['adb', 'install', apk_path])
        return result
    else:
        return "APK file not found."

def is_device_already_connected(ip_address):
    """Check if the device is already connected."""
    devices_output = run_adb_command(['adb', 'devices'])
    for line in devices_output.splitlines():
        if line.startswith(ip_address) and 'device' in line:
            return True, line.split(':')[1].split()[0]  # return True and the port
    return False, None

def disconnect_device(ip_address, port):
    """Disconnect the ADB device."""
    if port:
        disconnect_result = run_adb_command(['adb', 'disconnect', f'{ip_address}:{port}'])
    else:
        disconnect_result = run_adb_command(['adb', 'disconnect', ip_address])
    return disconnect_result

def main():
    """Main function to manage ADB connections and APK installations."""
    clear_console()
    print(Fore.CYAN + "ADB Port Finder and Manager")
    print(Fore.CYAN + "-"*30)
    print(Fore.CYAN + "This script automates the process of identifying available ADB (Android Debug Bridge) ports and connecting to an ADB-enabled device. It helps you find an open port, connect to the device, install APK files, and disconnect from the device.")
    print(Fore.CYAN + "="*30)
    ip_address = IP_ADDRESS  # Use the IP address from the configuration

    port = None
    already_connected, port = is_device_already_connected(ip_address)
    if already_connected:
        logging.info(Fore.GREEN + f"Device already connected at {ip_address}:{port}")
        connection_result = f"Device already connected at {ip_address}:{port}"
    else:
        logging.info(f"Starting to find the ADB port for IP address {ip_address}")
        while True:
            port, connection_result = find_open_adb_port(ip_address)
            if port:
                break
            else:
                print(Fore.RED + f"Error: {connection_result}")
                retry_choice = input(Fore.YELLOW + "Would you like to retry? (y/n): ").strip().lower()
                if retry_choice != 'y':
                    break

    if port or "already connected" in connection_result:
        print(Fore.CYAN + "="*30)
        print(Fore.GREEN + f"Successfully connected to {ip_address}:{port if port else 'N/A'}")
        print(Fore.GREEN + f"Connection Result:\n{connection_result}")
        print(Fore.CYAN + "="*30)

        while True:
            print(Fore.YELLOW + "Options:")
            print(Fore.YELLOW + "1. Install APK file")
            print(Fore.YELLOW + "2. Disconnect ADB")
            choice = input(Fore.YELLOW + "Enter your choice (1 or 2): ").strip()
            
            if choice == '1':
                apk_path = input(Fore.YELLOW + "Enter the path to the APK file for installation: ")
                installation_result = install_apk(apk_path)
                print(Fore.CYAN + "="*30)
                print(Fore.GREEN + f"APK Installation Result:\n{installation_result}")
                print(Fore.CYAN + "="*30)
            elif choice == '2':
                disconnect_result = disconnect_device(ip_address, port)
                print(Fore.CYAN + "="*30)
                print(Fore.GREEN + f"ADB Disconnect Result:\n{disconnect_result}")
                print(Fore.CYAN + "="*30)
                break
            else:
                print(Fore.RED + "Invalid choice. Please enter '1' for Install APK file or '2' for Disconnect ADB.")
        
    else:
        print(Fore.CYAN + "="*30)
        print(Fore.RED + f"Error: {connection_result}")
        print(Fore.CYAN + "="*30)

if __name__ == "__main__":
    main()
