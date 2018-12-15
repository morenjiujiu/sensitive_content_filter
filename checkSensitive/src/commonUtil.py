#encoding:utf-8
from __future__ import division

import sys

reload(sys)
sys.setdefaultencoding('utf-8')
# sys.path.append('/Users/luyao/anaconda/lib/python2.7/site-packages')
import re



def getReg(txt_convert):
    """
    对文本进行正则过滤，检测广告、链接等信息
    :param txt: 文本
    :return: 正则过滤后的文本
    """
    url_patten = r"([^\s]+(\.com))|([a-zA-z]+://[^\s]*)" #http://xxx, www.xxxx.com, 1234@qq.com
    html_patten=r"<(\S*?)[^>]*>.*?|<.*? />"
    qq_phone_patten=r"[1-9][0-9]{4,}" #第一位1-9之间的数字，第二位0-9之间的数字，大于1000号
    wx_patten=r"[a-zA-Z][a-zA-Z0-9_-]{5,19}$"

    if re.findall(url_patten,txt_convert).__len__()>0:
        result = u"疑似[网页链接或邮箱]"
    elif re.findall(html_patten,txt_convert).__len__()>0:
        result = u"疑似[html脚本]"
    elif re.findall(qq_phone_patten,txt_convert).__len__()>0:
        result = u"疑似[QQ号或手机号]"
    elif re.findall(wx_patten,txt_convert).__len__()>0:
        result = u"疑似[微信号]"
    else:
        result = u"非广告文本"
    return result



def calcScore(sensitiveWordStr):
    b=sensitiveWordStr
    b1=b.split(",")
    b2=[i.split(":")[0] for i in b1 if len(i) > 1]

    score = 0
    for x in b2:
        if x in (u"毒品", u"色情", u"赌博"):
            score += 5
        elif x in (u"政治", u"反动", u"暴恐"):
            score += 4
        elif x == u"社会":
            score += 3
        else: #其他
            score += 2
    return score



def calcGrade(score,sensitive_list_word_length,txt_length):
    if score>15 and sensitive_list_word_length/txt_length>=0.33:
        suggest=u"删除"
    elif score==0:
        suggest=u"通过"
    else:
        suggest=u"掩码"
    return suggest






