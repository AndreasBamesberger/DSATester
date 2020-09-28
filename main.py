""" Reads config file and starts interface """
from libs.interfaces.cli import CLI
from libs.interfaces.gui import GUI
from libs.backend.dsa_game import GameLogic, GameState
from libs.languages.languages import english, german


def read_config(config_name):
    """
    Opens text file, looks for keywords and creates a dictionary entry for
    each match.

    Parameters:
        config_name (str): The name of the file, e.g. 'config.txt'

    Returns:
        out_dict (dict): The created dictionary
    """

    out_dict = {}
    str_entries = ("output file", "interface",
                   "dice", "hero folder", "language")
    int_entries = ("font size", "width", "height")
    float_entries = "scaling"
    with open(config_name, "r", encoding="utf-8") as configfile:
        for line in configfile.readlines():
            if line.startswith('#') or line == '\n':
                continue
            split = line.split(': ')
            split[-1] = split[-1].rstrip()
            if split[0] in str_entries:
                out_dict.update({split[0]: split[-1]})
            elif split[0] in int_entries:
                out_dict.update({split[0]: int(split[-1])})
            elif split[0] in float_entries:
                out_dict.update({split[0]: float(split[-1])})

    return out_dict


if __name__ == '__main__':
    lang = None
    interface = None
    configs = read_config("config.txt")
    state = GameState()

    if configs["language"] == "english":
        lang = english
    elif configs["language"] == "german":
        lang = german

    game = GameLogic(configs, lang)

    if configs["interface"] == "CLI":
        interface = CLI(game, state, configs, lang)
    elif configs["interface"] == "GUI":
        interface = GUI(game, state, configs, lang)

    interface.loop()
