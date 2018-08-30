#encoding=utf-8
from urllib.parse import urlencode
import requests
from requests.exceptions import RequestException
import json
from bs4 import BeautifulSoup
import re
import pymongo
import os
from hashlib import md5
from multiprocessing import Pool

client = pymongo.MongoClient(host='localhost')
db = client['toutiao']

def get_page_index(offset,keyword):
    data= {
        'offset': offset,
        'format':'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': 20,
        'cur_tab': 3,
        'from': 'gallery'

    }
    url = 'https://www.toutiao.com/search_content/?' + urlencode(data)
    response = requests.get(url)
    try:
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print("请求索引出错！")
        return None
    
def parse_page_index(html):
    data = json.loads(html)
    if data and 'data' in data.keys():
        for item in data.get('data'):
            yield item.get('article_url')

def get_page_detail(url):
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
        }
    try:
        response = requests.get(url,headers= headers)
        if response.status_code == 200:
            return response.content.decode('utf-8')
        return None
    except RequestException:
        print("请求索引出错！",url)
        return None

def parse_page_detail(html,url):
    soup = BeautifulSoup(html,'lxml')
    title = soup.head.title.string
    images_pattern = re.compile('JSON\.parse\("(.*?)\"\)')
    result_temp = re.search(images_pattern,html)
    result_temp = result_temp.group(1)
    result_temp = result_temp.replace('\\',"")
    result = json.loads(result_temp)
    img_url_list =[]
    for item in result.get('sub_images'):
        img_url_list.append(item.get('url'))
    return {
        'title': title,
        'url' : url,
        'img_url_list' : img_url_list
        }

def save2mongo(result):
    if db["jie_pai"].insert(result):
        print("存储到mongodb成功", result)
        return True
    return False

def img_download(result):
    title = result.get('title')
    url = result.get('url')
    img_url_list = result.get('img_url_list')
    print("正在保存图片：")
    print('Title',title)

    for url in img_url_list:
        response = requests.get(url)
        print("url: ",url)
        save_img(response.content)

def save_img(content):
    file_path = '{0}/{1}.{2}'.format(os.getcwd(),md5(content).hexdigest(),'jpg')
    print(file_path)
    if not os.path.exists(file_path):
        with open(file_path,'wb') as f:
            f.write(content)
            f.close 
    
def main(offset):
    search_html = get_page_index(offset,'街拍')
    for url in parse_page_index(search_html):
        page_html = get_page_detail(url)
        result = parse_page_detail(page_html,url)
        save2mongo(result)   
        img_download(result)
if __name__ == "__main__":
    groups = [i*20 for i in range(0,20)]
    pool = Pool()
    pool.map(main,groups)
