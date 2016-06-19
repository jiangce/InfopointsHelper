# -*- coding: utf-8 -*-

import jieba
from fuzzywuzzy import fuzz

USER_DICT_FILE = 'dict.ini'

jieba.load_userdict(USER_DICT_FILE)


class Semanteme(object):
    '''
    解析目标点名称语意的类
    '''

    def __init__(self, sentence):
        self.sentence = sentence.strip()
        self.fenci = ' '.join(jieba.cut(self.sentence))

    def getOrderList(self, points):
        '''
        查询一系列句子，返回一个顺序排列的点表，顶端是可能性最大的
        points: [(名称, 点号), ...]
        '''
        order = []
        for point in points:
            order.append((point, fuzz.ratio(self.fenci, Semanteme(point[0]).fenci)))
        order.sort(key=lambda x: x[1], reverse=True)
        return [item[0] for item in order]


if __name__ == '__main__':
    s = '西安图迹信息科技有限公司'
    t1 = ('湖南大唐先一科技有限公司', 1)
    t2 = ('西安汇能科技有限公司', 2)
    sem = Semanteme(s)
    for name, id in sem.getOrderList([t1, t2]):
        print(id, name)