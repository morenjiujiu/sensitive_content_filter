## sensitive_content_filter  中文敏感词过滤

- 参考博客 https://my.oschina.net/magicalSam/blog/1528428， 本文是python实现的，在博客的基础上多了一点功能
- 添加了全角半角转换等功能，可以检测“法@@轮！功”这种中间有干扰项的字符串

## 运行环境
- python2.7

## 程序启动
- 运行 sensitiveApi.py 可直接启动
- 测试demo
1、curl -H "Content-type: application/json; charset=utf-8" -X POST http://localhost:4000/sensitive -d '{"txt":"小姐姐真漂亮，像个大王八,大王八"}'  

2、curl -H "Content-type: application/json; charset=utf-8" -X POST http://localhost:4000/sensitive -d '{"txt":"访问 www.taobao.com"}'

## 返回格式
- 接口返回json格式，字段可能是如下2种形式。如果检测到是广告文本，则不再进行敏感词检测；如果不是广告文本，则接着下一步的敏感词检测。

  a 检测为广告文本  
  待检测语句: txt,  
  待检测语句字数: txtLength,  
  敏感等级: grade,  
  正则过滤结果: regularResult  

  b 非广告文本进一步检测  
  待检测语句: txt,  
  待检测语句字数: txtLength,  
  正则过滤结果: regularResult,  
  是否包含敏感词汇: ifContainSensitiveWord,  
  语句中包含敏感词的个数: sensitiveWordCount,  
  语句中包含敏感词: sensitiveWordList,  
  敏感度得分: score,  
  敏感等级: grade,  
  替换敏感词后的语句: txtReplace  
  
  
