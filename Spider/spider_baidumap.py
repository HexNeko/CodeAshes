import pandas as pd;
import json
import queue
import requests
import threading
from urllib.parse import urlencode

#预设属性
path_excel='CFPS区县编码对照表.xlsx'
key_nums=[2,3,4]
#表头
output_data=[['provname','cityname','countyname','电信','移动','联通','总计']]
data_unsort=[]
keys_q=queue.Queue()
count=0
#url中的变量
url_data = {
    'newmap': '1',
    'reqflag': 'pcmap',
    'biz': '1',
    'from': 'webmap',
    #'da_par': 'direct',
    'pcevaname': 'pc4.1',
    'qt': 's',
    'from': 'webmap',
    'wd': '',
    'wd2': '',
    'pn': '0',
    'nn': '0',
    #'db': '0',
    'sug': '0',
    #'addr': '0',
    #'da_src': 'searchBox.button', 
    #'on_gel': '1',
    #'src': '7',
    #'gr': '3',
    #'rn': '50',
    'tn': 'B_NORMAL_MAP',
    'ie': 'utf-8',
    'newfrom': 'zhuzhan_webmap',
}
#模拟浏览器
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
}
#得到数量
def get_num(key):
    url_data['wd']=key
    # 把字典对象转化为url的请求参数
    url = 'https://map.baidu.com/?' + urlencode(url_data)
    response = requests.get(url, headers=headers,  timeout=60)
    response.encoding = 'utf-8'
    html = response.text
    #print(html)
    html=json.loads(html)
    num = html['result']['total']
    return num
#读取本地文件
def get_data():
    data=pd.read_excel(path_excel,sheet_name=0)
    row_nums=len(data.index.values)
    return data,row_nums
#从本地文件中拼接出搜索的key
def get_keys(data,row_nums):
    global key_nums
    for i in range(row_nums):
        key_line=[i]
        for j in key_nums:
            key_line.append(data.iloc[i,j])
        keys_q.put(key_line)
#搜索一行
def search_line():
    global count
    while True:
        try:
            key=keys_q.get(timeout=10)
        except:
            break
        '''
        dx=get_num(key[1]+' '+key[2]+' '+key[3]+' 中国电信')
        yd=get_num(key[1]+' '+key[2]+' '+key[3]+' 中国移动')
        lt=get_num(key[1]+' '+key[2]+' '+key[3]+' 中国联通')
        '''
        dx=get_num(key[1]+key[2]+key[3]+' 中国电信')
        yd=get_num(key[1]+key[2]+key[3]+' 中国移动')
        lt=get_num(key[1]+key[2]+key[3]+' 中国联通')
        sum=dx+yd+lt
        line=[key[0],key[1],key[2],key[3],dx,yd,lt,sum]
        data_unsort.append(line)
        print(line)
        count+=1
        print(count)
        if keys_q.empty():
            break
#爬虫
def spider():
    thread_pool=[]
    for i in range(20):
        t=threading.Thread(target=search_line)
        t.start()
        thread_pool.append(t)
    for thread in thread_pool:
        thread.join()
    data_unsort.sort(key=lambda ele: ele[0])
    #输出
    for i in data_unsort:
        output_data.append(i[1:])
    df=pd.DataFrame(output_data[1:],columns=output_data[0])
    df.to_excel("res_test2.xlsx",index=False)

if __name__=='__main__':
    data,row_nums=get_data()
    get_keys(data,row_nums)
    spider()

