# *_*coding:utf-8 *_*
# *_*coding:utf-8 *_*
import  js2py
import HackRequests
import re
import getopt,sys
import requests
import traceback
def getTime(second:int)->str:

    m = second /60
    s = second %60
    h = m/60 if m>60 else None
    m = m%60 if m>60 else m
    return  ("%02d:%02d:%02d" % (h,m,s)) if h else ("00:%02d:%02d" % (m,s))
def parse_raw(rawContent:str):
    """
    Parsed Returns data needed to make request and even call to request itself for the lazy
    """
    lines = rawContent.splitlines()

    headers = {} #Header stored here in dictionary format so it's easy to to use in 'requests'
    body = "" #Body is saved as a string
    method = None
    url = None

    header_is_finished = False
    first_body_line = True
    line_number = 1

    for line in lines:
        if not line.strip() and not header_is_finished:    #Checks if current line is empty to know where is the end of header/start of body
            header_is_finished = True   #A way to know if header is finished

        elif line_number == 1:  #If it's the first line we get request url and method
            rmethod = line.split(" ")
            method = rmethod[0]
            url = rmethod[1]

        elif not header_is_finished:    #Check if still header
            key, value = line.split(':', 1)
            headers.update({key.strip() : value.strip() })

        elif header_is_finished:    #If header part of the request is finished that means it's time for BODY
            if first_body_line:
                body = line
                first_body_line = False
            else:
                body = "{}\n{}".format(body, line)
        line_number += 1

    return {
        'headers' : headers,
        'url' : "https://study.163.com"+url,
        'method' : method,
        'body' : body,
        #'_request' : lambda: request(method=method, url="https://study.163.com"+url, data=body,headers=headers)
    }


def len_zh(data):
    temp = re.findall('[^a-zA-Z0-9.]+', data)
    count = 0
    for i in temp:
        count += len(i)
    return (count)


def my_format(str,width,align,sep=' '):#定义函数接受三个参数：要输出的字符串(str)、总占用宽度（int）、对齐方式（str:l、r、c对应左右中）
	sigle=0
	double=0
	for i in str:#统计单字宽和双字宽的数目
		if len(i.encode('gb2312'))==1:
			sigle+=1
		elif len(i.encode('gb2312'))==2:
			double+=1
	if align=='l':
		return str+(width*2-sigle-double*2)*sep
	elif align=='r':
		return (width*2-sigle-double*2)*sep+str
	elif align=='c':
		return int((width*2-sigle-double*2)//2)*sep+str+int((width*2-sigle-double*2)-(width*2-sigle-double*2)//2)*sep



def getTimeInfo(courseId):
    text = """POST /dwr/call/plaincall/PlanNewBean.getPlanCourseDetail.dwr HTTP/1.1
Host: study.163.com
Connection: close
Content-Length: 253
Pragma: no-cache
Cache-Control: no-cache
Origin: https://study.163.com
providerId: 1021000286
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36
Content-Type: text/plain
Accept: */*
Referer: https://study.163.com/course/introduction.htm?courseId=1004016002
Accept-Language: zh-CN,zh;q=0.9
Cookie:  

callCount=1
scriptSessionId=${scriptSessionId}191
httpSessionId=0bf2a155644541f8a026097260f243f7
c0-scriptName=PlanNewBean
c0-methodName=getPlanCourseDetail
c0-id=0
c0-param0=string:1005355015
c0-param1=number:0
c0-param2=null:null
batchId=1559655289189
    """
    text = text.replace("1005355015",str(courseId))
    # print(text)
    aa = parse_raw(text)
    response = requests.post(aa["url"], data=aa["body"], headers=aa["headers"], ).text
    # r = re.compile()
    response = response.replace("//#DWR-INSERT", "")
    response = response.replace("//#DWR-REPLY", "")
    response = re.sub("dwr.engine._remoteHandleCallback\(.*\);", "", response)
    # print(response)
    context = js2py.EvalJs()
    context.execute(response.replace("\n", ""))
    totalTime = 0
    content = ""
    pcontent = ""

    for i in range(200):
        try:
            s = eval("context.s" + str(i))

            if s["allCount"] and s["allCount"] > 0:
                chapterTime = 0.0;
                chapterName = s["name"]
                chapterList = list()
                for j in range(len(s["lessonDtos"])):
                    lessonDto = s["lessonDtos"][j]
                    time = lessonDto.videoTime;
                    chapterTime += time;
                    chapterList.insert(0, (lessonDto.lessonName, getTime(time)))
                totalTime += chapterTime
                chapterTime = getTime(chapterTime)
                content += "{}({})\n".format(chapterName, chapterTime)
                pcontent += "{}  {}\n".format(my_format(chapterName+" ",19,'l','+'), chapterTime)
                for t in range(len(chapterList)):
                    sn, st = chapterList[t]
                    zh = len_zh(sn)

                    content += "{},{}\n".format(sn, st)
                    pcontent += "{}{}\n".format(my_format(sn,20,'l'), st)
                content += "\n"
                pcontent += "\n"
        except Exception as e:
            if str(e) in ("'>' not supported between instances of 'NoneType' and 'int'","'int' object is not iterable"): continue
            if str(e).startswith("ReferenceError:"):continue
            print(e)
            traceback.print_exc()
            continue
    content += "总计,{}".format(getTime(totalTime))
    pcontent += "{}  {}\n".format(my_format("总计 ",19,'l','+'),getTime(totalTime))
    return (content,pcontent)

# print("共:" + getTime(totalTime))
if __name__ == "__main__":

    helpText = """
-n 生成文件的名字，默认为time(扩展名为csv)
-f 是否生成文件
-c 课程id    
"""
    createFile = False
    name = "time.csv"
    try:
        opts, args = getopt.getopt(sys.argv[1:], "-n:-f-c:-h", ["name=", "file","courseId="])
        for opt, arg in opts:
            if opt == "-n":
                name = str(arg)+".csv"
            elif opt == "-c":
                courseId = arg
            elif opt == "-f":
                createFile = True
            elif opt == "-h":
                print(helpText)
                sys.exit(0)
        if courseId is None :
            print("必须有courseId")
            sys.exit(0)
        content,pcontent = getTimeInfo(courseId)
        print(pcontent)
        if createFile:
            f = open(name, "w")
            f.write(content)
            f.close()
            print("\n{} 已生成".format(name))

    except Exception as e:
        traceback.print_exc()


