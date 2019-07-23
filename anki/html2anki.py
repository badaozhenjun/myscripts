# *_*coding:utf-8 *_*
import requests
from lxml import etree
import getopt
import sys
from loguru import logger
import re
import json

logger.add(sys.stderr, format="{time} {level} {message}", filter="my_module", level="INFO")


class AnkiHelper:
    def __init__(self):
        pass

    @staticmethod
    def addNote(front: str, back: str, deckName="每日一记", tags=None):

        payload = """
            {"action": "addNotes",
            "version": 6,
            "params": {
                "notes": [
                    {
                        "deckName": "%s",
                        "modelName": "每日一记",
                        "fields": {
                            "Front": "",
                            "Back": ""
                        },
                        "tags": [

                        ]
                    }
                ]
            }
        }
            """ % (deckName)
        payload = json.loads(payload)
        payload["params"]["notes"][0]["fields"]["Front"] = front.strip()
        payload["params"]["notes"][0]["fields"]["Back"] = back
        payload["params"]["notes"][0]["tags"] = tags if tags else []
        payload = json.dumps(payload)
        logger.info("发现tags:{}".format(tags))
        logger.info("添加 paload= %s" % payload)
        r = requests.post("http://localhost:8765", headers={'Content-Type': 'application/json'},
                          data=payload)
        logger.info("add结果{}".format(r.content))

    @staticmethod
    def update_note(id, front=None, back=None, tags=None):
        if not front or not back:
            raise Exception("front or back require")
        payload = """
                   {
                        "action": "updateNoteFields",
                        "version": 6,
                        "params": {
                            "note": {
                                "id": %s,
                                "deckName": "每日一记",

                                "fields": {
                                    "Front": "",
                                    "Back": ""
                                }
                            }
                        }
                    }
                   """ % id
        payload = json.loads(payload)
        payload["params"]["note"]["fields"]["Front"] = front.strip()
        payload["params"]["note"]["fields"]["Back"] = back
        payload["params"]["note"]["tags"] = tags if tags else []
        payload = json.dumps(payload)
        logger.info("发现tags:{}".format(tags))
        logger.info("更新 paload= %s" % payload)
        r = requests.post("http://localhost:8765", headers={'Content-Type': 'application/json'},
                          data=payload.encode("utf8"))
        logger.info("更新结果{}".format(r.content))

    @staticmethod
    def _find_note(front) -> str:
        payload = """{
                        "action": "findNotes",
                        "version": 6,
                        "params": {
                            "query": "front:%s"
                        }
                     }""" % re.sub('[ ()<>"]{1}', '_', front.strip())

        # logger.info("查找 paload= %s" % payload)
        r = requests.post("http://localhost:8765", headers={'Content-Type': 'application/json'},
                          data=payload.encode("utf8"))
        r = json.loads(r.content.decode("utf8"))
        if r is None: return None
        result = r.get("result", ["None"])
        return None if len(result) == 0 else result[0]

    @staticmethod
    def add_or_update(front, back: str, deckName="每日一记", tags=None):

        t, front = AnkiHelper.parse_tags(front)
        if t is not None:
            tags = t

        id = AnkiHelper._find_note("{}".format(front))
        back = re.sub(r"\(#(.*?)#\)", "<font class=\"cloze\">\g<1></font>", back)
        if id:
            logger.info("已存在 id = {} front={}".format(id, front))
            # AnkiHelper.update_note(id,front,back,tags=tags)
        else:
            # logger.debug("不存在 id = {} front={}".format(id,front))
            AnkiHelper.addNote(front, back, deckName, tags=tags)

    @staticmethod
    def parse_tags(tags_str: str):
        tags = None
        s = re.findall(r"\[#(.*?)#\]", tags_str)
        for ss in s:
            if not tags:
                tags = []
            if "," in ss:
                tags.extend(ss.split(","))
            else:
                if len(ss) > 0:
                    tags.append(ss)

        tags_str = re.sub(r"\[#(.*?)#\]", "", tags_str)
        return tags, tags_str
class Note:
    front = ""
    back = ""
    h2 = None
    h3 = None
    def __str__(self):
        return "front = %s,back = %s" % (self.front,self.back)

@logger.catch
def parseHtml(url:str,name:str) -> dict:
    req = requests.request(method="get", url=url, timeout=10)

    url = url if url.endswith("/") else url+"/"
    html = etree.HTML(req.content.decode("utf8"))
    h1 = html.xpath("//h1")[0]
    t = html.xpath("string(//div[@class='postdate']/time[1])").replace("-",".")

    html_content = html.xpath('//div[@class="content"]/*') #type:etree._Element
    h2 = None
    h3 = None
    h4 = None
    currentNode = None
    notes = []
    tags = []
    nt = None
    for n in html_content: # type:etree._Element
        # logger.info(n.tag)
        if n.tag == "h2":
            if nt:
                # logger.info("已经有了")

                notes.append(nt)
                nt = Note()
            else:
                # logger.info("第一次")
                nt = Note()
            question = str(n.xpath("string(.)")).strip()
            nt.front = re.sub(r"\d+\.","",question,1)
            nt.h2 = nt.front
        elif n.tag == "h3":
            if nt.h3:
                notes.append(nt)
                h2 = nt.h2
                nt = Note()
                nt.h2 = h2
                nt.front = h2
            nt.h3 = question
            question = str(n.xpath("string(.)")).strip()
            nt.front = nt.front+"<br><li>"+question+"</li>"
        else:

            answer = etree.tostring(n,encoding="utf8", pretty_print=True, method="html")
            if not nt:
                ts,s = AnkiHelper.parse_tags(answer.decode("utf8"))
                if len(ts)>0:
                    tags.extend(ts)
            # answer = h.unescape(answer)
            if nt:
                nt.back += answer.decode("utf8")
    if nt:
        notes.append(nt)
    # xmind.save(workbook)

    i = 0
    for nt in notes:
        if nt.front.startswith("*"):
            i = i+1

    logger.info("检测到{}张卡片，其中{}张无效，{}张有效".format(len(notes),i,len(notes)-i))




    for i in range(len(notes)):
        nt = notes[i]
        if nt.front.startswith("*"):
            continue
        logger.debug("正在插入第{}张卡片:{}.{}".format(i,nt.h2,nt.h3 if nt.h3 else ""))
        nt.front = nt.front + "<br><p style=\"color:white;font-size:14px;\">{}</p>".format(t)
        AnkiHelper.add_or_update(notes[i].front,notes[i].back,tags=tags)

if __name__ == "__main__":
    name = None
    url = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], "-n:-u:h", ["help", "name=","url="])
        for opt,arg in opts:
            if opt == "-n":
                name = arg
            elif opt == "-u":
                url = arg
        if url is None:
            print("-u 不可为空")
            sys.exit(0)
        parseHtml(url, name)
    except Exception as e:
        print(str(e))