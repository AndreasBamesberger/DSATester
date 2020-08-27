""" creates window using tkinter, communicates with GameLogic through the dataclass GameState"""
import re
import tkinter as tk

class GUI():
    """ creates window using tkinter, communicates with GameLogic through the dataclass GameState"""
    def __init__(self, game, state, configs):
        self.game = game
        self.state = state
        self.font = "none " + str(configs["font size"]) + " bold"
        self.scaling = configs["scaling"]
        self.width = configs["width"]
        self.height = configs["height"]
        self.state.dice = configs["dice"]

        self.window = tk.Tk()
        self.window.geometry(str(self.width) + 'x' + str(self.height))
        self.window.tk.call('tk', 'scaling', self.scaling)
        self.window.title("DSA rng")
        self.window.configure(background="black")

        self.old_category = None
        self.old_input = None
        self.old_hero_input = None
        self.printable_options = None

        self.text_outputs = {}
        self.text_inputs = {}
        self.buttons = {}

        # text input for hero input
        self.var_hero = tk.StringVar()
        self.var_hero.set('')
        self.input_hero = tk.Entry(self.window, textvariable=self.var_hero, width=20, bg="white")
        self.input_hero.grid(row=1, column=1, sticky=tk.W)

        # text input for test input
        self.var_input = tk.StringVar()
        self.var_input.set('')
        self.input_test = tk.Entry(self.window, textvariable=self.var_input, width=20, bg="white")
        self.input_test.grid(row=3, column=1, sticky=tk.W)

        self.var_hero.trace('w', self.button_hero)
        self.var_input.trace('w', self.button_input)

        self.setup_window()
#        self.update()
        self.text_outputs["var_roll_nr"].configure(text=str(self.state.counter))

    def loop(self):
        """ gets executed by main.py, reads inputs, sends inputs to GameLogic,
        shows results in tkinter window """

        self.window.mainloop()
#        while True:
#            self.get_hero()
#            self.get_first_input()
#
#            if self.old_category != self.state.category:
#                self.clear_screen()
#                self.setup_window()
#                self.state.result = None
#                self.old_category = self.state.category
#
#            if self.old_hero_input != self.state.current_hero:
#                self.clear_screen()
#                self.setup_window()
#                self.state.result = None
#                self.old_hero_input = self.state.current_hero
#
#            self.text_outputs["var_roll_nr"].configure(text=str(self.state.counter))
#            self.text_outputs["var_matching_hero"].configure(text=self.state.current_hero)
#
#            if self.state.category in ("attr", "skill", "spell", "fight_talent"):
#                self.text_outputs["var_matching"].configure(text=self.state.name)
#                self.get_mod(self.text_inputs["mod"].get().lower())
#
#            if self.state.category:
#                self.state.desc = self.text_inputs["desc"].get()
#
#            if not self.state.category:
#                self.text_outputs["var_matching"].configure(text=self.printable_options)
#
#            self.update()

    def reset(self):
        """ every variable of GameState back to None (save is set to False),
        deletes user input typed into first input field """
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

        self.input_test.delete(0, 'end')

    def update(self):
        """ components of tk.mainloop """
        self.window.update_idletasks()
        self.window.update()

    def clear_screen(self):
        """ destroy all widgets except for roll number and input field """
        for key, field in self.text_outputs.items():
            if key == "var_roll_nr":
                continue
            field.destroy()

        for key, field in self.text_inputs.items():
            if key in ("first_input", "hero_input"):
                continue
            field.destroy()

        for key, field in self.buttons.items():
            field.destroy()

    def get_hero(self):
        hero_input = self.text_inputs["hero_input"].get().lower()
        hero_options = self.game.get_hero_list()
        templist = []
        for index, value in enumerate(hero_options):
            if hero_input in value:
                templist.append(value)
        if len(templist) == 1:
            self.state.current_hero = templist[0]


    def get_first_input(self):
        """ checks input for misc input regular expressions, if it matches sets
        test category to misc, else it sends input to game autocomplete to get
        matching entry. if just 1 entry matches then set this as current test
        """
        pattern1 = "^(\d+)[dDwW](\d+)$" # 3d20 -> 3, 20 #pylint: disable=anomalous-backslash-in-string
        pattern2 = "^(\d+)[dDwW](\d+)\+(\d+)$" # 8d3+4 -> 8, 3, 4 #pylint: disable=anomalous-backslash-in-string
        pattern3 = "^(\d+)[dDwW](\d+)-(\d+)$" # 8d3-4 -> 8, 3, 4 #pylint: disable=anomalous-backslash-in-string

        if self.state.current_hero is None:
            print("need to match a hero file first")
            return False

        self.state.first_input = self.text_inputs["first_input"].get().lower()

        if self.state.first_input != self.old_input:
            self.old_input = self.state.first_input
        else:
            return False

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

        if self.state.category and not match1 and not match2 and not match3:
            self.state.category = None

        if self.state.first_input == '':
            self.state.category = None
            self.printable_options = ''
        elif self.state.category != "misc":
            self.state = self.game.autocomplete(self.state)

            self.printable_options = []

            self.printable_options.append(str(len(self.state.option_list)) + " matches\n")

            for _, value in enumerate(self.state.option_list):
                self.printable_options.append(value[0])
#                if len(self.printable_options) > 5:
#                    break

            self.printable_options = "\n".join(map(str, self.printable_options))

            if self.state.option_list and len(self.state.option_list) == 1:
                self.state.name = self.state.option_list[0][0]
                self.state.category = self.state.option_list[0][1]
            elif self.state.option_list and self.state.first_input.lower() == self.state.option_list[0][0].lower():
                self.state.name = self.state.option_list[0][0]
                self.state.category = self.state.option_list[0][1]
            else:
                self.state.category = None
                self.state.name = None

    def get_mod(self, mod_string):
        """ use reg ex to get integer from input field. input = string from input field """
        pattern = "^-?\d+$" #pylint: disable=anomalous-backslash-in-string

        if re.match(pattern, mod_string):
            self.state.mod = int(mod_string)
        else:
            self.state.mod = 0

    def get_manual_dice(self, rolls_string):
        """ take manual dice input and save it into self.state.rolls """
        pattern = "\d+" #pylint: disable=anomalous-backslash-in-string
        outlist = []

        if self.state.category in ("attr", "fight_talent"):
            dice_count = 1
        elif self.state.category in ("skill", "spell"):
            dice_count = 3

        rolls_list = rolls_string.split(' ')

        for item in rolls_list:
            match = re.match(pattern, item)
            if match:
                if int(item) in range(1, 21):
                    outlist.append(int(item))

        self.state.rolls = outlist

        if len(self.state.rolls) != dice_count:
            self.state.rolls = None

    def setup_window(self):
        """ clear all widgets and, based on current test category, set up screen again """
        self.text_outputs.clear()
        self.text_inputs.clear()
        self.buttons.clear()
        if not self.state.category:
            self.setup_input_screen()

        elif self.state.category == "misc":
            self.setup_misc_screen()

        elif self.state.category == "attr":
            self.setup_attr_screen()

        elif self.state.category == "fight_talent":
            self.setup_fight_talent_screen()

        elif self.state.category in ("skill", "spell"):
            self.setup_skill_screen()

    def button_test(self):
        """ method that gets executed when "test" button is clicked. calls
        GameLogic.test and displays result """

        self.get_mod(self.text_inputs["mod"].get().lower())

        if self.state.dice == "manual":
            self.get_manual_dice(self.text_inputs["dice_input"].get())

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
                if self.state.mod + self.state.value < 0:
                    value_string = str(self.state.value) + " -> " + str(self.state.value + self.state.mod)
                    attrs_string = [i.abbr + '(' + str(i.value) + "->" + str(i.modified) + ')' for _, i in enumerate(self.state.attrs)]
                else:
                    attrs_string = [i.abbr + '(' + str(i.value) + ')' for _, i in enumerate(self.state.attrs)]
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

    def button_save(self):
        """ gets executed when "Test" button is clicked. runs
        GameLogic.save_to_csv and then calls reset """
        if self.state.result is None:
            return False
        self.state.save = True
        self.state = self.game.save_to_csv(self.state)
        self.reset()
        self.clear_screen()
        self.setup_window()
        self.text_outputs["var_roll_nr"].configure(text=str(self.state.counter))
        self.text_outputs["var_matching_hero"].configure(text=self.state.current_hero)

    # tkinter trace method passes 3 arguments that are not used
    def button_hero(self, a=None, b=None, c=None):
        self.get_hero()
        if self.old_hero_input != self.state.current_hero:
            self.clear_screen()
            self.setup_window()
            self.state.result = None
            self.old_hero_input = self.state.current_hero
        self.text_outputs["var_matching_hero"].configure(text=self.state.current_hero)

    # tkinter trace method passes 3 arguments that are not used
    def button_input(self, a=None, b=None, c=None):
        self.get_first_input()
        if self.old_category != self.state.category:
            self.clear_screen()
            self.setup_window()
            self.state.result = None
            self.old_category = self.state.category

        if self.state.category in ("attr", "skill", "spell", "fight_talent"):
            self.text_outputs["var_matching"].configure(text=self.state.name)
        else:
            self.text_outputs["var_matching"].configure(text=self.printable_options)

        self.text_outputs["var_matching_hero"].configure(text=self.state.current_hero)


    def setup_input_screen(self):
        """ create tkinter widgets """
        outputs = [["roll_nr", "Roll #", 0, 0, tk.E],
                   ["var_roll_nr", '', 0, 1, tk.W],
                   ["hero_prompt", "Hero file: ", 1, 0, tk.E],
                   ["matching_hero", "Matching hero: ", 2, 0, tk.E],
                   ["var_matching_hero", '', 2, 1, tk.W],
                   ["input_prompt", "Input: ", 3, 0, tk.E],
                   ["matching", "Matching: ", 4, 0, tk.NE],
                   ["var_matching", '', 4, 1, tk.W]]

        for _, value in enumerate(outputs):
            key = value[0]
            text = value[1]
            row = value[2]
            column = value[3]
            sticky = value[4]

            temp = tk.Label(self.window, text=text, bg="black", fg="white", font=self.font)
            temp.grid(row=row, column=column, sticky=sticky)

            self.text_outputs.update({key: temp})

        self.text_inputs.update({"first_input": self.input_test})
        self.text_inputs.update({"hero_input": self.input_hero})

#        buttons = [["hero", "Submit", 4, self.button_hero, 1, 2, False],
#                   ["input", "Submit", 4, self.button_input, 3, 2, False]]
#
#        for _, value in enumerate(buttons):
#            key = value[0]
#            text = value[1]
#            width = value[2]
#            command = value[3]
#            row = value[4]
#            column = value[5]
#            sticky = value[6]
#            font = self.font
#
#            temp = tk.Button(self.window, text=text, width=width, command=command, font=font)
#            if sticky:
#                temp.grid(row=row, column=column, sticky=sticky)
#            else:
#                temp.grid(row=row, column=column)
#
#            self.buttons.update({key: temp})

    def setup_attr_screen(self):
        """ create tkinter widgets """
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

        for _, value in enumerate(outputs):
            key = value[0]
            text = value[1]
            row = value[2]
            column = value[3]
            sticky = value[4]

            temp = tk.Label(self.window, text=text, bg="black", fg="white", font=self.font)
            temp.grid(row=row, column=column, sticky=sticky)

            self.text_outputs.update({key:temp})


        # pressing the tab key while inside a text entry jumps to the next one
        # in the list. because of this, this list has to be created in the
        # order the entries appear on screen.
        inputs = []
        inputs.append(["mod", 20, 5, 1, tk.W])

#        inputs = [["mod", 20, 3, 1, tk.W],
#                  ["desc", 20, 11, 1, tk.W]]

        if self.state.dice == "manual":
            inputs.append(["dice_input", 20, 6, 1, tk.W])

        inputs.append(["desc", 20, 13, 1, tk.W])

        for _, value in enumerate(inputs):
            key = value[0]
            width = value[1]
            row = value[2]
            column = value[3]
            sticky = value[4]

            temp = tk.Entry(self.window, width=width, bg="white")
            temp.grid(row=row, column=column, sticky=sticky)

            self.text_inputs.update({key: temp})

        self.text_inputs.update({"first_input": self.input_test})
        self.text_inputs.update({"hero_input": self.input_hero})

        buttons = [#["hero", "Submit", 4, self.button_hero, 1, 2, False],
                   #["input", "Submit", 4, self.button_input, 3, 2, False],
                   ["test", "Test", 4, self.button_test, 7, 0, False],
                   ["save", "Save", 4, self.button_save, 14, 0, False]]

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

    def setup_fight_talent_screen(self):
        """ create tkinter widgets """
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

        for _, value in enumerate(outputs):
            key = value[0]
            text = value[1]
            row = value[2]
            column = value[3]
            sticky = value[4]

            temp = tk.Label(self.window, text=text, bg="black", fg="white", font=self.font)
            temp.grid(row=row, column=column, sticky=sticky)

            self.text_outputs.update({key:temp})

        # pressing the tab key while inside a text entry jumps to the next one
        # in the list. because of this, this list has to be created in the
        # order the entries appear on screen.
        inputs = []
        inputs.append(["mod", 20, 5, 1, tk.W])

        if self.state.dice == "manual":
            inputs.append(["dice_input", 20, 6, 1, tk.W])

        inputs.append(["desc", 20, 12, 1, tk.W])

        for _, value in enumerate(inputs):
            key = value[0]
            width = value[1]
            row = value[2]
            column = value[3]
            sticky = value[4]

            temp = tk.Entry(self.window, width=width, bg="white")
            temp.grid(row=row, column=column, sticky=sticky)

            self.text_inputs.update({key: temp})

        self.text_inputs.update({"first_input": self.input_test})
        self.text_inputs.update({"hero_input": self.input_hero})

        buttons = [#["hero", "Submit", 4, self.button_hero, 1, 2, False],
                   #["input", "Submit", 4, self.button_input, 3, 2, False],
                   ["test", "Test", 4, self.button_test, 7, 0, False],
                   ["save", "Save", 4, self.button_save, 14, 0, False]]

        for _, value in enumerate(buttons):
            key = value[0]
            text = value[1]
            width = value[2]
            command = value[3]
            row = value[4]
            column = value[5]
            sticky = value[6]
            font = self.font

            temp = tk.Button(self.window, text=text, width=width, command=command, font = font)
            if sticky:
                temp.grid(row=row, column=column, sticky=sticky)
            else:
                temp.grid(row=row, column=column)

            self.buttons.update({key: temp})

    def setup_skill_screen(self):
        """ create tkinter widgets """
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

        for _, value in enumerate(outputs):
            key = value[0]
            text = value[1]
            row = value[2]
            column = value[3]
            sticky = value[4]

            temp = tk.Label(self.window, text=text, bg="black", fg="white", font=self.font)
            temp.grid(row=row, column=column, sticky=sticky)

            self.text_outputs.update({key:temp})

        # pressing the tab key while inside a text entry jumps to the next one
        # in the list. because of this, this list has to be created in the
        # order the entries appear on screen.
        inputs = []
        inputs.append(["mod", 20, 5, 1, tk.W])

        if self.state.dice == "manual":
            inputs.append(["dice_input", 20, 6, 1, tk.W])

        inputs.append(["desc", 20, 14, 1, tk.W])

        for _, value in enumerate(inputs):
            key = value[0]
            width = value[1]
            row = value[2]
            column = value[3]
            sticky = value[4]

            temp = tk.Entry(self.window, width=width, bg="white")
            temp.grid(row=row, column=column, sticky=sticky)

            self.text_inputs.update({key: temp})

        self.text_inputs.update({"first_input": self.input_test})
        self.text_inputs.update({"hero_input": self.input_hero})

        buttons = [#["hero", "Submit", 4, self.button_hero, 1, 2, False],
                   #["input", "Submit", 4, self.button_input, 3, 2, False],
                   ["test", "Test", 4, self.button_test, 7, 0, False],
                   ["save", "Save", 4, self.button_save, 15, 0, False]]

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


    def setup_misc_screen(self):
        """ create tkinter widgets """
        outputs = [["roll_nr", "Roll #", 0, 0, tk.E],
                   ["var_roll_nr", '', 0, 1, tk.W],
                   ["hero_prompt", "Hero file: ", 1, 0, tk.E],
                   ["matching_hero", "Matching hero: ", 2, 0, tk.E],
                   ["var_matching_hero", '', 2, 1, tk.W],
                   ["input_prompt", "Input: ", 3, 0, tk.E],
                   ["rolls", "Rolls: ", 5, 0, tk.E],
                   ["var_rolls", '', 5, 1, tk.W],
                   ["result", "Result: ", 6, 0, tk.E],
                   ["var_result", '', 6, 1, tk.W],
                   ["desc", "Description: ", 7, 0, tk.E]]

        for _, value in enumerate(outputs):
            key = value[0]
            text = value[1]
            row = value[2]
            column = value[3]
            sticky = value[4]

            temp = tk.Label(self.window, text=text, bg="black", fg="white", font=self.font)
            temp.grid(row=row, column=column, sticky=sticky)

            self.text_outputs.update({key:temp})

        inputs = [["desc", 20, 7, 1, tk.W]]
        for _, value in enumerate(inputs):
            key = value[0]
            width = value[1]
            row = value[2]
            column = value[3]
            sticky = value[4]

            temp = tk.Entry(self.window, width=width, bg="white")
            temp.grid(row=row, column=column, sticky=sticky)

            self.text_inputs.update({key: temp})

        self.text_inputs.update({"first_input": self.input_test})
        self.text_inputs.update({"hero_input": self.input_hero})

        buttons = [#["hero", "Submit", 4, self.button_hero, 1, 2, False],
                   #["input", "Submit", 4, self.button_input, 3, 2, False],
                   ["test", "Test", 4, self.button_test, 7, 0, False],
                   ["save", "Save", 4, self.button_save, 14, 0, False]]

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

#class Watcher:
#    """ A simple class, set to watch its variable. """
#    def __init__(self, value):
#        self.variable = value
#
#    def set_value(self, new_value):
#        if self.value != new_value:
#            self.pre_change()
#            self.variable = new_value
#            self.post_change()
#
#    def pre_change(self):
#        # do stuff before variable is about to be changed
#
#    def post_change(self):
#        # do stuff right after variable has changed
