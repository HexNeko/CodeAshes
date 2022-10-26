from bs4 import BeautifulSoup
import requests
import re

def get_html(url):
    '''请求网页,返回网页的text格式和关联url列表'''
    #经观察链接中包含news/post/upload大都是新闻报道等无关内容，直接跳过
    if 'news' in url or 'post' in url or 'upload' in url:
        return None,None
    try:
        r=requests.get(url,timeout=1)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        url_list=set()
        '''找到网站前缀，用于修补一些简写的链接'''
        base=re.search(r'(?<=://)[a-zA-Z\.0-9]+(?=\/)',url)
        if base:
            base=base.group(0)
        soup=BeautifulSoup(r.text,'lxml')
        for tag in soup.select('a'):
            if not tag.get('href') == None:
                context = str(tag['href'])
                if not context.startswith('http') and not context.startswith('.') and base:
                    context = 'https://' + base + '/' + context
                if context.__contains__('xmu.edu.cn') and len(context)<80:
                    url_list.add(context)
        return r.text,url_list
    except:
        return None,None
