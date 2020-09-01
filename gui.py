""" file that holds the GUI class """
import re
import tkinter as tk

class GUI(): # pylint: disable=too-many-instance-attributes
    """ creates window using tkinter, communicates with GameLogic using the dataclass GameState"""
    def __init__(self, game, state, configs):
        self.game = game
        self.state = state
        self.font = "none " + str(configs["font size"]) + " bold"
        self.scaling = configs["scaling"]
        self.width = configs["width"]
        self.height = configs["height"]
        self.state.dice = configs["dice"]

        self.window = tk.Tk()
        # create a predefined window size so that the window doesn't start really tiny
        self.window.geometry(str(self.width) + 'x' + str(self.height))
        self.window.tk.call('tk', 'scaling', self.scaling)
        self.window.title("DSATester")
        self.window.configure(background="black")

        # variables to see if state has changed
        self.old_category = None
        self.old_input = None
        self.old_hero_input = None

        self.printable_options = None

        # these dicts hold all widgets shown in the GUI
        self.text_outputs = {}
        self.text_inputs = {}
        self.buttons = {}

        # these two inputs have to persist through window changes, so they are
        # created here. tk.StringVar is used to have an event when the strings
        # change

        # text input for hero input
        self.var_hero = tk.StringVar()
        self.var_hero.set('')
        self.perm_input_hero = tk.Entry(self.window, textvariable=self.var_hero, width=20, bg="white") # pylint: disable=line-too-long
        self.perm_input_hero.grid(row=1, column=1, sticky=tk.W)

        # text input for test input
        self.var_input = tk.StringVar()
        self.var_input.set('')
        self.perm_input_test = tk.Entry(self.window, textvariable=self.var_input, width=20, bg="white") # pylint: disable=line-too-long
        self.perm_input_test.grid(row=3, column=1, sticky=tk.W)

        self.var_hero.trace('w', self.trace_hero)
        self.var_input.trace('w', self.trace_test)

        self.setup_window()
        self.text_outputs["var_roll_nr"].configure(text=str(self.state.counter))

    def loop(self):
        """ gets executed by main.py, only executes the tkinter mainloop, every
        change is event driven """

        self.window.mainloop()

    def reset(self):
        """ every variable of GameState back to None (save is set to False),
        deletes user input typed into the test input field """
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

        self.perm_input_test.delete(0, 'end')

    def clear_screen(self):
        """ destroy all widgets except for roll number, test input field and
        hero input field """
        for key, field in self.text_outputs.items():
            if key == "var_roll_nr":
                continue
            field.destroy()

        for key, field in self.text_inputs.items():
            if key in ("test_input", "hero_input"):
                continue
            field.destroy()

        for key, field in self.buttons.items():
            field.destroy()

    def get_hero(self):
        """ gets user input from hero input field, gets all available heroes as
        list from GameLogic and looks for a match. if only one hero matches the
        input, this hero is selected for the test """

        hero_input = self.text_inputs["hero_input"].get().lower()
        hero_options = self.game.get_hero_list()
        templist = []
        for _, value in enumerate(hero_options):
            if hero_input in value.lower():
                templist.append(value)
        if len(templist) == 1:
            self.state.current_hero = templist[0]

    def get_mod(self, mod_string):
        """ use regular expression to read the modifier as an integer from the
        given string. no match or empty string is interpreted as 0. the matched
        integer is stored in GameState.mod
        input: mod_string:str, usually taken from modifier text input """

        # check for integer using regex
        # regex:
            # ^, $: match from start to end of string
            # -?: match 0 or 1 '-' signs
            # \d+: match 1 or more integers
        pattern = "^-?\d+$" #pylint: disable=anomalous-backslash-in-string

        if re.match(pattern, mod_string):
            self.state.mod = int(mod_string)
        else:
            self.state.mod = 0

    def get_manual_dice(self, rolls_string):
        """ use regular expression to read the dice input as integers from the
        given string and store them in GameState.rolls
        input: rolls_string:str, usually from manual dice text input """

        # attribute and fight talent tests take 1D20
        if self.state.category in ("attr", "fight_talent"):
            dice_count = 1
        # skill and spell tests take 3D20
        elif self.state.category in ("skill", "spell"):
            dice_count = 3
        # misc dice roll takes whatever was specified earlier
        elif self.state.category == "misc":
            dice_count = self.state.misc.dice_count

        # allow matches for "10, 4, 14" and "10 4 14"
        rolls_string = rolls_string.replace(',', '')
        rolls_list = rolls_string.split(' ')

        self.state = self.game.match_manual_dice(self.state, rolls_list)

        if len(self.state.rolls) != dice_count:
            self.state.rolls = None

    def button_test(self):
        """ method that gets executed when "test" button is clicked. calls
        GameLogic.test and displays result
        output: bool, False if test was not successful"""

        # misc test has modifier already typed in
        if self.state.category in ("attr", "skill", "spell", "fight_talent"):
            self.get_mod(self.text_inputs["mod"].get().lower())

        if self.state.dice == "manual":
            dice_string = self.text_inputs["dice_input"].get()
            self.state = self.game.match_manual_dice(self.state, dice_string)

        self.state = self.game.test(self.state)

        if self.state.result is None or self.state.rolls is None:
            return False

        rolls = ", ".join(map(str, self.state.rolls))

        if self.state.category == "misc":
            self.text_outputs["var_rolls"].configure(text=str(rolls))
            self.text_outputs["var_result"].configure(text=str(self.state.result))

        if self.state.category == "attr":
            if self.state.result is not None:
                self.text_outputs["var_tested"].configure(text=self.state.name)
                self.text_outputs["var_value"].configure(text=str(self.state.value))
                self.text_outputs["var_rolls"].configure(text=str(self.state.rolls[0]))
                self.text_outputs["var_result"].configure(text=str(self.state.result))

        if self.state.category == "fight_talent":
            if self.state.result is not None:
                self.text_outputs["var_tested"].configure(text=self.state.name)
                self.text_outputs["var_value"].configure(text=str(self.state.value))
                self.text_outputs["var_rolls"].configure(text=str(self.state.rolls[0]))
                self.text_outputs["var_result"].configure(text=str(self.state.result))

        if self.state.category in ("skill", "spell"):
            if self.state.result is not None:
                # if a negative modifier changed the attribute values, this
                # change has to be shown on screen
                if self.state.mod + self.state.value < 0:
                    # value string example "8 -> 5"
                    value_string = str(self.state.value) + " -> " + str(self.state.value + self.state.mod) # pylint: disable=line-too-long
                    # attrs_string example: "KL(14->12), IN(13->11), FF(12->10)"
                    attrs_string = [i.abbr + '(' + str(i.value) + "->" + str(i.modified) + ')' for _, i in enumerate(self.state.attrs)] # pylint: disable=line-too-long
                else:
                    attrs_string = [i.abbr + '(' + str(i.value) + ')' for _, i in enumerate(self.state.attrs)] # pylint: disable=line-too-long
                    value_string = str(self.state.value)
                attrs_string = ", ".join(map(str, attrs_string))

                remaining_string = [i.remaining for _, i in enumerate(self.state.attrs)]
                remaining_string = ", ".join(map(str, remaining_string))

                self.text_outputs["var_tested"].configure(text=self.state.name)
                self.text_outputs["var_tested_attrs"].configure(text=attrs_string)
                self.text_outputs["var_value"].configure(text=value_string)
                self.text_outputs["var_rolls"].configure(text=rolls)
                self.text_outputs["var_remaining"].configure(text=remaining_string)
                self.text_outputs["var_result"].configure(text=str(self.state.result))
        return True

    def button_save(self):
        """ gets executed when "Test" button is clicked. runs
        GameLogic.save_to_csv(), then calls reset() and shows the updated
        current roll number and the selected hero file
        output: bool, False if there is no result to save """

        if self.state.result is None:
            return False
        self.state.save = True
        self.state = self.game.save_to_csv(self.state)
        self.reset()
        self.clear_screen()
        self.setup_window()
        self.text_outputs["var_roll_nr"].configure(text=str(self.state.counter))
        self.text_outputs["var_matching_hero"].configure(text=self.state.current_hero)

        return True

    def trace_hero(self, a=None, b=None, c=None): # pylint: disable=unused-argument, invalid-name
        """ gets executed when the hero text input changes. calls get_hero(),
        if hero selection has changed the screen is reset. the full hero file
        name is shown on screen
        input: a, b, c are all passed from the tkinter trace method but are not
        used """
        self.get_hero()
        if self.old_hero_input != self.state.current_hero:
            self.clear_screen()
            self.setup_window()
            self.state.result = None
            self.old_hero_input = self.state.current_hero
        self.text_outputs["var_matching_hero"].configure(text=self.state.current_hero)

    # tkinter trace method passes 3 arguments that are not used
    def trace_test(self, a=None, b=None, c=None): # pylint: disable=unused-argument, invalid-name
        """ gets executed when the test text input changes. calls
        GameLogic.match_test_input(), if test selection has changed the screen
        is reset, then (based on the current test category) matching entries
        and the hero file name are shown
        input: a, b, c are all passed from the tkinter trace method but are not
        used """
        if self.state.current_hero is None:
            print("can't look up a test without a given hero file")
            return False

        self.state.test_input = self.text_inputs["test_input"].get().lower()

        self.state = self.game.match_test_input(self.state)

        if self.state.test_input == '':
            self.state.category = None
            self.printable_options = ''
        elif self.state.category != "misc":
            self.printable_options = []

            # print number of matching entries plus all matching entries below
            self.printable_options.append(str(len(self.state.option_list)) + " matches\n")

            for _, value in enumerate(self.state.option_list):
                self.printable_options.append(value[0])

            # join list to string, each list element in new line
            self.printable_options = "\n".join(map(str, self.printable_options))

            # if just 1 entry matches, this entry is used for the current test
            if self.state.option_list and len(self.state.option_list) == 1:
                self.state.name = self.state.option_list[0][0]
                self.state.category = self.state.option_list[0][1]
            # if more than 1 entries match but 1 entry matches the user input
            # exactly, this entry is used for the current test
            elif self.state.option_list and self.state.test_input.lower() == self.state.option_list[0][0].lower(): # pylint: disable=line-too-long
                self.state.name = self.state.option_list[0][0]
                self.state.category = self.state.option_list[0][1]
            else:
                self.state.category = None
                self.state.name = None

        if self.old_category != self.state.category:
            self.clear_screen()
            self.setup_window()
            self.state.result = None
            self.old_category = self.state.category

        if self.state.category in ("attr", "skill", "spell", "fight_talent"):
            self.text_outputs["var_matching"].configure(text=self.state.name)
        elif self.state.category is None:
            self.text_outputs["var_matching"].configure(text=self.printable_options)

        self.text_outputs["var_matching_hero"].configure(text=self.state.current_hero)

        return True

    def setup_window(self):
        """ clear all widgets and, based on current test category, set up screen again """
        self.text_outputs.clear()
        self.text_inputs.clear()
        self.buttons.clear()

        if not self.state.category:
            outputs, inputs, buttons = self.setup_input_screen()

        elif self.state.category == "misc":
            outputs, inputs, buttons = self.setup_misc_screen()

        elif self.state.category == "attr":
            outputs, inputs, buttons = self.setup_attr_screen()

        elif self.state.category == "fight_talent":
            outputs, inputs, buttons = self.setup_fight_talent_screen()

        elif self.state.category in ("skill", "spell"):
            outputs, inputs, buttons = self.setup_skill_screen()

        # set up outputs dictionary
        for _, value in enumerate(outputs):
            key = value[0]
            text = value[1]
            row = value[2]
            column = value[3]
            sticky = value[4]

            temp = tk.Label(self.window, text=text, bg="black", fg="white", font=self.font)
            temp.grid(row=row, column=column, sticky=sticky)

            self.text_outputs.update({key: temp})

        # set up inputs dictionary
        self.text_inputs.update({"hero_input": self.perm_input_hero})
        self.text_inputs.update({"test_input": self.perm_input_test})

        for _, value in enumerate(inputs):
            key = value[0]
            width = value[1]
            row = value[2]
            column = value[3]
            sticky = value[4]

            temp = tk.Entry(self.window, width=width, bg="white")
            temp.grid(row=row, column=column, sticky=sticky)

            self.text_inputs.update({key: temp})

        # set up button dictionary
        for _, value in enumerate(buttons):
            key = value[0]
            text = value[1]
            width = value[2]
            command = value[3]
            row = value[4]
            column = value[5]
            sticky = value[6]
            font = self.font

            temp = tk.Button(self.window, text=text, width=width, command=command, font=font)
            if sticky:
                temp.grid(row=row, column=column, sticky=sticky)
            else:
                temp.grid(row=row, column=column)

            self.buttons.update({key: temp})

    @staticmethod
    def setup_input_screen():
        """ create tkinter widgets for the input screen, when
        GameState.category is None
        output: outputs:list
                inputs:list
                buttons:list """

        outputs = [["roll_nr", "Roll #", 0, 0, tk.E],
                   ["var_roll_nr", '', 0, 1, tk.W],
                   ["hero_prompt", "Hero file: ", 1, 0, tk.E],
                   ["matching_hero", "Matching hero: ", 2, 0, tk.E],
                   ["var_matching_hero", '', 2, 1, tk.W],
                   ["input_prompt", "Input: ", 3, 0, tk.E],
                   ["matching", "Matching: ", 4, 0, tk.NE],
                   ["var_matching", '', 4, 1, tk.W]]

        inputs = []
        buttons = []

        return outputs, inputs, buttons

    def setup_attr_screen(self):
        """ create tkinter widgets for the attribute test screen, when
        GameState.category is attr
        output: outputs:list
                inputs:list
                buttons:list """

        outputs = [["roll_nr", "Roll #", 0, 0, tk.E],
                   ["var_roll_nr", '', 0, 1, tk.W],
                   ["hero_prompt", "Hero file: ", 1, 0, tk.E],
                   ["matching_hero", "Matching hero: ", 2, 0, tk.E],
                   ["var_matching_hero", '', 2, 1, tk.W],
                   ["input_prompt", "Input: ", 3, 0, tk.E],
                   ["matching", "Matching: ", 4, 0, tk.E],
                   ["var_matching", '', 4, 1, tk.W],
                   ["mod", "Modifier: ", 5, 0, tk.E],
                   ["tested", "Tested attribute: ", 8, 0, tk.E],
                   ["var_tested", '', 8, 1, tk.W],
                   ["value", "Value: ", 9, 0, tk.E],
                   ["var_value", '', 9, 1, tk.W],
                   ["rolls", "Rolls: ", 10, 0, tk.E],
                   ["var_rolls", '', 10, 1, tk.W],
                   ["result", "Result: ", 12, 0, tk.E],
                   ["var_result", '', 12, 1, tk.W],
                   ["desc", "Description: ", 13, 0, tk.E]]

        if self.state.dice == "manual":
            outputs.append(["dice_input", "Manual dice input: ", 6, 0, tk.E])

        # pressing the tab key while inside a text entry jumps to the next one
        # in the list. because of this, this list has to be created in the
        # order the entries appear on screen.
        inputs = []
        inputs.append(["mod", 20, 5, 1, tk.W])

        if self.state.dice == "manual":
            inputs.append(["dice_input", 20, 6, 1, tk.W])

        inputs.append(["desc", 20, 13, 1, tk.W])


        buttons = [["test", "Test", 4, self.button_test, 7, 0, False],
                   ["save", "Save", 4, self.button_save, 14, 0, False]]

        return outputs, inputs, buttons

    def setup_fight_talent_screen(self):
        """ create tkinter widgets for the fight talent test, when
        GameState.category is fight_talent
        output: outputs:list
                inputs:list
                buttons:list """

        outputs = [["roll_nr", "Roll #", 0, 0, tk.E],
                   ["var_roll_nr", '', 0, 1, tk.W],
                   ["hero_prompt", "Hero file: ", 1, 0, tk.E],
                   ["matching_hero", "Matching hero: ", 2, 0, tk.E],
                   ["var_matching_hero", '', 2, 1, tk.W],
                   ["input_prompt", "Input: ", 3, 0, tk.E],
                   ["matching", "Matching: ", 4, 0, tk.E],
                   ["var_matching", '', 4, 1, tk.W],
                   ["mod", "Modifier: ", 5, 0, tk.E],
                   ["tested", "Tested fight talent: ", 8, 0, tk.E],
                   ["var_tested", '', 8, 1, tk.W],
                   ["value", "Value: ", 9, 0, tk.E],
                   ["var_value", '', 9, 1, tk.W],
                   ["rolls", "Rolls: ", 10, 0, tk.E],
                   ["var_rolls", '', 10, 1, tk.W],
                   ["result", "Result: ", 11, 0, tk.E],
                   ["var_result", '', 11, 1, tk.W],
                   ["desc", "Description: ", 12, 0, tk.E]]

        if self.state.dice == "manual":
            outputs.append(["dice_input", "Manual dice input: ", 6, 0, tk.E])

        # pressing the tab key while inside a text entry jumps to the next one
        # in the list. because of this, this list has to be created in the
        # order the entries appear on screen.
        inputs = []
        inputs.append(["mod", 20, 5, 1, tk.W])

        if self.state.dice == "manual":
            inputs.append(["dice_input", 20, 6, 1, tk.W])

        inputs.append(["desc", 20, 12, 1, tk.W])

        buttons = [["test", "Test", 4, self.button_test, 7, 0, False],
                   ["save", "Save", 4, self.button_save, 14, 0, False]]

        return outputs, inputs, buttons

    def setup_skill_screen(self):
        """ create tkinter widgets for skill/spell tests, when
        GameState.category is skill or spell
        output: outputs:list
                inputs:list
                buttons:list """

        outputs = [["roll_nr", "Roll #", 0, 0, tk.E],
                   ["var_roll_nr", '', 0, 1, tk.W],
                   ["hero_prompt", "Hero file: ", 1, 0, tk.E],
                   ["matching_hero", "Matching hero: ", 2, 0, tk.E],
                   ["var_matching_hero", '', 2, 1, tk.W],
                   ["input_prompt", "Input: ", 3, 0, tk.E],
                   ["matching", "Matching: ", 4, 0, tk.E],
                   ["var_matching", '', 4, 1, tk.W],
                   ["mod", "Modifier: ", 5, 0, tk.E],
                   ["tested", "Tested skill/spell: ", 8, 0, tk.E],
                   ["var_tested", '', 8, 1, tk.W],
                   ["tested_attrs", "Tested attributes: ", 9, 0, tk.E],
                   ["var_tested_attrs", '', 9, 1, tk.W],
                   ["value", "Value: ", 10, 0, tk.E],
                   ["var_value", '', 10, 1, tk.W],
                   ["rolls", "Rolls: ", 11, 0, tk.E],
                   ["var_rolls", '', 11, 1, tk.W],
                   ["remaining", "Attribute values remaining: ", 12, 0, tk.E],
                   ["var_remaining", '', 12, 1, tk.W],
                   ["result", "Result: ", 13, 0, tk.E],
                   ["var_result", '', 13, 1, tk.W],
                   ["desc", "Description: ", 14, 0, tk.E]]

        if self.state.dice == "manual":
            outputs.append(["dice_input", "Manual dice input: ", 6, 0, tk.E])

        # pressing the tab key while inside a text entry jumps to the next one
        # in the list. because of this, this list has to be created in the
        # order the entries appear on screen.
        inputs = []
        inputs.append(["mod", 20, 5, 1, tk.W])

        if self.state.dice == "manual":
            inputs.append(["dice_input", 20, 6, 1, tk.W])

        inputs.append(["desc", 20, 14, 1, tk.W])

        buttons = [["test", "Test", 4, self.button_test, 7, 0, False],
                   ["save", "Save", 4, self.button_save, 15, 0, False]]

        return outputs, inputs, buttons

    def setup_misc_screen(self):
        """ create tkinter widgets for a misc dice sum test, when
        GameState.category is misc
        output: outputs:list
                inputs:list
                buttons:list """

        outputs = [["roll_nr", "Roll #", 0, 0, tk.E],
                   ["var_roll_nr", '', 0, 1, tk.W],
                   ["hero_prompt", "Hero file: ", 1, 0, tk.E],
                   ["matching_hero", "Matching hero: ", 2, 0, tk.E],
                   ["var_matching_hero", '', 2, 1, tk.W],
                   ["input_prompt", "Input: ", 3, 0, tk.E],
                   ["rolls", "Rolls: ", 6, 0, tk.E],
                   ["var_rolls", '', 6, 1, tk.W],
                   ["result", "Result: ", 7, 0, tk.E],
                   ["var_result", '', 7, 1, tk.W],
                   ["desc", "Description: ", 8, 0, tk.E]]

        if self.state.dice == "manual":
            outputs.append(["dice_input", "Manual dice input: ", 4, 0, tk.E])

        inputs = []
        if self.state.dice == "manual":
            inputs.append(["dice_input", 20, 4, 1, tk.W])
        inputs.append(["desc", 20, 8, 1, tk.W])

        buttons = [["test", "Test", 4, self.button_test, 5, 0, False],
                   ["save", "Save", 4, self.button_save, 9, 0, False]]

        return outputs, inputs, buttons
