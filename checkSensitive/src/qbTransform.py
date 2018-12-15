#encoding:utf-8
from __future__ import division

import sys

reload(sys)
sys.setdefaultencoding('utf-8')
# sys.path.append('/Users/luyao/anaconda/lib/python2.7/site-packages')


def strQ2B(ustring):
    """全角转半角"""
    rstring = ""
    if type(ustring)=='unicode':
        pass
    else:
        ustring=ustring.decode('utf-8')
    for uchar in ustring:
        inside_code = ord(uchar)
        if inside_code == 12288:  #全角空格直接转换
            inside_code = 32
        elif (inside_code >= 65281 and inside_code <= 65374):  # 全角字符（除空格）根据关系转化
            inside_code -= 65248

        rstring += unichr(inside_code)
    return rstring


def strB2Q(ustring):
    """半角转全角"""
    rstring = ""
    if type(ustring)=='unicode':
        pass
    else:
        ustring=ustring.decode('utf-8')
    for uchar in ustring:
        inside_code = ord(uchar)
        if inside_code == 32:  # 半角空格直接转化
            inside_code = 12288
        elif inside_code >= 32 and inside_code <= 126:  # 半角字符（除空格）根据关系转化
            inside_code += 65248

        rstring += unichr(inside_code)
    return rstring

"""
chr()函数用一个范围在range（256）内的（就是0～255）整数作参数，返回一个对应的字符。
unichr()跟它一样，只不过返回的是Unicode字符。
ord()函数是chr()函数（对于8位的ASCII字符串）或unichr()函数（对于Unicode对象）的配对函数，
它以一个字符（长度为1的字符串）作为参数，返回对应的ASCII数值，或者Unicode数值。
"""


# b = strQ2B(u"ｍｎ123abc博客 园") #全角转半角
# print b #mn123abc博客园
#
# c = strB2Q(u"ｍｎ123abc 博客 园") #半角转全角
# print c #ｍｎ１２３ａｂｃ博客园
#
# e = strQ2B(u"I have a pen")
# print e #I have a pen
#
# d = strB2Q(u"I have a pen")
# print d #Ｉ　ｈａｖｅ　ａ　ｐｅｎ




