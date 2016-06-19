# -*- coding: utf-8 -*-

import quickexcel
import re
from semanteme import Semanteme

REPLACE_WORDS_FILE = 'replace.ini'

_replace_words = []


def _load_replace_words():
   '''
   读取替换配置文件
   '''
   global _replace_words
   _replace_words = []
   try:
      with open(REPLACE_WORDS_FILE) as f:
         lines = [line for line in f.readlines() if line.strip()]
      for line in lines:
         _replace_words.append(tuple([s.strip() for s in line.split(':')]))
   except:
      pass


_load_replace_words()


def replace(word):
   '''
   使用替换配置文件对单词进行替换
   '''
   for o, n in _replace_words:
      word = word.replace(o, n)
   return word


def loadTargetPoints(filename, startlinenum=1):
   '''
   读取目标点表txt文件，文件最后一列为点号
   返回：[(名称, 点号), ...]
   '''
   with open(filename) as f:
      txt = f.read()
   lines = [line.strip() for line in txt.split('\n') if line.strip()]
   target_points = []
   for line in lines[startlinenum:]:
      p = line.split()
      target_points.append((' '.join(p[:-1]), int(p[-1])))
   return target_points


def loadSourcePoints(filename):
   '''
   读取源点表excel文件，从单元格A1开始，第一列为点号，第二列为名称
   返回：[(名称, 点号), ...]
   '''
   excelapp = quickexcel.ExApp()
   excelapp.visible = True
   wb = excelapp.getworkbook(filename)
   ws = wb.getworksheet(1)
   i = 1
   point_number_set = set()
   result = []
   doubleponit = set()
   while True:
      try:
         point_number = ws.gettext('A%s' % i).strip()
      except:
         raise Exception(u'解析到第%s行出现错误！' % i)
      try:
         if point_number == '':
            break
         else:
            point_number = int(point_number)
      except:
         raise Exception(u'源信息点表有错误，第%s行点号无法解析！' % i)
      try:
         point_name = replace(ws.gettext('B%s' % i).strip())
      except:
         raise Exception(u'解析到第%s行出现错误！' % i)
      if point_number in point_number_set:
         doubleponit.add(point_number)
      point_number_set.add(point_number)
      result.append((point_name, point_number))
      i += 1
   if doubleponit:
      raise Exception(u'源信息点表有错误，包含相同的点号：\n%s' % str(list(doubleponit)))
   return result


def getOrderSource(sentence, sourcepoints):
   '''
   根据源点表，得到一个句子的排序源点表，该源点表从最有可能到可能性最小排序
   '''
   if sentence:
      sem = Semanteme(sentence)
      return sem.getOrderList(sourcepoints)
   else:
      return sourcepoints


def filterSource(condition_include, condition_outclude, sourcepoints):
   '''
   根据字符串条件过滤源
   '''
   condition_include = condition_include.strip()
   condition_outclude = condition_outclude.strip()
   if not condition_include and not condition_outclude:
      return sourcepoints
   r = set()

   def getregexes(condition):
      words = condition.split()
      return [re.compile(word, re.I) for word in words]

   cs1 = getregexes(condition_include)
   cs2 = getregexes(condition_outclude)
   for point in sourcepoints:
      sentence, num = point
      flag = True
      for c in cs1:
         flag = flag and c.findall(sentence)
      for c in cs2:
         flag = flag and not c.findall(sentence)
      if flag:
         r.add((sentence, num))
   return [point for point in sourcepoints if point in r]
