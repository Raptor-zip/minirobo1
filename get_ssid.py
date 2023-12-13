import subprocess

def get_current_wifi_ssid():
    try:
        result = subprocess.check_output(['iwgetid', '-r'], universal_newlines=True)
        return result.strip()
    except subprocess.CalledProcessError:
        return "Error retrieving Wi-Fi information"

if __name__ == "__main__":
    ssid = get_current_wifi_ssid()
    print("Current Wi-Fi SSID:", ssid)