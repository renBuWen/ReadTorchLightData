#coding:utf8
'''
收集三个文件的dat 数据
Unity 中在 
    levelPrefab
    prefabs
    prefabs/props 
中寻找对应的GUID 的资源
     

'''
#将Layout 文件转化成Json 文件
#从Layout中收集所有的 RoomPieces 对应的 fbx 模型放到unity 对应文件夹里面 去掉重复的 GUID

#mine.dat
#mineProps.dat
#props.dat 

'''
分析上面三个文件 得到GUID --->file 的映射关系

分析layout 文件 得到 去重复的 RoomPieces set 几何

确定Unity 中没有相关的RoomPieces 文件 
    从对应目录获取fbx文件

输入：
    三个 .dat  外加一个 layout

输出:
    RoomPieces
    guid ---> filename  映射


'''
import os
import sys
import codecs
import json
import re
stack = None
lines = None


#readFile = sys.argv[1]

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
            '''
            if key == 'DESCRIPTOR' and value == 'Layout Link':
                isLight = True
                layers.append(result)
            ''' 
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

                if result["stackName"] == "PIECE":
                    layers.append(result)
                return result, l, isLight #堆栈当前结束位置

            else:
                con, l, isLight = readStack(l)
                if result["stackName"] == "PIECE":
                    layers.append(result)
                    #isLight = False

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

trans("Mine.dat", handleFunc)
trans("Props.dat", handleFunc)
trans("MineProps.dat", handleFunc)

wf = open('data.json', 'w')
resJson = json.dumps(layers, separators=(', ', ': '), indent=4)
wf.write(resJson)
wf.close()

print "TotalPieces", len(layers)

mapRes = dict()
for l in layers:
    mapRes[l["GUID"]] = l
wf = open('map.json','w')
resJson = json.dumps(mapRes, separators=(', ', ': '), indent=4)
wf.write(resJson)
wf.close()


'''
print 'len layouts', len(layers)
wf = open('layers.json', 'w')
wf.write(json.dumps(layers, separators=(', ', ': '), indent=4))
wf.close()
'''

