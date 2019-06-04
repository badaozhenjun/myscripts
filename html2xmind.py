# *_*coding:utf-8 *_*
import requests
import xmind
from lxml import etree
import getopt
import sys

from lxml.etree import Element
from xmind.core.topic import TopicElement


def parseHtml(url:str,name:str) -> dict:
    req = requests.request(method="get", url=url, timeout=10)
    url = url if url.endswith("/") else url+"/"
    html = etree.HTML(req.text)
    h1 = html.xpath("//h1")[0]
    workbook = xmind.load("{}.xmind".format(name))
    sheet1 = workbook.getPrimarySheet()
    sheet1.setTitle(name+"-1")
    rootTopic = sheet1.getRootTopic()
    rootTopic.setTitle(name)
    rootTopic = rootTopic.addSubTopic()
    rootTopic.setTitle(h1.text.strip())
    html_content = html.xpath('//div[@class="content"]/*') #type:etree._Element
    # subNodes = html_content.xpath("/*")
    h2 = None
    h3 = None
    h4 = None
    currentNode = None
    for n in html_content: # type:etree._Element

        if n.tag == "h2":
            subTopic = TopicElement(ownerWorkbook=workbook)
            rootTopic.addSubTopic(subTopic)
            subTopic.setTitle(str(n.xpath("string(.)")))
            subTopic.setURLHyperlink(url+"#"+subTopic.getTitle().strip().lower().replace(".","").replace(" ","-"))
            h2 = subTopic
            currentNode = subTopic
        elif n.tag == "h3":
            pTopic = h2 if h2 else rootTopic
            subTopic = TopicElement(ownerWorkbook=workbook)
            pTopic.addSubTopic(subTopic)
            subTopic.setTitle(str(n.xpath("string(.)")))
            subTopic.setURLHyperlink(url +"#"+ subTopic.getTitle().strip().lower().replace(".","").replace(" ","-"))
            h3 = subTopic
            currentNode = subTopic
        elif n.tag == "h4":
            pTopic = h3 if h3 else rootTopic
            subTopic = TopicElement(ownerWorkbook=workbook)
            pTopic.addSubTopic(subTopic)
            subTopic.setTitle(str(n.xpath("string(.)")))
            subTopic.setURLHyperlink(url +"#"+subTopic.getTitle().strip().lower().replace(".","").replace(" ","-"))
            h4 = subTopic
            currentNode = subTopic
        else:
            content = currentNode.getNotes()
            content = content if content is not None else ""
            content = content + "\r\n" + (str(n.xpath("string(.)")))
            currentNode.setPlainNotes(content)
            a_ = n.xpath("./a")
            if len(a_) > 0:
                for a in a_:
                    subTopic = TopicElement(ownerWorkbook=workbook)
                    currentNode.addSubTopic(subTopic)
                    subTopic.setTitle(str(a.xpath("string(.)")))
                    subTopic.setURLHyperlink(str(a.attrib.get('href')))

    xmind.save(workbook)


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
        if name is None or url is None:
            print("-n -u 缺一不可")
            sys.exit(0)
        parseHtml(url, name)
    except Exception as e:
        print(str(e))