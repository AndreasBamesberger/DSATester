""" file that holds the GUI class """
import re
import tkinter as tk


class GUI:  # pylint: disable=too-few-public-methods, too-many-instance-attributes
    """ creates window using tkinter, communicates with GameLogic using the dataclass GameState"""

    def __init__(self, game, state, configs, lang):
        self._game = game
        self._state = state
        self._font = "none " + str(configs["font size"]) + " bold"
        self._scaling = configs["scaling"]
        self._width = configs["width"]
        self._height = configs["height"]
        self._state.dice = configs["dice"]
        self._lang = lang

        self._window = tk.Tk()
        # create a predefined window size so that the window doesn't start really tiny
        self._window.geometry(str(self._width) + 'x' + str(self._height))
        self._window.tk.call('tk', 'scaling', self._scaling)
        self._window.title("DSATester")
        self._window.configure(background="black")

        # variables to see if state has changed
        self._old_hero_input = None

        self._printable_options = None

        # these dicts hold all widgets shown in the GUI
        self._text_outputs = {}
        self._text_inputs = {}
        self._buttons = {}

        # these two inputs have to persist through window changes, so they are
        # created here. tk.StringVar is used to have an event when the strings
        # change

        # text input for hero input
        self._var_hero = tk.StringVar()
        self._var_hero.set('')
        self._perm_input_hero = tk.Entry(self._window,
                                         textvariable=self._var_hero,
                                         width=20, bg="white")
        self._perm_input_hero.grid(row=1, column=1, sticky=tk.W)

        # text input for test input
        self._var_input = tk.StringVar()
        self._var_input.set('')
        self._perm_input_test = tk.Entry(self._window,
                                         textvariable=self._var_input,
                                         width=20, bg="white")
        self._perm_input_test.grid(row=3, column=1, sticky=tk.W)

        self._var_hero.trace('w', self._trace_hero)
        self._var_input.trace('w', self._trace_test)

        self._setup_window()
        self._text_outputs["var_roll_nr"].configure(text=str(self._state.counter))

    def loop(self):
        """ gets executed by main.py, only executes the tkinter mainloop, every
        change is event driven """

        self._window.mainloop()

    def _reset(self):
        """ every variable of GameState back to None (save is set to False),
        deletes user input typed into the test input field """
        self._state.save = False
        self._state.attrs = None
        self._state.mod = None
        self._state.rolls = None
        self._state.result = None
        self._state.desc = None
        self._state.test_input = None
        self._state.option_list = None
        self._state.selection = None

        self._perm_input_test.delete(0, 'end')

    def _clear_screen(self):
        """ destroy all widgets except for roll number, test input field and
        hero input field """
        for key, field in self._text_outputs.items():
            if key == "var_roll_nr":
                continue
            field.destroy()

        for key, field in self._text_inputs.items():
            if key in ("test_input", "hero_input"):
                continue
            field.destroy()

        for key, field in self._buttons.items():
            field.destroy()

    def _get_hero(self):
        """ gets user input from hero input field, gets all available heroes as
        list from GameLogic and looks for a match. if only one hero matches the
        input, this hero is selected for the test """

        hero_input = self._text_inputs["hero_input"].get().lower()
        hero_options = self._game.get_hero_list()
        temp_list = []
        for _, value in enumerate(hero_options):
            if hero_input in value.lower():
                temp_list.append(value)
        if len(temp_list) == 1:
            self._state.current_hero = temp_list[0]

    def _get_mod(self, mod_string):
        """ use regular expression to read the modifier as an integer from the
        given string. no match or empty string is interpreted as 0. the matched
        integer is stored in GameState.mod
        input: mod_string:str, usually taken from modifier text input """

        # check for integer using regex
        # regex:
        # ^, $: match from start to end of string
        # -?: match 0 or 1 '-' signs
        # \d+: match 1 or more integers
        pattern = r"^-?\d+$"

        if re.match(pattern, mod_string):
            self._state.mod = int(mod_string)
        else:
            self._state.mod = 0

    def _button_test(self):
        """ method that gets executed when "test" button is clicked. calls
        GameLogic.test and displays result
        output: bool, False if test was not successful"""

        # misc test has modifier already typed in
        if self._state.selection.category in self._game.supported_tests:
            self._get_mod(self._text_inputs["mod"].get().lower())

        if self._state.dice == "manual":
            dice_string = self._text_inputs["dice_input"].get()
            self._state = self._game.match_manual_dice(self._state, dice_string)

        self._state = self._game.test(self._state)

        if self._state.result is None or self._state.rolls is None:
            return False

        rolls = ", ".join(map(str, self._state.rolls))

        if self._state.selection.category == "misc":
            self._text_outputs["var_rolls"].configure(text=str(rolls))
            self._text_outputs["var_result"].configure(text=str(self._state.result))

        if self._state.selection.category in ("attr", "fight_talent", "advantage"):
            if self._state.result is not None:
                self._text_outputs["var_tested"].configure(text=self._state.selection.name)
                self._text_outputs["var_value"].configure(text=str(self._state.selection.value))
                self._text_outputs["var_rolls"].configure(text=str(self._state.rolls[0]))
                self._text_outputs["var_result"].configure(text=str(self._state.result))

        if self._state.selection.category in ("skill", "spell"):
            if self._state.result is not None:
                # if a negative modifier changed the attribute values, this
                # change has to be shown on screen
                if self._state.mod + self._state.selection.value < 0:
                    # value string example "8 -> 5"
                    value_string = str(self._state.selection.value) + " -> " + \
                                   str(self._state.selection.value + self._state.mod)
                    # attrs_string example: "KL(14->12), IN(13->11), FF(12->10)"
                    attrs_list = [i.abbr + '(' + str(i.value) + "->" +
                                  str(i.modified) + ')' for _, i in enumerate(self._state.attrs)]
                else:
                    attrs_list = [i.abbr + '(' + str(i.value) + ')' for _, i in
                                  enumerate(self._state.attrs)]
                    value_string = str(self._state.selection.value)
                attrs_string = ", ".join(map(str, attrs_list))

                remaining_string = [i.remaining for _, i in enumerate(self._state.attrs)]
                remaining_string = ", ".join(map(str, remaining_string))

                self._text_outputs["var_tested"].configure(text=self._state.selection.name)
                self._text_outputs["var_tested_attrs"].configure(text=attrs_string)
                self._text_outputs["var_value"].configure(text=value_string)
                self._text_outputs["var_rolls"].configure(text=rolls)
                self._text_outputs["var_remaining"].configure(text=remaining_string)
                self._text_outputs["var_result"].configure(text=str(self._state.result))
        return True

    def _button_save(self):
        """ gets executed when "Test" button is clicked. runs
        GameLogic.save_to_csv(), then calls reset() and shows the updated
        current roll number and the selected hero file
        output: bool, False if there is no result to save """

        if self._state.result is None:
            return False
        self._state.save = True

        self._state.desc = self._text_inputs["desc"].get()

        self._state = self._game.save_to_csv(self._state)
        self._reset()
        self._clear_screen()
        self._setup_window()
        self._text_outputs["var_roll_nr"].configure(text=str(self._state.counter))
        self._text_outputs["var_matching_hero"].configure(text=self._state.current_hero)

        return True

    # tkinter trace method passes 3 arguments that are not used
    def _trace_hero(self, *_):
        """ gets executed when the hero text input changes. calls get_hero(),
        if hero selection has changed the screen is reset. the full hero file
        name is shown on screen
        input: a, b, c are all passed from the tkinter trace method but are not
        used """
        self._get_hero()
        if self._old_hero_input != self._state.current_hero:
            self._state.result = None
            self._state.selection = None
            self._clear_screen()
            self._setup_window()
            self._old_hero_input = self._state.current_hero
        self._text_outputs["var_matching_hero"].configure(text=self._state.current_hero)

    # tkinter trace method passes 3 arguments that are not used
    def _trace_test(self, *_):
        """ gets executed when the test text input changes. calls
        GameLogic.match_test_input(), if test selection has changed the screen
        is reset, then (based on the current test category) matching entries
        and the hero file name are shown
        input: a, b, c are all passed from the tkinter trace method but are not
        used """
        if self._state.current_hero is None:
            print("can't look up a test without a given hero file")
            return False

        self._state.selection = None

        self._state.test_input = self._text_inputs["test_input"].get().lower()

        # if no input
        if self._state.test_input == '':
            self._printable_options = ''
        else:
            self._state = self._game.match_test_input(self._state)

            # if input is no misc roll
            if self._state.selection is None:

                self._printable_options = []

                # print number of matching entries plus all matching entries below
                self._printable_options.append(str(len(self._state.option_list)) + " matches\n")

                for _, value in enumerate(self._state.option_list):
                    #                    option_string = "{0} ({1})".format(value.name, value.category)
                    option_string = "{0} ({1})".format(value.name, self._lang[value.category])
                    self._printable_options.append(option_string)

                # join list to string, each list element in new line
                self._printable_options = "\n".join(map(str, self._printable_options))

                # if just 1 entry matches, this entry is used for the current test
                if self._state.option_list and len(self._state.option_list) == 1:
                    self._state.selection = self._state.option_list[0]
                # if more than 1 entries match but 1 entry matches the user input
                # exactly, this entry is used for the current test
                elif self._state.option_list and self._state.test_input.lower() \
                        == self._state.option_list[0].name.lower():
                    self._state.selection = self._state.option_list[0]
                else:
                    self._state.selection = None

        self._clear_screen()
        self._setup_window()
        self._state.result = None

        self._text_outputs["var_matching_hero"].configure(text=self._state.current_hero)

        if self._state.selection is None:
            self._text_outputs["var_matching"].configure(text=self._printable_options)
            return False

        if self._state.selection.category != "misc":
            self._text_outputs["var_matching"].configure(text=self._state.selection.name)

        return True

    def _setup_window(self):  # pylint: disable=too-many-locals
        """ clear all widgets and, based on current test category, set up screen again """

        format_dict = {"none": self._setup_input_screen,
                       "special_skill": self._setup_special_skill_screen,
                       "attr": self._setup_attr_screen,
                       "fight_talent": self._setup_attr_screen,
                       "skill": self._setup_skill_screen,
                       "spell": self._setup_skill_screen,
                       "misc": self._setup_misc_screen}

        self._text_outputs.clear()
        self._text_inputs.clear()
        self._buttons.clear()

        if self._state.selection is None:
            key = "none"
        # if an advantage has a value it can be tested, otherwise just show
        # it like a special talent
        elif self._state.selection.category == "advantage":
            if self._state.selection.value is None:
                key = "special_skill"
            else:
                key = "attr"
        else:
            key = self._state.selection.category

        outputs, inputs, buttons = format_dict[key]()

        # set up outputs dictionary
        for _, value in enumerate(outputs):
            key = value[0]
            text = value[1]
            row = value[2]
            column = value[3]
            sticky = value[4]

            temp = tk.Label(self._window, text=text, bg="black", fg="white", font=self._font)
            temp.grid(row=row, column=column, sticky=sticky)

            self._text_outputs.update({key: temp})

        # set up inputs dictionary
        self._text_inputs.update({"hero_input": self._perm_input_hero})
        self._text_inputs.update({"test_input": self._perm_input_test})

        for _, value in enumerate(inputs):
            key = value[0]
            width = value[1]
            row = value[2]
            column = value[3]
            sticky = value[4]

            temp = tk.Entry(self._window, width=width, bg="white")
            temp.grid(row=row, column=column, sticky=sticky)

            self._text_inputs.update({key: temp})

        # set up button dictionary
        for _, value in enumerate(buttons):
            key = value[0]
            text = value[1]
            width = value[2]
            command = value[3]
            row = value[4]
            column = value[5]
            sticky = value[6]
            font = self._font

            temp = tk.Button(self._window, text=text, width=width, command=command, font=font)
            if sticky:
                temp.grid(row=row, column=column, sticky=sticky)
            else:
                temp.grid(row=row, column=column)

            self._buttons.update({key: temp})

    def _setup_input_screen(self):
        """ create tkinter widgets for the input screen, when
        GameState.category is None
        output: outputs:list
                inputs:list
                buttons:list """

        outputs = [["roll_nr", self._lang["roll_nr"], 0, 0, tk.E],
                   ["var_roll_nr", '', 0, 1, tk.W],
                   ["hero_prompt", self._lang["hero_file"], 1, 0, tk.E],
                   ["matching_hero", self._lang["hero_match"], 2, 0, tk.E],
                   ["var_matching_hero", '', 2, 1, tk.W],
                   ["input_prompt", self._lang["input"], 3, 0, tk.E],
                   ["matching", self._lang["matching"], 4, 0, tk.NE],
                   ["var_matching", '', 4, 1, tk.W]]

        inputs = []
        buttons = []

        return outputs, inputs, buttons

    def _setup_attr_screen(self):
        """ create tkinter widgets for the attribute test screen, when
        GameState.category is attr
        output: outputs:list
                inputs:list
                buttons:list """

        outputs = [["roll_nr", self._lang["roll_nr"], 0, 0, tk.E],
                   ["var_roll_nr", '', 0, 1, tk.W],
                   ["hero_prompt", self._lang["hero_file"], 1, 0, tk.E],
                   ["matching_hero", self._lang["hero_match"], 2, 0, tk.E],
                   ["var_matching_hero", '', 2, 1, tk.W],
                   ["input_prompt", self._lang["input"], 3, 0, tk.E],
                   ["matching", self._lang["matching"], 4, 0, tk.E],
                   ["var_matching", '', 4, 1, tk.W],
                   ["mod", self._lang["mod"], 5, 0, tk.E],
                   ["var_tested", '', 8, 1, tk.W],
                   ["value", self._lang["test_value"], 9, 0, tk.E],
                   ["var_value", '', 9, 1, tk.W],
                   ["rolls", self._lang["test_1dice"], 10, 0, tk.E],
                   ["var_rolls", '', 10, 1, tk.W],
                   ["result", self._lang["test_result"], 12, 0, tk.E],
                   ["var_result", '', 12, 1, tk.W],
                   ["desc", self._lang["gui_desc"], 13, 0, tk.E]]

        if self._state.selection.category == "attr":
            outputs.append(["tested", self._lang["test_attr"], 8, 0, tk.E])
        elif self._state.selection.category == "fight_talent":
            outputs.append(["tested", self._lang["test_fight"], 8, 0, tk.E])
        elif self._state.selection.category == "advantage":
            outputs.append(["tested", self._lang["test_adv"], 8, 0, tk.E])

        if self._state.dice == "manual":
            outputs.append(["dice_input", self._lang["gui_manual"], 6, 0, tk.E])

        # pressing the tab key while inside a text entry jumps to the next one
        # in the list. because of this, this list has to be created in the
        # order the entries appear on screen.
        inputs = list()
        inputs.append(["mod", 20, 5, 1, tk.W])

        if self._state.dice == "manual":
            inputs.append(["dice_input", 20, 6, 1, tk.W])

        inputs.append(["desc", 20, 13, 1, tk.W])

        buttons = [["test", self._lang["button_test"],
                    len(self._lang["button_test"]),
                    self._button_test, 7, 0, False],
                   ["save", self._lang["button_save"],
                    len(self._lang["button_save"]),
                    self._button_save, 14, 0, False]]

        return outputs, inputs, buttons

    def _setup_skill_screen(self):
        """ create tkinter widgets for skill/spell tests, when
        GameState.category is skill or spell
        output: outputs:list
                inputs:list
                buttons:list """

        outputs = [["roll_nr", self._lang["roll_nr"], 0, 0, tk.E],
                   ["var_roll_nr", '', 0, 1, tk.W],
                   ["hero_prompt", self._lang["hero_file"], 1, 0, tk.E],
                   ["matching_hero", self._lang["hero_match"], 2, 0, tk.E],
                   ["var_matching_hero", '', 2, 1, tk.W],
                   ["input_prompt", self._lang["input"], 3, 0, tk.E],
                   ["matching", self._lang["matching"], 4, 0, tk.E],
                   ["var_matching", '', 4, 1, tk.W],
                   ["mod", self._lang["mod"], 5, 0, tk.E],
                   ["var_tested", '', 8, 1, tk.W],
                   ["tested_attrs", self._lang["test_attrs"], 9, 0, tk.E],
                   ["var_tested_attrs", '', 9, 1, tk.W],
                   ["value", self._lang["test_value"], 10, 0, tk.E],
                   ["var_value", '', 10, 1, tk.W],
                   ["rolls", self._lang["test_dice"], 11, 0, tk.E],
                   ["var_rolls", '', 11, 1, tk.W],
                   ["remaining", self._lang["test_remaining"], 12, 0, tk.E],
                   ["var_remaining", '', 12, 1, tk.W],
                   ["result", self._lang["test_result"], 13, 0, tk.E],
                   ["var_result", '', 13, 1, tk.W],
                   ["desc", self._lang["gui_desc"], 14, 0, tk.E]]

        if self._state.dice == "manual":
            outputs.append(["dice_input", self._lang["gui_manual"], 6, 0, tk.E])

        if self._state.selection.category == "skill":
            outputs.append(["tested", self._lang["test_skill"], 8, 0, tk.E])
        elif self._state.selection.category == "spell":
            outputs.append(["tested", self._lang["test_spell"], 8, 0, tk.E])

        # pressing the tab key while inside a text entry jumps to the next one
        # in the list. because of this, this list has to be created in the
        # order the entries appear on screen.
        inputs = list()
        inputs.append(["mod", 20, 5, 1, tk.W])

        if self._state.dice == "manual":
            inputs.append(["dice_input", 20, 6, 1, tk.W])

        inputs.append(["desc", 20, 14, 1, tk.W])

        buttons = [["test", self._lang["button_test"],
                    len(self._lang["button_test"]),
                    self._button_test, 7, 0, False],
                   ["save", self._lang["button_save"],
                    len(self._lang["button_save"]),
                    self._button_save, 15, 0, False]]

        return outputs, inputs, buttons

    def _setup_misc_screen(self):
        """ create tkinter widgets for a misc dice sum test, when
        GameState.category is misc
        output: outputs:list
                inputs:list
                buttons:list """

        outputs = [["roll_nr", self._lang["roll_nr"], 0, 0, tk.E],
                   ["var_roll_nr", '', 0, 1, tk.W],
                   ["hero_prompt", self._lang["hero_file"], 1, 0, tk.E],
                   ["matching_hero", self._lang["hero_match"], 2, 0, tk.E],
                   ["var_matching_hero", '', 2, 1, tk.W],
                   ["input_prompt", self._lang["input"], 3, 0, tk.E],
                   ["rolls", self._lang["test_dice"], 6, 0, tk.E],
                   ["var_rolls", '', 6, 1, tk.W],
                   ["result", self._lang["dice_sum"], 7, 0, tk.E],
                   ["var_result", '', 7, 1, tk.W],
                   ["desc", self._lang["gui_desc"], 8, 0, tk.E]]

        if self._state.dice == "manual":
            outputs.append(["dice_input", self._lang["gui_manual"], 4, 0, tk.E])

        inputs = []
        if self._state.dice == "manual":
            inputs.append(["dice_input", 20, 4, 1, tk.W])
        inputs.append(["desc", 20, 8, 1, tk.W])

        buttons = [["test", self._lang["button_test"],
                    len(self._lang["button_test"]),
                    self._button_test, 5, 0, False],
                   ["save", self._lang["button_save"],
                    len(self._lang["button_save"]),
                    self._button_save, 9, 0, False]]

        return outputs, inputs, buttons

    def _setup_special_skill_screen(self):
        """ create tkinter widgets for the special skill test screen, when
        GameState.category is special_skill
        output: outputs:list
                inputs:list
                buttons:list """

        outputs = [["roll_nr", self._lang["roll_nr"], 0, 0, tk.E],
                   ["var_roll_nr", '', 0, 1, tk.W],
                   ["hero_prompt", self._lang["hero_file"], 1, 0, tk.E],
                   ["matching_hero", self._lang["hero_match"], 2, 0, tk.E],
                   ["var_matching_hero", '', 2, 1, tk.W],
                   ["input_prompt", self._lang["input"], 3, 0, tk.E],
                   ["matching", self._lang["matching"], 4, 0, tk.E],
                   ["var_matching", '', 4, 1, tk.W]]

        # pressing the tab key while inside a text entry jumps to the next one
        # in the list. because of this, this list has to be created in the
        # order the entries appear on screen.
        inputs = []
        buttons = []

        return outputs, inputs, buttons
