from game_backend import GameLogic
from cli import CLI
from gui import GUI

def read_config(configname):
    with open(configname, "r", encoding="utf-8") as configfile:
        for line in configfile.readlines():
            if line.startswith('#'):
                continue
            if "interface" in line:
                split = line.split()
                return split[-1]

if __name__ == '__main__':
    interface_input = read_config("config.txt")
    if interface_input == "CLI":
        interface = CLI()
    elif interface_input == "GUI":
        interface = GUI()

    interface.loop()
