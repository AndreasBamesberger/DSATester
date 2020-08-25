""" creates window using tkinter, communicates with GameLogic through the dataclass GameState"""
import re
import tkinter as tk
from game_backend import GameLogic, GameState

game = GameLogic()


class GUI():
    """ creates window using tkinter, communicates with GameLogic through the dataclass GameState"""
    def __init__(self):
        self.state = GameState()
        self.read_config("config.txt")

        self.window = tk.Tk()
        self.window.tk.call('tk', 'scaling', self.scaling)
        self.window.title("DSA rng")
        self.window.configure(background="black")

        self.old_category = None
        self.old_input = None
        self.printable_options = None

        self.text_outputs = {}
        self.text_inputs = {}
        self.buttons = {}

        # text input for first_input
        self.input_firstinput = tk.Entry(self.window, width=20, bg="white")
        self.input_firstinput.grid(row=1, column=1, sticky=tk.W)

        self.setup_window()
        self.update()

    def loop(self):
        """ gets executed by main.py, reads inputs, sends inputs to GameLogic,
        shows results in tkinter window """
        while True:
            self.get_first_input()

            if self.old_category != self.state.category:
                self.clear_screen()
                self.setup_window()
                self.old_category = self.state.category

            self.text_outputs["var_roll_nr"].configure(text=str(self.state.counter))

            if self.state.category in ("attr", "skill", "spell", "fight_talent"):
                self.text_outputs["var_matching"].configure(text=self.state.name)
                self.get_mod(self.text_inputs["mod"].get().lower())

            if self.state.category:
                self.state.desc = self.text_inputs["desc"].get()

            if not self.state.category:
                self.text_outputs["var_matching"].configure(text=self.printable_options)

            self.update()

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

        self.input_firstinput.delete(0, 'end')

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
            if key == "first_input":
                continue
            field.destroy()

        for key, field in self.buttons.items():
            field.destroy()

    def get_first_input(self):
        """ checks input for misc input regular expressions, if it matches sets
        test category to misc, else it sends input to game autocomplete to get
        matching entry. if just 1 entry matches then set this as current test
        """
        pattern1 = "^(\d+)[dDwW](\d+)$" # 3d20 -> 3, 20 #pylint: disable=anomalous-backslash-in-string
        pattern2 = "^(\d+)[dDwW](\d+)\+(\d+)$" # 8d3+4 -> 8, 3, 4 #pylint: disable=anomalous-backslash-in-string
        pattern3 = "^(\d+)[dDwW](\d+)-(\d+)$" # 8d3-4 -> 8, 3, 4 #pylint: disable=anomalous-backslash-in-string


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
            self.state = game.autocomplete(self.state)

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

        if self.state.dice == "manual":
            self.get_manual_dice(self.text_inputs["dice_input"].get())

        self.state = game.test(self.state)

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
        self.state = game.save_to_csv(self.state)
        self.reset()

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
                if "scaling" in line:
                    split = line.split()
                    self.scaling = float(split[-1])
                if "font" in line:
                    line = line.replace("font: ", '')
                    line = line.rstrip()
                    self.font = line

    def setup_input_screen(self):
        """ create tkinter widgets """
        outputs = [["roll_nr", "Roll #", 0, 0, tk.E],
                   ["var_roll_nr", '', 0, 1, tk.W],
                   ["input_prompt", "Input: ", 1, 0, tk.E],
                   ["matching", "Matching: ", 2, 0, tk.NE],
                   ["var_matching", '', 2, 1, tk.W]]

        for _, value in enumerate(outputs):
            key = value[0]
            text = value[1]
            row = value[2]
            column = value[3]
            sticky = value[4]

            temp = tk.Label(self.window, text=text, bg="black", fg="white", font=self.font)
            temp.grid(row=row, column=column, sticky=sticky)

            self.text_outputs.update({key: temp})

        self.text_inputs.update({"first_input": self.input_firstinput})

    def setup_attr_screen(self):
        """ create tkinter widgets """
        outputs = [["roll_nr", "Roll #", 0, 0, tk.E],
                   ["var_roll_nr", '', 0, 1, tk.W],
                   ["matching", "Matching: ", 2, 0, tk.E],
                   ["var_matching", '', 2, 1, tk.W],
                   ["mod", "Modifier: ", 3, 0, tk.E],
                   ["tested", "Tested attribute: ", 6, 0, tk.E],
                   ["var_tested", '', 6, 1, tk.W],
                   ["value", "Value: ", 7, 0, tk.E],
                   ["var_value", '', 7, 1, tk.W],
                   ["rolls", "Rolls: ", 8, 0, tk.E],
                   ["var_rolls", '', 8, 1, tk.W],
                   ["result", "Result: ", 10, 0, tk.E],
                   ["var_result", '', 10, 1, tk.W],
                   ["desc", "Description: ", 11, 0, tk.E]]

        if self.state.dice == "manual":
            outputs.append(["dice_input", "Manual dice input: ", 4, 0, tk.E])

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
        inputs.append(["mod", 20, 3, 1, tk.W])

#        inputs = [["mod", 20, 3, 1, tk.W],
#                  ["desc", 20, 11, 1, tk.W]]

        if self.state.dice == "manual":
            inputs.append(["dice_input", 20, 4, 1, tk.W])

        inputs.append(["desc", 20, 11, 1, tk.W])

        for _, value in enumerate(inputs):
            key = value[0]
            width = value[1]
            row = value[2]
            column = value[3]
            sticky = value[4]

            temp = tk.Entry(self.window, width=width, bg="white")
            temp.grid(row=row, column=column, sticky=sticky)

            self.text_inputs.update({key: temp})

        self.text_inputs.update({"first_input": self.input_firstinput})

        buttons = [["test", "Test", 4, self.button_test, 5, 0, False],
                   ["save", "Save", 4, self.button_save, 12, 0, False]]

        for _, value in enumerate(buttons):
            key = value[0]
            text = value[1]
            width = value[2]
            command = value[3]
            row = value[4]
            column = value[5]
            sticky = value[6]

            temp = tk.Button(self.window, text=text, width=width, command=command)
            if sticky:
                temp.grid(row=row, column=column, sticky=sticky)
            else:
                temp.grid(row=row, column=column)

            self.buttons.update({key: temp})

    def setup_fight_talent_screen(self):
        """ create tkinter widgets """
        outputs = [["roll_nr", "Roll #", 0, 0, tk.E],
                   ["var_roll_nr", '', 0, 1, tk.W],
                   ["matching", "Matching: ", 2, 0, tk.E],
                   ["var_matching", '', 2, 1, tk.W],
                   ["mod", "Modifier: ", 3, 0, tk.E],
                   ["tested", "Tested fight talent: ", 6, 0, tk.E],
                   ["var_tested", '', 6, 1, tk.W],
                   ["value", "Value: ", 7, 0, tk.E],
                   ["var_value", '', 7, 1, tk.W],
                   ["rolls", "Rolls: ", 8, 0, tk.E],
                   ["var_rolls", '', 8, 1, tk.W],
                   ["result", "Result: ", 9, 0, tk.E],
                   ["var_result", '', 9, 1, tk.W],
                   ["desc", "Description: ", 10, 0, tk.E]]

        if self.state.dice == "manual":
            outputs.append(["dice_input", "Manual dice input: ", 4, 0, tk.E])

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
        inputs.append(["mod", 20, 3, 1, tk.W])

        if self.state.dice == "manual":
            inputs.append(["dice_input", 20, 4, 1, tk.W])

        inputs.append(["desc", 20, 10, 1, tk.W])

        for _, value in enumerate(inputs):
            key = value[0]
            width = value[1]
            row = value[2]
            column = value[3]
            sticky = value[4]

            temp = tk.Entry(self.window, width=width, bg="white")
            temp.grid(row=row, column=column, sticky=sticky)

            self.text_inputs.update({key: temp})

        self.text_inputs.update({"first_input": self.input_firstinput})

        buttons = [["test", "Test", 4, self.button_test, 5, 0, False],
                   ["save", "Save", 4, self.button_save, 11, 0, False]]

        for _, value in enumerate(buttons):
            key = value[0]
            text = value[1]
            width = value[2]
            command = value[3]
            row = value[4]
            column = value[5]
            sticky = value[6]

            temp = tk.Button(self.window, text=text, width=width, command=command)
            if sticky:
                temp.grid(row=row, column=column, sticky=sticky)
            else:
                temp.grid(row=row, column=column)

            self.buttons.update({key: temp})

    def setup_skill_screen(self):
        """ create tkinter widgets """
        outputs = [["roll_nr", "Roll #", 0, 0, tk.E],
                   ["var_roll_nr", '', 0, 1, tk.W],
                   ["matching", "Matching: ", 2, 0, tk.E],
                   ["var_matching", '', 2, 1, tk.W],
                   ["mod", "Modifier: ", 3, 0, tk.E],
                   ["tested", "Tested skill/spell: ", 6, 0, tk.E],
                   ["var_tested", '', 6, 1, tk.W],
                   ["tested_attrs", "Tested attributes: ", 7, 0, tk.E],
                   ["var_tested_attrs", '', 7, 1, tk.W],
                   ["value", "Value: ", 8, 0, tk.E],
                   ["var_value", '', 8, 1, tk.W],
                   ["rolls", "Rolls: ", 9, 0, tk.E],
                   ["var_rolls", '', 9, 1, tk.W],
                   ["remaining", "Attribute values remaining: ", 10, 0, tk.E],
                   ["var_remaining", '', 10, 1, tk.W],
                   ["result", "Result: ", 11, 0, tk.E],
                   ["var_result", '', 11, 1, tk.W],
                   ["desc", "Description: ", 12, 0, tk.E]]

        if self.state.dice == "manual":
            outputs.append(["dice_input", "Manual dice input: ", 4, 0, tk.E])

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
        inputs.append(["mod", 20, 3, 1, tk.W])

        if self.state.dice == "manual":
            inputs.append(["dice_input", 20, 4, 1, tk.W])

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

        self.text_inputs.update({"first_input": self.input_firstinput})

        buttons = [["test", "Test", 4, self.button_test, 5, 0, False],
                   ["save", "Save", 4, self.button_save, 13, 0, False]]

        for _, value in enumerate(buttons):
            key = value[0]
            text = value[1]
            width = value[2]
            command = value[3]
            row = value[4]
            column = value[5]
            sticky = value[6]

            temp = tk.Button(self.window, text=text, width=width, command=command)
            if sticky:
                temp.grid(row=row, column=column, sticky=sticky)
            else:
                temp.grid(row=row, column=column)

            self.buttons.update({key: temp})


    def setup_misc_screen(self):
        """ create tkinter widgets """
        outputs = [["input_prompt", "Input: ", 1, 0, tk.E],
                   ["roll_nr", "Roll #", 0, 0, tk.E],
                   ["var_roll_nr", '', 0, 1, tk.W],
                   ["rolls", "Rolls: ", 7, 0, tk.E],
                   ["var_rolls", '', 7, 1, tk.W],
                   ["result", "Result: ", 9, 0, tk.E],
                   ["var_result", '', 9, 1, tk.W],
                   ["desc", "Description: ", 10, 0, tk.E]]

        for _, value in enumerate(outputs):
            key = value[0]
            text = value[1]
            row = value[2]
            column = value[3]
            sticky = value[4]

            temp = tk.Label(self.window, text=text, bg="black", fg="white", font=self.font)
            temp.grid(row=row, column=column, sticky=sticky)

            self.text_outputs.update({key:temp})

        inputs = [["desc", 20, 10, 1, tk.W]]
        for _, value in enumerate(inputs):
            key = value[0]
            width = value[1]
            row = value[2]
            column = value[3]
            sticky = value[4]

            temp = tk.Entry(self.window, width=width, bg="white")
            temp.grid(row=row, column=column, sticky=sticky)

            self.text_inputs.update({key: temp})

        self.text_inputs.update({"first_input": self.input_firstinput})

        buttons = [["test", "Test", 4, self.button_test, 3, 0, False],
                   ["save", "Save", 4, self.button_save, 11, 0, False]]

        for _, value in enumerate(buttons):
            key = value[0]
            text = value[1]
            width = value[2]
            command = value[3]
            row = value[4]
            column = value[5]
            sticky = value[6]

            temp = tk.Button(self.window, text=text, width=width, command=command)
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

if __name__ == '__main__':
    interface = GUI()
    interface.loop()
