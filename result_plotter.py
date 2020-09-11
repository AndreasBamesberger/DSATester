""" visualise results from csv file """
import csv
from collections import namedtuple
from matplotlib import pyplot as plt

Test = namedtuple("Test", ["file", "category", "name",
                           "misc_count", "misc_eyes",
                           "value", "mod", "attrs",
                           "rolls", "result", "desc",
                           "time", "dice"])

test_list = []

name_dict = {}

roll_dict = {}

with open("output.csv") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            line_count += 1
        else:
            hero_file = row[0]
            category = row[1]
            name = row[2]
            misc_count = None
            misc_eyes = None
            if row[3] != '':
                misc_count, misc_eyes = row[3].split("D")
                misc_count = int(misc_count)
                misc_eyes = int(misc_eyes)
            value = row[4]
            mod = row[5]
            attrs = row[6]
            rolls = row[7].replace(' ', '').split(";")
            rolls = list(map(int, rolls))
            result = row[8]
            desc = row[9]
            time = row[10]
            dice = row[11]

            test_list.append(Test(hero_file, category, name,
                                  misc_count, misc_eyes,
                                  value, mod, attrs,
                                  rolls, result, desc,
                                  time, dice))

for test in test_list:
    if test.category not in ("attr", "skill", "spell", "fight_talent", "advantage"):
        continue
    try:
        name_dict[test.name] += 1
    except KeyError:
        name_dict.update({test.name: 1})

    if test.dice != "auto":
        continue

    for roll in test.rolls:
        try:
            roll_dict[roll] += 1
        except KeyError:
            roll_dict.update({roll: 1})


roll_dict_keys = sorted(roll_dict)
roll_dict_values = [value for (key, value) in sorted(roll_dict.items())]

plt.bar(roll_dict_keys, roll_dict_values)
plt.show()
