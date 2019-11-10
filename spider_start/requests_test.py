import requests
from bs4 import BeautifulSoup
from scrapy import Selector
# re=requests.get("http://www.baidu.com")

# print(re.headers)


# http://www.woshipm.com/category/pmd

re=requests.get("http://www.woshipm.com/category/pmd")
# print(re.text)
# bs=BeautifulSoup(re.text,"html.parser")
# li=bs.find("li",id="menu-item-155929")
# c=li.contents
# p=li.parents

# print(li)
# print(c)
# for pp in p:
#     print(pp)

sel=Selector(text=re.text)
tag=sel.xpath("/html/body/div[1]/div[4]/div[1]/div/div[1]/div[1]/div[2]/h2/a/text()").extract()[0]
print(tag)
tag=sel.css(".post-title").extract()[0]
print(tag)
# 192.168.43.200