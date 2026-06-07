import os
import time
from colorama import Fore, Back, Style, init
init(autoreset=True)
for i in range(1,101):
    print()
    print(f"[{Fore.GREEN +'='*i}{Fore.RED + '='*(100-i)}{Fore.WHITE}] {i}%",end = "\r")
    time.sleep(0.1)