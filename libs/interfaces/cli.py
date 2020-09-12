""" module that holds the CLI class """
import re

class CLI: # pylint: disable=too-few-public-methods
    """ command line interface, communicates with GameLogic """
    def __init__(self, game, state, configs, lang):
        """ input: game:GameLogic
                   state:GameState
                   configs:dict, config file entries """
        self._game = game
        self._state = state
        self._lang = lang
        self._state.dice = configs["dice"]

    def loop(self):
        """ this method is executed by main.py and will run until "quit" or
        "exit" are typed in as hero input """
        while True:
            print(self._lang["roll_nr"] + str(self._state.counter))
            # get hero file
            self._get_hero()

            # get test input
            self._state.test_input = input(self._lang["input"]).lower()
            # check for misc dice sum, then match with hero entries
            self._state = self._game.match_test_input(self._state)

            if self._state.option_list:
                 # ask user to select one of the matching entries
                self._get_selection()
            elif self._state.selection is None:
                # no matching entries found
                print(self._lang["no_hero_match"])
                continue

            # some "advantage" entries have a value, other do not
            if self._state.selection.category == "advantage":
                if self._state.selection.value is None:
                    continue
            # no "special skill" entries have a value that can be tested, but
            # it's still helpful to have them displayed
            if self._state.selection.category == "special_skill":
                continue

            if self._state.selection.category != "misc":
            # for misc test, the modifier is put into the input prompt
                self._get_mod()
            if self._state.dice == "manual":
                self._get_manual_dice()
            self._state = self._game.test(self._state)
            self._show_result()
            if self._get_save_choice():
                self._game.save_to_csv(self._state)
            self._reset()

    def _reset(self):
        """ reset self._state """
        self._state.save = False
        self._state.attrs = None
        self._state.mod = None
        self._state.rolls = None
        self._state.result = None
        self._state.desc = None
        self._state.test_input = None
        self._state.option_list = None
        self._state.selection = None

    def _get_selection(self):
        """ shows the user all hero entries matching the user's input. then the
        user is asked for an integer input to choose one entry """

        # regex:
            # ^, $: match from start to end of string
            # \d+: match one or more integers
        pattern = "^\d+$" #pylint: disable=anomalous-backslash-in-string

        # display all matching hero entries with incrementing number in front
        print(self._lang["entry_match"])
        for index, value in enumerate(self._state.option_list):
            print("\t{0:3d}: {1} ({2})".format((index+1), value.name, self._lang[value.category]))

        # ask for selection, if it's valid use selected entry for current test
        while True:
            selection = input(self._lang["input_nr"])
            match = re.match(pattern, selection)
            if match and int(selection) in range(1, len(self._state.option_list) + 1):
                self._state.selection = self._state.option_list[int(selection) - 1]
                break
            print(self._lang["invalid"])

    def _get_hero(self):
        """ show the user all found hero xml files. then the user is asked for
        an integer input to choose one hero """

        # regex:
            # ^, $: match from start to end of string
            # \d+: match one or more integers
        pattern = "^\d+$" #pylint: disable=anomalous-backslash-in-string

        hero_options = self._game.get_hero_list()
        # display all matching hero files with incrementing number in front
        while True:
            print(self._lang["heroes"])
            for index, value in enumerate(hero_options):
                print("\t{0}: {1}".format(str(index + 1), value))

            # ask for selection, if it's valid use selected hero for current test
            hero_input = input(self._lang["input_nr"])

            # check if user wants to exit
            if hero_input.lower() in ("exit", "quit"):
                raise SystemExit

            match = re.match(pattern, hero_input)
            if match and int(hero_input) in range(1, len(hero_options) + 1):
                self._state.current_hero = hero_options[int(hero_input) - 1]
                break
            print(self._lang["invalid"])

    def _get_mod(self):
        """ ask user for integer (positive or negative). empty string is interpreted as zero. """

        # regex:
            # ^, $: match from start to end of string
            # -?: 0 or 1 minus sign
            # \d+: match one or more integers
        pattern = "^-?\d+$" #pylint: disable=anomalous-backslash-in-string

        while True:
            mod_input = input(self._lang["mod"])
            if mod_input == '':
                self._state.mod = 0
                break

            match = re.match(pattern, mod_input)
            if match:
                self._state.mod = int(mod_input)
                break

            print(self._lang["invalid"])

    @staticmethod
    def _display_message(text):
        """ function to print text to screen, in case the string has to be
        transformed before being printed
        input: text:str, text to be printed """
        print(text)

    def _show_result(self):
        """ create output string based on the test category and print it """
        format_dict = {"attr": self._format_attr_result,
                       "fight_talent": self._format_attr_result,
                       "advantage": self._format_attr_result,
                       "skill": self._format_skill_result,
                       "spell": self._format_skill_result,
                       "misc": self._format_misc_result}

        outstring = format_dict[self._state.selection.category]()

        print(outstring)

    def _format_attr_result(self):
        """ format attr and fight talent test results
        output: outstring:str """

        outstr = ""
        outstr += "\t" + self._lang["test_hero"] + self._state.current_hero + "\n"

        if self._state.selection.category == "attr":
            outstr += "\t" + self._lang["test_attr"] + self._state.selection.name + "\n"
        elif self._state.selection.category == "fight_talent":
            outstr += "\t" + self._lang["test_fight"] + self._state.selection.name + "\n"
        outstr += "\t" + self._lang["test_value"] + str(self._state.selection.value) + "\n"
        outstr += "\t" + self._lang["test_mod"] + str(self._state.mod) + "\n"
        outstr += "\t" + self._lang["test_1dice"] + str(self._state.rolls[0]) + "\n"
        outstr += "\t" + self._lang["test_result"] + str(self._state.result)
        return outstr

    def _format_skill_result(self):
        """ format skill and spell test results
        output: outstring:str """
        # if the modifier changes the skill value to negative, all tested
        # attributes have to show their modified value too
        if self._state.mod + self._state.selection.value < 0:
            modified = str(self._state.selection.value + self._state.mod)
            value_string = str(self._state.selection.value) + " -> " + modified
            attrs_list = [i.abbr + '(' + str(i.value) + "->" + str(i.modified) + ')'\
                           for _, i in enumerate(self._state.attrs)]
        else:
            attrs_list = [i.abbr + '(' + str(i.value) + ')' \
                           for _, i in enumerate(self._state.attrs)]
            value_string = str(self._state.selection.value)

        # join lists to strings
        attrs_string = ", ".join(map(str, attrs_list))

        remaining_list = [i.remaining for _, i in enumerate(self._state.attrs)]
        remaining_string = ", ".join(map(str, remaining_list))

        dice_string = ", ".join(map(str, self._state.rolls))

        outstr = ""
        outstr += "\t" + self._lang["test_hero"] + self._state.current_hero + "\n"
        if self._state.selection.category == "skill":
            outstr += "\t" + self._lang["test_skill"] + self._state.selection.name + "\n"
        elif self._state.selection.category == "spell":
            outstr += "\t" + self._lang["test_spell"] + self._state.selection.name + "\n"
        outstr += "\t" + self._lang["test_attrs"] + attrs_string + "\n"
        outstr += "\t" + self._lang["test_value"] + value_string + "\n"
        outstr += "\t" + self._lang["test_mod"] + str(self._state.mod) + "\n"
        outstr += "\t" + self._lang["test_dice"] + dice_string + "\n"
        outstr += "\t" + self._lang["test_remaining"] + remaining_string + "\n"
        outstr += "\t" + self._lang["test_result"] + str(self._state.result)
        return outstr

    def _format_misc_result(self):
        """ format misc test results
        output: outstring:str """

        dice_string = ", ".join(map(str, self._state.rolls))

        outstr = ""
        outstr += "\t" + self._lang["dice_count"] + str(self._state.selection.dice_count) + "\n"
        outstr += "\t" + self._lang["dice_eyes"] + str(self._state.selection.dice_eyes) + "\n"
        outstr += "\t" + self._lang["test_mod"] + str(self._state.mod) + "\n"
        outstr += "\t" + self._lang["test_dice"] + dice_string + "\n"
        outstr += "\t" + self._lang["dice_sum"] + str(self._state.result)

        return outstr

    def _get_save_choice(self):
        """ ask user if current test should be saved in csv file
        output: self._state.save:bool, True if it should be saved """

        desc = input(self._lang["desc"])
        if desc.lower() == self._lang["no"]:
            self._state.save = False
        else:
            self._state.save = True
            self._state.desc = desc

        return self._state.save

    def _get_manual_dice(self):
        """ ask user for number of integers, check if the input fits the
        current test and save them in the GameState """

        if self._state.selection.category in ("attr", "fight_talent", "advantage"):
            prompt_string = self._lang["input_1"]
        elif self._state.selection.category in ("skill", "spell"):
            prompt_string = self._lang["input_many"]
        elif self._state.selection.category == "misc":
            dice_count = self._state.selection.dice_count
            prompt_string = self._lang["input_many"]
            prompt_string = prompt_string.replace("3", str(dice_count))

        while True:
            input_string = input(prompt_string)

            self._state = self._game.match_manual_dice(self._state, input_string)

            if self._state.rolls is None:
                print(self._lang["invalid"])
            else:
                break
