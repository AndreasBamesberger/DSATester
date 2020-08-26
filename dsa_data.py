""" this module features a class for every hero entry that is covered by DSATester """
abbr = [['Mut', 'MU'],
        ['Klugheit', 'KL'],
        ['Intuition', 'IN'],
        ['Charisma', 'CH'],
        ['Fingerfertigkeit', 'FF'],
        ['Gewandtheit', 'GE'],
        ['Konstitution', 'KO'],
        ['Körperkraft', 'KK']]

class Attribute:
    """object for attributes like Mut, Klugheit etc"""
    def __init__(self, attr_entry):
        attr_dict = attr_entry.attrib

#        for key, field in attr_dict.items():
#            print(repr(key), repr(field))
#        print("---")

#TODO: rework this
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

        if self.dict_value is not None and self.mod is not None:
            self.value = self.dict_value + self.mod

        self.abbr = ""
        if self.name is not None:
            for ab in abbr:
                if self.name == ab[0]:
                    self.abbr = ab[1]

    def __repr__(self):
        outstring = (f"{self.name} ({self.abbr})\n"
                     f"\tstart: {self.start}\n"
                     f"\tmod:  {self.mod}\n"
                     f"\tdict_value: {self.dict_value}\n"
                     f"\tmeditation: {self.meditation}\n"
                     f"\tmrmod: {self.mrmod}\n"
                     f"\tkarmal: {self.karmal}\n"
                     f"\tvalue: {self.value}\n")
        return outstring

class Skill:
    """object for skills like Zechen, Schwimmen etc"""
    def __init__(self, skill_entry):
        skill_dict = skill_entry.attrib

#        for key, field in skill_dict.items():
#            print(repr(key), repr(field))
#        print("---")

#TODO: rework this
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
            self.test = [self.dict_tests[2:4],
                         self.dict_tests[5:7],
                         self.dict_tests[8:10]]
        try:
            self.handicap = skill_dict["be"]
        except KeyError:
            self.handicap = None

    def __repr__(self):
        outstring = (f"{self.name}\n"
                     f"\tlearn: {self.learn}\n"
                     f"\tdict_tests: {self.dict_tests}\n"
                     f"\tvalue: {self.value}\n"
                     f"\ttest1: {self.test[0]}\n"
                     f"\ttest2: {self.test[1]}\n"
                     f"\ttest3: {self.test[2]}\n"
                     f"\tbe: {self.handicap}\n")
        return outstring

class Spell:
    """object for spells"""
    def __init__(self, spell_entry):
        spell_dict = spell_entry.attrib

#        for key, field in spell_dict.items():
#            print(repr(key), repr(field))
#        print("---")

#TODO: rework this
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
            self.test = [self.dict_tests[2:4],
                         self.dict_tests[5:7],
                         self.dict_tests[8:10]]

    def __repr__(self):
        outstring = (f"{self.name}\n"
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
                     f"\ttest1: {self.test[0]}\n"
                     f"\ttest2: {self.test[1]}\n"
                     f"\ttest3: {self.test[2]}\n")
        return outstring

class FightTalent:
    """ object for fight talents like raufen, ringen, hiebwaffen """
    def __init__(self, fight_entry, mode):
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
        outstring = (f"{self.name}\n"
                     f"\tvalue: {self.value}\n")
        return outstring
