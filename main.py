""" reads interface choice from config file and starts interface """
from cli import CLI
from gui import GUI
from game_backend import GameLogic, GameState

def read_config(configname):
    """ input = string, name of config file.
        output = string, name of chosen interface.
        searches config file for "interface" """

    output = ''

    with open(configname, "r", encoding="utf-8") as configfile:
        for line in configfile.readlines():
            # ignore comment lines
            if "interface" in line and not line.startswith('#'):
                output = line.split()[-1]

    return output

if __name__ == '__main__':
    interface_input = read_config("config.txt")
    game = GameLogic()
    state = GameState()
    if interface_input == "CLI":
        interface = CLI(game, state)
    elif interface_input == "GUI":
        interface = GUI(game, state)

    interface.loop()
