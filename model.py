import numpy as np

class Data:
    '''构造训练数据，读入数据'''

    def create_data(self,W,c,args):
        '''以y=W*X+c为原型生成带噪声的数据
        n为数据个数,low,high为X的区间,scale为生成噪声正态分布的规模'''
        (n,low,high,scale)=args
        data=[]
        N=len(W)
        for i in range(0,n):
            X=np.array([np.random.uniform(low, high) for i in range(N)])
            noise=np.random.normal(0., scale)
            y=W@X+c+noise
            data.append([X, y])
        print("data create success")
        return data

    def input_data(self,data):
        #get data form local
        pass
    def input_data_parted(self,data):
        #input parted data from big data
        pass

class Traning:
    '''模型的训练部分,进行迭代梯度下降部分'''

    def iterate_update(self,iterate_times,start_W,start_c,learning_rate,data_points):
        '''迭代iterate_times次'''
        new_W=start_W
        new_c=start_c
        dimension=len(new_W)
        for i in range(iterate_times): 
            print(new_W,new_c)      
            #得到W和c的梯度
            gradient_W,gradient_c=self.get_gradient(data_points,new_W,new_c,dimension)
            #梯度下降
            new_W=new_W-learning_rate*gradient_W
            new_c=new_c-learning_rate*gradient_c  

        return new_W,new_c

    def get_gradient(self,data_points,W,c,dimension):
        '''求出当前的梯度'''
        N=len(data_points)
        #初始化梯度值
        gradient_c,gradient_W=0,np.array([0.]*dimension)
        for (X,y) in data_points:
            #gradient=sum( 1/N*(W*x+c-y) ) 
            part_gradient=((W@X+c)-y)
            gradient_c=gradient_c+(1/N)*part_gradient
            gradient_W=gradient_W+(1/N)*X*part_gradient
            #print(gradient_W,gradient_c)
        return gradient_W,gradient_c

class Model:
    def __init__(self,arguments):
        self.data=Data()
        self.traning=Traning()
        self.arguments=arguments

    def loss(self,data_points,W,c):
        '''损失函数：loss=sum(w*xi+c-yi)**2,返回计算的值
        data_points为数据集,W,c为线性回归y=W*X+c的系数'''
        N=len(data_points)
        Wt=np.transpose(W)
        loss_sum=(1/N)*sum((Wt@point[0]+c-point[1])**2 for point in data_points)
        return loss_sum

    def start(self):
        args=self.arguments
        #训练数据
        data=None
        if args['data_type']==0:
            #数据来自随机创建
            data=self.data.create_data(args['goal_W'],args['goal_c'],args['data_args'])
        #开始迭代
        res_w,res_c=self.traning.iterate_update(args['iterate_times'],args['start_W'],args['start_c'],args['learning_rate'],data)
        print('result: w:',res_w,'c:',res_c)
        print('loss:',self.loss(data,res_w,res_c))

def main():
    args={}
    #设定参数
    args['goal_W']=np.array([2,3,4])
    args['goal_c']=5
    args['start_W']=np.array([0,0,0])
    args['start_c']=0
    args['iterate_times']=50000
    args['learning_rate']=0.0001
    args['data_type']=0 #0随机创建
    #参数：nums(数量),low(X最小值),high(X最大值),scale(生成噪音正态分布规模)
    args['data_args']=(100,-100,100,0.2)

    model=Model(args)
    model.start()

if __name__=='__main__':
    main()