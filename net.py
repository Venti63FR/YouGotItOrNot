import os

def clear():
    # 'nt' correspond a Windows, sinon c'est Mac/Linux
    os.system('cls' if os.name == 'nt' else 'clear')
