from random import shuffle
from yyagl.gameobject import GameObject


class ThanksNames(GameObject):

    @staticmethod
    def get_thanks(num, level):
        names, curr_level, curr_path = [], 5, ThanksNames.eng.curr_path
        while len(names) < num or curr_level >= level:
            fname = curr_path + 'assets/thanks%s.txt' % curr_level
            curr_names = open(fname).readlines()
            if curr_level >= level:
                names += curr_names
            else:
                shuffle(curr_names)
                names += curr_names[:num - len(names)]
            curr_level -= 1
        shuffle(names)
        return [name.strip() for name in names[:num]]

    @staticmethod
    def get_all_thanks():
        names = []
        for i in range(5, 1, -1):
            tfile = ThanksNames.eng.curr_path + 'assets/thanks%s.txt' % i
            names += [name.strip() for name in open(tfile).readlines()]
        return names
