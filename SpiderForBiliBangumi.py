import requests
import re

class UserInfomation:
    '''用户信息'''
    def __init__(self,uid):
        self.uid=uid
        self.bangumiNum=1
        self.bangumiUrl='https://api.bilibili.com/x/space/bangumi\
/follow/list?type=1&follow_status=0&pn=1&ps=15&vmid='+uid+'&ts=1664070901438'
    def nextPage(self):
        self.bangumiNum+=1
        self.bangumiUrl='https://api.bilibili.com/x/space/bangumi\
/follow/list?type=1&follow_status=0&pn='+str(self.bangumiNum)+'&ps=15&vmid='+self.uid+'&ts=1664070901438'

class WebSpider:
    '''爬虫主要部分'''
    def __init__(self,user):
        self.animeList=[]
        self.outPath=''
        self.user=user

    def getInfoInWeb(self,url):
        '''返回网页的文本内容'''
        try:
            r=requests.get(url,timeout=1)
            r.raise_for_status()
            r.encoding=r.apparent_encoding
            return r.text
        except:
            return None

    def InfoProcessing(self,goalUrl):
        '''处理信息'''
        data=self.getInfoInWeb(goalUrl)
        if data:
            message=re.search(r'("message":")([^"]+)"',data)
            message=message.group(2)
            if message=='用户隐私设置未公开':
                print(message)
            elif not message=='0':
                print("未知错误")
            else:
                animeReList=re.findall(r'("番剧","title":"|"国创","title":")([^"]+)"',data)
                if animeReList:
                    for anime in animeReList:
                        self.animeList.append(anime[1])
                        print(anime[1]+'  get')
                    return True
        return False

    def StartWebSpider(self,path):
        while self.InfoProcessing(self.user.bangumiUrl):
            self.user.nextPage()
        #输出
        self.outPath=path
        self.outPath=self.outPath+'追番列表.txt'
        if self.animeList:
            with open(self.outPath,'w',encoding='utf-8') as f:
                for anime in self.animeList:
                    print(anime,file=f)
        print("*over*")

def main():
    #隐藏番剧列表的无法爬取
    url=input("输入UID：")
    path=input("输入导出路径，不输默认目录下：")
    user=UserInfomation(url)
    bili=WebSpider(user)
    bili.StartWebSpider(path)

if __name__=='__main__':
    main()

    