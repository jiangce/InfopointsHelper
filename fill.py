# -*- coding: utf-8 -*-

import autopy.key as key
import autopy.mouse as mouse
import time


def simkey_type_words(pos, words, interal=0.1):
    mouse.move(*pos)
    mouse.click()
    for word in words:
        time.sleep(interal)
        key.tap('a', key.MOD_CONTROL)
        time.sleep(interal)
        key.type_string(word)
        key.tap(key.K_RETURN)


def get_type_pos():
    input('请将鼠标光标移至将要填写的单元格位置（但不要点击），然后按Enter键……')
    return mouse.get_pos()


if __name__ == '__main__':
    import sys

    l = 70
    print('#' * l)
    print('欢迎使用键盘模拟批量输入程序\t作者：姜策')
    print('#' * l)
    try:
        filename = sys.argv[1]
        with open(filename) as f:
            lines = f.readlines()
        words = [line.split()[0] for line in lines]
        pos = get_type_pos()
        cnt = input('模拟键盘的批量输入将开始，请确认是否继续？(y/n)').lower()
        if cnt == 'y':
            simkey_type_words(pos, words)
    except:
        print('出错，请检查后重试')