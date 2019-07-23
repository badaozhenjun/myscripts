# *_*coding:utf-8 *_*
import requests
import json
from loguru import logger
import re
import sys
class AnkiHelper:
    def __init__(self):
        pass
    @staticmethod
    def addNote(front:str,back:str,deckName="每日一记",tags=None):

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
        payload=json.dumps(payload)
        logger.info("发现tags:{}".format(tags))
        logger.info("添加 paload= %s" % payload)
        r = requests.post("http://localhost:8765", headers={'Content-Type': 'application/json'},
                          data=payload)
        logger.info("add结果{}".format(r.content))
    @staticmethod
    def update_note(id,front=None,back=None,tags=None):
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
        if r is None:return None
        result = r.get("result",["None"])
        return None if len(result) == 0 else result[0]
    @staticmethod
    def add_or_update(front,back:str,deckName="每日一记",tags=None):

        t,front = AnkiHelper.parse_tags(front)
        if t is not None:
            tags = t

        id = AnkiHelper._find_note("{}".format(front))
        back=re.sub(r"\(#(.*?)#\)", "<font class=\"cloze\">\g<1></font>", back)
        if id:
            logger.info("已存在 id = {} front={}".format(id,front))
            # AnkiHelper.update_note(id,front,back,tags=tags)
        else:
            # logger.debug("不存在 id = {} front={}".format(id,front))
            AnkiHelper.addNote(front,back,deckName,tags=tags)
    @staticmethod
    def parse_tags(tags_str:str):
        tags = None
        s = re.findall(r"\[#(.*?)#\]", tags_str)
        for ss in s:
            if not tags :
                tags = []
            if "," in ss:
                tags.extend(ss.split(","))
            else:
                if len(ss) > 0:
                    tags.append(ss)

        tags_str = re.sub(r"\[#(.*?)#\]", "", tags_str)
        return tags,tags_str
if __name__ == "__main__":
    # anki.add_or_update("eeee","aaaaaddd")
    payload = """
              {
    "action": "findNotes",
    "version": 6,
    "params": {
        "query": "front:"
    }
}
               """
    payload= """
    {
    "action": "notesInfo",
    "version": 6,
    "params": {
        "notes": [ 1563464791999]
    }
}"""
    payload = """
    {
    "action": "modelFieldNames",
    "version": 6,
    "params": {
        "modelName": "每日一记"
    }
}
    """
#     logger.info("添加 paload= %s" % payload)
#     r = requests.post("http://localhost:8765", headers={'Content-Type': 'application/json'},
#                       data=payload.encode("utf8"))
#     logger.info("add结果{}".format(r.content))
#     logger.debug("aaa")
# # AnkiHelper.add_or_update("1563464791999","aaaasda","cccc")
# # print(AnkiHelper._find_note("front:6.module.init()_takes_at_most_2_arguments_(3_given)"))
#     AnkiHelper.addNote("a2aa","cccd")

    # a="{#aaaa#}{#bbbb#}"
    # print()
    #
    # inputStr = "hello crifan, nihao crifan";
    # replacedStr = re.sub(r"hello (\w+), nihao \1", "\g<1>", inputStr);
    # print("replacedStr=", replacedStr)  # crifan
    s = ""
    s = re.findall(r"\[#(.*?)#\]",s)
    tags = None
    for ss in s:
        if not tags:
            tags = []
        if "," in ss:
            tags.extend(ss.split(","))
        else:
            if len(ss)>0:
                tags.append(ss)
    print(tags)