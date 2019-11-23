import requests
import json
from scrapy import Selector

print(requests.get(
    "https://sclub.jd.com/comment/productPageComments.action?productId=56128919687&score=0&sortType=5&page=0&pageSize=10&isShadowSku=0&fold=1"))


def parse_good(good_id):
    good_url_template = "https://item.jd.com/{}.html".format(good_id)
    html = requests.get(good_url_template).text
    sel = Selector(text=html)
    name = "".join(sel.xpath("//div[@class='sku-name']/text()").extract()[0]).strip()
    prince_url = "https://p.3.cn/prices/mgets?type=1&pdtk=&skuIds=J_{}&source=item-pc".format(
        good_id)
    price_text = requests.get(prince_url).text.strip()
    prince_json = json.loads(price_text)

    if prince_json:
        price = float(prince_json[0]["p"])
    comments_url = "https://sclub.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv700&productId={}&score=0&sortType=5&page=0&pageSize=10&isShadowSku=0&fold=1".format(
        good_id)
    # comments_url = "https://sclub.jd.com/comment/productPageComments.action?productId={}&score=0&scoreType=5&page={}&pageSize=10&isShadowSku=0&fold=1".format(
    #     good_id, 1)
    headers = {
         'User-Agent': "Mozilla / 5.0(Windows NT 6.1;Win64;x64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 70.0.3538.110Safari / 537.36",
        'Referer': 'https://item.jd.com/56128919687.html'}
    max_page = 0
    # response = requests.post(url=comments_url, data="", headers=headers)
    # evaluate_json = requests.get(comments_url).json()
    # ss=json.loads(requests.get(comments_url))
    # ss = json.loads(requests.post(comments_url）);
    # evaluate_json = json.loads(requests.post(comments_url).text.strip())
    comments_text=requests.get(comments_url,headers=headers)
    comments_text = json.loads(comments_text.text.lstrip('fetchJSON_comment98vv700(').rstrip(');'))
    # 得到响应
    # 去掉多余得到json格式
    # content = comments_text.strip('fetchJSON_comment98vv700();')

    print(comments_text)
    # comments_text = json.loads(jd)
    max_page=comments_text["maxPage"]
    statistics=comments_text["hotCommentTagStatistics"]
    summary=comments_text['productCommentSummary']
    evaluates=comments_text['comments']

    print(comments_text)
    print(prince_json)
    print(name)


if __name__ == "__main__":
    parse_good(56128919687)
