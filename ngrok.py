import os 
import time
import colorama
from colorama import Fore

colorama.init()

os.system('cls||clear')

print(Fore.RED + "ngrok serverı açılıyor...")

time.sleep(2)

os.system('ngrok http 5000')