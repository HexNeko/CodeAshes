import numpy as np
import pandas as pd
import random

class Data:
    '''构造训练数据，读入数据'''
    def __init__(self):
        self.datas=None

    def create_data(self,W,c,args):
        '''以y=W*X+c为原型生成带噪声的数据
        n为数据个数,low,high为X的区间,scale为生成噪声正态分布的规模'''
        path,n,low,high,scale=args
        data=[]
        data_local=[]
        N=len(W)
        for i in range(0,n):
            X_list=[np.random.uniform(low, high) for i in range(N)]
            X=np.array(X_list)
            noise=np.random.normal(0., scale)
            y=W@X+c+noise
            data.append([X, y])
            data_local.append([X_list, y])
        #将数据存到本地
        df=pd.DataFrame(data=data_local,columns=['x','y'])
        df.to_csv(path,index=False)
        print("data create success")
        self.datas=data
        return data

    def input_data(self,args):
        '''从本地读取文件'''
        (path)=args
        data=pd.read_csv(path)
        data=data.values.tolist()
        for one in data:
            one[0]=np.array(eval(one[0]))
        print('数据读取成功')
        self.datas=data
        return data

    def data_part_random(self,nums,data=None):
        '''随机抽取n个样本'''
        if not data:
            data=self.datas
        if nums<len(data):
            part = random.sample(data, nums)
            return part
        else:
            return data

class Traning:
    '''模型的训练部分,进行迭代梯度下降'''

    def iterate_update(self,iterate_times,start_W,start_c,learning_rate,data,part_nums):
        '''迭代iterate_times次'''
        new_W=start_W
        new_c=start_c
        dimension=len(new_W)
        #计算第一次的均方差
        gradient_W,gradient_c,eg2_W,eg2_c=self.get_gradient(data,part_nums,new_W,new_c,dimension)
        #开始迭代
        for i in range(iterate_times): 
            print(new_W,new_c)      
            #得到W和c的梯度
            gradient_W,gradient_c,eg2_Wt,eg2_ct=self.get_gradient(data,part_nums,new_W,new_c,dimension)
            #梯度下降,使用RMSProp算法优化学习率
            #计算均方差eg2(t)=eg2(t-1)*0.9+eg2(t)*0.1
            eg2_W=eg2_W*0.9+eg2_Wt*0.1
            eg2_c=eg2_c*0.9+eg2_ct*0.1
            new_W=new_W-(learning_rate/np.sqrt(eg2_W+1))*gradient_W
            new_c=new_c-(learning_rate/np.sqrt(eg2_c+1))*gradient_c  

        return new_W,new_c

    def get_gradient(self,data,part_nums,W,c,dimension):
        '''求出当前的梯度和梯度平方均值'''
        part_data=data.data_part_random(part_nums)
        N=len(part_data)
        #初始化梯度值
        gradient_c,gradient_W=0,np.array([0.]*dimension)
        eg2_c,eg2_W=0,np.array([0.]*dimension)
        #计算梯度和梯度平方均值
        for (X,y) in part_data:
            #gradient=sum( 1/N*(W*x+c-y) ) 
            part_gradient=((W@X+c)-y)
            gradient_c=gradient_c+(1/N)*part_gradient
            eg2_c=eg2_c+(1/N)*part_gradient**2
            gradient_W=gradient_W+(1/N)*X*part_gradient
            eg2_W=eg2_W+(1/N)*(X*part_gradient)**2

        return gradient_W,gradient_c,eg2_W,eg2_c


class Model:
    def __init__(self,arguments):
        self.data=Data()
        self.traning=Traning()
        self.arguments=arguments

    def loss(self,data,W,c):
        '''损失函数：loss=sum(w*xi+c-yi)**2,返回计算的值
        data_points为数据集,W,c为线性回归y=W*X+c的系数'''
        N=len(data.datas)
        Wt=np.transpose(W)
        loss_sum=(1/N)*sum((Wt@point[0]+c-point[1])**2 for point in data.datas)
        return loss_sum

    def start(self):
        args=self.arguments
        #训练数据
        if args['data_type']==0:
            #数据来自随机创建
            self.data.create_data(args['goal_W'],args['goal_c'],args['data_args'])
        elif args['data_type']==1:
            self.data.input_data(args['data_args'][0])
        #开始迭代
        res_w,res_c=self.traning.iterate_update(args['iterate_times'],args['start_W'],args['start_c'],\
            args['learning_rate'],self.data,args['part_nums'])

        print('result: w:',res_w,'c:',res_c)
        print('loss:',self.loss(self.data,res_w,res_c))

def main():
    args={}
    #设定参数
    args['goal_W']=np.array([10,20,30,40])
    args['goal_c']=50
    args['start_W']=np.array([0,0,0,0])
    args['start_c']=0
    args['iterate_times']=50000
    args['learning_rate']=0.01
    #0随机创建 1读取本地
    args['data_type']=0
    #每次迭代随机抽取样本数，若大于等于总样本数则全部抽取
    args['part_nums']=100
    #参数：path(路径),nums(数量),low(X最小值),high(X最大值),scale(生成噪音正态分布规模)
    args['data_args']=('./data.csv',1000,-100,100,0.2)

    model=Model(args)
    model.start()

if __name__=='__main__':
    main()
