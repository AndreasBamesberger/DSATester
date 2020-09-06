""" file that holds the CLI class """
import re

class CLI:
    """ command line interface, communicates with GameLogic """
    def __init__(self, game, state, configs, lang):
        """ input: game:GameLogic
                   state:GameState
                   configs:dict, config file entries """
        self.game = game
        self.state = state
        self.lang = lang
        self.state.dice = configs["dice"]

    def loop(self):
        """ this method is executed by main.py and will run until "quit" or
        "exit" are typed in as input or an error occurs """
        while True:
#            print("Roll #" + str(self.state.counter))
            print(self.lang["roll_nr"] + str(self.state.counter))
            self.get_hero()

#            self.state.test_input = input('Input: ').lower()
            self.state.test_input = input(self.lang["input"]).lower()
            self.state = self.game.match_test_input(self.state)

            if self.state.option_list:
                self.get_selection()
            elif self.state.category != "misc":
#                print("No matching entries found")
                print(self.lang["no_hero_match"])
                continue

            if self.state.category is not None:
                if self.state.category != "misc":
                # for misc test, the modifier is put into the input prompt
                    self.get_mod()
                if self.state.dice == "manual":
                    self.get_manual_dice()
                self.state = self.game.test(self.state)
                self.show_result()
                if self.get_save_choice():
                    self.game.save_to_csv(self.state)
            self.reset()

    def reset(self):
        """ reset self.state """
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
        self.state.test_input = None
        self.state.option_list = None
        self.state.selection = None

    def get_selection(self):
        """ shows the user all hero entries matching the user's input. then the
        user is asked for an integer input to choose one entry """

        # regex:
            # ^, $: match from start to end of string
            # \d+: match one or more integers
        pattern = "^\d+$" #pylint: disable=anomalous-backslash-in-string

        # display all matching hero entries with incrementing number in front
#        print("Character entries fitting input:")
        print(self.lang["entry_match"])
        for index, option in enumerate(self.state.option_list):
            print("\t{0:3d}: {1}".format((index+1), option[0]))

        # ask for selection, if it's valid use selected entry for current test
        while True:
#            selection = input("Enter number: ")
            selection = input(self.lang["input_nr"])
            match = re.match(pattern, selection)
            if match and int(selection) in range(1, len(self.state.option_list) + 1):
                self.state.selection = self.state.option_list[int(selection) - 1]
                self.state.name = self.state.option_list[int(selection) -1][0]
                self.state.category = self.state.option_list[int(selection) -1][1]
                break
#            print("Invalid input, try again")
            print(self.lang["invalid"])

    def get_hero(self):
        """ show the user all found hero xml files. then the user is asked for
        an integer input to choose one hero """

        # regex:
            # ^, $: match from start to end of string
            # \d+: match one or more integers
        pattern = "^\d+$" #pylint: disable=anomalous-backslash-in-string

        hero_options = self.game.get_hero_list()
        # display all matching hero files with incrementing number in front
        while True:
#            print("Available heroes: ")
            print(self.lang["heroes"])
            for index, value in enumerate(hero_options):
                print("\t{0}: {1}".format(str(index + 1), value))

            # ask for selection, if it's valid use selected hero for current test
#            hero_input = input("Enter number: ")
            hero_input = input(self.lang["input_nr"])

            # check if user wants to exit
            if hero_input.lower() in ("exit", "quit"):
                raise SystemExit

            match = re.match(pattern, hero_input)
            if match and int(hero_input) in range(1, len(hero_options) + 1):
                self.state.current_hero = hero_options[int(hero_input) - 1]
                break
#            print("invalid input, try again")
            print(self.lang["invalid"])

    def get_mod(self):
        """ ask user for integer (positive or negative). empty string is interpreted as zero. """

        # regex:
            # ^, $: match from start to end of string
            # -?: 0 or 1 minus sign
            # \d+: match one or more integers
        pattern = "^-?\d+$" #pylint: disable=anomalous-backslash-in-string

        while True:
#            mod_input = input("Modifier: ")
            mod_input = input(self.lang["mod"])
            if mod_input == '':
                self.state.mod = 0
                break

            match = re.match(pattern, mod_input)
            if match:
                self.state.mod = int(mod_input)
                break

#            print("Invalid")
            print(self.lang["invalid"])

    @staticmethod
    def display_message(text):
        """ function to print text to screen, in case the string has to be
        transformed before being printed
        input: text:str, text to be printed """
        print(text)

    def show_result(self):
        """ create output string based on the test category and print it """
        format_dict = {"attr": self.format_attr_result,
                       "fight_talent": self.format_attr_result,
                       "skill": self.format_skill_result,
                       "spell": self.format_skill_result,
                       "misc": self.format_misc_result}

        outstring = format_dict[self.state.category]()

        print(outstring)

    def format_attr_result(self):
        """ format attr and fight talent test results
        output: outstring:str """

        outstr = ""
        outstr += "\t" + self.lang["test_hero"] + self.state.current_hero + "\n"

        if self.state.category == "attr":
            outstr += "\t" + self.lang["test_attr"] + self.state.name + "\n"
        elif self.state.category == "fight_talent":
            outstr += "\t" + self.lang["test_fight"] + self.state.name + "\n"
        outstr += "\t" + self.lang["test_value"] + str(self.state.value) + "\n"
        outstr += "\t" + self.lang["test_mod"] + str(self.state.mod) + "\n"
        outstr += "\t" + self.lang["test_1dice"] + str(self.state.rolls[0]) + "\n"
        outstr += "\t" + self.lang["test_result"] + str(self.state.result)
        return outstr






#        if self.state.category == "attr":
#            tested = "attribute"
#        elif self.state.category == "fight_talent":
#            tested = "fight talent"
#        outstring = (f"\tTested hero: {self.state.current_hero}\n"
#                     f"\tTested {tested}: {self.state.name}\n"
#                     f"\tValue: {self.state.value}\n"
#                     f"\tModifier: {self.state.mod}\n"
#                     f"\tDice value: {self.state.rolls[0]}\n"
#                     f"\tResult: {self.state.result}")
#        return outstring

    def format_skill_result(self):
        """ format skill and spell test results
        output: outstring:str """
        # if the modifier changes the skill value to negative, all tested
        # attributes have to show their modified value too
        if self.state.mod + self.state.value < 0:
            value_string = str(self.state.value) + " -> " + str(self.state.value + self.state.mod)
            attrs_list = [i.abbr + '(' + str(i.value) + "->" + str(i.modified) + ')'\
                           for _, i in enumerate(self.state.attrs)]
        else:
            attrs_list = [i.abbr + '(' + str(i.value) + ')' \
                           for _, i in enumerate(self.state.attrs)]
            value_string = str(self.state.value)

        # join lists to strings
        attrs_string = ", ".join(map(str, attrs_list))

        remaining_list = [i.remaining for _, i in enumerate(self.state.attrs)]
        remaining_string = ", ".join(map(str, remaining_list))

        dice_string = ", ".join(map(str, self.state.rolls))

        outstr = ""
        outstr += "\t" + self.lang["test_hero"] + self.state.current_hero + "\n"
        if self.state.category == "skill":
            outstr += "\t" + self.lang["test_skill"] + self.state.name + "\n"
        elif self.state.category == "spell":
            outstr += "\t" + self.lang["test_spell"] + self.state.name + "\n"
        outstr += "\t" + self.lang["test_attrs"] + attrs_string + "\n"
        outstr += "\t" + self.lang["test_value"] + value_string + "\n"
        outstr += "\t" + self.lang["test_mod"] + str(self.state.mod) + "\n"
        outstr += "\t" + self.lang["test_dice"] + dice_string + "\n"
        outstr += "\t" + self.lang["test_remaining"] + remaining_string + "\n"
        outstr += "\t" + self.lang["test_result"] + str(self.state.result)
        return outstr


#        outstring = (f"\tTested hero: {self.state.current_hero}\n"
#                     f"\tTested {self.state.category}: {self.state.name}\n"
#                     f"\tRelated attributes: {attrs_string}\n"
#                     f"\tValue: {value_string}\n"
#                     f"\tModifier: {self.state.mod}\n"
#                     f"\tDice values: {dice_string}\n"
#                     f"\tAttribute values remaining: {remaining_string}\n"
#                     f"\tResult: {self.state.result}")
#        return outstring

    def format_misc_result(self):
        """ format misc test results
        output: outstring:str """

        dice_string = ", ".join(map(str, self.state.rolls))

        outstr = ""
        outstr += "\t" + self.lang["dice_count"] + str(self.state.misc.dice_count) + "\n"
        outstr += "\t" + self.lang["dice_eyes"] + str(self.state.misc.dice_eyes) + "\n"
        outstr += "\t" + self.lang["test_mod"] + str(self.state.mod) + "\n"
        outstr += "\t" + self.lang["test_dice"] + dice_string + "\n"
        outstr += "\t" + self.lang["dice_sum"] + str(self.state.result)

        return outstr



#        outstring = (f"\tDice count: {self.state.misc.dice_count}\n"
#                     f"\tDice eyes: {self.state.misc.dice_eyes}\n"
#                     f"\tModifier: {self.state.mod}\n"
#                     f"\tDice values: {dice_string}\n"
#                     f"\tSum: {self.state.result}")
#        return outstring

    def get_save_choice(self):
        """ ask user if current test should be saved in csv file
        output: self.state.save:bool, True if it should be saved """

#        desc = input('Type description to save roll, "no" to discard roll: ')
        desc = input(self.lang["desc"])
#        if desc.lower() == "no":
        if desc.lower() == self.lang["no"]:
            self.state.save = False
        else:
            self.state.save = True
            self.state.desc = desc

        return self.state.save

    def get_manual_dice(self):
        """ ask user for number of integers, check if the input fits the
        current test and save them in the GameState """

        if self.state.category in ("attr", "fight_talent"):
#            prompt_string = "Input 1 dice value: "
            prompt_string = self.lang["input_1"]
        elif self.state.category in ("skill", "spell"):
#            prompt_string = "Input 3 dice values, separated by whitespace: "
            prompt_string = self.lang["input_many"]
        elif self.state.category == "misc":
            dice_count = self.state.misc.dice_count
#            prompt_string = f"Input {dice_count} dice values, separated by whitespace: "
            prompt_string = self.lang["input_many"]
            prompt_string = prompt_string.replace("3", str(dice_count))

        while True:
            input_string = input(prompt_string)

            self.state = self.game.match_manual_dice(self.state, input_string)

            if self.state.rolls is None:
#                print("Wrong input, try again")
                print(self.lang["invalid"])
            else:
                break
