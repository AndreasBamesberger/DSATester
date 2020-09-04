""" reads config file and starts interface """
from interfaces.cli import CLI
from interfaces.gui import GUI
from game_backend.game_backend import GameLogic, GameState

def read_config(configname):
    """ Opens textfile, looks for keywords and creates a dictionary entry for each match.
    Input: configname: str, the name of the file, e.g. 'config.txt'
    Output: outdict: dict, the created dictionary """
    outdict = {}
    str_entries = ("output file", "interface", "dice", "hero folder")
    int_entries = ("font size", "width", "height")
    float_entries = ("scaling")
    with open(configname, "r", encoding="utf-8") as configfile:
        for line in configfile.readlines():
            if line.startswith('#') or line == '\n':
                continue
            split = line.split(': ')
            split[-1] = split[-1].rstrip()
            if split[0] in str_entries:
                outdict.update({split[0]: split[-1]})
            elif split[0] in int_entries:
                outdict.update({split[0]: int(split[-1])})
            elif split[0] in float_entries:
                outdict.update({split[0]: float(split[-1])})

    return outdict

if __name__ == '__main__':
    configs = read_config("config.txt")
    game = GameLogic(configs)
    state = GameState()

    if configs["interface"] == "CLI":
        interface = CLI(game, state, configs)
    elif configs["interface"] == "GUI":
        interface = GUI(game, state, configs)

    interface.loop()
