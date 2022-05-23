## sensitive_content_filter  中文敏感词过滤

- DFA原理参考java博客 https://blog.csdn.net/tigerfz/article/details/53376338
- 本文是python实现的，在博客的基础上增加了一些功能
- 添加了全角半角转换等功能；可以检测"法@@轮！功"这种中间有干扰项的字符串
- 根据计算出的敏感等级，可以对原文本进行*掩码或者不予显示

## 运行环境
- python3.9

## 程序说明
- data/dict.txt--收集的敏感词，"类别 词汇"
- data/stopword.txt--常见的特殊字符集，一般出现在有干扰的敏感词中，如"法@@轮！功"
- src/qbTransform--全角半角转换
- src/commonUtil.py--广告文本的正则匹配、计算敏感度得分、敏感等级
- src/sensitiveApi.py--DFA的实现以及接口

## 程序启动
- 运行 sensitiveApi.py 可直接启动
- 测试demo 
    - 检测为广告文本的  
    **调用接口** curl -H "Content-type: application/json; charset=utf-8" -X POST http://localhost:4000/sensitive -d '{"txt":"访问www.taobao.com，刷单5毛一条"}'  
    **返回结果** {"grade": "删除", "regularResult": "疑似[网页链接或邮箱]", "txt": "访问www.taobao.com，刷单5毛一条", "txtLength": 23}
    
    - 非广告文本的，进一步进行敏感词检测  
    **调用接口** curl -H "Content-type: application/json; charset=utf-8" -X POST http://localhost:4000/sensitive -d '{"txt":"小姐姐真漂亮，像个<font color=#FF7F50>大王八</font>,<font color=#FF7F50>大王八</font>"}'  
    **返回结果** {"sensitiveWordList": "[其他:王八,,其他:王八]", "ifContainSensitiveWord": true, "txtLength": 16, "grade": "掩码", "score": 4, "regularResult": "非广告文本", "txt": "小姐姐真漂亮，像个大王八,大王八", "txtReplace": "小姐姐真漂亮,像个大\*\*大\*\*", "sensitiveWordCount": 2}
      
     - 非广告文本的，进一步进行敏感词检测  
    **调用接口** curl -H "Content-type: application/json; charset=utf-8" -X POST http://127.0.0.1:4000/sensitive -d '{"txt":"国家主席<font color=#FF7F50>习近平</font>在中国青岛主持上海合作组织成员国元首理事会第十八次会议。<font color=#FF7F50>王八蛋</font>然后就是<font color=#FF7F50>fuck</font> dog 跟随着egg 主人公怒哀乐情节中。<font color=#FF7F50>法.轮#功</font> 难过就<font color=#FF7F50>手机卡复制器</font> ，<font color=#FF7F50>一个贱人</font> 去看电影。"}'  
    **返回结果** {"sensitiveWordList": "[政治:习近平,其他:王八,其他:fuck,暴恐:法.轮#功,暴恐:轮#功,社会:手机卡复制器,,色情:贱人]", "ifContainSensitiveWord": true, "txtLength": 93, "grade": "掩码",   "score": 24, "regularResult": "非广告文本", "txt": "国家主席习近平在中国青岛主持上海合作组织成员国元首理事会第十八次会议。王八蛋然后就是fuck dog 跟随着egg 主人公怒哀乐情节中。法.轮#功 难过就手机卡复制器，一个贱人去看电影。", "txtReplace": "国家主席\*\*\*在中国青岛主持上海合作组织成员国元首理事会第十八次会议。\*\*蛋然后就是\*\*\*\* dog 跟随着egg 主人公怒哀乐情节中。\*\*\*\*\* 难过就\*\*\*\*\*\*\*一个**去看电影。", "sensitiveWordCount": 7}
    
## 返回格式
- 接口返回json格式，字段可能是如下2种形式。如果检测到是广告文本，则不再进行敏感词检测；如果不是广告文本，则接着下一步的敏感词检测。

  a 检测为广告文本时，返回的字段说明如下:   
  待检测语句: txt,  
  待检测语句字数: txtLength,  
  敏感等级: grade,  
  正则过滤结果: regularResult  

  b 非广告文本进一步检测，返回的字段说明如下:   
  待检测语句: txt,  
  待检测语句字数: txtLength,  
  正则过滤结果: regularResult,  
  是否包含敏感词汇: ifContainSensitiveWord,  
  语句中包含敏感词的个数: sensitiveWordCount,  
  语句中包含敏感词: sensitiveWordList,  
  敏感度得分: score,  
  敏感等级: grade,  
  替换敏感词后的语句: txtReplace  
  
## 后续使用
- 可根据接口返回的结果"grade"一项，对文本采取不予显示或者掩码处理
- 如果“grade”="删除" ，则文本不予显示
- 如果“grade”="掩码"，则使用txtReplace作为输出
