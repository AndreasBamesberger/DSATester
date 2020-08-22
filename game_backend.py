""" DSA rules for testing, called upon by interfaces """
import random # for dice rolls
import csv # to write into file
import os.path # to check if file already exists
import datetime # to log time of dice roll
import xml.etree.ElementTree as ET # to parse input xml file
from collections import namedtuple
from dataclasses import dataclass # to create GameState
import operator # to subtract list from list
from DSA_data import Attribute, Skill, Spell, FightTalent

@dataclass
class GameState:
    """ dataclass used to transfer state of game between GameLogic and interfaces """
    done: bool = False        # exit when True (currently not used)
    save: bool = False        # export roll to csv if True (currently not used)
    dice: str = None          # "auto" or "manual" whether dice rolls are input or calculated
    counter: int = 1          # increases with every saved dice roll
    category: str = None      # "attr"/"skill"/"spell"/"misc"
    name: str = None          # name of tested attr/skill/spell
    attrs: tuple = None       # 1-3 attrs related to skill, spell
    value: int = None         # value related to attr/skill/spell
    mod: int = None           # test modifier input by user
    rolls: tuple = None       # calculated or manually input dice rolls
    result: int = None        # success if >= 0
    misc: tuple = None        # dice count and eyes on dice
    desc: str = None          # text to save in csv
    first_input: str = None   # user input to match tests to or declare misc test
    option_list: tuple = None # list of tests matching first input
    selection: list = None    # single entry from option_list


SkillAttr = namedtuple("SkillAttr", ["abbr", "value", "modified", "remaining"])

class GameLogic:
    """ DSA rules for testing, called upon by interfaces """
    def __init__(self):
        random.seed(a=None, version=2)
        self.hero_xml = None
        self.result_csv = None
        self.dice = "auto"

        self.read_config("config.txt")
        self.setup_output_file()
        self.root = self.parse_xml()

        self.attributes = self.read_attributes()
        self.skills = self.read_skills()
        self.spells = self.read_spells()
        self.fight_talents = self.read_fight_talents()

    def read_config(self, configname):
        """ input = string, name of config-file. scans config-file for names of
        input and output files """
        with open(configname, "r", encoding="utf-8") as configfile:
            for line in configfile.readlines():
                if line.startswith('#'):
                    continue
                if "input file" in line:
                    split = line.split()
                    self.hero_xml = split[-1]

                if "output file" in line:
                    split = line.split()
                    self.result_csv = split[-1]

    def parse_xml(self):
        """open and parse xml file with hero data"""

        # get input file from config
        # line should be something like: "input file: heroname.xml"

        tree = ET.parse(self.hero_xml)
        root = tree.getroot()
        return root

    def setup_output_file(self):
        """ prepares first line of output CSV if necessary """

        columns = ["Hero file",
                   "Test type",
                   "Rolls",
                   "Attribute/Skill",
                   "Attribute/Skill value",
                   "Modifier",
                   "Result",
                   "Description",
                   "Timestamp"]

        # if file does not exist, add first row of column names
        if not os.path.isfile(self.result_csv):
            with open(self.result_csv, "w", encoding="utf-8") as csvfile:
                filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL) #pylint: disable=line-too-long
                filewriter.writerow(columns)

    def save_to_csv(self, state):
        """add roll results to csv file"""
        if state.rolls == [] or state.rolls is None:
            return state
        timestamp = datetime.datetime.now()

        desc = f"Roll#{state.counter}: {state.desc}"
        desc = desc.replace(",", ";")

        printable_rolls = "; ".join(map(str, state.rolls))

        save_values = [self.hero_xml,
                       state.category,
                       printable_rolls,
                       state.name,
                       state.value,
                       state.mod,
                       state.result,
                       desc,
                       timestamp]

        with open(self.result_csv, "a", encoding="utf-8") as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL) #pylint: disable=line-too-long
            filewriter.writerow(save_values)

        state.counter += 1

        return state

    def write_all(self):
        """dump all information of xml file into txt"""
        #TODO: fix lebensenergie, ausdauer, magieresistenz, ini
        with open("dump.txt", "w", encoding="utf-8") as dumpfile:
            for i in range(len(self.root)): #pylint: disable=consider-using-enumerate
                for j in range(len(self.root[i])):
                    for k in range(len(self.root[i][j])):
                        output = "root[{0}][{1}][{2}]: {3}, {4}\n".format(i, j, k, self.root[i][j][k].tag, self.root[i][j][k].attrib) #pylint: disable=invalid-name, line-too-long
                        dumpfile.write(output)

    def read_attributes(self):
        """return list [name, value], eg: ['Mut', 15]"""
        output_list = []
        for i in range(len(self.root[0][2])):
            attr = Attribute(self.root[0][2][i])
            output_list.append(attr)
        return output_list

    def read_skills(self):
        """return list [name, value, test1, test2, test3, handicap], eg: ['Zechen', 6, 'IN', 'KO', 'KK', 0]""" #pylint: disable=line-too-long

        output_list = []
        for i in range(len(self.root[0][6])):
    #        skill = Skill(root[0][6][i])
            output_list.append(Skill(self.root[0][6][i]))

        return output_list

    def read_spells(self):
        output_list = []
        for i in range(len(self.root[0][7])):
            output_list.append(Spell(self.root[0][7][i]))
        return output_list

    def read_fight_talents(self):
        output_list = []
        for i in range(len(self.root[0][8])):
            output_list.append(FightTalent(self.root[0][8][i], "AT"))
            output_list.append(FightTalent(self.root[0][8][i], "PA"))
        return output_list

    def test(self, state):
        if state.dice == "manual" and (state.rolls is None or state.rolls == []):
            return state

        if state.category == "attr":
            for attr in self.attributes:
                if state.name == attr.name:
                    state = self.test_attr(attr, state)
        if state.category == "fight_talent":
            for fight_talent in self.fight_talents:
                if state.name == fight_talent.name:
                    state = self.test_fight_talent(fight_talent, state)
        elif state.category == "skill":
            for skill in self.skills:
                if state.name == skill.name:
                    state = self.test_skill(skill, state)
        elif state.category == "spell":
            for spell in self.spells:
                if state.name == spell.name:
                    state = self.test_skill(spell, state)
        elif state.category == "misc":
            state = self.test_misc(state)

        return state

    def test_attr(self, attr, state):
        state.value = attr.value
        if state.dice == "auto":
            state.rolls = self.roll_dice(1, 1, 20)

        state.result = attr.value + state.mod - state.rolls[0]
        return state

    def test_fight_talent(self, fight_talent, state):
        state.value = fight_talent.value
        if state.dice == "auto":
            state.rolls = self.roll_dice(1, 1, 20)
        state.result = state.value + state.mod - state.rolls[0]
        return state

    def test_skill(self, skill, state):
        attr_values = []
        attr_abbrs = []

        for attr in self.attributes:
            for _, skill_attr in enumerate(skill.test):
                if attr.abbr == skill_attr:
                    attr_values.append(attr.value)
                    attr_abbrs.append(attr.abbr)

        attr_values_orig = attr_values

        state.value = skill.value
        modded_value = skill.value + state.mod

        if modded_value < 0:
            attr_values = [x + modded_value for x in attr_values]

        if state.dice == "auto":
            state.rolls = self.roll_dice(3, 1, 20)

        remaining = list(map(operator.sub, attr_values, state.rolls))

        state.result = modded_value if modded_value > 0 else 0

        for _, attr_value in enumerate(remaining):
            if attr_value < 0:
                state.result += attr_value

        state.attrs = []
        for i in range(3):
            skill_attr = SkillAttr(attr_abbrs[i], attr_values_orig[i], attr_values[i], remaining[i])
            state.attrs.append(skill_attr)

        return state

    def test_misc(self, state):
        state.result = 0
        dice_count, dice_eyes = state.misc

        state.rolls = self.roll_dice(dice_count, 1, dice_eyes)

        for _, value in enumerate(state.rolls):
            state.result += value

        state.result += state.mod
        return state

    def roll_dice(self, dice_count, min_value, max_value):
        rolls = [random.randint(min_value, max_value) for i in range(dice_count)]
        return rolls

    def autocomplete(self, state):
        output_list = []

        for attr in self.attributes:
            if state.first_input.lower() in attr.name.lower() or state.first_input in attr.abbr:
                if attr.name in ("at", "pa"):
                    continue
                output_list.append([attr.name, "attr"])
        for skill in self.skills:
            if state.first_input.lower() in skill.name.lower():
                output_list.append([skill.name, "skill"])
        for spell in self.spells:
            if state.first_input.lower() in spell.name.lower():
                output_list.append([spell.name, "spell"])

        for fight_talent in self.fight_talents:
            if state.first_input.lower() in fight_talent.name.lower():
                output_list.append([fight_talent.name, "fight_talent"])

        state.option_list = output_list
        return state
