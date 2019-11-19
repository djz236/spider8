
import ast
import re
import time
from datetime import datetime
from threading import Thread
from urllib import parse

import requests
from scrapy import Selector

from csdn_spider.models import *

topic_list_urls=[]
topic_list=[]
author_list=[]
domain = "https://bbs.csdn.net"

def get_nodes_json():
    left_menu_text=requests.get("https://bbs.csdn.net/dynamic_js/left_menu.js?csdn").text
    nodes_str_match=re.search("forumNodes: (.*])",left_menu_text)
    if nodes_str_match:       #forumNodes
        node_str=nodes_str_match.group(1).replace("null","None")
        nodes_list =ast.literal_eval(node_str)
        return nodes_list
    return []

url_list=[]
def process_nodes_list(nodes_list):
    #将js的格式提取出url到list中
    for item in nodes_list:
        if "url" in item and item['url']:
            url_list.append(item["url"])
            if "children" in item:
                process_nodes_list(item["children"])

def get_level1_list(nodes_list):
    level1_url=[]
    for item in nodes_list:
        if "url" in item and item['url']:
            level1_url.append(item['url'])
    return level1_url

def get_last_urls():
    #获取最终需要抓取的url
    nodes_list=get_nodes_json()
    process_nodes_list(nodes_list)
    level1_url=get_level1_list(nodes_list)
    last_urls=[]
    for url in url_list:
        if url not in level1_url:
            last_urls.append(url)
    all_urls=[]
    for url in last_urls:
        # print(url)
        all_urls.append(parse.urljoin(domain,url))
        all_urls.append(parse.urljoin(domain, url+"/recommend"))
        all_urls.append(parse.urljoin(domain, url+"/closed"))
    return all_urls


class ParseTopicDetailThread(Thread):
    def run(self):
        while 1:#for url in topic_list:
            try:
               url = topic_list.pop()
            except IndexError as e:
                time.sleep(1)
                continue

            print("开始获取帖子：{}".format(url))
            # 获取帖子的详情以及回复
            topic_id = url.split("/")[-1]
            res_text = requests.get(url).text
            sel = Selector(text=res_text)
            all_divs = sel.xpath("//div[starts-with(@id,'post-')]")
            topic_item = all_divs[0]
            content = topic_item.xpath(".//div[@class='post_body post_body_min_h']").extract()[0]
            praised_nums = topic_item.xpath(".//label[@class='red_praise digg']//em/text()").extract()[0]
            jtl_str = topic_item.xpath(".//div[@class='close_topic']/text()").extract()[0]
            jtl = 0
            jtl_match = re.search("(\d+)%", jtl_str)
            if jtl_match:
                jtl = int(jtl_match.group(1))
            existed_topics = Topic.select().where(Topic.id == topic_id)
            if existed_topics:
                topic = existed_topics[0]
                topic.content = content
                topic.jtl = jtl
                topic.praised_nums = praised_nums
                topic.save()

            for answer_item in all_divs[1:]:
                answer = Answer()
                answer.topic_id = topic_id
                author_info = answer_item.xpath(".//div[@class='nick_name']//a[1]/@href").extract()[0]
                author_id = author_info.split("/")[-1]
                create_time = answer_item.xpath(".//label[@class='date_time']/text()").extract()[0]
                create_time = datetime.strptime(create_time, '%Y-%m-%d %H:%M:%S')
                answer.author = author_id
                answer.create_time = create_time
                praised_nums = int(topic_item.xpath(".//label[@class='red_praise digg']//em/text()").extract()[0])
                answer.parised_nums = praised_nums
                content = topic_item.xpath(".//div[@class='post_body post_body_min_h']/text()").extract()[0]
                answer_id = topic_item.xpath("//div[@class='mod_topic_wrap post topic']/@data-post-id").extract()[0]
                answer.id = answer_id
                answer.content = content
                existed_answer = Answer.select().where(Answer.id == answer_id)
                # print(answer_id)
                # print(url)
                if existed_answer:
                    answer.save()
                else:
                    answer.save(force_insert=True)

            next_page = sel.xpath("//a[@class='pageliststy next_page']/@href").extract()
            if next_page:
                topic_list.append(parse.urljoin(domain, next_page[0]))
            # if next_page:
            #     next_page = parse.urljoin(domain, next_page[0])
            #     parse_topic(next_page)


class ParseAuthorThread(Thread):
    def run(self):
         while 1:
            try:
                 url = author_list.pop()
            except IndexError as e:
                 time.sleep(1)
                 continue
            print("开始获取用户：{}".format(url))
            # url='https://me.csdn.net/blog/ojc8882003'
            author_id = url.split("/")[-1]
            # 获取用户的详情
            headers = {
                'User-Agent': 'Mozilla / 5.0(Windows NT 6.1;Win64;x64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 74.0.3729.108Safari / 537.36'
            }
            res_text = requests.get(url, headers=headers).text
            sel = Selector(text=res_text) 
            author = Author()
            author.id = author_id
            all_li_strs = sel.xpath("//ul[@class='me_chanel_list clearfix']/li/a/label/span[2]/text()").extract()
            if all_li_strs:
                click_nums = all_li_strs[0]
                if len(all_li_strs) > 1:
                    original_nums = all_li_strs[1]
                else:
                    original_nums = 0
                if len(all_li_strs) > 2:
                    forward_nums = all_li_strs[2]
                else:
                    forward_nums = 0
                if len(all_li_strs) > 3:
                    rate = all_li_strs[3]
                else:
                    rate = 0
                author.click_nums = click_nums
                author.original_nums = original_nums
                author.forward_nums = forward_nums
                author.rate = rate
            answer_nums = 1
            parised_nums = 1
            author.answer_nums = answer_nums
            author.parised_nums = parised_nums
            desc = sel.xpath("//div[@class='description_detail']/text()").extract()
            username = ""
            if sel.xpath("//p[@class='lt_title']/text()").extract():
                username = sel.xpath("//p[@class='lt_title']/text()").extract()[2].strip()
                author.name = username
            if desc:
                author.desc = desc
            location = sel.xpath("//div[@class='job clearfix']/p/text()").extract()[0].strip()
            author.location = location
            industry = sel.xpath("//div[@class='description clearfix']/p/text()").extract()[0].strip()
            author.industry = industry
            existed_author = Author.select().where(Author.id == author_id)
            if existed_author:
                author.save()
            else:
                author.save(force_insert=True)


class ParseTopicListThread(Thread):
    def run(self):
        while 1:
            try:
                url=topic_list_urls.pop()
            except IndexError as e:
                time.sleep(1)
                continue
            # for uu in topic_list_urls:
            #     print(uu)
            print("开始获取帖子列表页：{}".format(url))
            res_text=requests.get(url).text
            sel=Selector(text=res_text)
            all_trs=sel.xpath("//table[@class='forums_tab_table']/tbody//tr")[4:]
            for tr in all_trs:
                topic = Topic()
                if tr.xpath(".//td[1]/span/text()").extract():
                    status=tr.xpath("//td[1]/span/text()").extract()[0]
                    topic.status = status

                if tr.xpath(".//td[2]/em/text()").extract():
                    score = tr.xpath(".//td[2]/em/text()").extract()[0]
                    topic.score = int(score)
                print(tr)
                topic_url =""
                if len(tr.xpath(".//td[3]/a/@href").extract())==2:
                    topic_url= parse.urljoin(domain,tr.xpath(".//td[3]/a/@href").extract()[1])
                    print(topic_url)
                else:
                    topic_url = parse.urljoin(domain, tr.xpath(".//td[3]/a/@href").extract()[0])
                    print(topic_url)
                if tr.xpath(".//td[3]/a/text()").extract():
                    topic_title = tr.xpath(".//td[3]/a/text()").extract()[0]
                    topic.title = topic_title
                if tr.xpath(".//td[3]/a/text()").extract():
                    topic_title = tr.xpath(".//td[3]/a/text()").extract()[0]
                    topic.title = topic_title
                if tr.xpath(".//td[4]/a/@href").extract():
                    author_url = parse.urljoin(domain,tr.xpath(".//td[4]/a/@href").extract()[0])
                    author_id = author_url.split("/")[-1]
                    topic.author = author_id
                if tr.xpath(".//td[4]/em/text()").extract():
                    create_time=tr.xpath(".//td[4]/em/text()").extract()[0]
                    create_time=datetime.strptime(create_time,"%Y-%m-%d %H:%M")
                    topic.create_time = create_time
                if tr.xpath(".//td[5]/span/text()").extract():
                    answer_info = tr.xpath(".//td[5]/span/text()").extract()[0]
                if answer_info.split("/"):
                    answer_nums = answer_info.split("/")[0]
                    topic.answer_nums = answer_nums
                if answer_info.split("/"):
                    click_nums = answer_info.split("/")[1]
                    topic.click_nums = int(click_nums)
                if tr.xpath(".//td[6]/em/text()").extract():
                    last_time_str = tr.xpath(".//td[6]/em/text()").extract()[0]
                    last_time=datetime.strptime(last_time_str,"%Y-%m-%d %H:%M")
                    topic.last_answer_time = last_time
                topic.id=int(topic_url.split("/")[-1])
                existed_topics=Topic.select().where(Topic.id==topic.id)
                if existed_topics:
                    topic.save()
                else:
                    topic.save(force_insert=True)
                if topic_url!="":
                    topic_list.append(topic_url)
                author_list.append(author_url)

            next_page=sel.xpath("//a[@class='pageliststy next_page']/@href").extract()
            if next_page:
                topic_list_urls.append(parse.urljoin(domain, next_page[0]))
            # if next_page:
            #     next_page=parse.urljoin(domain,next_page[0])
            #     parse_list(next_page)

if __name__=="__main__":
    last_urls=get_last_urls()
    for url in last_urls:
        topic_list_urls.append(url)

    top_list_thread=ParseTopicListThread()
    top_detail_thread=ParseTopicDetailThread()
    author_thread=ParseAuthorThread()

    top_list_thread.start()
    top_detail_thread.start()
    author_thread.start()

