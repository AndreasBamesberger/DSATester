"""
The code to provide the logic behind DSATester
"""
import xml.etree.ElementTree  # To parse input xml file

import copy  # To make copies of attributo and sinnenschaerfe
import csv  # To write into file
import datetime  # To log time of dice roll
import operator  # To subtract list from list
import os  # To check if file already exists
import random  # For dice rolls
import re  # Regular expressions
import xml.etree.ElementTree  # To parse input xml file
from collections import namedtuple
from dataclasses import dataclass  # To create GameState

from libs.backend.dsa_data import Attribute, Skill, Spell, FightTalent, \
    Advantage, SpecialSkill, Misc


@dataclass
class GameState:
    """
    Dataclass used to transfer the state of the game between GameLogic and
    the active interface.

    ...

    Attributes
    ----------
    save (bool): Export roll to the output csv file if this is True
    dice (str): "auto" or "manual", if dice rolls are typed in or calculated
    current_hero (str): Which hero file will be evaluated
    counter (int): Increases with every saved dice roll
    attrs (list): 1-3 attribute abbreviations related to the current skill/spell
    mod (int): Test modifier input by user
    rolls (list): Calculated or manually typed in dice rolls
    result (int): Success if this is >= 0
    desc (str): Test description to save in output csv
    test_input (str): User input to match with hero entries or misc dice sum
    option_list (list): List of hero entries matching the test input
    selection (list): Single entry from option_list
    """
    save: bool = False
    dice: str = None
    current_hero: str = None
    counter: int = 1
    attrs: list = None
    mod: int = None
    rolls: list = None
    result: int = None
    desc: str = None
    test_input: str = None
    option_list: list = None
    selection: list = None


# Data type for every attribute related to a skill/spell test.
# abbr (str): Abbreviation of the attribute
# value (int): Original attribute value
# modified (int): If the user specified test modifier would reduce the
#                 skill/spell value below 0, all test related attribute
#                 values are decreased instead. "modified" holds this new value
# remaining (int): (Modified) attribute value minus the dice roll
SkillAttr = namedtuple("SkillAttr", ["abbr", "value", "modified", "remaining"])

# This represents one read in hero xml file
# "root" is the entire parsed xml file
Hero = namedtuple("Hero", ["name",
                           "root",
                           "attrs",
                           "skills",
                           "spells",
                           "fight_talents",
                           "advantages",
                           "special_skills"])


class GameLogic:
    """
    DSA 4.1 rules for testing, called upon by interfaces. Reads xml files,
    generates dice, performs tests, saves results in csv file.

    ...

    Attributes
    ----------
    supported_tests: list
        holds all test categories that can be tested
    _result_csv: str
        file path of output csv file
    _hero_folder: str
        directory where hero xml files are stored
    _lang: dict
        language dictionary holding all strings that will be displayed
    _heroes: dict
        dictionary holding all read in heroes. Keys are the hero names,
        fields are namedtuple Hero.
    _xml_list: list
        list of all found hero xml files

    Methods
    -------
    _get_all_xml():
        Read in all hero xml files and store contents in namedtuple Hero.
    _parse_xml(hero_file):
        Use xml.etree.ElementTree.parse to read in hero xml files.
    _setup_output_file():
        If output file doesn't exist, write csv header.
    save_to_csv(state):
        Write current test as new row in output csv file.
    _read_attributes(root):
        Make one Attribute object for each attribute entry and add it to list.
    _read_skills(root):
        Make one Skill object for each attribute entry and add it to list.
    _add_sinnenschaerfe(skill_list):
        Special case for this skill, add 2 skill entries.
    _read_spells(root):
        Make one Spell object for each attribute entry and add it to list.
    _add_attributo(spell_list):
        Special case for this spell, add 8 spell entries.
    _read_fight_talents(root):
        Make one FightTalent object for each attribute entry and add it to list.
    _read_advantages(root):
        Make one Advantage object for each attribute entry and add it to list.
    _read_special_skills(root):
        Make one SpecialSkill object for each attribute entry and add it to
        list.
    test(state):
        Based on the category, choose the correct test method and call it.
    _test_1dice(state):
        Test the categories attribute, fight talent, advantage.
    _test_3dice(state):
        Test the categories skill, spell.
    _test_misc(state):
        Add the values of a user specified number of dice to create the misc
        dice sum.
    _roll_dice(dice_count, min_value, max_value):
        Random number generator.
    autocomplete(state):
        Creates a list of hero entries (attributes, skills, spells,
        fight talents, special skills, advantages) that contain the user's
        test input and stores that list in GameState.option_list
    get_hero_list():
        Create a list of all available hero files to show to user in interface
    match_test_input(state):
        Match the user test input with regular expressions to find a misc
        dice roll, then match the user test input with all hero entries to
        find a matching test entry.
    match_manual_dice(state, rolls_string):
        Use regular expression to check if the manually typed in dice rolls
        are valid and save them to GameState.rolls.
    """

    def __init__(self, configs, lang):
        self.supported_tests = ["attr", "skill", "spell", "fight_talent",
                                "advantage"]
        random.seed(a=None, version=2)
        self._result_csv = configs["output file"]
        self._hero_folder = configs["hero folder"]
        self._lang = lang

        self._heroes = dict()  # entries are namedtuple Hero
        self._xml_list = list()

        self._get_all_xml()

        self._setup_output_file()

    def _get_all_xml(self):
        """ checks current working directory for xml files, reads all their
        relevant entries and stores them (using data types specified in
        dsa_data.py) as separate heroes (namedtuple Hero) """

        # add all xml files to list
        for file in os.listdir(self._hero_folder):
            if file.endswith(".xml"):
                self._xml_list.append(file)

        # read all attr, skill, spell, fight_talent entries of hero file
        for _, value in enumerate(self._xml_list):
            name = value.replace(".xml", '')
            hero_root = self._parse_xml(value)
            attrs = self._read_attributes(hero_root)
            skills = self._read_skills(hero_root)
            spells = self._read_spells(hero_root)
            fight_talents = self._read_fight_talents(hero_root)
            advantages = self._read_advantages(hero_root)
            special_skills = self._read_special_skills(hero_root)

            # some entries are both skill and special skill, e.g.
            # "Ritualkenntnis: Hexe", special skill does not need to be tested
            # so it is removed
            for skill in skills:
                for index, special_skill in enumerate(special_skills):
                    if skill.name == special_skill.name:
                        special_skills.pop(index)

            self._heroes.update({name: Hero(name,
                                            hero_root,
                                            attrs,
                                            skills,
                                            spells,
                                            fight_talents,
                                            advantages,
                                            special_skills)})

    def _parse_xml(self, hero_file):
        """ use xml.etree.ElementTree to parse xml file.
        input: hero_file:str, name of xml file
        output: root:xml.etree.ElementTree.Element """
        filepath = os.path.join(self._hero_folder, hero_file)

        tree = xml.etree.ElementTree.parse(filepath)
        root = tree.getroot()
        return root

    def _setup_output_file(self):
        """ prepares first line of output csv file if it doesn't already exist
        output: bool, True if first line had to be written """

        columns = ["Hero file",
                   "Test type",
                   "Name of tested entry",
                   "Misc dice sum input",
                   "Value of tested entry",
                   "Modifier",
                   "Values of related attributes",
                   "Rolls",
                   "Result",
                   "Description",
                   "Timestamp",
                   "Type of dice input"]

        # if file does not exist, add first row of column names
        if not os.path.isfile(self._result_csv):
            with open(self._result_csv, "w", encoding="utf-8") as csv_file:
                file_writer = csv.writer(csv_file, delimiter=',',
                                         quotechar='|',
                                         quoting=csv.QUOTE_MINIMAL)
                file_writer.writerow(columns)
            return True
        return False

    def save_to_csv(self, state):
        """ adds current test to csv file as new row and increments
        GameState.counter
        input: state:GameState
        output: state:GameState """

        if state.rolls == [] or state.rolls is None:
            # this should never happen but cancel save process just in case
            return state

        if state.selection.category == "misc":
            misc = str(state.selection.dice_count) + "D" + str(
                state.selection.dice_eyes)
        else:
            misc = ''

        if state.selection.category in ("skill", "spell"):
            if state.mod + state.selection.value < 0:
                # attrs_string example: "KL(14->12), IN(13->11), FF(12->10)"
                attrs_list = [i.abbr + '(' + str(i.value) + "->" +
                              str(i.modified) + ')' for _, i in
                              enumerate(state.attrs)]
            else:
                attrs_list = [i.abbr + '(' + str(i.value) + ')' for _, i in
                              enumerate(state.attrs)]
            attrs_string = "; ".join(map(str, attrs_list))
        else:
            attrs_string = ''

        # join list of rolls to string
        rolls = "; ".join(map(str, state.rolls))

        desc = f"Roll#{state.counter}: {state.desc}"
        # comma is used as delimiter in csv
        desc = desc.replace(",", ";")

        timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

        save_values = [state.current_hero + ".xml",
                       state.selection.category,
                       state.selection.name,
                       misc,
                       state.selection.value,
                       state.mod,
                       attrs_string,
                       rolls,
                       state.result,
                       desc,
                       timestamp,
                       state.dice]

        with open(self._result_csv, "a", encoding="utf-8") as csv_file:
            file_writer = csv.writer(csv_file,
                                     delimiter=',',
                                     quotechar='|',
                                     quoting=csv.QUOTE_MINIMAL)
            file_writer.writerow(save_values)

        # only saved rolls increase the roll count
        state.counter += 1

        return state

    @staticmethod
    def _read_attributes(root):
        """ for every attribute entry, create Attribute datatype and add it
        to list
        input: root:xml.etree.ElementTree.Element, root of one hero entry
        output: output_list:list, list of all found attribute entries """
        output_list = []
        for _, value in enumerate(root[0][2]):
            attr = Attribute(value)
            output_list.append(attr)
        return output_list

    def _read_skills(self, root):
        """ for every skill entry, create Skill datatype and add it to list
        input: root:xml.etree.ElementTree.Element, root of one hero entry
        output: output_list:list, list of all found skill entries """

        output_list = []
        for _, value in enumerate(root[0][6]):
            output_list.append(Skill(value))

            # check if sinnenschaerfe is part of skills
            if output_list[-1].name == "Sinnenschärfe":
                output_list = self._add_sinnenschaerfe(output_list)

        return output_list

    @staticmethod
    def _add_sinnenschaerfe(skill_list):
        """ special case for sinnenschaerfe, normal use is KL/IN/IN but if test
        relies on touching objects it changes to KL/IN/FF
        input: skill_list:list, list of skills
               ss_orig:Skill, original entry for sinnenschaerfe
        output: skill_list:list, list of all found skills """

        attr_list = ["IN", "FF"]
        # remove original sinnenschaerfe entry
        ss_orig = skill_list.pop(-1)

        # change original sinnenschaerfe entry and add it to skill list
        for _, value in enumerate(attr_list):
            ss_temp = copy.deepcopy(ss_orig)
            ss_temp.name = value + " Sinnenschärfe"
            ss_temp.attrs[2] = value
            skill_list.append(ss_temp)

        return skill_list

    def _read_spells(self, root):
        """ for every spell entry, create Spell datatype and add it to list
        input: root:xml.etree.ElementTree.Element, root of one hero entry
        output: output_list:list, list of all found spell entries """
        output_list = []
        for _, value in enumerate(root[0][7]):
            output_list.append(Spell(value))

            # check if attributo is part of spells
            if output_list[-1].name == "Attributo":
                output_list = self._add_attributo(output_list)

        return output_list

    @staticmethod
    def _add_attributo(spell_list):
        """ special case for attributo spell, the attribute that gets increased
        using this spell also needs to be part of the test, so one entry for
        every attribute is added to the spell list
        input: spell_list:list, list of spells
               attributo_orig:Spell, original entry for attributo
        output: spell_list:list, list of all found spells """

        attr_list = ["MU", "KL", "IN", "CH", "FF", "GE", "KO", "KK"]
        # remove original attributo entry
        attributo_orig = spell_list.pop(-1)

        # change original attributo entry and add it to skill list
        for _, value in enumerate(attr_list):
            attributo_temp = copy.deepcopy(attributo_orig)
            attributo_temp.name = value + " Attributo"
            attributo_temp.attrs[2] = value
            spell_list.append(attributo_temp)

        return spell_list

    @staticmethod
    def _read_fight_talents(root):
        """ for every fight talent entry, create FightTalent datatype and add
        it to list
        input: root:xml.etree.ElementTree.Element, root of one hero entry
        output: output_list:list, list of all found fight talent entries """
        output_list = []
        for _, value in enumerate(root[0][8]):
            # offensive and defensive test possible, so add every entry twice
            output_list.append(FightTalent(value, "AT"))
            output_list.append(FightTalent(value, "PA"))
        return output_list

    @staticmethod
    def _read_advantages(root):
        """ for every advantage/disadvantage entry, create Advantage datatype
        and add it to list
        input: root:xml.etree.ElementTree.Element, root of one hero entry
        output: output_list:list, list of all found advantage entries """
        output_list = []
        for _, value in enumerate(root[0][3]):
            output_list.append(Advantage(value))
        return output_list

    @staticmethod
    def _read_special_skills(root):
        """ for every special skill entry, create SpecialSkill datatype and
        add it to list
        input: root:xml.etree.ElementTree.Element, root of one hero entry
        output: output_list:list, list of all found special skill entries """
        output_list = []
        for _, value in enumerate(root[0][4]):
            output_list.append(SpecialSkill(value))
        return output_list

    def test(self, state):
        """ execute the correct test method based on state.category
        input: state:GameState
        output: state:Gamestate """

        # manual dice should have been typed in by this point, if they don't
        # exist exit
        if state.dice == "manual" and (
                state.rolls is None or state.rolls == []):
            return state

        test_dict = {"attr": self._test_1dice,
                     "fight_talent": self._test_1dice,
                     "advantage": self._test_1dice,
                     "skill": self._test_3dice,
                     "spell": self._test_3dice,
                     "misc": self._test_misc}

        state = test_dict[state.selection.category](state)

        return state

    def _test_1dice(self, state):
        """ used for attribute and fight talent tests, calculate result based
        on entry value, dice rolls and modifier. results are stored in GameState
        input: entry:Attribute/FightTalent, the specific attribute/fight talent
               state:GameState
        output: state:Gamestate """

        # quit if tested entry has no value
        if state.selection.value is None:
            return state

        if state.dice == "auto":
            state.rolls = self._roll_dice(1, 1, 20)

        state.result = state.selection.value + state.mod - state.rolls[0]
        return state

    def _test_3dice(self, state):
        """ used for skill and spell tests, calculate result based on entry
        value, dice rolls and modifier. results are stored in GameState
        input: entry:Skill/Spell, the specific skill/spell
               state:GameState
        output: state:GameState """

        # quit if tested entry has no value
        if state.selection.value is None:
            return state

        attr_values = []
        attr_abbrs = []

        hero = self._heroes[state.current_hero]

        # from all available attributes get the 3 related to the entry being
        # tested
        for attr in hero.attrs:
            for _, entry_attr in enumerate(state.selection.attrs):
                if attr.abbr == entry_attr:
                    attr_values.append(attr.value)
                    attr_abbrs.append(attr.abbr)

        # Ritualkenntnis: Hexe has no values, can't be tested
        if not attr_abbrs:
            return state

        # save original values in case a negative modifier lowers them
        attr_values_orig = attr_values

        modded_value = state.selection.value + state.mod

        # if the modifier lowers the skill/spell value below zero, the 3
        # related attributes get lowered by that value
        if modded_value < 0:
            attr_values = [x + modded_value for x in attr_values]

        if state.dice == "auto":
            state.rolls = self._roll_dice(3, 1, 20)

        # subtract the dice rolls from the (possibly modified) attribute values
        # this subtracts the dice list from the attribute list
        remaining = list(map(operator.sub, attr_values, state.rolls))

        state.result = modded_value if modded_value > 0 else 0

        # for every failed test, lower the result by that difference
        for _, attr_value in enumerate(remaining):
            if attr_value < 0:
                state.result += attr_value

        # to print the result, for every tested attribute a namedtuple is
        # created which holds the abbreviation, the unmodified and modified
        # values and how much is remaining after the test
        state.attrs = []

        for i in range(3):
            entry_attr = SkillAttr(attr_abbrs[i], attr_values_orig[i],
                                   attr_values[i], remaining[i])
            state.attrs.append(entry_attr)

        return state

    def _test_misc(self, state):
        """ used for misc dice sum tests, calculate result based on dice count,
        dice type and modifier. results are stored in GameState
        input: state:GameState
        output: state:GameState """
        state.result = 0
        dice_count = state.selection.dice_count
        dice_eyes = state.selection.dice_eyes

        if dice_count > 200:
            print(self._lang["too_many_dice"])
            return state

        if state.dice == "auto":
            state.rolls = self._roll_dice(dice_count, 1, dice_eyes)

        # create sum of all rolled dice and modifier
        for _, value in enumerate(state.rolls):
            state.result += value

        state.result += state.mod
        return state

    @staticmethod
    def _roll_dice(dice_count, min_value, max_value):
        """ random number generator
        input: dice_count:int, how many numbers to generate
               min_value:int, lowest possible number
               max_value:int, highest possible number
        output: rolls:list, list of generated numbers """
        rolls = [random.randint(min_value, max_value) for _ in
                 range(dice_count)]
        return rolls

    def autocomplete(self, state):
        """ creates a list of hero entries (attributes, skills, spells, fight
        talents) that contain the user's test input and stores that list in
        GameState.option_list
        input: state:GameState
        output: state:GameState"""
        output_list = []

        try:
            hero = self._heroes[state.current_hero]
        except KeyError:
            # this can occur if (using the GUI) user types in a test before a
            # matching a hero file
            print(self._lang["key_error"])
            return state

        for attr in hero.attrs:
            if state.test_input.lower() in attr.name.lower():
                output_list.append(attr)
        for skill in hero.skills:
            if state.test_input.lower() in skill.name.lower():
                output_list.append(skill)
        for spell in hero.spells:
            if state.test_input.lower() in spell.name.lower():
                output_list.append(spell)
        for fight_talent in hero.fight_talents:
            if state.test_input.lower() in fight_talent.name.lower():
                output_list.append(fight_talent)
        for advantage in hero.advantages:
            if state.test_input.lower() in advantage.name.lower():
                output_list.append(advantage)
        for special_skill in hero.special_skills:
            if state.test_input.lower() in special_skill.name.lower():
                output_list.append(special_skill)

        state.option_list = output_list
        return state

    def get_hero_list(self):
        """ create a list of all available hero files to show to user in
        interface
        output: out_list:list, list of hero names"""
        out_list = []
        for key, _ in self._heroes.items():
            out_list.append(key)
        out_list.sort()
        return out_list

    def match_test_input(self, state):
        """ match the user test input with regular expressions to find a misc
        dice roll, then match the user test input with all hero entries to find
        a matching test entry.
        input: state:Gamestate
        output: state:Gamestate """

        # check for misc dice input using regex
        # regex:
        # ^, $: match from start to end of string
        # \d+: match one or more integers
        # [dDwW]: match one of those four letters
        # [\+-]: match 0 or 1 plus or minus signs
        # \d*: match 0 or any number of numbers
        # e.g. "3d20+5" -> '3', '20', '+', '5'
        #      "2d6" -> '2', '6', '', ''

        pattern = r"^(\d+)[dDwW](\d+)([\+-]?)(\d*)$"
        match = re.match(pattern, state.test_input)
        if match and int(match.groups()[0]) > 0 and int(match.groups()[1]) > 0:
            matched = match.groups()
            state.selection = Misc(int(matched[0]), int(matched[1]))
            if matched[2] != '' and matched[3] != '':
                state.mod = int(matched[2] + matched[3])
            else:
                state.mod = 0
            return state

        state.selection = None

        # match input with hero entries
        state = self.autocomplete(state)

        return state

    @staticmethod
    def match_manual_dice(state, rolls_string):
        """ use regular expression to check if the manually typed in dice rolls
        are valid and save them to GameState.rolls
        input: state:GameState
               input_list:list, list of the typed in dice rolls
        output: state:GameState """

        # regex:
        # ^, $: match from start to end of string
        # \d+: match one or more integers
        pattern = r"^\d+$"
        out_list = []
        dice_count = None
        dice_max = None

        # attribute and fight talent tests take 1D20
        if state.selection.category in ("attr", "fight_talent", "advantage"):
            dice_count = 1
            dice_max = 20
        # skill and spell tests take 3D20
        elif state.selection.category in ("skill", "spell"):
            dice_count = 3
            dice_max = 20
        # misc dice roll takes whatever was specified earlier
        elif state.selection.category == "misc":
            dice_count = state.selection.dice_count
            dice_max = state.selection.dice_eyes

        # allow matches for dice separated by any number of whitespaces and
        # commas
        rolls_string = rolls_string.replace(',', ' ')
        rolls_list = rolls_string.split(' ')

        for item in rolls_list:
            match = re.match(pattern, item)
            if match:
                if int(item) in range(1, dice_max + 1):
                    out_list.append(int(item))

        state.rolls = out_list

        if len(state.rolls) != dice_count:
            state.rolls = None

        return state
