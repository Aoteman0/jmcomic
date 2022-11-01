import io

import requests
import time
import os,re
from multiprocessing import Queue
import threading
from threading import Lock
from lxml import etree
import math
import execjs
from PIL import Image
from myran import Myran
import get_jm_url

os.environ['EXECJS_RUNTIME'] = "JScript"

class Data(threading.Thread):
    def __init__(self,thread_name,book_name,albumid):
        super().__init__()
        self.thread_name = thread_name
        self.book_name=book_name
        self.albumid=albumid
    def run(self):
        print("%s开始了！" % self.thread_name)
        while not data_empty:
            try:
                if not data_queue.empty():
                    data = data_queue.get(False)
                else:
                    time.sleep(3)
                    data = data_queue.get(False)
                print("data_queue大小",data_queue.qsize())
                try:
                    #print(data[2])
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
                # except requests.exceptions.ConnectionError:
                #     print("重新抛入queue：",data)
                #     data_queue.put(data)
                except Exception as e:
                    print(e.__traceback__.tb_lineno,e)
                    print("重新抛入data_queue：")
                    data_queue.put(data)
            except:
                pass
    def parse(self,rsp,path_photo,photoid):
        rsp_etree=etree.HTML(rsp.text)
        img_list =rsp_etree.xpath("//div[@class='panel-body']/div/div[contains(@class,'center')]/img")
        #print("img_list:",len(img_list))
        for i in img_list:
            img_url= i.attrib['data-original']
            img_name = os.path.basename(img_url).split('.')[0]
            path_img = "%s\\%s.jpg" % (path_photo, img_name)
            #print([img_url,photoid,path_img])
            down_queue.put([img_url,photoid,path_img])
class Download(threading.Thread):
    def __init__(self,thread_name):
        super().__init__()
        self.thread_name = thread_name
    def run(self):
        print("%s开始了！"%self.thread_name)
        while not down_empty:
            try:
                print("还剩余%s张图片"%down_queue.qsize())
                if not down_queue.empty():
                    down = down_queue.get(False)
                else:
                    time.sleep(3)
                    down = down_queue.get(False)
                try:
                    print("down",down)
                    if not os.path.exists(down[2]):
                        #scramble_id=220980 网页固定值
                        if int(down[1])>220980:#albumid>aid就使用拼接函数 否则直接下载
                            print("拼接图片")
                            self.pjdown(down[0],down[1],down[2])
                        else:
                            print("直接下载图片")
                            self.dowm_img(down[0],down[2])

                except  Exception as e:
                    print(e.__traceback__.tb_lineno,e)
                    print("重新抛入queue：",down)
                    down_queue.put(down)
            except:
                pass
    def dowm_img(self,url,path_img):
        # s=random.choice(list(range(3)))+1+random.random()
        # time.sleep(s)
        #print("time.sleep=%d"%s)
        headers["User_Agent"]=myran.agents()
        response = requests.get(url,headers=headers,proxies=proxy)
        if response.status_code == 200:
            with open(path_img,"wb") as f:
                f.write(response.content)
        else:print("图片request失败")
    def pjdown(self,*args):
        imgurl = args[0]
        #print(imgurl)
        imgpath=args[-1]
        # httpproxy_handler = urllib.request.ProxyHandler(proxies=proxy)
        # opener = urllib.request.build_opener(httpproxy_handler)
        # urlz = urllib.request.Request(imgurl, headers={"User-Agent": myran.agents()})
        # im2 = Image.open(opener.open(urlz))

        headers["User_Agent"]=myran.agents()
        response=requests.get(imgurl, headers=headers,proxies=proxy)
        if response.status_code == 200:
            im2 = Image.open(io.BytesIO(response.content))
            #im2.show()
            #print(imgurl, args[1],imgpath, im2)
            self.splitimage(imgurl, args[1],imgpath, im2)
    def get_md5(self,num):
        with open('js/md5.js', 'r') as file:
            result = file.read()
        context1 = execjs.compile(result)
        result1 = context1.call('md5', num)
        return result1
    def get_num(self,e, t):
        #print(type(e),e, type(t),t)
        a = 10
        try:
            num_dict = {}
            for i in range(10):
                num_dict[i] = i * 2 + 2
            if (int(e) >= 268850):
                n = str(e) + t;
                # switch(n=(n = (n = md5(n)).substr(-1)), n %= 10) {
                #print("n=",n)
                tmp = ord(self.get_md5(n)[-1])
                result = num_dict[tmp % 10]
                a = result
            return a
        except Exception as e:
            print(e.__traceback__.tb_lineno,e)
            return False
    def splitimage(self,src, aid,imgpath,imageob=''):
        if imageob == '':
            image = Image.open(src)
        else:
            image = imageob
        w, h = image.size
        #image.show()
        img_name = os.path.basename(src).split('.')[0]
        # print(type(aid),type(img_name))
        if self.get_num(aid, img_name):
            s = self.get_num(aid, img_name)  # 随机值
            # print(s)
            l = h % s  # 切割最后多余的值
            box_list = []
            hz = 0
            for i in range(s):
                c = math.floor(h / s)
                g = i * c
                hz += c
                h2 = h - c * (i + 1) - l
                if i == 0:
                    c += l;hz += l
                else:
                    g += l
                box_list.append((0, h2, w, h - g))

            # print(box_list,len(box_list))
            item_width = w
            # box_list.reverse() #还原切图可以倒序列表
            # print(box_list, len(box_list))
            newh = 0
            image_list = [image.crop(box) for box in box_list]
            # print(box_list)
            newimage = Image.new("RGB", (w, h))
            for image in image_list:
                # image.show()
                b_w, b_h = image.size
                newimage.paste(image, (0, newh))

                newh += b_h
            newimage.save(imgpath)

data_queue=Queue()
down_queue=Queue()
data_empty = False
down_empty = False
lock = Lock()
myran = Myran()
headers = {
    #'cookie':'ipcountry=US; AVS=4eb0s4o5ho9hfmp704ge7jtium; ipm5=bb7f6ac39cebfa37e89bd07544c549fd; cover=1; guide=1; __atuvc=12|39,31|40,5|41,0|42,4|43; __atuvs=635cabf67eff0d49003; yuo1={"objName":"hT3l8Pyn15Uf","request_id":0,"zones":[{"idzone":"2967008","here":{}},{"idzone":"2967010","here":{}},{"idzone":"2967010","here":{}},{"idzone":"3597795","sub":"70","here":{}}]}',
    #'referer': 'https://18comic.org/',
    "User_Agent": myran.agents()
}
proxy = {
    #"http":"127.0.0.1:10809",
    #"https":"127.0.0.1:10809"
}
def app(url):
    try:
        global data_empty,down_empty

        newurl_list=get_jm_url.app()
        response=''
        if newurl_list:
            if re.findall(r'https://(.*?)/\w+/\d+/',url)[0] not in newurl_list:
                for newurl in newurl_list:
                    url = re.sub(re.findall(r'https://(.*?)/\w+/\d+/', url)[0], newurl, url)
                    response = requests.get(url=url, headers=headers, proxies=proxy)
                    break
            else:
                response = requests.get(url=url, headers=headers, proxies=proxy)
        else:
            response = requests.get(url=url, headers=headers, proxies=proxy)
        if response:
            albumid = re.search(r'/album/(\d+)', url).group(1)
            referer = re.search(r'(https://\w+\.\w+)/', url).group(1)
            print("albumid", albumid, referer, url)
            print(response.url)
            if response.status_code == 200:
                print(response.status_code)
                eth = etree.HTML(response.text)
                #拿到所有话数
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
                        data_queue.put((photo_name,photoid,referer+i.attrib['href']))
    except Exception as e:
        print(e.__traceback__.tb_lineno,e)
    if data_queue.qsize():
        data_queue_len  = data_queue.qsize()
        print("当前一共%s話" % data_queue_len)
        data_list=['data线程%s号'%s for s in list(range(1,data_queue_len if data_queue_len <= 8 else 8))]
        data_thread_list=[]
        for i in data_list:
            data=Data(i,book_name,albumid)
            data.start()
            time.sleep(0.7)
            data_thread_list.append(data)
        startime=time.perf_counter()
        while True:
            if down_queue.qsize()>100 or time.perf_counter()-startime>10:
                break
        print('down_queue.qsize():%s'%down_queue.qsize())
        down_list=['down下载线程%s号'%s for s in list(range(1,40 if down_queue.qsize()>40 else down_queue.qsize()))]
        down_thread_list=[]
        for i in down_list:
            down=Download(i)
            down.start()
            time.sleep(0.7)
            down_thread_list.append(down)
        while not data_queue.empty():
            pass
        data_empty=True
        for thread in data_thread_list:
            thread.join()
            print("%s结束了！"%thread.thread_name)

        while not down_queue.empty():
            pass
        down_empty=True
        for down_thread in down_thread_list:
            down_thread.join()
            print("%s结束了！"%down_thread.thread_name)


if __name__ == '__main__':
    app("https://18comic.vip/album/390129/")
