from bs4 import BeautifulSoup
import re
import csv
from pybloom_live import ScalableBloomFilter
from request_html import *

namep_r=r"厦门大学[\u4e00-\u9fa5]*|厦大[\u4e00-\u9fa5]*"
email_r=r"\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9._%+-]+)\s*<"

#过滤器
bloom_url=ScalableBloomFilter(initial_capacity=1e6,error_rate=0.0001)
bloom_info=ScalableBloomFilter(initial_capacity=1e6,error_rate=0.0001)
#开个文件写已爬网址
file_url=open('url.csv','w',encoding='utf-8-sig',newline='')
file_info=open('info.csv','w',encoding='utf-8-sig',newline='')
writer_url=csv.writer(file_url)
writer_info=csv.writer(file_info)
file_url.close()
def write_tel(list_p):
    '''将一个人员信息写入csv文件'''
    writer_info.writerow(list_p)
    del list_p

def url_search(url_q,url_list):
    '''将关联URL放入队列'''
    #print(url_q.qsize())#查看链接队列的大小
    for oneurl in url_list:
        if oneurl not in bloom_url:
            if url_q.qsize()>=10000:
                continue
            if not oneurl.startswith("http") or oneurl.endswith("pdf") or oneurl.endswith("ppt") \
                or oneurl.endswith("doc") or oneurl.endswith("xls") or oneurl.endswith('jpg'):
                continue
            url_q.put(oneurl)
            writer_url.writerow([oneurl])
            bloom_url.add(oneurl)
    del url_list

def name_and_tel(html,tel_dict):
    info=html
    '''寻找单位部门'''
    name_p=re.search(namep_r,info)
    if name_p:
        name_p=name_p.group(0)
    '''寻找单位电话'''
    t=r"(([\u4e00-\u9fa5]+)(：|:)((\d{11})|(\d{7,8})|((\d{3,4})-(\d{7,8}|\d{11}))))\b"
    all_tel=re.findall(t,info)
    tel=[]
    for i in all_tel:
        i=i[0]
        tel.append(i)
    if len(all_tel)>0:
        if name_p:
            tel_name=name_p
            if tel_name not in tel_dict:
                tel_dict[tel_name]=set(tel)
    
    '''寻找邮箱'''
    email=re.search(email_r,info)
    if email and not name_p==u'厦门大学':
        pos=email.start()
        email=email.group(1)
        if email not in bloom_info:
            near=info[pos-300:pos+300]
            #经过对数据的检测，大部分人员信息都有导师、教授关键字，可以提高准确率
            if u'教授' in near or u'导师' in near:
                '''寻找人名'''
                name_r = r'>\s*([\u4e00-\u9fa5]{2,3})\s*<'
                name=re.search(name_r,near)
                if name:
                    name=name.group(1)
                    bloom_url.add(email)
                    '''寻找电话'''
                    t=r"\b((\d{11})|(\d{7,8})|((\d{3,4})-(\d{7,8}|\d{11})))\b"
                    tele=re.search(t,near)
                    if tele:
                        tele=tele.group(0)
                    list_p=[name,email,tele,name_p]
                    bloom_info.add(email)
                    write_tel(list_p)
                    print(list_p)
    del html
