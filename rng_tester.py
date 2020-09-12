""" this module tests GameLogic.roll_dice() """
from libs.backend.dsa_game import GameLogic

if __name__ == '__main__':
    test_count = 10000000  # pylint: disable=invalid-name
    dice_count = 3  # pylint: disable=invalid-name
    min_value = 1  # pylint: disable=invalid-name
    max_value = 20  # pylint: disable=invalid-name

    rolls = [GameLogic._roll_dice(dice_count, min_value, max_value) for i in range(test_count)]

    print(repr(len(rolls)) + " dice rolls")
    #    print(repr(rolls))

    out_list = []
    for i in range(max_value):
        out_list.append(0)

    for index, value in enumerate(rolls):
        for i, v in enumerate(rolls[index]):
            out_list[v - 1] += 1

    for i in range(max_value):
        print("{0:2d}: {1:d}, {2:3.4f}%".format(i + 1, out_list[i], (
                    out_list[i] / (dice_count * test_count)) * 100))  # pylint: disable=line-too-long
