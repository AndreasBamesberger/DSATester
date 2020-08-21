import re
from game_backend import GameLogic, GameState
#from interface import Interface

game = GameLogic()

#class CLI(Interface):
class CLI:
    def __init__(self):
        self.state = GameState()
        self.state.dice = "auto"
        #self.state.dice = "manual"

    def loop(self):
        while True:
            self.get_test_input()
            if self.state.category != "misc":
                self.get_mod()
            if self.state.dice == "manual":
                self.get_dice()
            self.state = game.test(self.state)
            self.show_result()
            self.get_save_choice()
            if self.state.save:
                game.save_to_csv(self.state)
            self.reset()

    def reset(self):
#        game.reset()
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

    def get_test_input(self):
        self.state.first_input = input('Enter name of attr, skill, spell ("misc" for misc test): ').lower()
        if self.state.first_input in ("exit", "quit"):
            raise SystemExit

        pattern1 = "^(\d+)[d,D](\d+)$" # 3d20 -> 3, 20
        pattern2 = "^(\d+)[d,D](\d+)\+(\d+)$" # 8d3+4 -> 8, 3, 4
        pattern3 = "^(\d+)[d,D](\d+)-(\d+)$" # 8d3-4 -> 8, 3, 4

        match1 = re.match(pattern1, self.state.first_input)
        if match1:
            self.state.category = "misc"
            self.state.misc = (int(match1.groups()[0]), int(match1.groups()[1]))
            self.state.mod = 0

        match2 = re.match(pattern2, self.state.first_input)
        if match2:
            self.state.category = "misc"
            self.state.misc = (int(match2.groups()[0]), int(match2.groups()[1]))
            self.state.mod = int(match2.groups()[2])

        match3 = re.match(pattern3, self.state.first_input)
        if match3:
            self.state.category = "misc"
            self.state.misc = (int(match3.groups()[0]), int(match3.groups()[1]))
            self.state.mod = int(match3.groups()[2]) * -1
#        elif self.state.first_input == "misc":
#            self.state.category = "misc"
#            self.get_misc_input()
#        else:
        if self.state.category != "misc":
            self.state = game.autocomplete(self.state)
            if not self.state.option_list:
                self.display_message("No matches found")
                self.reset()
            else:
                self.get_selection()

    def get_misc_input(self):
        dice_pattern = '(\d*)d(\d*)' # two integers separated by the letter 'd', match both those integers
        mod_pattern = '-?\d*'
        while True:
            choice  = input("Dice type and count [e.g. 4d6]: ")
            match = re.match(dice_pattern, choice)
            if match:
                v1 = int(match.groups()[0])
                v2 = int(match.groups()[1])
                self.state.misc = (v1, v2)
                break

        self.get_mod()

    def get_selection(self):
        pattern = '\d*'
        print("Character entries fitting input:")
        for index, option in enumerate(self.state.option_list):
            print("\t{0}: {1} ({2})".format(str(index+1), option[0], option[1].capitalize()))

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
        pattern = '-?\d*'
        while True:
            mod_input = input("Modifier: ")
            if mod_input == '':
                return 0
            if re.match(pattern, mod_input):
                self.state.mod = int(mod_input)
                break
            else:
                print("Invalid")

        print("self.state.mod: " + repr(self.state.mod))

    def display_message(self, text):
        print(text)

    def show_result(self):
        if not self.state:
            print("empty")
            return
        if self.state.category == "attr":
            outstring = (f"\tTested attribute: {self.state.name}\n"
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

    def get_dice(self):
        pattern = "\d+"

        if self.state.category == "attr":
            dice_count = 1
        elif self.state.category in ("skill", "spell"):
            dice_count = 3

        while True:
            outlist = []
            prompt_string = "Input {0} dice values, separated by whitespace: ".format(str(dice_count))
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
    while True:
        interface.loop()
