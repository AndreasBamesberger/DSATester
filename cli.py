""" command line interface, communicates with GameLogic """
import re
from game_backend import GameLogic, GameState

game = GameLogic()

class CLI:
    """ command line interface, communicates with GameLogic """
    def __init__(self):
        self.state = GameState()
        self.read_config("config.txt")

    def loop(self):
        while True:
            print("Roll #" + str(self.state.counter))
            if self.get_test_input():
                if self.state.category != "misc":
                    self.get_mod()
                if self.state.dice == "manual" and self.state.category != "misc":
                    self.get_manual_dice()
                self.state = game.test(self.state)
                self.show_result()
                self.get_save_choice()
                if self.state.save:
                    game.save_to_csv(self.state)
            self.reset()

    def reset(self):
        self.state.save = False
        self.state.category = None
        self.state.name = None
        self.state.attrs = None
        self.state.value = None
        self.state.mod = None
        self.state.rolls = None
        self.state.result = None
        self.state.misc = None
        self.state.desc = None
        self.state.first_input = None
        self.state.option_list = None
        self.state.selection = None

    def read_config(self, configname):
        """ input = string, name of config-file. scans config-file for
        "scaling" and "font" entries and sets variables accordingly """
        with open(configname, "r", encoding="utf-8") as configfile:
            for line in configfile.readlines():
                if line.startswith('#'):
                    continue
                if "dice" in line:
                    split = line.split()
                    self.state.dice = split[-1]

    def get_test_input(self):
        return_value = None
        self.state.first_input = input('Input: ').lower()
        if self.state.first_input in ("exit", "quit"):
            raise SystemExit

        pattern1 = "^(\d+)[dDwW](\d+)$" # 3d20 -> 3, 20 #pylint: disable=anomalous-backslash-in-string
        pattern2 = "^(\d+)[dDwW](\d+)\+(\d+)$" # 8d3+4 -> 8, 3, 4 #pylint: disable=anomalous-backslash-in-string
        pattern3 = "^(\d+)[dDwW](\d+)-(\d+)$" # 8d3-4 -> 8, 3, 4 #pylint: disable=anomalous-backslash-in-string

        match1 = re.match(pattern1, self.state.first_input)
        if match1 and int(match1.groups()[0]) > 0 and int(match1.groups()[1]) > 0:
            self.state.category = "misc"
            self.state.misc = (int(match1.groups()[0]), int(match1.groups()[1]))
            self.state.mod = 0

        match2 = re.match(pattern2, self.state.first_input)
        if match2 and int(match2.groups()[0]) > 0 and int(match2.groups()[1]) > 0:
            self.state.category = "misc"
            self.state.misc = (int(match2.groups()[0]), int(match2.groups()[1]))
            self.state.mod = int(match2.groups()[2])

        match3 = re.match(pattern3, self.state.first_input)
        if match3 and int(match3.groups()[0]) > 0 and int(match3.groups()[1]) > 0:
            self.state.category = "misc"
            self.state.misc = (int(match3.groups()[0]), int(match3.groups()[1]))
            self.state.mod = int(match3.groups()[2]) * -1

        if self.state.category == "misc":
            return_value = True
        else:
            self.state = game.autocomplete(self.state)
            if not self.state.option_list:
                self.display_message("No matches found")
                return_value = False
            else:
                self.get_selection()
                return_value = True

        return return_value

    def get_selection(self):
        pattern = '^\d+$'
        print("Character entries fitting input:")
        for index, option in enumerate(self.state.option_list):
            print("\t{0}: {1}".format(str(index+1), option[0]))

        while True:
            selection = input("Enter number: ")
            if re.match(pattern, selection) and int(selection) in range(1, len(self.state.option_list) + 1):
                self.state.selection = self.state.option_list[int(selection) - 1]
                self.state.name = self.state.option_list[int(selection) -1][0]
                self.state.category = self.state.option_list[int(selection) -1][1]
                break
            else:
                print("invalid input, try again")

    def get_mod(self):
        pattern = '^-?\d+$'
        while True:
            mod_input = input("Modifier: ")
            if mod_input == '':
                self.state.mod = 0
                break
            if re.match(pattern, mod_input):
                self.state.mod = int(mod_input)
                break
            else:
                print("Invalid")

    def display_message(self, text):
        print(text)

    def show_result(self):
        if not self.state:
            print("empty")
            return #TODO: change this from None to something more meaningful
        if self.state.category == "attr":
            outstring = (f"\tTested attribute: {self.state.name}\n"
                         f"\tValue: {self.state.value}\n"
                         f"\tModifier: {self.state.mod}\n"
                         f"\tDice value: {self.state.rolls[0]}\n"
                         f"\tResult: {self.state.result}")
            print(outstring)
        elif self.state.category == "fight_talent":
            outstring = (f"\tTested fight talent: {self.state.name}\n"
                         f"\tValue: {self.state.value}\n"
                         f"\tModifier: {self.state.mod}\n"
                         f"\tDice value: {self.state.rolls[0]}\n"
                         f"\tResult: {self.state.result}")
            print(outstring)
        elif self.state.category in ("skill", "spell"):

            if self.state.mod + self.state.value < 0:
                value_string = str(self.state.value) + " -> " + str(self.state.value + self.state.mod)
                attrs_string = [i.abbr + '(' + str(i.value) + "->" + str(i.modified) + ')' for _, i in enumerate(self.state.attrs)]
            else:
                attrs_string = [i.abbr + '(' + str(i.value) + ')' for _, i in enumerate(self.state.attrs)]
                value_string = str(self.state.value)
            attrs_string = ", ".join(map(str, attrs_string))

            remaining_string = [i.remaining for _, i in enumerate(self.state.attrs)]
            remaining_string = ", ".join(map(str, remaining_string))

            outstring = (f"\tTested {self.state.category}: {self.state.name}\n"
                         f"\tRelated attributes: {attrs_string}\n"
                         f"\tSkill value: {value_string}\n"
                         f"\tModifier: {self.state.mod}\n"
                         f"\tDice values: {self.state.rolls[0]}, {self.state.rolls[1]}, {self.state.rolls[2]}\n"
                         f"\tAttribute values remaining: {remaining_string}\n"
                         f"\tResult: {self.state.result}")
            print(outstring)
        elif self.state.category == "misc":
            outstring = (f"\tDice count: {self.state.misc[0]}\n"
                         f"\tDice eyes: {self.state.misc[1]}\n"
                         f"\tModifier: {self.state.mod}\n"
                         f"\tDice values: {', '.join(map(str, self.state.rolls))}\n"
                         f"\tSum: {self.state.result}")
            print(outstring)

    def get_save_choice(self):
        desc = input('Type description to save roll, "no" to discard roll: ')
        if desc.lower() == "no":
            self.state.save = False
        else:
            self.state.save = True
            self.state.desc = desc

    def get_manual_dice(self):
        pattern = "^\d+$"

        if self.state.category in ("attr", "fight_talent"):
            prompt_string = "Input 1 dice value: "
            dice_count = 1
        elif self.state.category in ("skill", "spell"):
            prompt_string = "Input 3 dice values, separated by whitespace: "
            dice_count = 3

        while True:
            outlist = []
            input_list = input(prompt_string).split(' ')

            for item in input_list:
                match = re.match(pattern, item)
                if match:
                    if int(item) in range(1, 21):
                        outlist.append(int(item))

            if len(outlist) == dice_count:
                break
            else:
                print("wrong input, try again")

        self.state.rolls = outlist


if __name__ == '__main__':
    interface = CLI()
    interface.loop()
