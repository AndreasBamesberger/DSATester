""" this module tests GameLogic.roll_dice() """

from game_backend import GameLogic

if __name__ == '__main__':

    dice_count = 100000000 # pylint: disable=invalid-name
    min_value = 1 # pylint: disable=invalid-name
    max_value = 20 # pylint: disable=invalid-name

    rolls = GameLogic.roll_dice(dice_count, min_value, max_value)

    print(repr(len(rolls)) + " dice rolls")

    outlist = []
    for i in range(max_value):
        outlist.append(0)

    for index, value in enumerate(rolls):
        outlist[value-1] += 1

    for i in range(max_value):
        print("{0:2d}: {1:d}, {2:3.4f}%".format(i+1, outlist[i], (outlist[i]/dice_count)*100))
