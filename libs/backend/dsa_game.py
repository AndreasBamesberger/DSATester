""" file that holds GameLogic and GameState """
import random # for dice rolls
import csv # to write into file
import os # to check if file already exists
import datetime # to log time of dice roll
import xml.etree.ElementTree as ET # to parse input xml file
from collections import namedtuple
from dataclasses import dataclass # to create GameState
import operator # to subtract list from list
import copy # to make copies of attributo and sinnenschaerfe
import re
from libs.backend.dsa_data import Attribute, Skill, Spell, FightTalent

@dataclass
class GameState: # pylint: disable=too-many-instance-attributes
    """ dataclass used to transfer state of game between GameLogic and interfaces """
    done: bool = False        # exit when True (currently not used)
    save: bool = False        # export roll to csv if True
    dice: str = None          # "auto" or "manual" whether dice rolls are typed in or calculated
    current_hero: str = None  # which hero file will be evaluated
    counter: int = 1          # increases with every saved dice roll
    category: str = None      # "attr"/"skill"/"spell"/"misc/fight_talent"
    name: str = None          # name of tested attr/skill/spell/fight talent
    attrs: list = None        # 1-3 attrs related to skill, spell
    value: int = None         # value related to attr/skill/spell/fight talent
    mod: int = None           # test modifier input by user, positive makes test easier
    rolls: tuple = None       # calculated or manually input dice rolls
    result: int = None        # success if >= 0
    misc: tuple = None        # dice count and eyes on dice
    desc: str = None          # text to save in csv
    test_input: str = None   # user input to match tests to or declare misc test
    option_list: list = None  # list of tests matching first input
    selection: list = None    # single entry from option_list

# data type for misc dice sum input
Misc = namedtuple("Misc", ["dice_count", "dice_eyes"])

# data type for every attribute related to a skill/spell test
SkillAttr = namedtuple("SkillAttr", ["abbr", "value", "modified", "remaining"])

# data type for every hero xml file
Hero = namedtuple("Hero", ["name", "root", "attrs", "skills", "spells", "fight_talents"])

class GameLogic:
    """ DSA 4.1 rules for testing, called upon by interfaces. reads xml files,
    generates dice, performs tests, saves results in csv file """

    def __init__(self, configs, lang):
        random.seed(a=None, version=2)
        self.result_csv = configs["output file"]
        self.hero_folder = configs["hero folder"]
        self.lang = lang

        self.heroes = {} # entries are namedtuple Hero
        self.xml_list = []

        self.get_all_xml()

        self.setup_output_file()

    def get_all_xml(self):
        """ checks current working directory for xml files, reads all their
        relevant entries and stores them (using datatypes specified in
        dsa_data.py) as separate heroes (namedtuple Hero) """

        # add all xml files to list
        for file in os.listdir(self.hero_folder):
            if file.endswith(".xml"):
                self.xml_list.append(file)

        # read all attr, skill, spell, fight_talent entries of hero file
        for _, value in enumerate(self.xml_list):
            name = value.replace(".xml", '')
            hero_root = self.parse_xml(value)
            attrs = self.read_attributes(hero_root)
            skills = self.read_skills(hero_root)
            spells = self.read_spells(hero_root)
            fight_talents = self.read_fight_talents(hero_root)
            self.heroes.update({name: Hero(name, hero_root, attrs, skills, spells, fight_talents)})

    def parse_xml(self, hero_file):
        """ use xml.etree.ElementTree to parse xml file.
        input: hero_file:str, name of xml file
        output: root:xml.etree.ElementTree.Element """
        filepath = os.path.join(self.hero_folder, hero_file)

        tree = ET.parse(filepath)
        root = tree.getroot()
        return root

    def setup_output_file(self):
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
        if not os.path.isfile(self.result_csv):
            with open(self.result_csv, "w", encoding="utf-8") as csvfile:
                filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL) #pylint: disable=line-too-long
                filewriter.writerow(columns)
            return True
        return False

    def save_to_csv(self, state):
        """ adds current test to csv file as new row and increments GameState.counter
        input: state:GameState
        output: state:GameState """

        if state.rolls == [] or state.rolls is None:
            # this should never happen but cancel save process just in case
            return state

        if state.category == "misc":
            misc = str(state.misc.dice_count) + "D" + str(state.misc.dice_eyes)
        else:
            misc = ''

        if state.category in ("skill", "spell"):
            if state.mod + state.value < 0:
                # attrs_string example: "KL(14->12), IN(13->11), FF(12->10)"
                attrs_list = [i.abbr + '(' + str(i.value) + "->" + str(i.modified) + ')' for _, i in enumerate(state.attrs)] # pylint: disable=line-too-long
            else:
                attrs_list = [i.abbr + '(' + str(i.value) + ')' for _, i in enumerate(state.attrs)] # pylint: disable=line-too-long
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
                       state.category,
                       state.name,
                       misc,
                       state.value,
                       state.mod,
                       attrs_string,
                       rolls,
                       state.result,
                       desc,
                       timestamp,
                       state.dice]

        with open(self.result_csv, "a", encoding="utf-8") as csvfile:
            filewriter = csv.writer(csvfile,
                                    delimiter=',',
                                    quotechar='|',
                                    quoting=csv.QUOTE_MINIMAL)
            filewriter.writerow(save_values)

        # only saved rolls increase the roll count
        state.counter += 1

        return state

    @staticmethod
    def read_attributes(root):
        """ for every attribute entry, create Attribute datatype and add it to list
        input: root:xml.etree.ElementTree.Element, root of one hero entry
        output: output_list:list, list of all found attribute entries """
        output_list = []
        for i in range(len(root[0][2])):
            attr = Attribute(root[0][2][i])
            output_list.append(attr)
        return output_list

    def read_skills(self, root):
        """ for every skill entry, create Skill datatype and add it to list
        input: root:xml.etree.ElementTree.Element, root of one hero entry
        output: output_list:list, list of all found skill entries """

        output_list = []
        for i in range(len(root[0][6])):
            output_list.append(Skill(root[0][6][i]))

            # check if sinnenschaerfe is part of skills
            if output_list[-1].name == "Sinnenschärfe":
                output_list = self.add_sinnenschaerfe(output_list)

        return output_list

    @staticmethod
    def add_sinnenschaerfe(skill_list):
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
            ss_temp.test[2] = value
            skill_list.append(ss_temp)

        return skill_list

    def read_spells(self, root):
        """ for every spell entry, create Spell datatype and add it to list
        input: root:xml.etree.ElementTree.Element, root of one hero entry
        output: output_list:list, list of all found spell entries """
        output_list = []
        for i in range(len(root[0][7])):
            output_list.append(Spell(root[0][7][i]))

            # check if attributo is part of spells
            if output_list[-1].name == "Attributo":
                output_list = self.add_attributo(output_list)

        return output_list

    @staticmethod
    def add_attributo(spell_list):
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
            attributo_temp.test[2] = value
            spell_list.append(attributo_temp)

        return spell_list

    @staticmethod
    def read_fight_talents(root):
        """ for every fight talent entry, create FightTalent datatype and add it to list
        input: root:xml.etree.ElementTree.Element, root of one hero entry
        output: output_list:list, list of all found fight talent entries """
        output_list = []
        for i in range(len(root[0][8])):
            # offensive and defensive test possible, so add every entry twice
            output_list.append(FightTalent(root[0][8][i], "AT"))
            output_list.append(FightTalent(root[0][8][i], "PA"))
        return output_list

    def test(self, state): # pylint: disable=too-many-branches
        """ execute the correct test method based on state.category
        input: state:GameState
        output: state:Gamestate """

        # manual dice should have been typed in by this point, if they don't exist exit
        if state.dice == "manual" and (state.rolls is None or state.rolls == []):
            return state

        hero = self.heroes[state.current_hero]

        if state.category == "attr":
            for attr in hero.attrs:
                if state.name == attr.name:
                    state = self.test_1dice(attr, state)
        elif state.category == "fight_talent":
            for fight_talent in hero.fight_talents:
                if state.name == fight_talent.name:
                    state = self.test_1dice(fight_talent, state)
        elif state.category == "skill":
            for skill in hero.skills:
                if state.name == skill.name:
                    state = self.test_3dice(skill, state)
        elif state.category == "spell":
            for spell in hero.spells:
                if state.name == spell.name:
                    state = self.test_3dice(spell, state)
        elif state.category == "misc":
            state = self.test_misc(state)

        return state

    def test_1dice(self, entry, state):
        """ used for attribute and fight talent tests, calculate result based
        on entry value, dice rolls and modifier. results are stored in GameState
        input: entry:Attribute/FightTalent, the specific attribute/fight talent
               state:GameState
        output: state:Gamestate """
        state.value = entry.value
        if state.dice == "auto":
            state.rolls = self.roll_dice(1, 1, 20)

        state.result = entry.value + state.mod - state.rolls[0]
        return state

    def test_3dice(self, entry, state):
        """ used for skill and spell tests, calculate result based on entry
        value, dice rolls and modifier. results are stored in GameState
        input: entry:Skill/Spell, the specific skill/spell
               state:GameState
        output: state:GameState """
        attr_values = []
        attr_abbrs = []

        hero = self.heroes[state.current_hero]

        # from all available attributes get the 3 related to the entry being tested
        for attr in hero.attrs:
            for _, entry_attr in enumerate(entry.test):
                if attr.abbr == entry_attr:
                    attr_values.append(attr.value)
                    attr_abbrs.append(attr.abbr)

        # save original values in case a negative modifier lowers them
        attr_values_orig = attr_values

        state.value = entry.value

        modded_value = entry.value + state.mod

        # if the modifier lowers the skill/spell value below zero, the 3
        # related attributes get lowered by that value
        if modded_value < 0:
            attr_values = [x + modded_value for x in attr_values]

        if state.dice == "auto":
            state.rolls = self.roll_dice(3, 1, 20)

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
            entry_attr = SkillAttr(attr_abbrs[i], attr_values_orig[i], attr_values[i], remaining[i])
            state.attrs.append(entry_attr)

        return state

    def test_misc(self, state):
        """ used for misc dice sum tests, calculate result based on dice count,
        dice type and modifier. results are stored in GameState
        input: state:GameState
        output: state:GameState """
        state.result = 0
        dice_count = state.misc.dice_count
        dice_eyes = state.misc.dice_eyes

        if dice_count > 200:
#            print("Too many dice to roll")
            print(self.lang["too_many_dice"])
            return state

        if state.dice == "auto":
            state.rolls = self.roll_dice(dice_count, 1, dice_eyes)

        # create sum of all rolled dice and modifier
        for _, value in enumerate(state.rolls):
            state.result += value

        state.result += state.mod
        return state

    @staticmethod
    def roll_dice(dice_count, min_value, max_value):
        """ random number generator
        input: dice_count:int, how many numbers to generate
               min_value:int, lowest possible number
               max_value:int, highest possible number
        ouput: rolls:list, list of generated numbers """
        rolls = [random.randint(min_value, max_value) for i in range(dice_count)]
        return rolls

    def autocomplete(self, state):
        """ creates a list of hero entries (attributes, skills, spells, fight
        talents) that contain the user's test input and stores that list in
        GameState.option_list
        input: state:GameState
        output: state:GameState"""
        output_list = []

        try:
            hero = self.heroes[state.current_hero]
        except KeyError:
            # this can occur if (using the GUI) user types in a test before a
            # matching a hero file
#            print("KeyError, no hero matched")
            print(self.lang["key_error"])
            return state

        for attr in hero.attrs:
            if state.test_input.lower() in attr.name.lower():
                output_list.append([attr.name, "attr"])
        for skill in hero.skills:
            if state.test_input.lower() in skill.name.lower():
                output_list.append([skill.name, "skill"])
        for spell in hero.spells:
            if state.test_input.lower() in spell.name.lower():
                output_list.append([spell.name, "spell"])
        for fight_talent in hero.fight_talents:
            if state.test_input.lower() in fight_talent.name.lower():
                output_list.append([fight_talent.name, "fight_talent"])

        state.option_list = output_list
        return state

    def get_hero_list(self):
        """ create a list of all available hero files to show to user in interface
        output: outlist:list, list of hero names"""
        outlist = []
        for key, _ in self.heroes.items():
            outlist.append(key)
        outlist.sort()
        return outlist

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

        pattern = "^(\d+)[dDwW](\d+)([\+-]?)(\d*)$" #pylint: disable=anomalous-backslash-in-string
        match = re.match(pattern, state.test_input)
        if match and int(match.groups()[0]) > 0 and int(match.groups()[1]) > 0:
            matched = match.groups()
            state.category = "misc"
            state.misc = Misc(int(matched[0]), int(matched[1]))
            if matched[2] != '' and matched[3] != '':
                state.mod = int(matched[2] + matched[3])
            else:
                state.mod = 0

        if state.category != "misc":
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
        pattern = "^\d+$" #pylint: disable=anomalous-backslash-in-string
        outlist = []

        # attribute and fight talent tests take 1D20
        if state.category in ("attr", "fight_talent"):
            dice_count = 1
            dice_max = 20
        # skill and spell tests take 3D20
        elif state.category in ("skill", "spell"):
            dice_count = 3
            dice_max = 20
        # misc dice roll takes whatever was specified earlier
        elif state.category == "misc":
            dice_count = state.misc.dice_count
            dice_max = state.misc.dice_eyes

        # allow matches for dice separated by any number of whitespaces and commas
        rolls_string = rolls_string.replace(',', ' ')
        rolls_list = rolls_string.split(' ')

        for item in rolls_list:
            match = re.match(pattern, item)
            if match:
                if int(item) in range(1, dice_max + 1):
                    outlist.append(int(item))

        state.rolls = outlist

        if len(state.rolls) != dice_count:
            state.rolls = None

        return state