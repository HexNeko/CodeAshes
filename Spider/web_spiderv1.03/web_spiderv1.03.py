import csv
import queue
import threading
import os
import time

from find_and_filter import *
from request_html import *

'''全局变量'''
initial_url="https://www.xmu.edu.cn/"#起始网址
url_q=queue.Queue()#网址队列(栈)
count_url=0#爬取网址数
tel_dict={}#电话本
flag=True#程序是否结束,true继续false停止
wait_t=0#等待的线程数量,若所有线程都进入等待,则说明已结束

def search_and_removal(html,url_list):
    global tel_dict
    global url_q
    '''信息检索以及去重'''
    name_and_tel(html,tel_dict)
    url_search(url_q,url_list)

def html_search():
    global url_q
    global count_url
    global wait_t
    flag=False
    '''遍历所有网址'''
    while True:
        try:
            url=url_q.get(timeout=60)
        except:
            break
        if flag:
            wait_t-=1
        html,url_list=get_html(url)
        count_url+=1
        if html:
            search_and_removal(html,url_list)
        if url_q.empty():
            wait_t+=1
            flag=True
            if wait_t==300:
                break
    #print(threading.current_thread().name,"is over\n",end='')
    #查看消亡的线程
    
def save_in_file():
    dict_list=tel_dict.items()
    '''将结果写入文件'''
    file_tel=open('tel.csv','w',encoding='utf-8-sig',newline='')
    writer_tel=csv.writer(file_tel)
    for key,values in dict_list:
        writer_tel.writerow([key])
        writer_tel.writerows([[value] for value in values])
        writer_tel.writerow([' '])

def spider_begin():
    '''程序开始，设置300个线程'''
    global url_q
    url_q.put(initial_url)
    url_search(url_q,[initial_url])
    #html_search()
    thread_list=[]
    for i in range(300):
        athread=threading.Thread(target=html_search)
        athread.start()
        thread_list.append(athread)
    return thread_list
def display_now():
    global flag
    '''查看实时情况'''
    while flag:
        print("*now*")
        print("c_thr: %d"%(threading.active_count()))
        print("c_url: %d"%(count_url))
        #print("qsize: %d"%(url_q.qsize()))
        #time.sleep(3)#10s刷新一次
        os.system('cls')

def main():
    global flag
    print("*****web spider begin*****")
    begintime=time.strftime('%H:%M:%S',time.localtime(time.time()))
    #单独开一个线程监视事实情况
    t=threading.Thread(target=display_now)
    t.start()
    thread_list=spider_begin()
    #当所有线程结束
    for i in thread_list:
        i.join()
    flag=False
    t.join()
    print("*******save in file******")
    save_in_file()
    file_url.close()
    print("*******save success******")
    print("amount of url: %d"%(count_url))
    print("begin:",begintime)
    print("end:",time.strftime('%H:%M:%S',time.localtime(time.time())))
    print("*****web spider over*****")

if __name__ == '__main__':
    main()
