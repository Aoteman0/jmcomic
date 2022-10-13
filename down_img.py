# coding=gbk
import math
import os,io
import urllib.request
import requests
import execjs
from PIL import Image
from Include.useragents.myran import Myran

os.environ['EXECJS_RUNTIME'] = "JScript"

class Simg:
    def __init__(self):
        pass
    def app(self,*args):
        proxy = {
            "http": "127.0.0.1:10809",
            "https": "127.0.0.1:10809"
        }
        #print(args)
        myran = Myran()
        imgurl = args[0]
        #print(imgurl)
        imgpath=args[-1]
        try:
            # httpproxy_handler = urllib.request.ProxyHandler(proxies=proxy)
            # opener = urllib.request.build_opener(httpproxy_handler)
            # urlz = urllib.request.Request(imgurl, headers={"User-Agent": myran.agents()})
            # im2 = Image.open(opener.open(urlz))
            response=requests.get(imgurl, headers={"User-Agent": myran.agents()},proxies=proxy)
            if response.status_code == 200:
                im2 = Image.open(io.BytesIO(response.content))
                #im2.show()
                #print(imgurl, args[1],imgpath, im2)
                self.splitimage(imgurl, args[1],imgpath, im2)
        except Exception as e:
            print(e.__traceback__.tb_lineno,imgurl,e)
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
            # newimage.show()
            # print(image_list)
            # return image_list

#saveimg=Simg()
# print(saveimg.get_md5("wfwef"))
#print(saveimg.get_num(293360,'00005'))
#saveimg.app("https://cdn-msp.18comic.org/media/photos/250528/00002.webp",250528,"00002.jpg")