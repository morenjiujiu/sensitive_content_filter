#encoding:utf-8
from __future__ import division

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import commonUtil, qbTransform
import json
from flask import Flask,request,Response
from flask_restful import Api
from gevent.pywsgi import WSGIServer
import logging

#pip install flask
#pip install flask_restful
#pip install gevent

logger = logging.getLogger("cccode")
formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')
file_handler = logging.FileHandler("sensitive.log")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.setLevel(logging.INFO)



app = Flask(__name__)
api = Api(app)


MinMatchType = 1 #最小匹配规则，如：敏感词库["中国", "中国人"]，语句："我是中国人"，匹配结果：我是[中国]人
MaxMatchType = 2 #最大匹配规则，如：敏感词库["中国", "中国人"]，语句："我是中国人"，匹配结果：我是[中国人]


def initSensitiveWordMap(sensitiveWordSet):
    """
    初始化敏感词库，构建DFA算法模型
    :param sensitiveWordSet: 敏感词库,包括词语和其对应的敏感类别
    :return: DFA模型
    """
    sensitiveWordMap=dict()
    for category,key in sensitiveWordSet:
        if type(key)=='unicode' and type(category)=='unicode' : #转换为unicode
            pass
        else:
            key=unicode(key)
            category=unicode(category)

        nowMap = sensitiveWordMap
        for i in range(len(key)):
            keyChar =key[i]  # 转换成char型
            wordMap = nowMap.get(keyChar) #库中获取关键字
            #如果存在该key，直接赋值，用于下一个循环获取
            if wordMap != None:
                nowMap =wordMap
            else:
                #不存在则构建一个map，同时将isEnd设置为0，因为不是最后一个
                newWorMap = dict()
                #不是最后一个
                newWorMap["isEnd"]="0"
                nowMap[keyChar]=newWorMap
                nowMap = newWorMap
            #最后一个
            if i ==len(key)-1:
                nowMap["isEnd"]="1"
                nowMap["category"]=category
    return sensitiveWordMap


def checkSensitiveWord(txt,beginIndex,matchType=MinMatchType):
    """
    检查文字中是否包含敏感字符
    :param txt:待检测的文本
    :param beginIndex: 调用getSensitiveWord时输入的参数，获取词语的上边界index
    :param matchType:匹配规则 1：最小匹配规则，2：最大匹配规则
    :return:如果存在，则返回敏感词字符的长度，不存在返回0
    """
    flag=False
    category=""
    matchFlag=0  #敏感词的长度
    nowMap=sensitiveWordMap
    tmpFlag=0  #包括特殊字符的敏感词的长度

    # print "len(txt)",len(txt) #9
    for i in range(beginIndex,len(txt)):
        word = txt[i]

        #检测是否是特殊字符，eg"法&&轮&功..."
        if word in stopWordSet and len(nowMap)<100:
            #len(nowMap)<100 保证已经找到这个词的开头之后出现的特殊字符
            #eg"情节中,法&&轮&功..."这个逗号不会被检测
            tmpFlag += 1
            continue


        #获取指定key
        nowMap=nowMap.get(word)
        if nowMap !=None: #存在，则判断是否为最后一个
            #找到相应key，匹配标识+1
            matchFlag+=1
            tmpFlag+=1
            #如果为最后一个匹配规则，结束循环，返回匹配标识数
            if nowMap.get("isEnd")=="1":
                #结束标志位为true
                flag=True
                category=nowMap.get("category")
                #最小规则，直接返回,最大规则还需继续查找
                if matchType==MinMatchType:
                    break
        else: #不存在，直接返回
            break


    if matchFlag<2 or not flag: #长度必须大于等于1，为词
        tmpFlag=0
    return tmpFlag,category


def contains(txt,matchType=MinMatchType):
    """
    判断文字是否包含敏感字符
    :param txt: 待检测的文本
    :param matchType: 匹配规则 1：最小匹配规则，2：最大匹配规则
    :return: 若包含返回true，否则返回false
    """
    flag=False
    for i in range(len(txt)):
        matchFlag=checkSensitiveWord(txt,i,matchType)[0]
        if matchFlag>0:
            flag=True
    return flag


def getSensitiveWord(txt,matchType=MinMatchType):
    """
    获取文字中的敏感词
    :param txt: 待检测的文本
    :param matchType: 匹配规则 1：最小匹配规则，2：最大匹配规则
    :return:文字中的敏感词
    """
    sensitiveWordList=list()
    for i in range(len(txt)): #0---11
        length = checkSensitiveWord(txt, i, matchType)[0]
        category=checkSensitiveWord(txt, i, matchType)[1]
        if length>0:
            word=txt[i:i + length]
            sensitiveWordList.append(category+":"+word)
            i = i + length - 1
    return sensitiveWordList


def replaceSensitiveWord(txt, replaceChar, matchType=MinMatchType):
    """
    替换敏感字字符
    :param txt: 待检测的文本
    :param replaceChar:用于替换的字符，匹配的敏感词以字符逐个替换，如"你是大王八"，敏感词"王八"，替换字符*，替换结果"你是大**"
    :param matchType: 匹配规则 1：最小匹配规则，2：最大匹配规则
    :return:替换敏感字字符后的文本
    """
    tupleSet = getSensitiveWord(txt, matchType)
    wordSet=[i.split(":")[1] for i in tupleSet]
    resultTxt=""
    if len(wordSet)>0: #如果检测出了敏感词，则返回替换后的文本
        for word in wordSet:
            replaceString=len(word)*replaceChar
            txt = txt.replace(word, replaceString)
            resultTxt=txt
    else: #没有检测出敏感词，则返回原文本
        resultTxt = txt
    return resultTxt



# 特殊字符集
f = open("./data/stopword.txt")
stopWordSet = [i.split('\n')[0] for i in f.readlines()]

# 敏感词集
f1 = open("./data/dict.txt")
lst = f1.readlines()
sensitiveWordSet = [i.split("\n")[0].split("\t") for i in lst]
# print u"词汇总数:", len(sensitiveWordSet)
sensitiveWordMap = initSensitiveWordMap(sensitiveWordSet)
# print u"DFA结构词汇数:", len(sensitiveWordMap)



@app.route('/sensitive',methods=['POST'])
def get():
    # time_start = time.time()
    try:
        txt=request.json['txt']
        txt_length=len(txt)
        txt_convert= qbTransform.strQ2B(txt) #全角转半角
        reg_result= commonUtil.getReg(txt_convert) #正则过滤

        if reg_result==u"非广告文本":
            #是否包含敏感词
            contain = contains(txt=txt_convert,matchType=MaxMatchType) #默认 MinMatchType
            #敏感词和其类别
            sensitive_list = getSensitiveWord(txt=txt_convert, matchType=MaxMatchType)  #默认 MinMatchType
            sensitive_list_str=u','.join(sensitive_list) #字符串形式的敏感词和其类别
            sensitive_list_word=[i.split(":")[1] for i in sensitive_list] #敏感词
            #敏感词的字数
            sensitive_list_word_length=0
            for word in sensitive_list_word :
                if len(word)<=1:
                    continue
                sensitive_list_word_length+=len(word)

            #待检测语句的敏感度得分
            score= commonUtil.calcScore(sensitive_list_str)
            #待检测语句的敏感级别
            grade= commonUtil.calcGrade(score, sensitive_list_word_length, txt_length)
            #替换敏感词后的文本
            txt_replace=replaceSensitiveWord(txt=txt_convert,replaceChar='*',matchType=MaxMatchType) #默认MinMatchTYpe

            result_json={
                u"txt":txt,
                u"txtLength":txt_length,
                u"regularResult":reg_result,
                u"ifContainSensitiveWord":contain,
                u"sensitiveWordCount":len(sensitive_list),
                u"sensitiveWordList":"["+sensitive_list_str+u"]",
                u"score":score,
                u"grade":grade,
                u"txtReplace":txt_replace
            }

        else:
            result_json={
                u"txt":txt,
                u"txtLength":txt_length,
                u"regularResult":reg_result,
                u"grade":u"删除"
            }


        result_log=json.dumps(result_json, encoding='utf-8', ensure_ascii=False)
        logger.info(result_log)

        # time_end = time.time()
        # print u"运行时间:", (time_end - time_start) * 1000, u"ms"

    except Exception,e:
        result_log={}
        logger.info("please check the input query! {} will be given by default---"+str(e))

    r = Response(result_log, mimetype='application/json')
    r.headers['Content-Type'] = "application/json; charset=utf-8"

    return r




if __name__ == '__main__':
    # app.run(host='127.0.0.1', port=4000, debug=True)
    WSGIServer(('localhost', 4000), app).serve_forever()


"""
curl -H "Content-type: application/json; charset=utf-8" -X POST http://127.0.0.1:4000/sensitive -d '{"txt":"访问 www.taobao.com"}'

curl -H "Content-type: application/json; charset=utf-8" -X POST http://127.0.0.1:4000/sensitive -d '{"txt":"小姐姐真漂亮，像个大王八,大王八"}'

curl -H "Content-type: application/json; charset=utf-8" -X POST http://127.0.0.1:4000/sensitive -d '{"txt":"国家主席习近平在中国青岛主持上海合作组织成员国元首理事会第十八次会议。王八蛋 荧幕中的情节。然后就是fuck dog 跟随着egg 主人公怒哀乐情节中。法.轮#功 难过就躺在某一个人的怀里，尽情的阐述心扉或者手机卡复制器，一个贱人一杯红酒一部电影在夜深人静的晚上，关上电话静静的发呆着。"}'

"""