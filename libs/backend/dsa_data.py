"""
This file features a class for every hero entry that is covered by
DSATester.
"""
import re

abbr = {'Mut': 'MU',
        'Klugheit': 'KL',
        'Intuition': 'IN',
        'Charisma': 'CH',
        'Fingerfertigkeit': 'FF',
        'Gewandtheit': 'GE',
        'Konstitution': 'KO',
        'Körperkraft': 'KK'}


def match_attrs(attrs_string):
    """
    The attributes related to a skill test are stored as 3 abbreviations,
    e.g. " (KL/IN/CH)", this function separates them into a list with 3 entries.
    The string always starts with a whitespace.

    Parameters:
        attrs_string (str): The string from the xml file

    Returns:
        output_list (list): The 3 separated values
    """

    # regex: " (KL/IN/CH)" -> KL, IN, CH
    # ^, $: match from start to end of string
    # \s*: match any number of whitespaces
    # \(, \): match the parentheses around the expression
    # .{2}: match any two characters
    pattern = r'^\s*\((.{2})/(.{2})/(.{2})\)$'
    output_list = None

    match = re.match(pattern, attrs_string)
    if match:
        output_list = [value for _, value in enumerate(match.groups())]

    return output_list


class Misc:
    """
    Class for misc dice sum tests

    ...

    Attributes
    ----------
    name: str
        Name of the test, in this case None
    value: int
        Value of the tested hero entry, in this case None
    category: str
        What kind of test is executed
    dice_count: int
        How many dice should be rolled
    dice_eyes: int
        What kind of dice should be rolled
    """

    def __init__(self, dice_count, dice_eyes):
        self.name = None
        self.value = None
        self.category = "misc"
        self.dice_count = dice_count
        self.dice_eyes = dice_eyes

    def __repr__(self):
        out_string = (f"Dice sum test\n"
                      f"\tdice count: {self.dice_count}\n"
                      f"\tdice eyes:  {self.dice_eyes}\n")
        return out_string


class Attribute:
    """
    Class for attributes like Mut, Klugheit, etc.

    ...

    Attributes
    ----------
    name: str
        Name of the test
    value: int
        Value of the tested hero entry, value from xml file plus modifier
    category: str
        What kind of test is executed
    start: int
        Start value of the attribute, when character was created
    mod: int
        Modifier for attribute, e.g. increased using experience
    dict_value: int
        Value of attribute read from xml file, without modifier
    meditation: int
        ?Change of attribute value due to meditation, not used?
    mrmod: int
        Magic resist modifier, not used
    karmal: int
        ?Additional karma points from going on karma quests, not used?
    abbr: str
        Abbreviation of the attribute, e.g. "KL" for Klugheit
    """

    def __init__(self, attr_entry):
        self.category = "attr"
        attr_dict = attr_entry.attrib
        # not every attribute entry has all of these values
        try:
            self.name = attr_dict['name']
        except KeyError:
            self.name = ""
        try:
            self.start = int(attr_dict['startwert'])
        except KeyError:
            self.start = None
        try:
            self.mod = int(attr_dict['mod'])
        except KeyError:
            self.mod = None
        try:
            self.dict_value = int(attr_dict['value'])
        except KeyError:
            self.dict_value = None
        try:
            self.meditation = int(attr_dict['grossemeditation'])
        except KeyError:
            self.meditation = None
        try:
            self.mrmod = int(attr_dict['mrmod'])
        except KeyError:
            self.mrmod = None
        try:
            self.karmal = int(attr_dict['karmalqueste'])
        except KeyError:
            self.karmal = None

        # some attribute values change over time, this change is saved in
        # attr_dict['mod']
        if self.dict_value is not None and self.mod is not None:
            self.value = self.dict_value + self.mod

        self.abbr = ""
        if self.name != '':
            try:
                self.abbr = abbr[self.name]
            except KeyError:
                pass

    def __repr__(self):
        out_string = (f"\tname: {self.name} ({self.abbr})\n"
                      f"\tcategory: {self.category}\n"
                      f"\tstart: {self.start}\n"
                      f"\tmod:  {self.mod}\n"
                      f"\tdict_value: {self.dict_value}\n"
                      f"\tmeditation: {self.meditation}\n"
                      f"\tmrmod: {self.mrmod}\n"
                      f"\tkarmal: {self.karmal}\n"
                      f"\tvalue: {self.value}\n")
        return out_string


class Skill:
    """
    Class for attributes like Mut, Klugheit, etc.

    ...

    Attributes
    ----------
    name: str
        Name of the test
    value: int
        Value of the tested hero entry, value from xml file plus modifier
    category: str
        What kind of test is executed
    learn: str
        How the skill was learned, not used
    dict_tests: str
        String holding the (usually) 3 attributes to test the skill, leading
        with a whitespace, e.g. " ( KL/IN/CH)"
    attrs: list
        List holding the 3 attribute abbreviations extracted from dict_tests,
        e.g. ["KL", "IN", "CH"]
    handicap: str
        How handicap from equipment influences the skill test, e.g. "BEx2",
        not used
    """

    def __init__(self, skill_entry):
        self.category = "skill"
        skill_dict = skill_entry.attrib

        # not every attribute entry has all of these values
        try:
            self.learn = skill_dict['lernmethode']
        except KeyError:
            self.learn = None
        try:
            self.name = skill_dict['name']
        except KeyError:
            self.name = ""
        try:
            self.dict_tests = skill_dict['probe']
        except KeyError:
            self.dict_tests = None
        try:
            self.value = int(skill_dict['value'])
        except KeyError:
            self.value = None

        if self.dict_tests is not None:
            self.attrs = match_attrs(self.dict_tests)

        try:
            self.handicap = skill_dict["be"]
        except KeyError:
            self.handicap = None

    def __repr__(self):
        out_string = (f"\tname: {self.name}\n"
                      f"\tcategory: {self.category}\n"
                      f"\tlearn: {self.learn}\n"
                      f"\tdict_tests: {self.dict_tests}\n"
                      f"\tvalue: {self.value}\n"
                      f"\ttest1: {self.attrs[0]}\n"
                      f"\ttest2: {self.attrs[1]}\n"
                      f"\ttest3: {self.attrs[2]}\n"
                      f"\tbe: {self.handicap}\n")
        return out_string


class Spell:
    """
    Class for spells like Attributo, Radau, etc.

    ...

    Attributes
    ----------
    name: str
        Name of the test
    value: int
        Value of the tested hero entry, value from xml file plus modifier
    category: str
        What kind of test is executed
    comments: str
        Additional notes for this entry, not used
    origin: str
        ?Where/How the spell was learned, what tradition, not used?
    k: str
        ?I don't know, it's in the xml and was extracted, not used?
    cost: str
        Spell cost, not used
    learn: str
        How the skill was learned, not used
    range: str
        Spell range, not used
    representation: str
        ?Representation of the spell, not used?
    variant: str
        ?Spell variant, not used?
    effect_time: str
        How long spell lasts, not used
    charge_time: str
        How long until spell is ready
    comment: str
        Another additional note for the spell, not used
    dict_tests: str
        String holding the (usually) 3 attributes to test the skill, leading
        with a whitespace, e.g. " ( KL/IN/CH)"
    attrs: list
        List holding the 3 attribute abbreviations extracted from dict_tests,
        e.g. ["KL", "IN", "CH"]
    """

    def __init__(self, spell_entry):
        self.category = "spell"
        spell_dict = spell_entry.attrib

        # not every attribute entry has all of these values
        try:
            self.comments = spell_dict['anmerkungen']
        except KeyError:
            self.comments = None
        try:
            self.origin = spell_dict['hauszauber']
        except KeyError:
            self.origin = None
        try:
            self.k = spell_dict['k']
        except KeyError:
            self.k = None
        try:
            self.cost = spell_dict['kosten']
        except KeyError:
            self.cost = None
        try:
            self.learn = spell_dict['lernmethode']
        except KeyError:
            self.learn = None
        try:
            self.name = spell_dict['name']
        except KeyError:
            self.name = ""
        try:
            self.dict_tests = spell_dict['probe']
        except KeyError:
            self.dict_tests = None
        try:
            self.range = spell_dict['reichweite']
        except KeyError:
            self.range = None
        try:
            self.representation = spell_dict['repraesentation']
        except KeyError:
            self.representation = None
        try:
            self.value = int(spell_dict['value'])
        except KeyError:
            self.value = None
        try:
            self.variant = spell_dict['variante']
        except KeyError:
            self.variant = None
        try:
            self.effect_time = spell_dict['wirkungsdauer']
        except KeyError:
            self.effect_time = None
        try:
            self.charge_time = spell_dict['zauberdauer']
        except KeyError:
            self.charge_time = None
        try:
            self.comment = spell_dict['zauberkommentar']
        except KeyError:
            self.comment = None

        if self.dict_tests is not None:
            self.attrs = match_attrs(self.dict_tests)

    def __repr__(self):
        out_string = (f"\tname: {self.name}\n"
                      f"\tcategory: {self.category}\n"
                      f"\tcomments: {self.comments}\n"
                      f"\torigin: {self.origin}\n"
                      f"\tk: {self.k}\n"
                      f"\tcost: {self.cost}\n"
                      f"\tlearn: {self.learn}\n"
                      f"\tdict_tests: {self.dict_tests}\n"
                      f"\trange: {self.range}\n"
                      f"\trepresentation: {self.representation}\n"
                      f"\tvalue: {self.value}\n"
                      f"\tvariant: {self.variant}\n"
                      f"\teffect_time: {self.effect_time}\n"
                      f"\tcharge_time: {self.charge_time}\n"
                      f"\tcomment: {self.comment}\n"
                      f"\ttest1: {self.attrs[0]}\n"
                      f"\ttest2: {self.attrs[1]}\n"
                      f"\ttest3: {self.attrs[2]}\n")
        return out_string


class FightTalent:
    """
    Class for fight talents like Raufen, Hiebwaffen, etc.

    ...

    Attributes
    ----------
    name: str
        Name of the test
    value: int
        Value of the tested hero entry, value from xml file plus modifier
    category: str
        What kind of test is executed
    """

    def __init__(self, fight_entry, mode):
        self.category = "fight_talent"
        # for every fight talent, offensive and defensive tests are possible
        # so every fight talent has 2 entries
        if mode == "AT":
            try:
                self.name = "AT " + fight_entry.attrib["name"]
            except KeyError:
                self.name = None
            try:
                self.value = int(fight_entry[0].attrib["value"])
            except KeyError:
                self.value = None
        elif mode == "PA":
            try:
                self.name = "PA " + fight_entry.attrib["name"]
            except KeyError:
                self.name = None
            try:
                self.value = int(fight_entry[1].attrib["value"])
            except KeyError:
                self.value = None

    def __repr__(self):
        out_string = (f"\tname: {self.name}\n"
                      f"\tcategory: {self.category}\n"
                      f"\tvalue: {self.value}\n")
        return out_string


class Advantage:
    """
    Class for (dis)advantages like Goldgier, Neugier, etc.

    ...

    Attributes
    ----------
    name: str
        Name of the test
    value: int
        Value of the tested hero entry, value from xml file plus modifier
    category: str
        What kind of test is executed
    """

    def __init__(self, advantage_entry):
        self.category = "advantage"
        # example structure of advantages
        # <vt>
        #    <vorteil name="Vollzauberer"/>
        #    <vorteil name="Feste Gewohnheit"/>
        #    <vorteil name="Jähzorn" value="6"/>
        #    <vorteil name="Randgruppe"/>
        #    <vorteil name="Vorurteile gegen">
        #        <auswahl position="0" value="6"/>
        #        <auswahl position="1" value="Misstrauen gegen Obrigkeit"/>
        #    </vorteil>
        # </vt>

        try:
            self.name = advantage_entry.attrib["name"]
        except KeyError:
            self.name = None
        try:  # if this works then entry is a "vorurteile gegen"
            try:
                self.value = int(advantage_entry[0].attrib["value"])
            except KeyError:
                self.value = None
            try:
                self.name += ": " + advantage_entry[1].attrib["value"]
            except KeyError:
                pass
        except IndexError:
            try:
                self.value = int(advantage_entry.attrib["value"])
            except KeyError:
                self.value = None

    def __repr__(self):
        out_string = (f"\tname: {self.name}\n"
                      f"\tcategory: {self.category}\n"
                      f"\tvalue: {self.value}\n")
        return out_string


class SpecialSkill:
    """
    Class for special skills like Kulturkunde, Wuchtschlag, etc.

    ...

    Attributes
    ----------
    name: str
        Name of the test
    value: int
        Value of the tested hero entry, value from xml file plus modifier
    category: str
        What kind of test is executed
    """

    def __init__(self, special_skill_entry):
        self.category = "special_skill"
        # example structure of special skills
        # <sf>
        #    <sonderfertigkeit name="Ausweichen I"/>
        #    <sonderfertigkeit name="Kulturkunde">
        #        <kultur name="Orks"/>
        #    </sonderfertigkeit>
        #    <sonderfertigkeit name="Sturmangriff"/>
        #    <sonderfertigkeit name="Waldkundig"/>
        #    <sonderfertigkeit name="Wuchtschlag"/>
        # </sf>

        try:
            self.name = special_skill_entry.attrib["name"]
        except KeyError:
            self.name = None
        try:  # if this works then entry is a "vorurteile gegen"
            for _, value in enumerate(special_skill_entry):
                self.name += ", " + value.attrib["name"]
        except IndexError:
            try:
                self.value = int(special_skill_entry.attrib["value"])
            except KeyError:
                self.value = None

    def __repr__(self):
        out_string = (f"\tname: {self.name}\n"
                      f"\tcategory: {self.category}\n")
        return out_string
