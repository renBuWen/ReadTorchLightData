#coding:utf8
'''
输入：Layout文件
输入：Json文件  xxxx.layout.json
    用于Unity 中MakeScene 使用

参考笔记 场景制作流程:
    http://note.youdao.com/web/list?notebook=%2F&sortMode=0&note=%2F15AC25FF024C4D1B8A58CB9A4D6803CC%2Fweb1431916754852

'''
#将Layout 文件转化成Json 文件
#从json中只提取需要的Props 相关LayoutLink 信息
import os
import sys
import codecs
import json
import re
stack = None
lines = None


readFile = sys.argv[1]

#读取堆栈名称
def readName(lineNo):
    lcon = lines[lineNo].encode('utf8')
    token = ''
    for c in lcon:
        if c == '[':
            pass
        elif c == ']':
            break
        else:
            token += c
    return token
#读取堆栈属性
def readProp(lcon):
    state = 0
    token = ''
    typ = ''
    key = ''
    value = ''
    for c in lcon:
        if state == 0:
            if c == '<':
                state = 1
        elif state == 1:
            if c == '>':
                state = 2
            else:
                typ += c
        elif state == 2:
            if c == ':':
                state = 3
            else:
                key += c
        elif state == 3:
            if c == '\n':
                pass
            elif c == '\r':
                pass
            else:
                value += c
    if typ == 'BOOL':
        try:
            value = bool(int(value))
        except:
            if value == 'true':
                value = True
            else:
                value = False
    elif typ == 'STRING':
        pass
    elif typ == 'FLOAT':
        value = float(value)
    else:
        pass
    

    return {key: value}, key, value

#lightFiles = set()

layoutLinks = []

layers = []

#进入一个stack进行递归读取
def readStack(lineNo):
    result = {
        'stackName' : readName(lineNo),
        'children' : [],
    }
    lineNo += 1

    #print 'readStack', result['stackName']
    #readStackName
    l = lineNo
    isLight = False
    #读取DESCRIPTOR 如果是Particle 粒子 则设置Texture
    while  l < len(lines):
        lcon = lines[l].encode('utf8')
        if lcon[0] == '<':
            prop, key, value = readProp(lcon)
            if key == 'DESCRIPTOR' and value == 'Layout Link':
                isLight = True
                layers.append(result)
                
            '''
            #if key == 'TEXTURE':
                #lightFiles.add(value)
                #layoutLinks.append(value)
            '''

            result.update(prop)

        elif lcon[0] == '[':
            if lcon[1] == '/':
                #if result["stackName"] == "BASEOBJECT" and isLight:
                #    layers.append(result)
                #    isLight = False

                return result, l, isLight #堆栈当前结束位置

            else:
                con, l, isLight = readStack(l)
                if result["stackName"] == "BASEOBJECT" and isLight:
                    #layers.append(result)
                    isLight = False

                result['children'].append(con)
        l += 1

    return result, l, isLight


def handleFunc(name):
    print "file", name
    global stack
    stack = []
    global lines
    lines = codecs.open(name, encoding='utf16').readlines()
    result, l, isLight = readStack(0)

    print 'SaveFile', name+'.json'
    resJson = json.dumps(result, separators=(', ', ': '), indent=4)
    wf = open('%s.json' % (name), 'w')
    wf.write(resJson)
    wf.close()
    return resJson


def trans(cur, func):
    if not os.path.isdir(cur):
        return func(cur)
    else:
        allF = os.listdir(cur)
        for f in allF:
            name = os.path.join(cur, f)
            if os.path.isdir(name):
                trans(name, func)
                return
            elif name.find('.layout') != -1 and name.find('.json') == -1:
                fileContent = func(name)
                return

trans(readFile, handleFunc)


print 'len layouts', len(layers)
wf = open('layers.json', 'w')
wf.write(json.dumps(layers, separators=(', ', ': '), indent=4))
wf.close()
print 'Layout'
for l in layers:
    print l["LAYOUT FILE"]


