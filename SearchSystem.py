import os
import pickle
import time
import threading
import jieba
import tkinter as tk
from math import *

class Node:
    #倒排索引表节点
    def __init__(self,term,freq,lists):
        self.term=term
        self.freq=freq
        self.lists=lists
    def __lt__(self,b):
        return self.term<b.term

class Node_vector:
    #权值向量
    def __init__(self,id,val):
        self.id=id
        self.val=val
    def __lt__(self,b):
        return self.val>b.val

class List_Creat:
    #负责构建倒排索引表
    def __init__(self):
        self.path='./已分词数据'

    def change_path(self,string_path):
        self.path = string_path

    def judge_term(self,term,stopword):
        '''判断是否为非汉字或停用词'''
        if term<'\u4e00' or term>'\u9fff':
            return False
        if term==' ' or term =='\n':
            return False
        if term in stopword:
            return False
        return True

    def input_file(self,id_dict,text):
        '''读取文件'''
        #停用词表
        stopword=[]
        if os.path.isfile('.\stop_word.txt'):
            with open('.\stop_word.txt','r',encoding='utf-8') as f:
                stopword=f.read().split()
        else:
            print("无停用词表")
        #构建词条序列
        files=os.listdir(self.path)
        #倒排索引表
        indexer={}
        #tf矩阵
        tf_matrix={}
        docid=-1
        #文件个数
        N=len(files)
        for file in files:
            docid+=1
            id_dict[docid]=file
            #给文件编号
            position=self.path+'\\'+file
            #去重
            filter=set([])
            #只打开文本文件
            if not position.endswith("txt"):
                continue
            with open(position,'r',encoding='GBK',errors='ignore') as f:
                data=f.read()
                #利用jieba库进行分词
                data=jieba.lcut(data)
                #读取文件内容，以空格分割
                for term in data:
                    #若已经在倒排索引表中
                    if term in indexer:
                        tf_matrix[term][docid]+=1
                        if term not in filter:
                            filter.add(term)
                            indexer[term].lists.append(docid)
                            indexer[term].freq+=1
                        continue
                    if self.judge_term(term,stopword):
                        indexer[term]=Node(term,0,[])
                        indexer[term].lists.append(docid)
                        indexer[term].freq+=1
                        filter.add(term)
                        tf_matrix[term]=[0 for i in range(0,N)]
                        tf_matrix[term][docid]+=1
            text.delete('1.0','end')
            text.insert(tk.INSERT,'***创建进度'+str(docid+1)+'/'+str(N))
            print(docid)
        #更新提示信息
        text.delete('1.0','end')
        text.insert(tk.INSERT,'***创建完成，可以开始搜索')   
        return indexer,tf_matrix

    def creat(self,text):
        '''建立倒排索引表'''
        id_dict={}
        indexer,tf_matrix=self.input_file(id_dict,text)
        print('indexer length',len(indexer))
        with open('./data.pickle','wb') as f:
            pickle.dump([indexer,tf_matrix,id_dict,self.path],f)
        #将字典转化为一个列表，用于排序记录
        indexer_list=[indexer[Node] for Node in indexer]
        indexer_list.sort()
        #将建好的表存入文件，用于调试
        with open('./indexer.txt','w',encoding='utf-8') as f:
            for i in indexer_list:
                print(i.term,i.freq,i.lists,file=f)
        with open('./tf_list.txt','w',encoding='utf-8') as f:
            for i in indexer_list:
                print(i.term,tf_matrix[i.term],file=f)
        print('success Creating')
        return indexer,tf_matrix,id_dict

class Bool_Operation:
    #负责布尔检索的布尔运算
    def list_and(self,a,b):
        '''a and b'''
        posa,posb=0,0
        ans=[]
        while posa<len(a) and posb<len(b):
            if a[posa]==b[posb]:
                ans.append(a[posa])
                posa+=1
                posb+=1
            elif a[posa]<b[posb]:
                posa+=1;
            else:
                posb+=1
        return ans

    def list_or(self,a,b):
        '''a or b'''
        ans=[]
        posa,posb=0,0
        while posa<len(a) and posb<len(b):
            if a[posa]==b[posb]:
                ans.append(a[posa])
                posa+=1
                posb+=1
            elif a[posa]<b[posb]:
                ans.append(a[posa])
                posa+=1
            else:
                ans.append(b[posb])
                posb+=1
        while posa<len(a):
            ans.append(a[posa])
            posa+=1
        while posb<len(b):
            ans.append(b[posb])
            posb+=1
        return ans

    def list_not(self,b,N):
        '''not b'''
        ans=[]
        a=range(0,N)
        posa,posb=0,0
        while posa<len(a) and posb<len(b):
            if a[posa]==b[posb]:
                posa+=1
                posb+=1
            elif a[posa]<b[posb]:
                ans.append(a[posa])
                posa+=1
            else:
                posb+=1
        while posa<len(a):
            ans.append(a[posa])
            posa+=1
        return ans

class Main(List_Creat,Bool_Operation):
    #程序主要部分
    def __init__(self):
        super(Main,self).__init__()
        self.indexer={}
        self.tf_matrix={}
        self.id_dict={}
        self.N=0

    def grade(self,termlist,id,N):
        '''输入词项序列,docid,文件个数'''
        '''求出向量'''
        vector=[]
        if id==-1:
            #计算输入表达式的tf-idf权重
            for term in termlist:
            #tf-idf权重计算
                val=self.indexer.get(term,None)
                if val:
                    r=0.5+log(N/val.freq,5)
                else:
                    #若信息集中没有此关键词则赋权为0
                    r=0
                vector.append(r)
        else:
            for term in termlist:
                #tf-idf权重计算
                val=self.indexer.get(term,None)
                if val:
                    r=(1+log(self.tf_matrix[term][id],2))
                else:
                    r=0
                vector.append(r)
        return vector

    def similar(self,base,b):
        '''求出A,B的余弦相似度'''
        length=len(base)
        sim=sum(base[i]*b[i] for i in range(0,length))
        return sim

    def operation(self,s_input):
        '''解析输入字符串,并运算'''
        stack=[]
        s_input='('+s_input+')'
        s_input=s_input.replace('AND',' AND ')
        s_input=s_input.replace('NOT',' NOT ')
        s_input=s_input.replace('OR',' OR ')
        s_input=s_input.replace('（',' ( ')
        s_input=s_input.replace('(',' ( ')
        s_input=s_input.replace('）',' ) ')
        s_input=s_input.replace(')',' ) ')
        s_input=s_input=s_input.split()
        #消除中文括号
        for i in range(0,len(s_input)):
            if s_input[i]=='（':
                s_input[i]='('
            elif s_input[i]=='）':
                s_input[i]=')'
        for i in range(0,len(s_input)):
            #如果不是运算符，则将其替换成序列列表
            if s_input[i] not in {'AND','OR','NOT','(',')'}:
                val=self.indexer.get(s_input[i],None)
                if val:
                    s_input[i]=val.lists
                else:
                    s_input[i]=[]
        for i in s_input:
            #解析输入的字符串，更加关键词分割
            if isinstance(i,str) and i==')':
                operate=[]
                while stack[-1]!='(':
                    operate.append(stack.pop())
                stack.pop()
                operate.reverse()
                tem=[]
                for n in range(0,len(operate)):
                    if isinstance(operate[n],str) and operate[n]=='NOT':
                        operate[n+1]=self.list_not(operate[n+1],self.N)
                    else:
                        tem.append(operate[n])
                operate=tem
                if len(tem)>0:
                    tem=operate[0]
                else:
                    tem=[]
                j=1
                while j<len(operate):
                    if operate[j]=='AND':
                        tem=self.list_and(tem,operate[j+1])
                        j+=2
                    elif operate[j]=='OR':
                        tem=self.list_or(tem,operate[j+1])
                        j+=2
                    else:
                        tem=self.list_and(tem,operate[j])
                        j+=1
                stack.append(tem)
            else:
                stack.append(i)
        return stack[0]

    def s_search(self,s_input):
        #负责信息搜索
        time_begin=time.time()*1000
        result=[]
        s=s_input
        ids=self.operation(s_input)
        if 'OR' in s_input or 'NOT' in s_input:
            for id in ids:
                result.append([id,str(self.id_dict[id])])
        else:
            #对AND链接的表达式进行权重排序
            termlist=[]
            for term in s.split():
                if term not in {'AND','(',')','（','）'}:
                    termlist.append(term)
            base=self.grade(termlist,-1,self.N)
            res=[]
            for id in ids:
                v=self.grade(termlist,id,self.N)
                res.append(Node_vector(id,self.similar(base,v)))
            res.sort()
            for i in res:
                result.append([i.id,str(self.id_dict[i.id]),str(i.val)])
        time_end=time.time()*1000
        return result,time_end-time_begin

    def init(self,text,position):
        #初始化数据
        if os.path.isfile('.\data.pickle'):
            with open('.\data.pickle','rb') as f:
                self.indexer,self.tf_matrix,self.id_dict,self.path=pickle.load(f)
                self.N=len(self.id_dict)
            position.delete(0,'end')
            position.insert(0,self.path)
            text.delete('1.0','end')
            text.insert(tk.INSERT,'初始化数据成功')
        else:
            text.delete('1.0','end')
            text.insert(tk.INSERT,'请先初始化数据')

#系统UI部分，基于Tkinter
def button_search(m,entry,lb,result_m,text):
    '''搜索按钮相关'''
    s_input=entry.get()
    try:
        result,time_cost=m.s_search(s_input)
    except Exception as e:
        print(e)
        text.delete('1.0','end')
        text.insert(tk.INSERT,"***系统错误！")
    #搜索结果数&消耗时间(毫秒)
    result_m.set('搜索耗时：'+str(round(time_cost,3))+'ms'+'\n'+'搜索结果：'+str(len(result))+' 个')
    #清屏&输出
    lb.delete(0,'end')
    count=0
    #输出结果
    for i in result:
        count+=1
        lb.insert('end','num:'+str(count) \
            +' '*(30-2*len(str(count))) \
            +i[1])

def button_creat(position,m,text):
    '''创建按钮相关'''
    path = position.get()
    m.change_path(path)
    t = threading.Thread(target=creat_data,args=(m,text,position))
    t.start()

def button_openf(m,lb,text):
    '''打开文件按钮相关'''
    try:
        filename = lb.get(lb.curselection())
        filename = filename.split()[1]
        os.startfile(m.path+'/'+filename)
    except Exception as e:
        print(e)
        text.delete('1.0','end')
        text.insert("***打开文件失败！")

def creat_data(m,text,position):
    '''建立数据'''
    try:
        m.creat(text)
        m.init(text,position)
    except Exception as e:
        print(e)
        text.delete('1.0','end')
        text.insert("***构建错误！")

def start():
    '''初始化UI'''
    m=Main()
    #新建窗口root
    root=tk.Tk()
    root.title('文本信息快速检索系统 V1.0')
    if os.path.exists('./favicon.ico'):
        root.iconbitmap('./favicon.ico')
    root.geometry('680x560')
    #输入框
    m_search=tk.Message(root,text='搜索栏：',width=300)
    entry=tk.Entry(root,width=70)
    m_position=tk.Message(root,text='地址栏：',width=300)
    position=tk.Entry(root,width=70)
    #提示信息文本框
    m_text=tk.Message(root,text='提示信息：',width=300)
    text=tk.Text(root,width=20,height=10)
    #搜索结果
    m_list=tk.Message(root,text='搜索结果：',width=300)
    lb=tk.Listbox(root,width=70,height=20)
    scrollbar=tk.Scrollbar(root,orient=tk.VERTICAL)
    #滚动条绑定
    scrollbar.config(command=lb.yview)
    text.config(yscrollcommand=scrollbar.set)
    #消耗时间 搜索结果数
    result_m=tk.StringVar()
    result_m.set('搜索耗时：'+'0.0ms'+'\n'+'搜索结果：'+'0 个')
    #搜索按钮
    b_search=tk.Button(root,text='搜索',\
        command=lambda:button_search(m,entry,lb,result_m,text),width=15,height=1)
    #创建链表
    b_creat=tk.Button(root,text='创建',\
        command=lambda:button_creat(position,m,text),width=15,height=1)
    #打开文件
    b_openf=tk.Button(root,text='打开所选文件',\
        command=lambda:button_openf(m,lb,text),width=15,height=1)
    #提示信息
    mess='*注意：\n*支持关键词检索(关键词以空格隔开)以及布尔检索(支持AND/OR/NOT以及括号,算符必须大写)*'
    m_mess=tk.Message(root,text=mess,width=700)
    result_message=tk.Message(root,textvariable=result_m,width=720)
    #布局
    m_search.grid(row=0,column=0,sticky='sw')
    entry.grid(row=1,column=0)
    b_search.grid(row=1,column=1)
    m_position.grid(row=2,column=0,sticky='sw')
    position.grid(row=3,column=0)
    b_creat.grid(row=3,column=1)
    m_mess.grid(row=4)
    m_list.grid(row=5,column=0,sticky='sw')
    lb.grid(row=6,column=0,rowspan=3)
    m_text.grid(row=5,column=1,sticky='sw')
    text.grid(row=6,column=1,sticky='n')
    b_openf.grid(row=7,column=1,sticky='n')
    scrollbar.grid(row=6,column=2)
    result_message.grid(row=8,column=1)
    m.init(text,position)
    root.mainloop()

def main():
    '''主函数'''
    start()

if __name__=="__main__":
    main()