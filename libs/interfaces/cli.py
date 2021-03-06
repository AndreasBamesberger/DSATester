""" file that holds the CLI class """
import re


class CLI:
    """
    Command line interface, communicates with GameLogic

    ...

    Attributes
    ---------
    _game: class libs.backend.dsa_game.GameLogic
        instance of the GameLogic class, does all the DSA game mechanics
    _state: class libs.backend.dsa_game.GameState
        contains user input, selected test, rolls, result
    _lang: dict
        dictionary holding all strings that will be printed

    Methods
    ------

    loop():
        Executed by main.py and will run until "quit" or "exit" are typed in as
        input or an error occurs.
    reset():
        Reset self._state.
    _get_selection():
        Shows the user all hero entries matching the user's input. Then the
        user is asked for an integer input to choose one entry.
    _get_hero():
        Show the user all found hero xml files. Then the user is asked for
        an integer input to choose one hero.
    _get_mod():
        Ask user for integer (positive or negative). Empty string is
        interpreted as zero.
    _display_message(text):
        Function to print text to screen, in case the string has to be
        transformed before being printed.
    _show_result():
        Create output string based on the test category and print it.
    _format_attr_result():
        Format attr and fight talent test results.
    _format_skill_result():
        Format skill and spell test results.
    _format_misc_result():
        Format misc test results.
    _get_save_choice():
        Ask user if current test should be saved in csv file.
    _get_manual_dice():
        Ask user for number of integers, check if the input fits the current
        test and save them in the GameState.
    """

    def __init__(self, game, state, configs, lang):
        """
        Parameters:
            game (libs.backend.dsa_game.GameLogic): DSA game mechanics

            state (libs.backend.dsa_game.GameState): contains user input,
            matching and selected hero entries, rolls, result

            configs (dict): user input from config file

            lang (dict): holds all strings that will be printed
        """
        self._game = game
        self._state = state
        self._lang = lang
        self._state.dice = configs["dice"]

    def loop(self):
        """
        This method is executed by main.py and will run until "quit" or
        "exit" are typed in as input or an error occurs
        """
        while True:
            print(self._lang["roll_nr"] + str(self._state.counter))
            self._get_hero()

            self._state.test_input = input(self._lang["input"]).lower()
            self._state = self._game.match_test_input(self._state)

            if self._state.option_list:
                self._get_selection()

            if self._state.selection is None:
                print(self._lang["no_hero_match"])
                continue

            if self._state.selection.category == "advantage":
                if self._state.selection.value is None:
                    continue
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
            self.reset()

    def reset(self):
        """
        Reset self._state
        """
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
        """
        Shows the user all hero entries matching the user's input. Then the
        user is asked for an integer input to choose one entry.
        """

        # regex:
        # ^, $: match from start to end of string
        # \d+: match one or more integers
        pattern = r"^\d+$"

        # display all matching hero entries with incrementing number in front
        print(self._lang["entry_match"])
        for index, value in enumerate(self._state.option_list):
            print("\t{0:3d}: {1} ({2})".format((index + 1), value.name,
                                               self._lang[value.category]))

        # ask for selection, if it's valid use selected entry for current test
        while True:
            selection = input(self._lang["input_nr"])
            match = re.match(pattern, selection)
            if match and int(selection) in range(1, len(
                    self._state.option_list) + 1):
                self._state.selection = self._state.option_list[
                    int(selection) - 1]
                break
            print(self._lang["invalid"])

    def _get_hero(self):
        """
        Show the user all found hero xml files. Then the user is asked for
        an integer input to choose one hero.
        """

        # regex:
        # ^, $: match from start to end of string
        # \d+: match one or more integers
        pattern = r"^\d+$"

        hero_options = self._game.get_hero_list()
        # display all matching hero files with incrementing number in front
        while True:
            print(self._lang["heroes"])
            for index, value in enumerate(hero_options):
                print("\t{0}: {1}".format(str(index + 1), value))

            # ask for selection, if it's valid use selected hero for current
            # test
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
        """
        Ask user for integer (positive or negative). Empty string is
        interpreted as zero.
        """

        # regex:
        # ^, $: match from start to end of string
        # -?: 0 or 1 minus sign
        # \d+: match one or more integers
        pattern = r"^-?\d+$"

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
        """
        Function to print text to screen, in case the string has to be
        transformed before being printed.

        Parameters:
            text (str): text to be printed
        """

        print(text)

    def _show_result(self):
        """
        Create output string based on the test category and print it.
        """
        format_dict = {"attr": self._format_attr_result,
                       "fight_talent": self._format_attr_result,
                       "advantage": self._format_attr_result,
                       "skill": self._format_skill_result,
                       "spell": self._format_skill_result,
                       "misc": self._format_misc_result}

        out_string = format_dict[self._state.selection.category]()

        print(out_string)

    def _format_attr_result(self):
        """
        Format attr and fight talent test results

        Returns:
            out_str (str)
        """

        out_str = ""
        out_str += "\t" + self._lang[
            "test_hero"] + self._state.current_hero + "\n"

        if self._state.selection.category == "attr":
            out_str += "\t" + self._lang[
                "test_attr"] + self._state.selection.name + "\n"
        elif self._state.selection.category == "fight_talent":
            out_str += "\t" + self._lang[
                "test_fight"] + self._state.selection.name + "\n"
        out_str += "\t" + self._lang["test_value"] + str(
            self._state.selection.value) + "\n"
        out_str += "\t" + self._lang["test_mod"] + str(self._state.mod) + "\n"
        out_str += "\t" + self._lang["test_1dice"] + str(
            self._state.rolls[0]) + "\n"
        out_str += "\t" + self._lang["test_result"] + str(self._state.result)
        return out_str

    def _format_skill_result(self):
        """
        Format skill and spell test results

        Returns:
            out_str (str)
        """
        # if the modifier changes the skill value to negative, all tested
        # attributes have to show their modified value too
        if self._state.mod + self._state.selection.value < 0:
            modified = str(self._state.selection.value + self._state.mod)
            value_string = str(self._state.selection.value) + " -> " + modified
            attrs_list = [
                i.abbr + '(' + str(i.value) + "->" + str(i.modified) + ')'
                for _, i in enumerate(self._state.attrs)]
        else:
            attrs_list = [i.abbr + '(' + str(i.value) + ')'
                          for _, i in enumerate(self._state.attrs)]
            value_string = str(self._state.selection.value)

        # join lists to strings
        attrs_string = ", ".join(map(str, attrs_list))

        remaining_list = [i.remaining for _, i in enumerate(self._state.attrs)]
        remaining_string = ", ".join(map(str, remaining_list))

        dice_string = ", ".join(map(str, self._state.rolls))

        out_str = ""
        out_str += "\t" + self._lang[
            "test_hero"] + self._state.current_hero + "\n"
        if self._state.selection.category == "skill":
            out_str += "\t" + self._lang[
                "test_skill"] + self._state.selection.name + "\n"
        elif self._state.selection.category == "spell":
            out_str += "\t" + self._lang[
                "test_spell"] + self._state.selection.name + "\n"
        out_str += "\t" + self._lang["test_attrs"] + attrs_string + "\n"
        out_str += "\t" + self._lang["test_value"] + value_string + "\n"
        out_str += "\t" + self._lang["test_mod"] + str(self._state.mod) + "\n"
        out_str += "\t" + self._lang["test_dice"] + dice_string + "\n"
        out_str += "\t" + self._lang["test_remaining"] + remaining_string + "\n"
        out_str += "\t" + self._lang["test_result"] + str(self._state.result)
        return out_str

    def _format_misc_result(self):
        """
        Format misc test results

        Returns:
            out_str (str)
        """

        dice_string = ", ".join(map(str, self._state.rolls))

        out_str = ""
        out_str += "\t" + self._lang["dice_count"] + str(
            self._state.selection.dice_count) + "\n"
        out_str += "\t" + self._lang["dice_eyes"] + str(
            self._state.selection.dice_eyes) + "\n"
        out_str += "\t" + self._lang["test_mod"] + str(self._state.mod) + "\n"
        out_str += "\t" + self._lang["test_dice"] + dice_string + "\n"
        out_str += "\t" + self._lang["dice_sum"] + str(self._state.result)

        return out_str

    def _get_save_choice(self):
        """ Ask user if current test should be saved in csv file.

        Returns:
            self._state.save (bool): True if it should be saved
        """

        desc = input(self._lang["desc"])
        if desc.lower() == self._lang["no"]:
            self._state.save = False
        else:
            self._state.save = True
            self._state.desc = desc

        return self._state.save

    def _get_manual_dice(self):
        """
        Ask user for number of integers, check if the input fits the
        current test and save them in the GameState
        """
        prompt_string = None

        if self._state.selection.category in ("attr",
                                              "fight_talent", "advantage"):
            prompt_string = self._lang["input_1"]
        elif self._state.selection.category in ("skill", "spell"):
            prompt_string = self._lang["input_many"]
        elif self._state.selection.category == "misc":
            dice_count = self._state.selection.dice_count
            prompt_string = self._lang["input_many"]
            prompt_string = prompt_string.replace("3", str(dice_count))

        while True:
            input_string = input(prompt_string)

            self._state = self._game.match_manual_dice(self._state,
                                                       input_string)

            if self._state.rolls is None:
                print(self._lang["invalid"])
            else:
                break
