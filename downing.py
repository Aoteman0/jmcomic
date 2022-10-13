import requests
import time
import os,re
from multiprocessing import Queue
import threading
from threading import Lock
from myran import Myran
from lxml import etree
from down_img import Simg

class Data(threading.Thread):
    def __init__(self,book_name,albumid,downqueue):
        super().__init__()
        self.book_name=book_name
        self.albumid=albumid
        self.down_queue=downqueue
    def run(self):
        while not data_empty:
            time.sleep(1)
            try:
               data = data_queue.get(False)
               #print(data)
               try:
                    headers['referer']=data[2]
                    response = requests.get(url=data[2], headers=headers, proxies=proxy)
                    if response.status_code==200:
                        path_album = "G:\\comic\\%s" % self.book_name
                        path_photo = "%s\\%s" % (path_album, data[0])
                         # path_img = "path_photo\\%s.jpg" %img_name
                        with lock:  # 判断文件夹是否存在要加锁
                            if not os.path.exists("G:\\comic"): os.mkdir("G:\\comic")
                            if not os.path.exists(path_album): os.mkdir(path_album)
                            if not os.path.exists(path_photo): os.mkdir(path_photo)
                        self.parse(response,path_photo,data[1])
               except Exception as e:
                   data_queue.put(data)
                   print(e.__traceback__.tb_lineno,e,data)

            except Exception as e:
                pass
    def parse(self,rsp,path_photo,photoid):
        rsp_etree=etree.HTML(rsp.text)
        img_list =rsp_etree.xpath("//div[@class='panel-body']/div/div[contains(@class,'center')]/img")
        #print("img_list:",len(img_list))
        for i in img_list:
            img_url= i.attrib['data-original']
            img_name = os.path.basename(img_url).split('.')[0]
            path_img = "%s\\%s.jpg" % (path_photo, img_name)
            #print(path_img)
            self.down_queue.put([img_url,photoid,path_img])
class Download(threading.Thread):
    def __init__(self):
        super().__init__()
    def run(self):
        while not down_empty:
            try:
                down = down_queue.get(False)
                try:
                    if not os.path.exists(down[2]):
                        #scramble_id=220980 网页固定值
                        if int(down[1])>220980:#albumid>aid就使用拼接函数 否则直接下载
                            print("拼接图片")
                            saveimg.app(down[0],down[1],down[2])
                        else:
                            print("直接下载图片")
                            self.dowm_img(down[0],down[2])
                except:
                    down_queue.put(down)
            except:
                break
    def dowm_img(self,url,path_img):
        try:
            # s=random.choice(list(range(3)))+1+random.random()
            # time.sleep(s)
            #print("time.sleep=%d"%s)
            response = requests.get(url,headers=headers,proxies=proxy)
            if response.status_code == 200:
                with open(path_img,"wb") as f:
                    f.write(response.content)
            else:print("图片request失败")
        except Exception as e:
            pass

data_queue=Queue()
down_queue=Queue()
data_empty = False
down_empty = False
lock = Lock()
myran = Myran()
saveimg=Simg()
headers = {
    #'cookie': '_ga=GA1.2.1540031906.1664414186; _ga_VW05C6PGN3=GS1.1.1664789639.4.0.1664789640.59.0.0; __atuvc=14%7C39%2C9%7C40%2C1%7C41; ipcountry=US; AVS=ajmoaur97d4npbl01m57kr35m3; cover=1; shuntflag=1; guide=1; ipm5=0cd9de309e89bd6bbae94102596909b7; yuo1=%7B%22objName%22:%22nLBcY3VxeaTgP%22,%22request_id%22:0,%22zones%22:%5B%7B%22idzone%22:%223648533%22,%22here%22:%7B%7D%7D,%7B%22idzone%22:%223648533%22,%22here%22:%7B%7D%7D%5D%7D',
    #'referer': 'https://18comic.org/',
    "User_Agent": myran.agents()
}
proxy = {
    "http": "127.0.0.1:10809",
    "https": "127.0.0.1:10809",
}
def app(url):
    global data_queue,down_queue,data_empty,down_empty
    albumid = re.search(r'/album/(\d+)',url).group(1)
    #print(albumid)
    try:
        while True:
            if proxy:
                response=requests.get(url=url,headers=headers,proxies=proxy)
            else:response=requests.get(url=url,headers=headers,proxies=proxy)
            if response.status_code == 200:
                #print(response.text)
                eth = etree.HTML(response.text)
                nums = eth.xpath("//div[@class='row']/div[6]/div[1]/div[1]/ul[contains(@class,'btn-toolbar')]/a")
                book_name = eth.xpath("//div[@itemprop='name']/h1[@id='book-name']/text()")[0]
                book_name = re.sub(r'[\\\/\|\(\)\~\?\.\:\：\-\*\<\>]', '', book_name)

                if nums:
                    for i in nums:
                        photo_name_list = i.xpath("li/text()")[0].split()
                        #print(re.findall(r'[\u4E00-\u9FA5]+.*?', i.xpath("li/text()")[0]))
                        try:
                            if re.findall(r'[\u4E00-\u9FA5]', photo_name_list[2]):
                                photo_name=re.sub(r'\s','',photo_name_list[0])+' '+photo_name_list[2]
                            else:photo_name=re.sub(r'\s','',photo_name_list[0])
                        except Exception as e:
                            photo_name = re.sub(r'\s', '', photo_name_list[0])
                        photo_name = re.sub(r'[\\\/\|\(\)\~\?\.\:\：\-\*\<\>\-]', '',photo_name)
                        #print(photo_name)
                        photoid=i.attrib['data-album']
                        data_queue.put((photo_name,photoid,"https://18comic.org"+i.attrib['href']))
                break
    except Exception as e:
        print(e.__traceback__.tb_lineno,e)
    if data_queue:
        data_queue_len  = data_queue.qsize()
        print("当前一共%s話" % data_queue_len)
        data_list=list(range(data_queue_len if data_queue_len <= 8 else 8))
        data_thread_list=[]
        for i in data_list:
            data=Data(book_name,albumid,down_queue)
            data.start()
            data_thread_list.append(data)
        time.sleep(1)
        down_list=list(range(30))
        down_thread_list=[]
        for i in down_list:
            down=Download()
            down.start()
            down_thread_list.append(down)
        while not data_queue.empty():
            pass
        data_empty=True
        for thread in data_thread_list:
            thread.join()
            print("data线程%s结束了！"%thread.getName())

        while not down_queue.empty():
            pass
        down_empty=True
        for down_thread in down_thread_list:
            down_thread.join()
            print("down线程%s结束了！"%down_thread.getName())


if __name__ == '__main__':
    app("https://18comic.org/album/146417")