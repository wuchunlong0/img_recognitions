# -*- coding: utf-8 -*-
# https://console.bce.baidu.com/ai/?_=1530048735638&fromai=1#/ai/ocr/app/detail~appId=416472
# 有道云笔记 图像识别   使用baidu-aip模块 识别中文图像okokok! 优点是：快、准、简洁 

#baidu 接入流程 http://ai.baidu.com/docs#/Begin/top

# 下面的方法，识别效果都不理想！！！
#0、import pytesseract 模块仓库源代码。       https://github.com/madmaze/pytesseract/blob/master/src/pytesseract.py
#1、Python PIL ImageDraw 和ImageFont模块学习。 https://www.cnblogs.com/Chilly2015/p/5705700.html
#2、安装Pillow、tesseract-ocr与pytesseract模块的安装。  https://www.cnblogs.com/hupeng1234/p/7136442.html
#3、tesseract-ocr识别英文和中文图片文字以及扫描图片实例讲解。    https://blog.csdn.net/wanghui2008123/article/details/37694307
#4、图片操作技巧总结 http://www.jb51.net/Special/645.htm
# PIL 图像处理二。    https://blog.csdn.net/u013378306/article/details/70156842
#  PIL ImageDraw 和ImageFont     https://blog.csdn.net/dou_co/article/details/17618319
# Pillow模块使用例程。   https://www.cnblogs.com/Lival/p/6211602.html
# Pillow 图片处理的使用。   http://www.yeayee.com/article-6739499-1.html
# PIL-Python图像库。   http://yongyuan.name/pcvwithpython/chapter1.html
# 高级示例：图像去噪。 http://book.51cto.com/art/201406/442238.htm
# 完整的图片去噪代码。  http://dream-people.iteye.com/blog/379064
from __future__ import unicode_literals

from django.shortcuts import render
from django.http.response import HttpResponseRedirect, HttpResponse
from PIL import Image, ImageDraw, ImageFont, ImageFilter,ImageEnhance
import pytesseract
from numpy import *
import os 

from aip import AipOcr
import re

# 重要说明：
#执行其他方法时将文件名路径 改为name = 'img/cuili.jpeg'  



AppID = '11450107'
API_Key = 'uAA5KGXAzDDk2ewBa3dvRrWj'
Secret_Key = 'CgLyabrL4WH5KV0yyT074cMx8GyAnRGt'
#使用baidu-aip模块 识别中文图像okokok! 优点是：快、准、简洁 
#  http://localhost:9000/distinguish_img_str/  
def distinguish_img_str(reuqest):  #test
    #身份证图像
    name = 'img/cuili.jpeg'  #
    name = 'img/wuchunlong.jpeg' #
    name = 'imgchunlong.jpeg' #
    name = 'img/wu1.jpeg'  #  ok
    name = 'img/wu2.jpeg'  #  ok
#    name = 'img/wu3.jpeg' #图像逆时针90度  baidu-aip模块不能识别旋转的图像
#    name = 'img/wj1.jpeg' #
#    name = 'img/wj2.jpeg' 
        
    s = ''
    client = AipOcr(AppID,API_Key,Secret_Key)
    img = open(name,'rb').read()
    msg = client.basicGeneral(img)
    for m in msg.get('words_result'):
        s += m.get('words') +'<br>' 
        print( m.get('words'))
    return HttpResponse(s)


def get_distinguish_img_str(name):
    s = ''
    client = AipOcr(AppID,API_Key,Secret_Key)
    img = open(name,'rb').read()
    msg = client.basicGeneral(img)
    for m in msg.get('words_result'):
        s += m.get('words') + '\n'
    return s

from django.http import JsonResponse

#  http://localhost:9000/distinguish_img/  
def distinguish_img(request):
    name ='name_img.jpg'   
    res = get_distinguish_img_str(name)
    mylist = [{"res" : res}] 
    return JsonResponse(mylist, safe = False) 

#  http://localhost:9000/wx_uploadFile/
# def wx_uploadFile(request):
#     name = ''
#     if request.method == 'POST':   
#         myfile = request.FILES.get("file", None)
#         if myfile:
#             with open('name_img.jpg','wb') as file:
#                 file.write(myfile.read())
#     mylist = [{"name" : name}] 
#     return JsonResponse(mylist, safe = False) 


def wx_uploadFile(request):
    name = ''
    if request.method == 'POST':   
        myfile = request.FILES.get("file", None)
        if myfile:
            if not WriteFile(myfile):
                name = 'Img file err!'
    mylist = [{"name" : name}] 
    return JsonResponse(mylist, safe = False) 
 
def WriteFile(myfile):
    try:
        with open('name_img.jpg','wb') as file:
            file.write(myfile.read())
    except:
        return False
    return True


#--下面用 pytesseract模块 识别中文图像效果差。加上自己的算法有改善，但通用性不好 ----#
# 1、真实姓名 max-min = 134-142
# 2、有字区  max-min  = 84-102
# 3、边缘区 max-min  = 46-116
# 4、空白区 max-min = 35-40

PROBE_W = 30 #矩形探头宽
PROBE_H = 30 #矩形探头高


# rectangle((200,200,500,500),outline = "red")

PRO_W,PRO_H = 2,2
# 点(PRO_W*PRO_H)如果不全为0，则将该点置255。功能：清除字边缘的黑点
def Eliminate_edge(imarr,x1,y1,w,h):
    #w,h = w-PRO_W,h-PRO_H
    for y0 in  range(h/PRO_H):
        y = y1 + y0*PRO_H 
        for x0 in  range(w/PRO_W):
            x = x1 + x0*PRO_W
            if Average(imarr,x,y,PRO_W,PRO_H) != 0 :#
                setbox_255(imarr,x,y,PRO_W,PRO_H,0) 
    return 0,0

# 点(PRO_W*PRO_H)外框，如果全为255，则将该点置255。 功能：清除单独的黑点
def Eliminate_Alone(imarr,x1,y1,w,h):
    for y0 in  range(h/PRO_H):
        y = y1 + y0*PRO_H 
        for x0 in  range(w/PRO_W):
            x = x1 + x0*PRO_W
            minbox = x,y,PRO_W,PRO_H
            maxbox = minbox[0]-1,minbox[1]-1,minbox[2]+2,minbox[3]+2
            if get_empty_box_Average(imarr,maxbox,minbox) == 255:#
                setbox_255(imarr,x,y,PRO_W,PRO_H,0) 
    return 0,0

#清除噪声
def Eliminate_Noise(imarr,x1,y1,w,h):
    min,max =getbox_min_max(im,x,y,w,h)
    v=(min+max)/2
    if v<100:
        v=100
    setbox_255(imarr,x,y,w,h,v)
    setbox_0(imarr,x,y,w,h,v)    
    Eliminate_edge(imarr,x,y,w,h)    
    Eliminate_Alone(imarr,x,y,w,h)
    print( 'min,max,v=(min+max)/2 ',min,max,v)
    return ''


# 测试
#     imarr[100][100],imarr[100][101] = 0,0
#     imarr[101][100],imarr[101][101] = 0,0
#     imarr[99][99], imarr[99][100], imarr[99][101], imarr[99][102] = 255, 255,            255,           255
#     imarr[100][99],imarr[100][100],imarr[100][101],imarr[100][102] = 255, imarr[100][100],imarr[100][101],255
#     imarr[101][99],imarr[101][100],imarr[101][101],imarr[101][102] = 255, imarr[101][100],imarr[101][101],255
#     imarr[102][99],imarr[102][100],imarr[102][101],imarr[102][102] = 255, 255,            255,            255
#     maxbox = 99,99,4,4
#     minbox = 100,100,2,2
#     print 'get_empty_box_Average==',get_empty_box_Average(imarr,maxbox,minbox)
#获得大矩形框与小矩形框之间的平均值
def get_empty_box_Average(imarr,maxbox,minbox):
    return (Total(imarr,maxbox[0],maxbox[1],maxbox[2],maxbox[3]) - Total(imarr,minbox[0],minbox[1],minbox[2],minbox[3]))/(maxbox[2]*maxbox[3]-minbox[2]*minbox[3])
                
def Eliminate_Noise(im,imarr,x,y,w,h):
    min,max = getbox_min_max(im,x,y,w,h)
    v = (min+max)/2
    if v > 127:
        v = 127
    elif min == 0:
        if v > 100 : #min == 0 and v > 100 特殊值
            v -= 10
        elif max == 157:  #min == 0 and v < 100 特殊值
            v += 23     
        else:
            v += 0    #10
    elif min != 0 and min < 50 and v < 100: #特殊值
        if min == 40 and max == 153: #年
            v -= 2
        elif min == 33 and max == 163:#33 163
            v += 20
        else:
            v += 7 #10
    else:
        pass
    setbox_255(imarr,x,y,w,h,v)
    setbox_0(imarr,x,y,w,h,v)    
    Eliminate_edge(imarr,x,y,w,h)    
    Eliminate_Alone(imarr,x,y,w,h)
    print( 'min,max,v=(min+max)/2 ',min,max,v)
    return ''


# http://localhost:9000/test_img/  
def test_img(reuqest):
    name = 'cuili.jpeg'  #
#     name = 'wuchunlong.jpeg' #
#     name = 'chunlong.jpeg' #
    name = 'wu1.jpeg'  #  ok
#    name = 'wu2.jpeg'  #  ok
#     name = 'wu3.jpeg' #图像逆时针90度
#     name = 'wj1.jpeg' #
#    name = 'wj2.jpeg' 

    img,imgarr,IMG_W,IMG_H,name_x0,name_y0,endx,endy = get_img_basedata(name)
    if IMG_W == -1 or IMG_H == -1:
        return HttpResponse(str(img))
    
    #获得单字（真实姓名）开始坐标、宽度和高度 ok
    name_startx,name_starty,w1,h1 = get_xy_w_h(img,name_x0,name_y0,4,90)

    
    box1,box2,liftBOX,nameBOX,sexBOX,nationBOX,hanBOX,y1961BOX,yearBOX,\
        a12BOX,monthBOX,a25BOX,dayBOX,addressBOX,citizenBOX,num620BOX = \
        get_img_coordinate(img,imgarr,name_x0,name_y0,w1,h1,endx,endy) #显示准确定位的矩形框
    im = Image.new('L',[IMG_W,IMG_H],"white") #创建新图像
    region = img.crop(box1) # 设置区域内，拷贝原图
    im.paste(region,box1) # 区域内，原图 粘贴到创建新图像
    region1 = img.crop(box2) # 设置区域内，拷贝原图
    im.paste(region1,box2) # 区域内，原图 粘贴到创建新图像
    imarr = array(im)
    
    #左边矩形框
    x,y,w,h = liftBOX[0],liftBOX[1],liftBOX[2],liftBOX[3]
    Eliminate_Noise(im,imarr,x,y,w,h)
    
#     x,y,w,h = nameBOX[0],nameBOX[1],nameBOX[2],liftBOX[3] #右框 置白
#     setbox_255(imarr,x,y,w,h,0)
      
    x,y,w,h = nameBOX[0],nameBOX[1],nameBOX[2],nameBOX[3]
    Eliminate_Noise(im,imarr,x,y,w,h)
    x,y,w,h = sexBOX[0],sexBOX[1],sexBOX[2],sexBOX[3]
    Eliminate_Noise(im,imarr,x,y,w,h)
    x,y,w,h = nationBOX[0],nationBOX[1],nationBOX[2],nationBOX[3]
    Eliminate_Noise(im,imarr,x,y,w,h)
    x,y,w,h = hanBOX[0],hanBOX[1],hanBOX[2],hanBOX[3]
    Eliminate_Noise(im,imarr,x,y,w,h)
    x,y,w,h = y1961BOX[0],y1961BOX[1],y1961BOX[2],y1961BOX[3]
    Eliminate_Noise(im,imarr,x,y,w,h)
    x,y,w,h = yearBOX[0],yearBOX[1],yearBOX[2],yearBOX[3]
    Eliminate_Noise(im,imarr,x,y,w,h)
    x,y,w,h = a12BOX[0],a12BOX[1],a12BOX[2],a12BOX[3]
    Eliminate_Noise(im,imarr,x,y,w,h)
    x,y,w,h = monthBOX[0],monthBOX[1],monthBOX[2],monthBOX[3]
    Eliminate_Noise(im,imarr,x,y,w,h)
    x,y,w,h = a25BOX[0],a25BOX[1],a25BOX[2],a25BOX[3]
    Eliminate_Noise(im,imarr,x,y,w,h)
    x,y,w,h = dayBOX[0],dayBOX[1],dayBOX[2],dayBOX[3]
    Eliminate_Noise(im,imarr,x,y,w,h)
    x,y,w,h = addressBOX[0],addressBOX[1],addressBOX[2],addressBOX[3]
    Eliminate_Noise(im,imarr,x,y,w,h)

       
    # 公民身份号
    x,y,w,h = citizenBOX[0],citizenBOX[1],citizenBOX[2],citizenBOX[3]
    Eliminate_Noise(im,imarr,x,y,w,h)
    
    # 620
    x,y,w,h = num620BOX[0],num620BOX[1],num620BOX[2],num620BOX[3]
    Eliminate_Noise(im,imarr,x,y,w,h)
         
    im = Image.fromarray(imarr) # 二维数组转换成图像
    print( pytesseract.image_to_string(im,lang='chi_sim') )
    return HttpResponse(im.show(),"GIF")     
    return HttpResponse('ok')


 

# 获得单字开始坐标、宽度和高度。x,y单字左上方坐标，w,h 例如4,90 x+90要能覆盖到检测的单字。
def get_xy_w_h(img,x,y,w,h):
    x0,y0,w0,h0 = x,y,w,h   
    x1,y1 = get_absmin_x(img,x0,y0,w0,h0)
    x2,y2 = get_absmin_x(img,x1+10,y1,w0,h0)
    x0,y0,w0,h0 = x,y,h,w
    x3,y3 = get_absmin_y(img,x0,y0,w0,h0)
    x4,y4 = get_absmin_y(img,x3,y3+10,w0,h0)
    return x1,y3,x2-x1,y4-y3 #开始坐标，高、宽
# 图像基本操作 图像粘贴 http://localhost:9000/index/  
def index(reuqest):
    name = 'cuili.jpeg'
#     name = 'wuchunlong.jpeg'
#    name = 'chunlong.jpeg'
#    name = 'wu1.jpeg'
#     name = 'wu2.jpeg'  #？
#     name = 'wu3.jpeg' #图像逆时针90度
#    name = 'wj1.jpeg'
#    name = 'wj2.jpeg' 
    img = Image.open(name).convert('L') #转换成灰度图像
    img.save('L'+name)
    img = Image.open('L'+name).convert('L') #作用？屏蔽了，get_box_xy() 获得坐标结果不同
    IMG_W = img.size[0]
    IMG_H = img.size[1]
    imgarr = array(img) #图像变为二维数组
    
    #图像粘贴 ok
    im = Image.new('L',[IMG_W,IMG_H],"white") #创建新图像
    box=(IMG_W/2-200,IMG_H/2-200,IMG_W/2+200,IMG_H/2+200)#设置区域    
    region = img.crop(box) # 设置区域内，拷贝原图
    im.paste(region,box) # 区域内，原图 粘贴到创建新图像       
    img = Image.fromarray(imgarr) # 二维数组转换成图像
    return HttpResponse(im.show(),"GIF") 


    
    img = Image.fromarray(imgarr) # 二维数组转换成图像
    return HttpResponse(img.show(),"GIF")     
    return HttpResponse('ok') 
  
# def box_abs_minmax_name_threshold(img,x,y,w,h):
#     THRESHOLD = core_sub_maxmin(img)
#     if THRESHOLD > 115:
#         THRESHOLD = 115    
#     min,max = box_min_max(img,x,y,w,h)           
#     return abs(min-max) > THRESHOLD


IS_NAME_BOX_MIN_THRESHOLD = 60 #设置姓名 验证矩形框中 最小值 阀值
IS_NAME_BOX_SUB_MAXMIN_THRESHOLD = 100 #设置获得姓名 验证矩形框中 最大值-最小值 阀值
LOOKUP_NAME_THRESHOLD = 100 #设置姓名 阀值

IS_620_BOX_MIN_THRESHOLD = 50 #设置620 验证矩形框中 最小值 阀值
IS_620_BOX_SUB_MAXMIN_THRESHOLD = 100 #设置620 验证矩形框中 最大值-最小值 阀值
LOOKUP_620_THRESHOLD = 100 #设置620 阀值

def get_sub_maxmin_x(img,x1,y1,w,h,t):
    for n in  range(1000):
        x = x1+n
        if box_sub_maxmin_name_threshold(img,x,y1,w,h,t):       
            return x,y1
    return 0,0


#同一矩形框中 判断 最大值-最小值 > 设置阀值
def box_sub_maxmin_620_threshold(img,x,y,w,h): 
    min,max = box_min_max(img,x,y,w,h)           
    return max-min > LOOKUP_620_THRESHOLD
 
#同一矩形框中 判断 最大值-最小值 > 设置阀值
def box_sub_maxmin_name_threshold(img,x,y,w,h,t): 
    min,max = box_min_max(img,x,y,w,h)           
    return max-min > t


#上下扫描
def get_name_x(img,x1,y1,w,h,t):
    for y0 in  range(h/PROBE_H):
        y = y1 + y0*PROBE_H 
        for x0 in  range(w/PROBE_W):
            x = x1 + x0*PROBE_W
            if box_sub_maxmin_name_threshold(img,x,y,PROBE_W,PROBE_H,t) and is_x_name(img,x,y):#
                return x,y 
    return 0,0
#左右扫描
def get_name_y(img,x1,y1,w,h,t):
    t+=5 #提高左边(把标签当干扰)阀值
    for x0 in  range(w/PROBE_W):
        x = x1 + x0*PROBE_W 
        for y0 in  range(h/PROBE_H):
            y = y1 + y0*PROBE_H 
            if box_sub_maxmin_name_threshold(img,x,y,PROBE_W,PROBE_H,t) and is_y_name(img,x,y):# and box_sub_maxmin_name_threshold(img,x+PROBE_W*2,y+PROBE_H,PROBE_W,PROBE_H,t):
                return x,y 
    return 0,0

def get_name_xy(img):
    t = LOOKUP_NAME_THRESHOLD
    x1,y1 = 0,0
    w,h = img.size[0]/2,img.size[1]/2
    xx,xy = get_name_x(img,x1,y1,w,h,t)
    yx,yy = get_name_y(img,x1,y1,w,h,t)
    return yx,xy 
#验证矩形框,作用：清除干扰
def is_x_name(img,x1,y1):
    BOX = x1+40,y1+30,5,30 #设置验证矩形框
    min,max =  getbox_min_max(img,BOX[0],BOX[1],BOX[2],BOX[3] )     
    if min<IS_NAME_BOX_MIN_THRESHOLD and max-min>IS_NAME_BOX_SUB_MAXMIN_THRESHOLD:
        return True
    return False
#验证矩形框,作用：清除干扰
def is_y_name(img,x1,y1):
    BOX = x1+40,y1+30,5,30 #设置验证矩形框
    min,max =  getbox_min_max(img,BOX[0],BOX[1],BOX[2],BOX[3] )     
    if min<IS_NAME_BOX_MIN_THRESHOLD and max-min>IS_NAME_BOX_SUB_MAXMIN_THRESHOLD:
        return True
    return False



#验证矩形框,作用：清除干扰
def is_x_620(img,x1,y1):
    BOX = x1-100,y1,50,40 #设置验证矩形框
    min,max =  getbox_min_max(img,BOX[0],BOX[1],BOX[2],BOX[3] )     
    if min<IS_620_BOX_MIN_THRESHOLD and (max-min)>IS_620_BOX_SUB_MAXMIN_THRESHOLD:
        return True
    return False

def get_620_x(img):
    x0,y0 = img.size[0]-PROBE_W,img.size[1]-PROBE_H
    w,h = x0+PROBE_W,y0+PROBE_H
    for y1 in  range(h/PROBE_H):
        y = y0 - y1*PROBE_H 
        for x1 in  range(w/PROBE_W):
            x = x0 - x1*PROBE_W
            if box_sub_maxmin_620_threshold(img,x,y,PROBE_W,PROBE_H) and is_x_620(img,x,y):# is_620() 清除干扰
                return x,y 
    return 0,0


#单元测试 http://localhost:9000/unit_test   
def unit_test(reuqest):
    name = 'cuili.jpeg'
#     name = 'wuchunlong.jpeg'  # 有边框 ok
#     name = 'chunlong.jpeg' #下面有干扰点 有边框 ok
#    name = 'wu1.jpeg' # 有边框 ok
#    name = 'wu2.jpeg' #有边框 ok 
#    name = 'wu3.jpeg' #图像逆时针90度 no
#     name = 'wj1.jpeg' #有边框 ok 
#     name = 'wj2.jpeg' #有边框 ok

    #图像变为二维数组 
    img = Image.open(name).convert('L') #转换成灰度图像
    img.save('L'+name)
    img = Image.open('L'+name).convert('L') #作用？屏蔽了，get_box_xy() 获得坐标结果不同
    IMG_W = img.size[0]
    IMG_H = img.size[1]
    imgarr = array(img) #图像变为二维数组   

#---------------------测试函数 get_anme_xy -----------------# 
#函数 get_anme_xy使用了下面3个全局变量
# IS_NAME_BOX_MIN_THRESHOLD = 60 #设置姓名 验证矩形框中 最小值 阀值
# IS_NAME_BOX_SUB_MAXMIN_THRESHOLD = 100 #设置获得姓名 验证矩形框中 最大值-最小值 阀值
# LOOKUP_NAME_THRESHOLD = 100 #设置姓名 阀值
#---------------------测试获得真实姓名 左上方坐标 有验证 get_anme_xy----------# 
#     x,y = get_name_xy(img)
#     doline(imgarr,x,y,30,30)
#     doline(imgarr,x+40,y+30,5,30)
#---------------------测试   get_620_x   -----------------#                
#     x,y = get_620_x(img)
#     doline(imgarr,x,y,30,30)
#---------------------测试函数 get_img_basedata --------------------------#  
#     img,imgarr,IMG_W,IMG_H,name_x0,name_y0,endx,endy = get_img_basedata(name)
#     if IMG_W == -1 or IMG_H == -1:
#         return HttpResponse(str(img))
#     print 'IMG_W,IMG_H = ', IMG_W,IMG_H
#     doline(imgarr,10,10,IMG_W-21,IMG_H-21)
#     doline(imgarr,name_x0,name_y0,10,10)
#     doline(imgarr,endx,endy,10,10)    

#---------------------  测试函数 get_xy_w_h ------------------------------#
#     img,imgarr,IMG_W,IMG_H,name_x0,name_y0,endx,endy = get_img_basedata(name)
#     if IMG_W == -1 or IMG_H == -1:
#         return HttpResponse(str(img))
#   
#     #获得单字（真实姓名）开始坐标、宽度和高度 ok
#     name_startx,name_starty,w1,h1 = get_xy_w_h(img,name_x0,name_y0,4,90)
#     print 'w1,h1=',w1,h1
#     doline(imgarr,name_x0,name_y0,4,90) #移动的采样矩形框
#     doline(imgarr,name_startx,name_starty,w1,h1) #测试结果
#----------------------测试函数 test_get_img_coordinate -------------------------------#
    img,imgarr,IMG_W,IMG_H,name_x0,name_y0,endx,endy = get_img_basedata(name)
    if IMG_W == -1 or IMG_H == -1:
        return HttpResponse(str(img))
    
    #获得单字（真实姓名）开始坐标、宽度和高度 ok
    name_startx,name_starty,w1,h1 = get_xy_w_h(img,name_x0,name_y0,4,90)
          
    box1,box2,liftBOX,nameBOX,sexBOX,nationBOX,hanBOX,y1961BOX,yearBOX,\
        a12BOX,monthBOX,a25BOX,dayBOX,addressBOX,citizenBOX,num620BOX = \
        test_get_img_coordinate(img,imgarr,name_x0,name_y0,w1,h1,endx,endy) #显示准确定位的矩形框

#-----------------------各种类型30*30矩形框 测试值比较----------------------#
#     name = 'cuili.jpeg'
#     #测试各种类型30*30矩形框  min max  max-min  Average() - (min+max)/2 （平均值相减）
#     img,imgarr,IMG_W,IMG_H,name_x0,name_y0,endx,endy = get_img_basedata(name)
#     if IMG_W == -1 or IMG_H == -1:
#         return HttpResponse(str(img))
#     name_startx,name_starty,w1,h1 = get_xy_w_h(img,name_x0,name_y0,4,90)    
#     w1,h1 = PROBE_W,PROBE_H
#            
#     x0,y0,w0,h0 = name_startx,name_starty,w1,h1
#     min,max =  getbox_min_max(img,x0,y0,w0,h0 )
#     doline(imgarr,x0,y0,w0,h0 ) 
#     print '崔 min,max =',min,max,max-min,Average(array(img),x0,y0,w0,h0 )-(min+max)/2  
#     
#     x0,y0,w0,h0 = name_startx,name_starty-120,w1,h1
#     min,max =  getbox_min_max(img,x0,y0,w0,h0)
#     doline(imgarr,x0,y0,w0,h0) 
#     print '崔上方 min,max =',min,max,max-min,Average(array(img),x0,y0,w0,h0)-(min+max)/2    
# 
#     x0,y0,w0,h0 = name_startx+900,name_starty-120,60,60
#     min,max =  getbox_min_max(img,x0,y0,w0,h0)
#     doline(imgarr,x0,y0,w0,h0) 
#     print '崔上方 右 min,max =',min,max,max-min,Average(array(img),x0,y0,w0,h0)-(min+max)/2    
# 
#     
#     x0,y0,w0,h0 = name_x0-100,name_y0+30,4,60
#     min,max =  getbox_min_max(img,x0,y0,w0,h0)
#     doline(imgarr,x0,y0,w0,h0) 
#     print '名 min,max =',min,max,max-min,Average(array(img),x0,y0,w0,h0)-(min+max)/2     
#     
#     x0,y0,w0,h0 = name_x0-50,name_y0+30,4,60
#     min,max =  getbox_min_max(img,x0,y0,w0,h0)
#     doline(imgarr,x0,y0,w0,h0) 
#     print '名右边 min,max =',min,max,max-min,Average(array(img),x0,y0,w0,h0)-(min+max)/2     
# 
#     x0,y0,w0,h0 = name_x0-125,name_y0+160,4,60
#     min,max =  getbox_min_max(img,x0,y0,w0,h0)
#     doline(imgarr,x0,y0,w0,h0) 
#     print '别 前1 min,max =',min,max,max-min,Average(array(img),x0,y0,w0,h0)-(min+max)/2     
# 
#     x0,y0,w0,h0 = name_x0-115,name_y0+160,4,60
#     min,max =  getbox_min_max(img,x0,y0,w0,h0)
#     doline(imgarr,x0,y0,w0,h0) 
#     print '别 前2 min,max =',min,max,max-min,Average(array(img),x0,y0,w0,h0)-(min+max)/2     
# 
#     x0,y0,w0,h0 = name_x0-105,name_y0+160,4,60
#     min,max =  getbox_min_max(img,x0,y0,w0,h0)
#     doline(imgarr,x0,y0,w0,h0) 
#     print '别 min,max =',min,max,max-min,Average(array(img),x0,y0,w0,h0)-(min+max)/2     
# 
#     x0,y0,w0,h0 = name_x0-55,name_y0+160,4,60
#     min,max =  getbox_min_max(img,x0,y0,w0,h0)
#     doline(imgarr,x0,y0,w0,h0) 
#     print '别 后 min,max =',min,max,max-min,Average(array(img),x0,y0,w0,h0)-(min+max)/2     
# 
#     x0,y0,w0,h0 = name_x0+270,name_y0+160,4,60
#     min,max =  getbox_min_max(img,x0,y0,w0,h0)
#     doline(imgarr,x0,y0,w0,h0) 
#     print '族 前1 min,max =',min,max,max-min,Average(array(img),x0,y0,w0,h0)-(min+max)/2     
# 
#     x0,y0,w0,h0 = name_x0+280,name_y0+160,4,60
#     min,max =  getbox_min_max(img,x0,y0,w0,h0)
#     doline(imgarr,x0,y0,w0,h0) 
#     print '族 前2 min,max =',min,max,max-min,Average(array(img),x0,y0,w0,h0)-(min+max)/2     
# 
# 
#     x0,y0,w0,h0 = name_x0+290,name_y0+160,4,60
#     min,max =  getbox_min_max(img,x0,y0,w0,h0)
#     doline(imgarr,x0,y0,w0,h0) 
#     print '族 min,max =',min,max,max-min,Average(array(img),x0,y0,w0,h0)-(min+max)/2     
    
#----------------------中心区域 -------------------------------#
#     box=(IMG_W/2-20,IMG_H/2-50,40,100)#设置区域    
#     doline(imgarr,box[0],box[1],box[2],box[3])
#     min,max =  getbox_min_max(img,box[0],box[1],box[2],box[3])
#     print 'min,max =', min,max,max-min
#     print core_sub_maxmin(img)
#---------------------测试函数 老函数 没有验证 get_box_xy get_endbox_xy -----------------#     
#     x1,y1 = get_box_xy(img,0,0,IMG_W,IMG_H) #ok wu1 33-45; cuili 33-40; wuchunlong 33-45; chunlong 33-43;
#     x2,y2 = get_endbox_xy(img,IMG_W,IMG_H) #结束坐标
#     doline(imgarr,x1,y1,30,30)
#     doline(imgarr,x2,y2,30,30)

    
    
    img = Image.fromarray(imgarr) # 二维数组转换成图像
    return HttpResponse(img.show(),"GIF") 
    return HttpResponse('ok')   


def core_sub_maxmin(img):
    IMG_W,IMG_H = img.size[0],img.size[1]
    box=(IMG_W/2-20,IMG_H/2-50,40,100)#设置区域
    min,max =  getbox_min_max(img,box[0],box[1],box[2],box[3])
    return max-min

#获得图像文字部分坐标
def get_img_coordinate(img,imgarr,name_x0,name_y0,w1,h1,endx,endy):
    #标签姓名 左上方坐标
    tag_name_x0,tag_name_y0 = name_x0-w1*4,name_y0  
    
    # 左边区域
    w,h =ag_w,ag_h = w1*4,h1*9
    

    # 右边区域
    # 真实姓名 吴春龙  崔丽
    namex,namey,namew,nameh =xx,yy,ww,hh= name_x0,name_y0,w1*4,h1*2-10
#     doline(imgarr,namex,namey,10,10)#真实姓名开始坐标
    
    # 男 女 开始坐标
    Sex_x0,Sex_y0 = Sex_x,Sex_y = name_x0,name_y0+nameh
#     doline(imgarr,Sex_x,Sex_y,10,10) # 男 女 左上方 坐标 
    
    x0,y0,w0,h0 = Sex_x,Sex_y ,100,4 # 设置检测 男 前面 矩形框
#     doline(imgarr,x0,y0,w0,h0) #
    x,y = get_absmin_y(img,x0,y0,w0,h0) # 获得 男 前面 坐标
#     doline(imgarr,x,y,10,10) 
    Sex_y = y
         
    x0,y0,w0,h0 = Sex_x+w1*8,Sex_y,6,w1 #汉 设置检测矩形框 从右往左检测
    x,y = get_absmin_end_x(img,x0,y0,w0,h0) #获得 汉 结束坐标
#     doline(imgarr,x0,y0,w0,h0)
#     doline(imgarr,x,y,10,10)
    
    x0,y0,w0,h0 = x-14,y,6,w1 #汉 设置检测矩形框 从右往左检测 
    han_x,han_y = x,y = get_absmin_end_x(img,x0,y0,w0,h0) #获得 汉 开始坐标
#     doline(imgarr,x0,y0,w0,h0)
#     doline(imgarr,x,y,10,10)    
         
     
    # 1960 1961 1988
    startx,starty = Sex_x0,Sex_y0+nameh
#     doline(imgarr,startx,starty,10,10)  # 1960 1961 1988开始坐标
    
    x0,y0,w0,h0 = startx,starty ,100,4 # 设置检测 1960 1961 1988 前面 矩形框
#     doline(imgarr,x0,y0,w0,h0) #
    x,y = get_absmin_y(img,x0,y0,w0,h0) # 获得 1960 1961 1988 前面 坐标
#     doline(imgarr,x,y,10,10) 
    
    x0,y0,w0,h0 = x+70,y,30,w1 #设置检测 1960 1961 1988 矩形框
#     doline(imgarr,x0,y0,w0,h0)
    x,y = get_absmin_x(img,x0,y0,w0,h0)
#     doline(imgarr,x,y,10,10) #获得1960 1961 1988 结束坐标    
    Sexw = x+w1/2-startx    
    y1961BOX = startx,starty ,Sexw,nameh

    # 年
    yearx,yeary,yearw,yearh = startx+Sexw,starty,w1+5,nameh
    yearBOX = yearx,yeary,yearw,yearh
 
    # 12
    a12x,a12y,a12w,a12h = yearx+yearw,starty,han_x-(yearx+yearw)-10,nameh
    a12BOX = a12x,a12y,a12w,a12h
     
    # 月
    monthx,monthy,monthw,monthh = a12x +a12w,a12y,w1+5,nameh
    monthBOX = monthx,monthy,monthw,monthh
     
    #25
    a25x,a25y,a25w,a25h = monthx+monthw,monthy,w1+20,monthh
    a25BOX = a25x,a25y,a25w,a25h
     
    # 日
    dayx,dayy,dayw,dayh = a25x+a25w,a25y,140,a25h
         
     
    # 男 女 矩形框
    Sexx,Sexy,Sexw,Sexh = Sex_x0,Sex_y0,Sexw,nameh
    sexBOX = Sexx,Sexy,Sexw,Sexh
    #doline(imgarr,Sexx,Sexy,Sexw,Sexh)  
    # 民族 矩形框
    Nationx,Nationy,Nationw,Nationh = Sexx+Sexw,Sexy,han_x-(Sexx+Sexw),Sexh
    nationBOX = Nationx,Nationy,Nationw,Nationh
    #doline(imgarr,Nationx,Nationy,Nationw,Nationh)         
    
    # 甘肃省
    address_x,address_y = name_x0,dayy+dayh #
#     doline(imgarr,address_x,address_y,10,10) # 甘肃省开始坐标
    x0,y0,w0,h0 = address_x,address_y ,150,4 # 设置检测 甘肃省 前面 矩形框
#     doline(imgarr,x0,y0,w0,h0) #
    x,y = get_absmin_y(img,x0,y0,w0,h0)
#     doline(imgarr,x,y,10,10) 
     
    x0,y0,w0,h0 = x+150,y,30,w1 #设置检测甘肃省矩形框
    x,y = get_absmin_x(img,x0,y0,w0,h0) #检测结果坐标
    addressx,addressy,addressw,addressh = address_x,address_y,x-address_x +5,w1*3+10
#     doline(imgarr,x0,y0,w0,h0) #显示检测甘肃省矩形框
#     doline(imgarr,x,y,10,10) #显示检测结果坐标
        
    #公民 身份证号码
    x0,y0,w0,h0 = tag_name_x0,tag_name_y0 + ag_h + 1,200,4 #+30 设置检测 公民身份证号码 矩形框
#     doline(imgarr,x0,y0,w0,h0) #
    citizen_x,citizen_y = get_absmin_y(img,x0,y0,w0,h0)  #获得公民身份证号码 前面 坐标 
#     doline(imgarr,citizen_x,citizen_y,10,10) 

    x0,y0,w0,h0 = tag_name_x0+w1*10,tag_name_y0 + ag_h + 1,w1,4 #获得620 上面 检测框
#     doline(imgarr,x0,y0,w0,h0) # 
    x,y = get_absmin_y(img,x0,y0,w0,h0) #获得620  检测框 开始坐标
    x0,y0,w0,h0 = x,y,w0,h1 #获得620  检测框 
#     doline(imgarr,x0,y0,w0,h0) # 
    citizen_end_x,citizen_end_y = get_absmin_end_x(img,x0,y0,w0,h0) #获得 公民身份证号码 结束坐标
#     doline(imgarr,citizen_end_x,citizen_end_y,10,10)
    
    end_620_x,end_620_y = get_absmin_x(img,x0,y0,w0,h0) #获得 620 结束坐标
#     doline(imgarr,end_620_x,end_620_y,10,10)  
     
    citizenx,citizeny,citizenw,citizenh = tag_name_x0,citizen_y-30,citizen_end_x-tag_name_x0+5,h1*2+20
                
    citizenBOX = citizenx,citizeny,citizenw,citizenh      
    liftBOX = tag_name_x0,tag_name_y0,w,h #左边矩形框
    nameBOX = namex,namey,addressx+addressw-namex,nameh #吴春龙
    hanBOX = Nationx+Nationw,Nationy,addressx+addressw-(Nationx+Nationw),Nationh #汉
      
    dayBOX = dayx,dayy,addressx+addressw-dayx,dayh #日  
    addressBOX = addressx,addressy,addressw,tag_name_y0+h-addressy # 甘肃省    
    num620BOX = citizenx+citizenw,citizeny,endx-(citizenx+citizenw)+30,citizenh #620。。。
      
#     doline(imgarr,liftBOX[0],liftBOX[1],liftBOX[2],liftBOX[3]) #画左边矩形框
#     doline(imgarr,nameBOX[0],nameBOX[1],nameBOX[2],nameBOX[3]) #吴春龙   
#     doline(imgarr,nationBOX[0],nationBOX[1],nationBOX[2],nationBOX[3])#民族    
#     doline(imgarr,sexBOX[0],sexBOX[1],sexBOX[2],sexBOX[3])  # 男 女 矩形框          
#     doline(imgarr,hanBOX[0],hanBOX[1],hanBOX[2],hanBOX[3]) #汉   
#     doline(imgarr,y1961BOX[0],y1961BOX[1],y1961BOX[2],y1961BOX[3])
#     doline(imgarr,yearBOX[0],yearBOX[1],yearBOX[2],yearBOX[3])
#     doline(imgarr,a12BOX[0],a12BOX[1],a12BOX[2],a12BOX[3])
#     doline(imgarr,monthBOX[0],monthBOX[1],monthBOX[2],monthBOX[3])#月
#     doline(imgarr,a25BOX[0],a25BOX[1],a25BOX[2],a25BOX[3])   
#     doline(imgarr,dayBOX[0],dayBOX[1],dayBOX[2],dayBOX[3]) #日
#     doline(imgarr,addressBOX[0],addressBOX[1],addressBOX[2],addressBOX[3]) # 甘肃省     
#     doline(imgarr,citizenBOX[0],citizenBOX[1],citizenBOX[2],citizenBOX[3]) #公民身份号码          
#     doline(imgarr,num620BOX[0],num620BOX[1],num620BOX[2],num620BOX[3])#620
      
    box1 = tag_name_x0,tag_name_y0,w+addressx+addressw-namex,h
    box2 = citizenx,citizeny,num620BOX[0]+num620BOX[2]-citizenx,num620BOX[1]+num620BOX[3]-citizeny

#     doline(imgarr,box1[0],box1[1],box1[2],box1[3]) #左框
#     doline(imgarr,box2[0],box2[1],box2[2],box2[3]) #公民身份号码 620
         
    box11 = box1[0],box1[1],box1[2]+box1[0],box1[3]+box1[1] #转换  
    box22 = box2[0],box2[1],box2[2]+box2[0],box2[3]+box2[1]
#     return  (0,0,0,0),(0,0,0,0),(0,0,0,0),(0,0,0,0),(0,0,0,0),(0,0,0,0),(0,0,0,0),(0,0,0,0),\
#             (0,0,0,0),(0,0,0,0),(0,0,0,0),(0,0,0,0),(0,0,0,0),(0,0,0,0),(0,0,0,0),(0,0,0,0)
    return box11,box22,liftBOX,nameBOX,sexBOX,nationBOX,hanBOX,y1961BOX,\
            yearBOX,a12BOX,monthBOX,a25BOX,dayBOX,addressBOX,citizenBOX,\
            num620BOX

def test_get_img_coordinate(img,imgarr,name_x0,name_y0,w1,h1,endx,endy):
    #标签姓名 左上方坐标
    tag_name_x0,tag_name_y0 = name_x0-w1*4,name_y0  
    
    # 左边区域
    w,h =ag_w,ag_h = w1*4,h1*9
    

    # 右边区域
    # 真实姓名 吴春龙  崔丽
    namex,namey,namew,nameh =xx,yy,ww,hh= name_x0,name_y0,w1*4,h1*2-10
    doline(imgarr,namex,namey,10,10)#真实姓名开始坐标
    
    # 男 女 开始坐标
    Sex_x0,Sex_y0 = Sex_x,Sex_y = name_x0,name_y0+nameh
    doline(imgarr,Sex_x,Sex_y,10,10) # 男 女 左上方 坐标 
    
    x0,y0,w0,h0 = Sex_x,Sex_y ,100,4 # 设置检测 男 前面 矩形框
    doline(imgarr,x0,y0,w0,h0) #
    x,y = get_absmin_y(img,x0,y0,w0,h0) # 获得 男 前面 坐标
    doline(imgarr,x,y,10,10) 
    Sex_y = y
         
    x0,y0,w0,h0 = Sex_x+w1*8,Sex_y,6,w1 #汉 设置检测矩形框 从右往左检测
    x,y = get_absmin_end_x(img,x0,y0,w0,h0) #获得 汉 结束坐标
    doline(imgarr,x0,y0,w0,h0)
    doline(imgarr,x,y,10,10)
    
    x0,y0,w0,h0 = x-14,y,6,w1 #汉 设置检测矩形框 从右往左检测 
    han_x,han_y = x,y = get_absmin_end_x(img,x0,y0,w0,h0) #获得 汉 开始坐标
    doline(imgarr,x0,y0,w0,h0)
    doline(imgarr,x,y,10,10)    
         
     
    # 1960 1961 1988
    startx,starty = Sex_x0,Sex_y0+nameh
    doline(imgarr,startx,starty,10,10)  # 1960 1961 1988开始坐标
    
    x0,y0,w0,h0 = startx,starty ,100,4 # 设置检测 1960 1961 1988 前面 矩形框
    doline(imgarr,x0,y0,w0,h0) #
    x,y = get_absmin_y(img,x0,y0,w0,h0) # 获得 1960 1961 1988 前面 坐标
    doline(imgarr,x,y,10,10) 
    
    x0,y0,w0,h0 = x+70,y,30,w1 #设置检测 1960 1961 1988 矩形框
    doline(imgarr,x0,y0,w0,h0)
    x,y = get_absmin_x(img,x0,y0,w0,h0)
    doline(imgarr,x,y,10,10) #获得1960 1961 1988 结束坐标    
    Sexw = x+w1/2-startx    
    y1961BOX = startx,starty ,Sexw,nameh

    # 年
    yearx,yeary,yearw,yearh = startx+Sexw,starty,w1+5,nameh
    yearBOX = yearx,yeary,yearw,yearh
 
    # 12
    a12x,a12y,a12w,a12h = yearx+yearw,starty,han_x-(yearx+yearw)-10,nameh
    a12BOX = a12x,a12y,a12w,a12h
     
    # 月
    monthx,monthy,monthw,monthh = a12x +a12w,a12y,w1+5,nameh
    monthBOX = monthx,monthy,monthw,monthh
     
    #25
    a25x,a25y,a25w,a25h = monthx+monthw,monthy,w1+20,monthh
    a25BOX = a25x,a25y,a25w,a25h
     
    # 日
    dayx,dayy,dayw,dayh = a25x+a25w,a25y,140,a25h
         
     
    # 男 女 矩形框
    Sexx,Sexy,Sexw,Sexh = Sex_x0,Sex_y0,Sexw,nameh
    sexBOX = Sexx,Sexy,Sexw,Sexh
    #doline(imgarr,Sexx,Sexy,Sexw,Sexh)  
    # 民族 矩形框
    Nationx,Nationy,Nationw,Nationh = Sexx+Sexw,Sexy,han_x-(Sexx+Sexw),Sexh
    nationBOX = Nationx,Nationy,Nationw,Nationh
    #doline(imgarr,Nationx,Nationy,Nationw,Nationh)         
    
    # 甘肃省
    address_x,address_y = name_x0,dayy+dayh #
    doline(imgarr,address_x,address_y,10,10) # 甘肃省开始坐标
    x0,y0,w0,h0 = address_x,address_y ,150,4 # 设置检测 甘肃省 前面 矩形框
    doline(imgarr,x0,y0,w0,h0) #
    x,y = get_absmin_y(img,x0,y0,w0,h0)
    doline(imgarr,x,y,10,10) 
     
    x0,y0,w0,h0 = x+150,y,30,w1 #设置检测甘肃省矩形框
    x,y = get_absmin_x(img,x0,y0,w0,h0) #检测结果坐标
    addressx,addressy,addressw,addressh = address_x,address_y,x-address_x +5,w1*3+10
    doline(imgarr,x0,y0,w0,h0) #显示检测甘肃省矩形框
    doline(imgarr,x,y,10,10) #显示检测结果坐标
        
    #公民 身份证号码
    x0,y0,w0,h0 = tag_name_x0,tag_name_y0 + ag_h + 1,200,4 #+30 设置检测 公民身份证号码 矩形框
    doline(imgarr,x0,y0,w0,h0) #
    citizen_x,citizen_y = get_absmin_y(img,x0,y0,w0,h0)  #获得公民身份证号码 前面 坐标 
    doline(imgarr,citizen_x,citizen_y,10,10) 

    x0,y0,w0,h0 = tag_name_x0+w1*10,tag_name_y0 + ag_h + 1,w1,4 #获得620 上面 检测框
    doline(imgarr,x0,y0,w0,h0) # 
    x,y = get_absmin_y(img,x0,y0,w0,h0) #获得620  检测框 开始坐标
    x0,y0,w0,h0 = x,y,w0,h1 #获得620  检测框 
    doline(imgarr,x0,y0,w0,h0) # 
    citizen_end_x,citizen_end_y = get_absmin_end_x(img,x0,y0,w0,h0) #获得 公民身份证号码 结束坐标
    doline(imgarr,citizen_end_x,citizen_end_y,10,10)
    
    end_620_x,end_620_y = get_absmin_x(img,x0,y0,w0,h0) #获得 620 结束坐标
    doline(imgarr,end_620_x,end_620_y,10,10)  
     
    citizenx,citizeny,citizenw,citizenh = tag_name_x0,citizen_y-30,citizen_end_x-tag_name_x0+5,h1*2+20
                
    citizenBOX = citizenx,citizeny,citizenw,citizenh      
    liftBOX = tag_name_x0,tag_name_y0,w,h #左边矩形框
    nameBOX = namex,namey,addressx+addressw-namex,nameh #吴春龙
    hanBOX = Nationx+Nationw,Nationy,addressx+addressw-(Nationx+Nationw),Nationh #汉
      
    dayBOX = dayx,dayy,addressx+addressw-dayx,dayh #日  
    addressBOX = addressx,addressy,addressw,tag_name_y0+h-addressy # 甘肃省    
    num620BOX = citizenx+citizenw,citizeny,endx-(citizenx+citizenw)+30,citizenh #620。。。
      
#     doline(imgarr,liftBOX[0],liftBOX[1],liftBOX[2],liftBOX[3]) #画左边矩形框
#     doline(imgarr,nameBOX[0],nameBOX[1],nameBOX[2],liftBOX[3]) #画右边矩形框
    
#     doline(imgarr,nameBOX[0],nameBOX[1],nameBOX[2],nameBOX[3]) #吴春龙   
#     doline(imgarr,nationBOX[0],nationBOX[1],nationBOX[2],nationBOX[3])#民族    
#     doline(imgarr,sexBOX[0],sexBOX[1],sexBOX[2],sexBOX[3])  # 男 女 矩形框          
#     doline(imgarr,hanBOX[0],hanBOX[1],hanBOX[2],hanBOX[3]) #汉   
#     doline(imgarr,y1961BOX[0],y1961BOX[1],y1961BOX[2],y1961BOX[3])
#     doline(imgarr,yearBOX[0],yearBOX[1],yearBOX[2],yearBOX[3])
#     doline(imgarr,a12BOX[0],a12BOX[1],a12BOX[2],a12BOX[3])
#     doline(imgarr,monthBOX[0],monthBOX[1],monthBOX[2],monthBOX[3])#月
#     doline(imgarr,a25BOX[0],a25BOX[1],a25BOX[2],a25BOX[3])   
#     doline(imgarr,dayBOX[0],dayBOX[1],dayBOX[2],dayBOX[3]) #日
#     doline(imgarr,addressBOX[0],addressBOX[1],addressBOX[2],addressBOX[3]) # 甘肃省     
#     doline(imgarr,citizenBOX[0],citizenBOX[1],citizenBOX[2],citizenBOX[3]) #公民身份号码          
#     doline(imgarr,num620BOX[0],num620BOX[1],num620BOX[2],num620BOX[3])#620
      
    box1 = tag_name_x0,tag_name_y0,w+addressx+addressw-namex,h
    box2 = citizenx,citizeny,num620BOX[0]+num620BOX[2]-citizenx,num620BOX[1]+num620BOX[3]-citizeny

#    doline(imgarr,box1[0],box1[1],box1[2],box1[3]) #上框
#     doline(imgarr,box2[0],box2[1],box2[2],box2[3]) #公民身份号码 620
         
    box11 = box1[0],box1[1],box1[2]+box1[0],box1[3]+box1[1] #转换  
    box22 = box2[0],box2[1],box2[2]+box2[0],box2[3]+box2[1]
#     return  (0,0,0,0),(0,0,0,0),(0,0,0,0),(0,0,0,0),(0,0,0,0),(0,0,0,0),(0,0,0,0),(0,0,0,0),\
#             (0,0,0,0),(0,0,0,0),(0,0,0,0),(0,0,0,0),(0,0,0,0),(0,0,0,0),(0,0,0,0),(0,0,0,0)
    return box11,box22,liftBOX,nameBOX,sexBOX,nationBOX,hanBOX,y1961BOX,\
            yearBOX,a12BOX,monthBOX,a25BOX,dayBOX,addressBOX,citizenBOX,\
            num620BOX



def get_correct(min,max,average_ver):
    Average =  (min+max)/2
    if Average > 127:
        if min==90 and max==187 and average_ver==172 : #90 187 120 172
            return 127
        return 120
    elif Average > 100 and min < 45 and average_ver!=158 and average_ver!=147\
        and average_ver!=148:
        return 88
    elif Average < 80:
        return Average  
    else:            
        #特殊值部分处理  写入判断值、写入返回值 37 173 88 148       
        if min==37 and max==173 and average_ver==148 :#37 173 88 148
            return 100
        if min==15 and max==171 and average_ver==153 :#15 171 93 153
            return 96 #94-108
        if min==0 and max==189 and average_ver==158 : # 0 189 60 158
            return 50 # 45-61 53不行
        
        if min==36 and max==190 and average_ver==155 : #36 190 113 155
            return 100
        if min==42 and max==170 and average_ver==143 : #42 170 106 143
            return 100
        if min==7 and max==180 and average_ver==150 : #汉7 180 93 150 ？
            return 110
                
        if min==49 and max==188 and average_ver==154 : #49 188 118 154
            return 110
        if min==69 and max==185 and average_ver==170 : #69 185 122 170
            return 127
        if min==5 and max==161 and average_ver==138 : #真实姓名 5 161 78 138
            return 75
        if min==6 and max==204 and average_ver==147 : #真实姓名6 204 100 147
            return 84 #84
        else:          
            return Average-5

#身份证 识别 http://localhost:9000/identity_recognition
#资料：https://blog.csdn.net/u013378306/article/details/70156842
def identity_recognition(reuqest):
    name = 'cuili.jpeg'  #
#     name = 'wuchunlong.jpeg' #
#     name = 'chunlong.jpeg' #
    name = 'wu1.jpeg'  # ok
#     name = 'wu2.jpeg'  #ok
#     name = 'wu3.jpeg' #图像逆时针90度
#     name = 'wj1.jpeg' #?
    name = 'wj2.jpeg' 

#     #获得图像基本数据
#     img,imgarr,IMG_W,IMG_H,name_x0,name_y0,endx,endy = get_img_basedata(name) #name_x0,name_y0 真实姓名左上方坐标
#     if IMG_W == -1 or IMG_H == -1:
#         return HttpResponse(str(img))
#          
#     #获得真实姓名 开始坐标 name_startx,name_starty 单字 宽高w0,h0
#     name_startx,name_starty,w1,h1 = get_xy_w_h(img,name_x0,name_y0,4,90)
#     #标签姓名 左上方坐标
#     tag_name_x0,tag_name_y0 = name_x0-w1*4,name_y0  
# 
#    
#     #获得标签姓名 开始坐标
#     tag_name_startx, tag_name_starty = get_startchar_xy1(imgarr,tag_name_x0,tag_name_y0,w1*2,100,10,10)
    img,imgarr,IMG_W,IMG_H,name_x0,name_y0,endx,endy = get_img_basedata(name)
    if IMG_W == -1 or IMG_H == -1:
        return HttpResponse(str(img))
    
    #获得单字（真实姓名）开始坐标、宽度和高度 ok
    name_startx,name_starty,w1,h1 = get_xy_w_h(img,name_x0,name_y0,4,90)

    
    box1,box2,liftBOX,nameBOX,sexBOX,nationBOX,hanBOX,y1961BOX,yearBOX,\
        a12BOX,monthBOX,a25BOX,dayBOX,addressBOX,citizenBOX,num620BOX = \
        get_img_coordinate(img,imgarr,name_x0,name_y0,w1,h1,endx,endy) #显示准确定位的矩形框
    im = Image.new('L',[IMG_W,IMG_H],"white") #创建新图像
    region = img.crop(box1) # 设置区域内，拷贝原图
    im.paste(region,box1) # 区域内，原图 粘贴到创建新图像
    region1 = img.crop(box2) # 设置区域内，拷贝原图
    im.paste(region1,box2) # 区域内，原图 粘贴到创建新图像
    imarr = array(im)
    
    #左边矩形框
    x,y,w,h = liftBOX[0],liftBOX[1],liftBOX[2],liftBOX[3]
    min,max =getbox_min_max(im,x,y,w,h)
    x1,y1,w1,h1 = x,y,w,10
    average_ver = Average(imgarr,x1,y1,w1,h1)
    correct = get_correct(min,max,average_ver)
    setbox_255(imarr,x,y,w,h,correct)
    print( '左边矩形框 min,max,correct,average_ver= ',min,max,correct,average_ver)
   
    #真实姓名
    x,y,w,h = nameBOX[0],nameBOX[1],nameBOX[2],nameBOX[3]
    min,max =getbox_min_max(im,x,y,w,h)
    x1,y1,w1,h1 = x,y,w,10
    average_ver = Average(imgarr,x1,y1,w1,h1)
    correct = get_correct(min,max,average_ver)
    setbox_255(imarr,x,y,w,h,correct)
    print( '真实姓名 min,max,correct,average_ver= ',min,max,correct,average_ver)
    
    
    
    
    rprint(imarr,x,y,w,h)
    
    
    


    #性别
    x,y,w,h = sexBOX[0],sexBOX[1],sexBOX[2],sexBOX[3]
    min,max =getbox_min_max(im,x,y,w,h)
    x1,y1,w1,h1 = x,y,w,10
    average_ver = Average(imgarr,x1,y1,w1,h1)
    correct = get_correct(min,max,average_ver)
    setbox_255(imarr,x,y,w,h,correct)
    print( '性别 sexBOX min,max,correct,average_ver= ',min,max,correct,average_ver)

    
    x,y,w,h = nationBOX[0],nationBOX[1],nationBOX[2],nationBOX[3]
    min,max =getbox_min_max(im,x,y,w,h)
    x1,y1,w1,h1 = x,y,w,10
    average_ver = Average(imgarr,x1,y1,w1,h1)
    correct = get_correct(min,max,average_ver)
    setbox_255(imarr,x,y,w,h,correct)
    print( '民族 nationBOX min,max,correct,average_ver= ',min,max,correct,average_ver)
       
    x,y,w,h = hanBOX[0],hanBOX[1],hanBOX[2],hanBOX[3]
    min,max =getbox_min_max(im,x,y,w,h)
    x1,y1,w1,h1 = x,y,w,10
    average_ver = Average(imgarr,x1,y1,w1,h1)
    correct = get_correct(min,max,average_ver)
    setbox_255(imarr,x,y,w,h,correct)
    print( '汉 hanBOX min,max,correct,average_ver= ',min,max,correct,average_ver)
    
    x,y,w,h = y1961BOX[0],y1961BOX[1],y1961BOX[2],y1961BOX[3]
    min,max =getbox_min_max(im,x,y,w,h)
    x1,y1,w1,h1 = x,y,w,10
    average_ver = Average(imgarr,x1,y1,w1,h1)
    correct = get_correct(min,max,average_ver)
    setbox_255(imarr,x,y,w,h,correct)
    print( 'y1961BOX min,max,correct,average_ver= ',min,max,correct,average_ver)

    
    # 年    
    x,y,w,h = yearBOX[0],yearBOX[1],yearBOX[2],yearBOX[3]
    min,max =getbox_min_max(im,x,y,w,h)
    x1,y1,w1,h1 = x,y,w,10
    average_ver = Average(imgarr,x1,y1,w1,h1)
    correct = get_correct(min,max,average_ver)
    setbox_255(imarr,x,y,w,h,correct)
    print( '年 yearBOX min,max,correct,average_ver= ',min,max,correct,average_ver)
    
    x,y,w,h = a12BOX[0],a12BOX[1],a12BOX[2],a12BOX[3]
    min,max =getbox_min_max(im,x,y,w,h)
    x1,y1,w1,h1 = x,y,w,10
    average_ver = Average(imgarr,x1,y1,w1,h1)
    correct = get_correct(min,max,average_ver)
    setbox_255(imarr,x,y,w,h,correct)
    print( 'a12BOX min,max,correct,average_ver= ',min,max,correct,average_ver)
    
    # 月
    x,y,w,h = monthBOX[0],monthBOX[1],monthBOX[2],monthBOX[3]
    min,max =getbox_min_max(im,x,y,w,h)
    x1,y1,w1,h1 = x,y,w,10
    average_ver = Average(imgarr,x1,y1,w1,h1)
    correct = get_correct(min,max,average_ver)
    setbox_255(imarr,x,y,w,h,correct)
    print( '月 monthBOX min,max,correct,average_ver= ',min,max,correct,average_ver)
    
    x,y,w,h = a25BOX[0],a25BOX[1],a25BOX[2],a25BOX[3]
    min,max =getbox_min_max(im,x,y,w,h)
    x1,y1,w1,h1 = x,y,w,10
    average_ver = Average(imgarr,x1,y1,w1,h1)
    correct = get_correct(min,max,average_ver)
    setbox_255(imarr,x,y,w,h,correct)
    print( 'a25BOX min,max,correct,average_ver= ',min,max,correct,average_ver)
    
    
    x,y,w,h = dayBOX[0],dayBOX[1],dayBOX[2],dayBOX[3]
    min,max =getbox_min_max(im,x,y,w,h)
    x1,y1,w1,h1 = x,y,w,10
    average_ver = Average(imgarr,x1,y1,w1,h1)
    correct = get_correct(min,max,average_ver)
    setbox_255(imarr,x,y,w,h,correct)
    print( '日 dayBOX min,max,correct,average_ver= ',min,max,correct,average_ver)
        
    x,y,w,h = addressBOX[0],addressBOX[1],addressBOX[2],addressBOX[3]
    min,max =getbox_min_max(im,x,y,w,h)
    x1,y1,w1,h1 = x,y,w,10
    average_ver = Average(imgarr,x1,y1,w1,h1)
    correct = get_correct(min,max,average_ver)
    setbox_255(imarr,x,y,w,h,correct)
    print( '甘肃省addressBOX min,max,correct,average_ver= ',min,max,correct,average_ver)
    
    #公民
    x,y,w,h = citizenBOX[0],citizenBOX[1],citizenBOX[2],citizenBOX[3]
    min,max =getbox_min_max(im,x,y,w,h)
    x1,y1,w1,h1 = x,y,w,10
    average_ver = Average(imgarr,x1,y1,w1,h1)
    correct = get_correct(min,max,average_ver)
    setbox_255(imarr,x,y,w,h,correct)
    print( '公民 min,max,correct,average_ver= ',min,max,correct,average_ver)
    
    #620
    x,y,w,h = num620BOX[0],num620BOX[1],num620BOX[2],num620BOX[3]    
    min,max =getbox_min_max(im,x,y,w,h)
    x1,y1,w1,h1 = x,y,w,10
    average_ver = Average(imgarr,x1,y1,w1,h1)
    correct = get_correct(min,max,average_ver)
    setbox_255(imarr,x,y,w,h,correct)
    print( '620 min,max,correct,average_ver= ',min,max,correct,average_ver)       
    
    im = Image.fromarray(imarr) # 二维数组转换成图像
    print( pytesseract.image_to_string(im,lang='chi_sim') )
    return HttpResponse(im.show(),"GIF")  
       
#     img = Image.fromarray(imgarr) # 二维数组转换成图像
#     return HttpResponse(img.show(),"GIF") 
    return HttpResponse('ok')                   


def Total(imgarr,x1,y1,w,h):
    t=0
    for y in  range(h):
        y += y1
        for x in  range(w):
            x += x1
            t += int(imgarr[y][x])
    return t       


#计算矩形平均值
def Average(imgarr,x1,y1,w,h):
    return Total(imgarr,x1,y1,w,h)/(w*h)        

#获得 中心 区域最小值最大值
def box_core_min_max(img,w,h):
    return box_min_max(img,img.size[0]/2-w/2,img.size[1]/2-h/2,w,h)
     
#获得区域最小值最大值
def box_min_max(img,x,y,w,h):
    box = (x,y,x+w,y+h) 
    boximg = array(img.crop(box))
    return int(boximg.min()),int(boximg.max())            


BOX_MIN_THRESHOLD = 50 #设置两个矩形框中，最小值相减的绝对值 阀值 50。参见：有道云笔记。图像识别 数据分析与结论 
#判断 两个矩形框中，最小值相减的绝对值
def box_abs_min_threshold(img,x,y,w,h,min):
    min0,max = box_min_max(img,x,y,w,h)           
    return abs(min0-min) > BOX_MIN_THRESHOLD
 
 
#水平扫描检测
def get_absmin_x(img,x1,y1,w,h):
    min,max = getbox_min_max(img,x1,y1,w,h)
    for n in  range(1000):
        x = x1+n
        if box_abs_min_threshold(img,x,y1,w,h,min):       
            return x,y1
    return 0,0


#竖直扫描检测
def get_absmin_y(img,x1,y1,w,h):
    min,max = getbox_min_max(img,x1,y1,w,h)
    for n in  range(1000):
        y = y1+n
        if box_abs_min_threshold(img,x1,y,w,h,min):       
            return x1,y
    return 0,0
 
def get_absmin_end_x(img,x1,y1,w,h):
    min,max = getbox_min_max(img,x1,y1,w,h)
    for n in  range(1000):
        x = x1-n
        if box_abs_min_threshold(img,x,y1,w,h,min):       
            return x,y1
    return 0,0

#BOX_AVERAGE_THRESHOLD = 35 #矩形框中 平均值阀值
#BOX_MIN_MAX_NAME_THRESHOLD = 120 #设定矩形框中有无 真实姓名 阀值

# ERROR_0 = 9 #低电平(黑)区域误差    
# WORLD_W_H = 55 #身份证 字大小 吴34*33  崔51*44 
  
# #水平线上只有一个达到阀值True
# def is_x(imgarr,x0,y0,w,threshold):
#     for x in  range(w):
#         x += x0
#         if imgarr[y0][x] <= threshold:
#             return True
#     return False

# # 判断是不是干扰
# def is_start_interfere_x(img,x0,y0,w):    
#     imgarr = array(img)
#     min,max = box_min_max(img,x0,y0,PROBE_W,PROBE_H)
#     x,y = get_min_xy(array(img),x0,y0,PROBE_W,PROBE_H,min)
#     if is_x(imgarr,x+60,y+10,w,min) or is_x(imgarr,x+60,y+30,w,min):        
#         return True
#     return False

# # 判断是不是干扰
# def is_interfere_x(img,x0,y0,w):
#     imgarr = array(img)
#     min,max = box_min_max(img,x0,y0,PROBE_W,PROBE_H)
#     x,y = get_min_xy(array(img),x0,y0,PROBE_W,PROBE_H,min)
#     if x > img.size[0]/2:
#         if is_x(imgarr,x-100,y+3,w,min) :  # +3 ?     
#             return True
#     else:
#         if is_x(imgarr,x+100,y+3,w,min):
#             return True
#     return False    
# #获得最小值的坐标
# def get_min_xy(imgarr,x0,y0,w,h,min):
#     for y in  range(h):
#         y += y0 
#         for x in  range(w):
#             x += x0
#             if imgarr[y][x] == min:
#                 return x,y
#     return 0,0


# #???
# def get_end_xy(img,x1,y1,w,h):
#     for n in  range(100):
#         x,y = x1+n,y1+n
#         if not box_abs_minmax_threshold(img,x,y,w,h):       
#             return x,y
#     return 0,0


# # 矩形框w*h从左往右扫描，获得x方向结束坐标 
# def get_leave_x(img,x1,y1,w,h):
#     for n in  range(1000):
#         x = x1+n       
#         if not box_abs_minmax_threshold(img,x,y1,w,h):       
#             return x,y1
#     return 0,0
# # 矩形框w*h从上往下扫描，获得y方向结束坐标
# def get_leave_y(img,x1,y1,w,h):
#     for n in  range(1000):
#         y = y1+n
#         if not box_abs_minmax_threshold(img,x1,y,w,h):       
#             return x1,y
#     return 0,0
# # 获得（单字）的宽度、高度
# def get_world_w_h(img,a0,b0,xh,yw):#xh 从左往右扫描高度，yw从上往下扫描宽度 
#     x1,y1 = get_leave_x(img,a0,b0,5,xh)  #矩形框 宽*高xh 从左往右扫描 
#     x2,y2 = get_leave_y(img,a0,b0,yw,5)  #矩形框 宽yw#高 从上往下扫描
#     w,h = x1-a0,y2-b0 
#     return w,h   


def openfile(name): 
    img = Image.open(name).convert('L') #转换成灰度图像,作用？
    IMG_W = img.size[0]
    IMG_H = img.size[1]
#     a0,b0 = get_box_xy(img,0,0,IMG_W,IMG_H) #ok wu1 33-45; cuili 33-40; wuchunlong 33-45; chunlong 33-43;
#     a1,b1 = get_endbox_xy(img,IMG_W,IMG_H) #结束坐标
    a0,b0 = get_name_xy(img)
    a1,b1 = get_620_x(img) 
    return name,a0,b0,a1,b1
#图像初始化，如果图像是逆时针90度的，把图像逆时针旋转270度， 转化为正常图像
def img_init(str,name):
    try:
        img = Image.open(name).convert('L') #转换成灰度图像
        img.save(str+name) #保存图像 
        name,a0,b0,a1,b1 = openfile(str+name)
        if a1-a0 < b1-b0:
            im = img.transpose(Image.ROTATE_270) #逆时针旋转270度        
            im.save(str+name) #保存图像
            name,a0,b0,a1,b1 = openfile(str+name)
        return name,a0,b0,a1,b1
    except Exception as ex:
        return ex,-1,-1,-1,-1



# #  http://localhost:9000/specimen_cuili
# def specimen_cuili(reuqest):
#     name = 'cuili.jpeg'
# #     name = 'wuchunlong.jpeg'
#     name = 'chunlong.jpeg'  # 干扰测试
#     
# 
# #     name = 'wu1.jpeg'
# #     name = 'wu2.jpeg'
# #     name = 'wu3.jpeg' #图像逆时针90度
# #     name = 'wj1.jpeg'
# #    name = 'wj2.jpeg' 
#     
#     newname = img_init('L',name) #图像初始化
#     img = Image.open(newname).convert('L') #转换成灰度图像
#     imgarr = array(img) #图像变为二维数组  
#     IMG_W = img.size[0]
#     IMG_H = img.size[1]
# 
#     #获得真实姓名 左上方坐标
#     name_x0,name_y0 = get_box_xy(img,0,0,IMG_W,IMG_H) #ok wu1 33-45; cuili 33-40; wuchunlong 33-45; chunlong 33-43;
#     doline(imgarr,name_x0,name_y0,10,10)   
#     #获得真实姓名 开始坐标
#     a0,b0 = get_startchar_xy1(imgarr,name_x0,name_y0,200,200,20,20)
#     doline(imgarr,a0,b0,10,10)
#      
#     #获得真实姓名 单字 宽 高
#     w1,h1 = get_world_w_h(img,a0,b0,80,80)  
#     doline(imgarr,a0,b0,w1,h1) 
#     
#     #获得结束坐标
#     endx,endy = get_endbox_xy(img,IMG_W,IMG_H,36)
#  
# #      
# #     #获得标签姓名 左上方坐标
# #     tab_name_x0,tab_name_y0 = name_x0-w1*3-w1*3/5,name_y0
# #     doline(imgarr,tab_name_x0,tab_name_y0,10,10)
#       
#     #获得标签姓名 开始坐标
#     #a0,b0 = get_startchar_xy1(imgarr,tab_name_x0,tab_name_y0,100,100,10,10)
# #     print 'tab_name_x0,tab_name_y0=',tab_name_x0,tab_name_y0 
# #     a0,b0 = get_into_x(img,tab_name_x0,tab_name_y0,2,60)
# #     a1,b1 = get_into_y(img,tab_name_x0,tab_name_y0,60,2)
# #     print 'a0,b0=',a0,b0
# #     print 'a1,b1=',a1,b1
# #     doline(imgarr,a0,b1,30,30) 
#     
#     
# 
# #     #获得标签姓名 单字 宽 高
# #     w0,h0 = 30,30 #get_world_w_h(img,a0,b1,70,70)  
# #     print 'w0,h0=' ,w0,h0
# #     doline(imgarr,a0,b1,w0,h0) 
# 
# 
# 
# #     #获得真实性别 左上方坐标
# #     sex_x0,sex_y0 = name_x0,name_y0 + h1*2 
# #     #获得真实性别 第一个字所有参数
# #     a2,b2,c2,d2,w2,h2 = get_w(img,sex_x0,sex_y0,w1*2,h1*2,15,10)
# #  
# #     #获得标签 民族 开始坐标
# #     tab_Nation_x,tab_Nation_y = get_into_x(img,a2+w2*3,b2,2,h2)
# #     #获得标签 民族 第一个字所有参数
# #     a3,b3,c3,d3,w3,h3 = get_w(img,tab_Nation_x+w2*3/2,tab_Nation_y,w1*3/2,h1*3/2,10,10)
# #     doline(imgarr,tab_Nation_x,tab_Nation_y,5,5) 
# #     doline(imgarr,tab_Nation_x+w2*3/2,tab_Nation_y,5,5)    
# #     
# #     doline(imgarr,tab_Nation_x,tab_Nation_y,w2,h2)   
# #     print 'w2 =',w2
# #     print 'w2*3/2 =',w2*3/2
# #     
# #     doline(imgarr,a3,b3,5,5,)
# #     doline(imgarr,a2+w2*3,b2,5,5)
# #     
# #     x,y = get_into_x(img,tab_Nation_x+w0*3+38,b2,2,h2)
# #     doline(imgarr,x,y,10,10)
# #     doline(imgarr,tab_Nation_x+w0*3+38,b2,5,5)
#     
#     
# #     #获得真实1960 左上方坐标
# #     y19_x0,y19_y0 = name_x0,name_y0 + h1*4
# #      
# #     #获得真实性别 矩形框
# #     sex_x,sex_y,sex_w,sex_h = sex_x0,sex_y0,w1*3-5,y19_y0-sex_y0
# #     doline(imgarr,sex_x,sex_y,sex_w,sex_h)
# #  
# #     #获得标签民族 矩形框
# #     tab_Nation_x,tab_Nation_y,tab_Nation_w,tab_Nation_h = sex_x+sex_w,sex_y,w1*2,sex_h    
# #     doline(imgarr,tab_Nation_x,tab_Nation_y,tab_Nation_w,tab_Nation_h)
# #     
# #     #获得汉 矩形框
# #     Nation_x,Nation_y,Nation_w,Nation_h = tab_Nation_x+tab_Nation_w,sex_y,w0*4,sex_h    
# #     doline(imgarr,Nation_x,Nation_y,Nation_w,Nation_h)
# # 
# # 
# #     
# #     #获得真实住址 左上方坐标
# #     addr_x0,addr_y0 = name_x0,name_y0 + h1*6
# #     addr_x,addr_y = get_startchar_xy1(imgarr,addr_x0,addr_y0,w1*4,h1*4,15,15) 
# #     #获得真实住址 右坐标
# #     addr_r_x,addr_r_y  = get_leave_x(img,addr_x+10,addr_y,30,30)+10,addr_y    
# #     
# #     
# #     addr_end_y = get_leave_y(img,addr_x,addr_y,30,60)
# #     x,y = get_into_y(img,addr_x+20,addr_end_y+20,60,30) #获得地址下方纵坐标
# #     x1 = get_leave_x(img,addr_x,y,30,60) #获得标签公民身份证橫（右）坐标
# #     print 'y=',y
# # 
# #     #获得标签公民身份证 左上方坐标
# #     tab_citizen_x0,tab_citizen_y0 = tab_name_x0,y
# #     
# #     citizen_x0,citizen_y0 = x1+w0,y
# 
# #     #获得图像左坐标宽高
# #     
# #     
# #     tab_620_end_x0,tab_620_end_y0 = tab_620_x0 + w1*8,tab_620_y0
# #     
# #
# 
#     
#   
# #     doline(imgarr,citizen_x0,citizen_y0,10,10)
# #     doline(imgarr,tab_citizen_x0,tab_citizen_y0,10,10)
# #     doline(imgarr,addr_x,addr_end_y,10,10)
# #        
# #     doline(imgarr,addr_x0,addr_y0,10,10)
# #     doline(imgarr,addr_r_x,addr_r_y,10,10)
# #     doline(imgarr,y19_x0,y19_y0,10,10)
# #     doline(imgarr,sex_x0,sex_y0,10,10)
# #     doline(imgarr,tab_name_x0,tab_name_y0,10,10)
# #     doline(imgarr,name_x0,name_y0,10,10)
#     doline(imgarr,endx,endy,10,10)
# 
#     img = Image.fromarray(imgarr) # 二维数组转换成图像
#     return HttpResponse(img.show(),"JPG")     
#     return HttpResponse('ok')
 
# #  http://localhost:9000/specimen_test
# def specimen_test(reuqest):
#     name = 'cuili.jpeg'
#     name = 'wu1.jpeg'
#     name = 'wuchunlong.jpeg'
#     name = 'chunlong.jpeg'
#     name = 'wu2.jpeg'
# #     name = 'wu3.jpeg'
#     img = Image.open(name).convert('L') #转换成灰度图像
#     IMG_W = img.size[0]
#     IMG_H = img.size[1]
#     imgarr = array(img) #图像变为二维数组
#     a0,b0 = get_box_x(img,IMG_W-30,IMG_H-30,36) #wu1 33-45; cuili 33-40; wuchunlong 33-45; chunlong 33-43;
#      
#     doline(imgarr,a0,b0,30,30) 
#     img = Image.fromarray(imgarr) # 二维数组转换成图像
#     return HttpResponse(img.show(),"JPG") 
# 
# #     #空白区域0
# #     
#     x,y,w,h = 923,122,30,30
#     min,max = box_min_max(img,923,122,30,30)
#     print '空白区域0 min max = ',name,min,max,max-min,(max+min)/2    
#     print '空白区域0 Average = ',Average(imgarr,x,y,w,h)
#     print '空白区域0 Average - (max+min)/2',Average(imgarr,x,y,w,h)-(max+min)/2
#     #return HttpResponse('ok') 
#     doline(imgarr,x,y,w,h)
#     img = Image.fromarray(imgarr) # 二维数组转换成图像
#     return HttpResponse(img.show(),"JPG") 
# 
# #     min,max = box_min_max(img,50,570,30,30)
# #     print '空白区域1 min max = ',name,min,max,max-min,(max+min)/2    
# #     print '空白区域1 Average = ',Average(imgarr,50,570,30,30)
# #     print '空白区域1 Average - (max+min)/2',Average(imgarr,50,570,30,30)-(max+min)/2
# #     doline(imgarr,50,570,30,30)
# #     
# #     
# #     
# #     
# #     x,y,w,h = 550,980,30,30
# #     min,max = box_min_max(img,x,y,w,h)
# #     print '空白区域3 min max = ',name,min,max,max-min,(max+min)/2    
# #     print '空白区域3 Average = ',Average(imgarr,x,y,w,h)
# #     print '空白区域3 Average - (max+min)/2',Average(imgarr,x,y,w,h)-(max+min)/2
# #     #doline(imgarr,x,y,w,h)
# #     
# #     x,y,w,h = 550,1210,30,30
# #     min,max = box_min_max(img,x,y,w,h)
# #     print '空白区域4 min max = ',name,min,max,max-min,(max+min)/2    
# #     print '空白区域4 Average = ',Average(imgarr,x,y,w,h)
# #     print '空白区域4 Average - (max+min)/2',Average(imgarr,x,y,w,h)-(max+min)/2
# #     #doline(imgarr,x,y,w,h)
# # 
# #     x,y,w,h = 550,1310,30,30
# #     min,max = box_min_max(img,x,y,w,h)
# #     print '空白区域5 min max = ',name,min,max,max-min,(max+min)/2    
# #     print '空白区域5 Average = ',Average(imgarr,x,y,w,h)
# #     print '空白区域5 Average - (max+min)/2',Average(imgarr,x,y,w,h)-(max+min)/2
# #     #doline(imgarr,x,y,w,h)
# # 
# #     
# #     
# # 
# #     t=30#(max-min) #wu1 40
# #     a0,b0 = get_startchar_xy1(imgarr,0,0,IMG_W-10,IMG_H-10,t,t)
# #     a1,b1 = get_endchar_xy1(imgarr,IMG_W-10,IMG_H-10,IMG_W-10,IMG_H-10,t,t)
# #     print 'IMG_W-10,IMG_H-10=',IMG_W-10,IMG_H-10
# #     print 'a1,b1=',a1,b1
#     
# #     doline(imgarr,a1,b1,10,10)
#      
#     
# #     x,y=IMG_W-11, 1600
# #     a1,b1 = get_endchar_xy1(imgarr,x,y,IMG_W/2,IMG_H/2,37,37) #25
# #     print 'x,y=',x,y
# #     print 'a1,b1=',a1,b1
# #     rprint(imgarr,a1-5,b1-5,10,10)
# #     doline(imgarr,x,y,5,5)
# #     doline(imgarr,a1,b1,10,10)
#     #return HttpResponse('ok') 
# #     #空白区域1
# #     doline(imgarr,a0,IMG_H/2-380,100,30)
# #     min,max = box_min_max(img,a1,b1,10,10)
# #     print '空白区域1 min max = ',name,min,max,max-min    
#     
# 
# #     #空白区域2
# #     doline(imgarr,IMG_W/2,IMG_H/2-380,100,30)
# #     min,max = box_min_max(img,IMG_W/2,IMG_H/2-380,100,30)
# #     print '空白区域2 min max = ',name,min,max,max-min    
# # 
# #     #空白区域3
# #     doline(imgarr,a0,IMG_H/2-330,100,30)
# #     min,max = box_min_max(img,a0,IMG_H/2-330,100,30)
# #     print '空白区域3 min max = ',name,min,max,max-min    
# # 
# #     #空白区域4
# #     doline(imgarr,IMG_W/2,IMG_H/2-330,100,30)
# #     min,max = box_min_max(img,IMG_W/2,IMG_H/2-330,100,30)
# #     print '空白区域4 min max = ',name,min,max,max-min    
# # 
# #     #空白区域5
# #     doline(imgarr,a0,IMG_H/2-330,100,30)
# #     min,max = box_min_max(img,a0,IMG_H/2-330,100,30)
# #     print '空白区域5 min max = ',name,min,max,max-min    
# # 
# #     #空白区域6
# #     doline(imgarr,IMG_W/2,IMG_H/2-330,100,30)
# #     min,max = box_min_max(img,IMG_W/2,IMG_H/2-330,100,30)
# #     print '空白区域6 min max = ',name,min,max,max-min    
# #     
# #     #中心区域 
# #     doline(imgarr,IMG_W/2-100,IMG_H/2-270,200,540)
# #     min,max = box_core_min_max(img,200,540)
# #     print '中心区域 min max = ',name,min,max,max-min    
# 
#     return HttpResponse('ok') 

# 数组行相减 -1----255  -2----254  -3----253 ...
#  http://localhost:9000/test_array
def test_array(reuqest):
    name = 'cuili.jpeg'
    img = Image.open(name).convert('L') #转换成灰度图像
    #保存图像  
    img.save('g'+name)    
    IMG_W = img.size[0]
    IMG_H = img.size[1]
    
    imgarr = array(img) #图像变为二维数组

    #民区域
    x,y,w,h = 530,293,50,50
    #doline(imgarr,x,y,w,h)
    rprint(imgarr,x,y,w,h)
    print( '民 区域min max = ',getbox_min_max(img,x,y,w,h))
    
    x1,y1= x,y
    for y0 in  range(h):
        y0 += y1
        imgarr[y0] = imgarr[y0] - imgarr[y0+1] #数组行相减
     
         
    rprint(imgarr,x,y,w,h)
    return HttpResponse('ok')
    img = Image.fromarray(imgarr) # 二维数组转换成图像
    print( pytesseract.image_to_string(img,lang='chi_sim')) 
    return HttpResponse(img.show(),"GIF")


 

#doline(imgarr,startx,starty,w12,h)
def rprint(imgarr,x1,y1,w,h):
    min=1000
    s=''
    yy=''
    for y in  range(h):
        y += y1
        for x in  range(w):
            x += x1
            a = int(imgarr[y][x])
            if a<min:
                yy = y
                min = a
            if a<10:
                s += '00' +str(a) +' '
            elif a<100:
                s += '0' +str(a) +' '
            else:
                s += str(a) +' '
        s += 'y='+str(y) + '\n'    
    print( s,yy,min)
    return HttpResponse(s)


                   
# def get_x_min(imgarr,x0,y0,w,h):
#     max = 0
#     for y in  range(h):
#         y +=y0
#         for x in  range(w):
#             x +=x0
#             m = absXT(imgarr,x,y)
#             if  m > max:
#                 max = m
#     return max
# def absXT(imgarr,x,y):
#     a = (int(imgarr[y][x-1]) - int(imgarr[y][x]))
#     b = (int(imgarr[y][x]) - int(imgarr[y][x+1]))
#     if a>b:
#         return b
#     return a

# #获得x横向边缘值
# def get_x_edge(imgarr,x0,y0,w,h,d):
#     for y in  range(h):
#         y += y0 + 1
#         for x in  range(w):
#             x += x0 + 1
#             if XT(imgarr,x,y,d):
#                 return int(imgarr[y][x-1]),int(imgarr[y][x]),int(imgarr[y][x+1]) 
#     return 0,0,0
# #获得y竖向边缘值
# def get_y_edge(imgarr,x0,y0,w,h,d):
#     for x in  range(w):
#         x += x0 + 1       
#         for y in  range(h):
#             y += y0 + 1
#             if YT(imgarr,x,y,d):
#                 return int(imgarr[y-1][x]),int(imgarr[y][x]),int(imgarr[y+1][x]) 
#     return 0,0,0
# 
# 
# # x0,y0待测字符左上方坐标；w横线扫描长度，h竖线扫描长度，d字符边缘变化值
# # 注意：w横线 w>x0到待测字符的水平距离+待测字符宽度；h竖线 h>y0到待测字符的垂直距离+待测字符高度
# #竖线从左往右扫描  在竖线上判断。主要获得第一个字符开始坐标x。
# def get_startchar_y(imgarr,x0,y0,w,h,d):
#     for x in  range(w):
#         x += x0 + 1
#         for y in  range(h):
#             y += y0 + 1
#             if YT(imgarr,x,y,d) and ERROR_0_y_l(imgarr,x+1,y+1,ERROR_0,h) < 60:
#                 return x,y 
#     return 0,0
# 
# #横线从上往下扫描  在横线上判断。主要获得第一个字符开始坐标y。
# def get_startchar_x(imgarr,x0,y0,w,h,d):
#     for y in  range(h):
#         y += y0 + 1
#         for x in  range(w):
#             x += x0 + 1
#             if XT(imgarr,x,y,d) and ERROR_0_x_l(imgarr,x+1,y+1,ERROR_0,w) < 60:
#                 return x,y 
#     return 0,0
# 
# def get_startchar_y1(imgarr,x0,y0,w,h,d):
#     for x in  range(w):
#         x += x0 + 1
#         for y in  range(h):
#             y += y0 + 1
#             if YT(imgarr,x,y,d):
#                 return x,y 
#     return 0,0
# def get_startchar_x1(imgarr,x0,y0,w,h,d):
#     for y in  range(h):
#         y += y0 + 1
#         for x in  range(w):
#             x += x0 + 1
#             if XT(imgarr,x,y,d):
#                 return x,y 
#     return 0,0
# 
# def get_endchar_x(imgarr,x0,y0,w,h,d):
#     for y1 in  range(h):
#         y = y0 - y1
#         for x1 in  range(w):
#             x = x0 - x1
#             if XT(imgarr,x,y,d) and ERROR_0_x_l(imgarr,x+1,y+1,ERROR_0,w) < 60:
#                 return x,y 
#     return 0,0
# def get_endchar_y(imgarr,x0,y0,w,h,d):
#     for x1 in  range(w):
#         x = x0 - x1
#         for y1 in  range(h):
#             y = y0 - y1
#             if YT(imgarr,x,y,d) and ERROR_0_y_l(imgarr,x+1,y+1,ERROR_0,h) < 60:
#                 return x,y 
#     return 0,0
# 
# 
# def get_endchar_x1(imgarr,x0,y0,w,h,d):
#     for y1 in  range(h):
#         y = y0 - y1
#         for x1 in  range(w):
#             x = x0 - x1
#             if XT(imgarr,x,y,d):
#                 return x,y 
#     return 0,0
# def get_endchar_y1(imgarr,x0,y0,w,h,d):
#     for x1 in  range(w):
#         x = x0 - x1
#         for y1 in  range(h):
#             y = y0 - y1
#             if YT(imgarr,x,y,d):
#                 return x,y 
#     return 0,0
# 
# 
# def get_endchar_xy2(imgarr,x0,y0,w,h,dx,dy):
#     xx,xy = get_endchar_x1(imgarr,x0,y0,w,h,dx)
#     yx,yy = get_endchar_y1(imgarr,x0,y0,w,h,dy)
#     return yx,xy
# 
# 
# def get_endchar_xy1(imgarr,x0,y0,w,h,dx,dy):
#     xx,xy = get_endchar_x1(imgarr,x0,y0,w,h,dx)
#     yx,yy = get_endchar_y1(imgarr,x0,y0,w,h,dy)
#     return yx+5,xy+5
# 
# def get_endchar_xy(imgarr,x0,y0,w,h,dx,dy):
#     xx,xy = get_endchar_x(imgarr,x0,y0,w,h,dx)
#     yx,yy = get_endchar_y(imgarr,x0,y0,w,h,dy)
#     return yx,xy
# 
# #获得字符开始坐标
# def get_startchar_xy(imgarr,x0,y0,w,h,dx,dy):
#     xx,xy = get_startchar_x(imgarr,x0,y0,w,h,dx)
#     yx,yy = get_startchar_y(imgarr,x0,y0,w,h,dy)
#     return yx,xy
# 
# def get_startchar_xy1(imgarr,x0,y0,w,h,dx,dy):
#     xx,xy = get_startchar_x1(imgarr,x0,y0,w,h,dx)
#     yx,yy = get_startchar_y1(imgarr,x0,y0,w,h,dy)
#     return yx,xy
# 
# # 横线 获得黑长条长度
# def ERROR_0_x_l(imgarr,x,y,ERROR_0,w):
#     for x in  range(w):
#         if not abs_x(imgarr,x,y,ERROR_0):
#             return x  
# # 竖线 获得黑长条长度
# def ERROR_0_y_l(imgarr,x,y,ERROR_0,h):
#     for y in  range(h):
#         if not abs_y(imgarr,x,y,ERROR_0):
#             return y
# 
# # 排除黑长条干扰             
# def abs_x(imgarr,x,y,ERROR_0):
#     return abs(int(imgarr[y][x]) - int(imgarr[y][x+1])) < ERROR_0     
# def abs_y(imgarr,x,y,ERROR_0):
#     return abs(int(imgarr[y][x]) - int(imgarr[y+1][x])) < ERROR_0     
# 
#                          
# # 水平 x值判断 x,y开始坐标 d有字符与无字符之间的差值
# def XT(imgarr,x,y,d):
#     n = 0
#     linesize = 3  #设置线粗细 
#     for l in  range(linesize):
#         if int(imgarr[y][x]) - int(imgarr[y][x+l+1]) > d and int(imgarr[y][x-1]) - int(imgarr[y][x]) > d:
#             n += 1
#             if n == linesize:
#                 return True
#         else:
#             n = 0             
#     return False 
#        
# # 垂直 y值判断 x,y开始坐标 d有字符与无字符之间的差值
# def YT(imgarr,x,y,d):
#     n = 0
#     linesize = 3  #设置线粗细 
#     for l in  range(linesize):
#         if int(imgarr[y-1][x]) - int(imgarr[y][x]) > d and  int(imgarr[y][x]) - int(imgarr[y+l+1][x]) > d:
#             n += 1
#             if n == linesize:
#                 return True
#         else:
#             n = 0             
#     return False             
# 
# def endXT(imgarr,x,y,d):
#     n = 0
#     linesize = 3  #设置线粗细 
#     for l in  range(linesize):
#         if int(imgarr[y][x]) - int(imgarr[y][x+l+1]) < -d and int(imgarr[y][x-1]) - int(imgarr[y][x]) < -d:
#             n += 1
#             if n == linesize:
#                 return True
#         else:
#             n = 0             
#     return False 
# 
# def endYT(imgarr,x,y,d):
#     n = 0
#     linesize = 3  #设置线粗细 
#     for l in  range(linesize):
#         if int(imgarr[y-1][x]) - int(imgarr[y][x]) < -d and  int(imgarr[y][x]) - int(imgarr[y+l+1][x]) < -d:
#             n += 1
#             if n == linesize:
#                 return True
#         else:
#             n = 0             
#     return False 
#
             
def get_img_basedata(name):
    newname,startx,starty,endx,endy= img_init('L',name) #图像初始化
    if 'L'+name not in newname:
        return newname,'',-1,-1,-1,-1,-1,-1
    img = Image.open(newname).convert('L') #转换成灰度图像
    endx,endy = endx+30,endy+30 #图像不清楚时，阀值会把图像判断为不存在
    return img,array(img),int(img.size[0]),int(img.size[1]),startx,starty,endx,endy
 
  

#获得图像区域内的最小值、最大值
def getbox_min_max(img,x,y,w,h):
    box = (x,y,x+w,y+h)
    cropImg = img.crop(box) #裁切图片
    boximg = array(cropImg)
    return int(boximg.min()),int(boximg.max())

#将图像区域内 值>=threshold阀值  置255
def setbox_255(imgarr,x1,y1,w,h,threshold):
    for y in  range(h):
        y += y1
        for x in  range(w):
            x += x1
            if int(imgarr[y][x]) >= threshold:
                imgarr[y][x] = 255
    return ''

#将图像区域内 值<=threshold阀值  置0
def setbox_0(imgarr,x1,y1,w,h,threshold):
    for y in  range(h):
        y += y1
        for x in  range(w):
            x += x1
            if int(imgarr[y][x]) <= threshold:
                imgarr[y][x] = 0
    return ''


#break  # 跳出当前循环
# box = (x,y,300,500)
# region = img.crop(box)
#min = imgarr[y].min() 
#在图像指定坐标画矩形 
def doline(imgarr,x,y,lx,ly):
    #获得一条橫线
    for x1 in range(lx):
        x1 = x1+x
        imgarr[y][x1] = 255
    for x1 in range(lx):
        x1 = x1+x
        imgarr[ly+y][x1] = 255

    
    #获得一条竖线
    for y1 in range(ly):
        y1 = y1+y
        imgarr[y1][x] = 255
    for y1 in range(ly):
        y1 = y1+y
        imgarr[y1][lx+x] = 255

#--------------------box_abs_minmax_threshold---------------------#
BOX_MIN_MAX_THRESHOLD = 100 #设定矩形框中有无字 阀值
def box_abs_minmax_threshold(img,x,y,w,h):
    min,max = box_min_max(img,x,y,w,h)           
    return abs(min-max) > BOX_MIN_MAX_THRESHOLD
#-----------           get_box_xy          ----------#
def get_box_x(img,x1,y1,w,h):
    for y0 in  range(h/PROBE_H):
        y = y0*PROBE_H + y1
        for x0 in  range(w/PROBE_W):
            x = x0*PROBE_W + x1
            if box_abs_minmax_threshold(img,x,y,PROBE_W,PROBE_H) and box_abs_minmax_threshold(img,x+PROBE_W,y+PROBE_H,PROBE_W,PROBE_H): 
                return x,y 
    return 0,0

def get_box_y(img,x1,y1,w,h):
    for x0 in  range(w/PROBE_W):
        x = x0*PROBE_W + x1
        for y0 in  range(h/PROBE_H):
            y = y0*PROBE_H + y1
            if box_abs_minmax_threshold(img,x,y,PROBE_W,PROBE_H) and box_abs_minmax_threshold(img,x+PROBE_W,y+PROBE_H,PROBE_W,PROBE_H):            
                return x,y 
    return 0,0
def get_box_xy(img,x1,y1,w,h):
    xx,xy = get_box_x(img,x1,y1,w,h)
    yx,yy = get_box_y(img,x1,y1,w,h)
    return yx,xy 
#-----------           get_endbox_xy          ----------#
#横向（从右向左）  从下向上搜索
def get_endbox_x(img,x0,y0):
    x0,y0 = x0-PROBE_W,y0-PROBE_H #防止设置初始坐标，小于探头大小的情况
    w,h = x0+PROBE_W,y0+PROBE_H
    for y1 in  range(h/PROBE_H):
        y = y0 - y1*PROBE_H
        for x1 in  range(w/PROBE_W):
            x = x0 - x1*PROBE_W
            if box_abs_minmax_threshold(img,x,y,PROBE_W,PROBE_H) and box_abs_minmax_threshold(img,x-PROBE_W*2,y-PROBE_H,PROBE_W,PROBE_H):             
                return x,y 
    return 0,0

#竖向（从下向上）  从右向左搜索
def get_endbox_y(img,x0,y0):
    x0,y0 = x0-PROBE_W,y0-PROBE_H #防止设置初始坐标，小于探头大小的情况
    w,h = x0+PROBE_W,y0+PROBE_H
    for x1 in  range(w/PROBE_W):
        x = x0 - x1*PROBE_W
        for y1 in  range(h/PROBE_H):
            y = y0 - y1*PROBE_H
            if box_abs_minmax_threshold(img,x,y,PROBE_W,PROBE_H) and box_abs_minmax_threshold(img,x-PROBE_W*2,y-PROBE_H,PROBE_W,PROBE_H):             
                return x,y 
    return 0,0

def get_endbox_xy(img,x0,y0):
    xx,xy = get_endbox_x(img,x0,y0)
    yx,yy = get_endbox_y(img,x0,y0)
    return yx,xy 

#----------------------#
# 二值化函数
# def Two_value(threshold):    
#     table = []
#     for i in range(256):    
#         if i < threshold:    
#             table.append(0)    
#         else:    
#             table.append(1)    
#     return table
#一行代码实现 二值化函数
def Two_value(threshold):
    return [0 if i < threshold else 1 for i in range(256)]




# # 图像基本操作  http://localhost:9000/index/
# def index(reuqest):
#      return HttpResponse(blank.show(),"GIF")


#圆、椭圆  http://localhost:9000/index/
# def index(reuqest):
#     blank = Image.new("RGB",[1024,768],"white")
#     drawObject = ImageDraw.Draw(blank)
#     drawObject.ellipse((100,100,600,600),outline = 128)
#     drawObject.ellipse((100,250,600,450),fill = "blue")  
#     return HttpResponse(blank.show(),"GIF")


# #mystr = "姓名性别民族出生年月日住址"
# mystr = "姓 名 民 族"
# #二值化 识别英文、数字 身份证中文识别不好 
# # http://localhost:9000/ocr_text/
# def ocr_text(reuqest):
#     str = ''
#     name = 'cuili.jpeg'    
#     image = Image.open(name) #准确率90%  test.jpeg;  准确率100% test_ok.png
#     #threshold = 135 # "姓名性别民族出生年月日" 132 - 135  134
#     #threshold = 50  #身份证号码 30  73
#     #threshold = 110  #公民身份号码 110
#     #threshold = 90  #住址 89 90
#     threshold = 80
#     #转化到灰度图  
#     imgry = image.convert('L') 
#     
#       
#     #保存图像  
#     imgry.save('g'+name)
#     table=Two_value(threshold)
# #     #二值化，采用阈值分割法，threshold为分割点   
#     out = imgry.point(table,'1')    
#     out.save('b'+name)   
#     str =pytesseract.image_to_string(out,lang='chi_sim')
# 
# #     while(mystr not in str):
# #         threshold = threshold + 1    
# #         table=Two_value(threshold)
# #         #二值化，采用阈值分割法，threshold为分割点   
# #         out = imgry.point(table,'1')    
# #         out.save('b'+name)
# #         str =pytesseract.image_to_string(out,lang='chi_sim')
#     print 'threshold=',threshold
#     print str
#     return HttpResponse(out.show(),"GIF")

# # http://localhost:9000/test_Two_value/
# def test_Two_value(reuqest):
#     str = ''
#     name = 'cuili.jpeg'    
#     image = Image.open(name) 
# 
#     #转化到灰度图  
#     imgry = image.convert('L')
#      
# 
#     threshold = 115    
#       
#     #保存图像  
#     imgry.save('g'+name)
#     table=Two_value(threshold)
#      #二值化，采用阈值分割法，threshold为分割点   
#     out = imgry.point(table,'1')    
#     out.save('b'+name)   
#     str =pytesseract.image_to_string(image,lang='chi_sim')
# 
#     print 'threshold=',threshold
#     print str
#     return HttpResponse(out.show(),"GIF")

'''

$ tesseract
Usage:
  tesseract --help | --help-psm | --help-oem | --version
  tesseract --list-langs [--tessdata-dir PATH]
  tesseract --print-parameters [options...] [configfile...]
  tesseract imagename|stdin outputbase|stdout [options...] [configfile...]

OCR options:
  --tessdata-dir PATH   Specify the location of tessdata path.
  --user-words PATH     Specify the location of user words file.
  --user-patterns PATH  Specify the location of user patterns file.
  -l LANG[+LANG]        Specify language(s) used for OCR.
  -c VAR=VALUE          Set value for config variables.
                        Multiple -c arguments are allowed.
  --psm NUM             Specify page segmentation mode.
  --oem NUM             Specify OCR Engine mode.
NOTE: These options must occur before any configfile.
页面分割模式：
0 方向和脚本检测（OSD）只。
1 利用OSD进行自动页面分割。
2自动分页，但没有OSD或OCR。
3全自动分页，但没有OSD。（默认）
4假设一列可变大小的文本。
5假设一个垂直对齐文本的统一块。
6假设一个统一的文本块。
7将图像视为单个文本行。
8把图像当作一个词来对待。
9将图像作为一个单词在一个圆中处理。
10将图像视为单个字符。
11稀疏文本。找到尽可能多的文本，没有特别的顺序。
12带有OSD的稀疏文本。
13条原料线。将图像视为单个文本行，
        绕过特定的特塞尔特的黑客。

Page segmentation modes:
  0    Orientation and script detection (OSD) only.
  1    Automatic page segmentation with OSD.
  2    Automatic page segmentation, but no OSD, or OCR.
  3    Fully automatic page segmentation, but no OSD. (Default)
  4    Assume a single column of text of variable sizes.
  5    Assume a single uniform block of vertically aligned text.
  6    Assume a single uniform block of text.
  7    Treat the image as a single text line.
  8    Treat the image as a single word.
  9    Treat the image as a single word in a circle.
 10    Treat the image as a single character.
 11    Sparse text. Find as much text as possible in no particular order.
 12    Sparse text with OSD.
 13    Raw line. Treat the image as a single text line,
            bypassing hacks that are Tesseract-specific.

OCR Engine modes:
  0    Original Tesseract only.
  1    Cube only.
  2    Tesseract + cube.
  3    Default, based on what is available.

Single options:
  -h, --help            Show this help message.
  --help-psm            Show page segmentation modes.
  --help-oem            Show OCR Engine modes.
  -v, --version         Show version information.
  --list-langs          List available languages for tesseract engine.
  --print-parameters    Print tesseract parameters to stdout.

准确率90% 
1

Pa e segmentation modes: .
g Orientation and script detection (05D) only.

1 Automatic page segmentation with OSD.

2 Automatic page segmentation, but no 050, or' OCR.

3 Fully automatic page segmentation, but no 059. (Default)
4 Assume a single column of text of variable sues.

5 Assume a single uniform block of vertically ahgned text.
6

7

8

Assume a single uniform block of text.

Treat the image as a single text line.
Treat the image as a single word.
9 Treat the image as a single word in a circle.

10 Treat the image as a single character.
11 Sparse text. Find as much text as possible in no particular order.

12 Sparse text with OSD.
13 Raw line. Treat the image as a single text line,
bypassing hacks that are Tesseract-specific.

OCR Engine modes:
0 Original Tesseract only.
1 Cube only.
2 Tesseract + cube.
3 Default, based on what is available.

'''

#由于都是数字    
#对于识别成字母的 采用该表进行修正    
rep={'O':'0',    
    'I':'1','L':'1',    
    'Z':'2',    
    'S':'8'    
    };    
    
def get_img_txt(name,threshold):          
    #打开图片    
    im = Image.open(name)    
    #转化到灰度图  
    imgry = im.convert('L')  
    #保存图像  
    imgry.save('g'+name)    
    #二值化，采用阈值分割法，threshold为分割点 
    table = Two_value(threshold)  
    out = imgry.point(table,'1')    
    out.save('b'+name)    
    #识别    
    text = pytesseract.image_to_string(out)    
    #识别对吗    
    text = text.strip()    
#    text = text.upper();      
#     for r in rep:    
#         text = text.replace(r,rep[r])     
    #out.save(text+'.jpg')    
    print( text)    
    return text

#识别图片数字 准确率100% http://localhost:9000/get_numimg/
#参考： https://blog.csdn.net/djd1234567/article/details/50739872
def get_numimg(reuqest):    
    txt = get_img_txt('num.png',130)  #阀值130 
    return HttpResponse(txt) 

import sys
import pyocr
import pyocr.builders

import os
import subprocess

def image_to_string(img, cleanup=True, plus=''):
    # cleanup为True则识别完成后删除生成的文本文件
    # plus参数为给tesseract的附加高级参数
    subprocess.check_output('tesseract ' + img + ' ' +
                            img + ' ' + plus, shell=True)  # 生成同名txt文件
    text = ''
    with open(img + '.txt', 'r') as f:
        text = f.read().strip()
    if cleanup:
        os.remove(img + '.txt')
    return text

#英文图片测试 http://localhost:9000/test_English_img
def test_English_img(reuqest):
    #txt = image_to_string('cuili.jpeg', False,'chi_sim')
    txt = image_to_string('eng.jpeg', False)
    print(txt) 
    return HttpResponse(txt) 

# # 奇异值分解（SVD）实现简单的图像降噪处理
# from numpy import *  
# from numpy import linalg as la 

# #准确识别吴春龙身份证，但不能通用。 http://localhost:9000/test_svd
# def test_svd(reuqest):
#     line_min = 127 #(吴春龙84 准确识别)  一级阀值（最小值113） line_min>127 255；line_min<=127
#     name = 'cuili.jpeg'
#     #name = 'wuchunlong.jpeg'
#     im = Image.open(name).convert('L') #转换成灰度图像
# 
#     x1 = im.size[0] #整形
#     y1 = im.size[1]
#     imgarr = array(im) #图像变为二维数组
#     min = imgarr.min()
#     max = imgarr.max()
#     print 'min = ',min,max #wuchunlong.jpeg 0 201 ,cuili.jpeg 0 254
#     h=500
#     for y in  range(h):
#         for x in  range(x1):
#             # 一行中大于阀值，置255 白
#             if imgarr[y][x] > line_min:
#                 imgarr[y][x] = 255
# 
#     
#     img = Image.fromarray(imgarr) # 二维数组转换成图像
#     print pytesseract.image_to_string(img,lang='chi_sim')    
#     return HttpResponse(img.show(),"GIF") 
#     return HttpResponse('ok')


# #准确定位到字符 http://localhost:9000/test_svd_denoise1
# def test_svd_denoise1(reuqest):   
#     name = 'cuili.jpeg'
#     name = 'wuchunlong.jpeg'
#     name = 'chunlong.jpeg'
#     
# #     name = 'wu1.jpeg'
# #     name = 'wu2.jpeg'
# #     name = 'wu3.jpeg' #图像逆时针90度
# #     name = 'wj1.jpeg'
# #     name = 'wj2.jpeg' 
#        
#     img = Image.open(name).convert('L') #转换成灰度图像
#     #保存图像  
#     img.save('L'+name)    
# 
#     IMG_W = img.size[0]
#     IMG_H = img.size[1]
#     imgarr = array(img) #图像变为二维数组
#     
#     # 左边区域
#     # 姓名 左上角坐标
#     a0,b0 = get_startchar_xy(imgarr,WORLD_W_H,WORLD_W_H,IMG_W-200,IMG_H-200,16,10)
#     a1,b1 = a0-30,b0-30 #设置富余量值 30
# 
#     # 姓名
#     x0,y0 = get_startchar_xy1(imgarr,a1,b1,100,100,16,10) # 获得开始坐标
#     endx,endy = x0+WORLD_W_H,y0+WORLD_W_H
#     endw,endh = WORLD_W_H*2,WORLD_W_H*2
#     x1,y1 = get_endchar_xy1(imgarr,endx,endy,endw,endh,9,9) # 获得结束坐标    
#     w0,h0 = x1-x0, y1-y0
#     w,h = w0*4,h0*14
#     x,y = x0-w0,y0-h0
#     min,max =getbox_min_max(img,x,y,w,h)
#     print min,max
#     setbox_255(imgarr,x,y,w,h,min+40)
#     doline(imgarr,x,y,w,h)
#      
#     #公民身份证号码
#     startx,starty = x0-w0-10,y0+h+10
#     x0,y0 = get_startchar_xy1(imgarr,startx,starty,w0*2,IMG_H-starty-10,9,9) # 获得开始坐标    
#     w,h = w0*9,h0*2
#     x,y = x0-w0,y0-15
#     min,max =getbox_min_max(img,x,y,w,h)
#     print min,max
#     setbox_255(imgarr,x,y,w,h,100)
#     doline(imgarr,x,y,w,h)
#       
#     #620。。。
#     w,h = w0*20,h0*2
#     x,y =x0+w0*9,y0-15
#     min,max =getbox_min_max(img,x,y,w,h)
#     print min,max
#     setbox_255(imgarr,x,y,w,h,50)
#     doline(imgarr,x,y,w,h)
# 
#     # 右边区域
#     # 吴春龙  崔丽
#     startx,starty = a0+w0*3+20,b0-h0
#     x0,y0 = get_startchar_xy1(imgarr,startx,starty,WORLD_W_H*2,WORLD_W_H*2,9,9) # 获得开始坐标
#     endx,endy = startx+w0*5+20,starty+w0*3
#     x1,y1 = get_endchar_xy1(imgarr,endx,endy,endw,endh,10,10) # 获得结束坐标    
#     w,h = x1-x0+30,y1-y0+30
#     x,y = x0-15,y0-15
#     min,max =getbox_min_max(img,x,y,w,h)
#     print min,max
#     setbox_255(imgarr,x,y,w,h,min+40)
#     doline(imgarr,x,y,w,h)
# 
#     # 男 女
#     Sexx,Sexy = a0+w0*3+20,b0+h0*3-20
#     x0,y0 = get_startchar_xy1(imgarr,Sexx,Sexy,WORLD_W_H*2,WORLD_W_H*2,9,9) # 获得开始坐标
#     endx,endy = Sexx+w0*2,Sexy+w0*2    
#     x1,y1 = get_endchar_xy1(imgarr,endx,endy,100,100,10,10) # 获得结束坐标    
#     w1,h1 = x1-x0,y1-y0
#     w,h = w1+15,h1+30
#     x,y = x0-15,y0-15
#     min,max =getbox_min_max(img,x,y,w,h)
#     print min,max
#     setbox_255(imgarr,x,y,w,h,min+40)
#     doline(imgarr,x,y,w,h)
#     
#     # 民族  
#     startx,starty = x0+w1+5,y0
#     w,h = w0*5+10,h1+30
#     x,y = startx,starty-15    
#     min,max =getbox_min_max(img,x,y,w,h)
#     print '民族', min,max
#     setbox_255(imgarr,x,y,w,h,min+36)
#     doline(imgarr,x,y,w,h)
# 
#       
#     # 汉
#     startx,starty =startx+w,starty
#     w,h = w1+20,h+30
#     x,y = startx,starty-15
#     min,max =getbox_min_max(img,x,y,w,h)
#     print min,max
#     setbox_255(imgarr,x,y,w,h,min+40)
#     doline(imgarr,x,y,w,h)
#     
#     # 1961
#     startx,starty = Sexx,Sexy + w1*2
#     x0,y0 = get_startchar_xy1(imgarr,startx,starty,WORLD_W_H*2,WORLD_W_H*2,9,9) # 获得开始坐标
#     endx,endy = startx+w0*4-10,starty+w0*2    
#     x1,y1 = get_endchar_xy1(imgarr,endx,endy,100,100,10,10) # 获得结束坐标    
#     w,h = x1-x0+20,y1-y0+20
#     x,y =x0-15,y0-15
#     min,max =getbox_min_max(img,x,y,w,h)
#     print min,max
#     setbox_255(imgarr,x,y,w,h,min+40)
#     doline(imgarr,x,y,w,h)
#    
# 
#     # 年    
#     x0 = x1+ w0 -15
#     w,h = w0+15,h
#     x,y = x0,y0-15
#     min,max =getbox_min_max(img,x,y,w,h)
#     print min,max
#     setbox_255(imgarr,x,y,w,h,min+40)
#     doline(imgarr,x,y,w,h)
# 
#     # 12
#     x0 = x0 + w0*2 -10
#     w,h = w0*2 -25,h
#     x,y = x0,y0-15
#     min,max =getbox_min_max(img,x,y,w,h)
#     print min,max
#     setbox_255(imgarr,x,y,w,h,min+40)
#     doline(imgarr,x,y,w,h)
#     
#     # 月
#     x0 = x0 + w+5
#     w = w0 +10
#     x,y = x0,y0-15
#     min,max =getbox_min_max(img,x,y,w,h)
#     print min,max
#     setbox_255(imgarr,x,y,w,h,min+40)
#     doline(imgarr,x,y,w,h)
#     
#     #25
#     x0 = x0 + w+2
#     w,h = w0*2-5,h
#     x,y = x0,y0-15
#     min,max =getbox_min_max(img,x,y,w,h)
#     print min,max
#     setbox_255(imgarr,x,y,w,h,min+40)
#     doline(imgarr,x,y,w,h)
#     
#     # 日
#     x0 = x0 + w
#     x,y = x0,y0-15
#     min,max =getbox_min_max(img,x,y,w,h)
#     print min,max
#     setbox_255(imgarr,x,y,w,h,min+40)
#     doline(imgarr,x,y,w,h)
#     
#     # 甘肃省
#     startx,starty = Sexx,Sexy + w1*4 +20
#     x0,y0 = get_startchar_xy1(imgarr,startx,starty,WORLD_W_H*2,WORLD_W_H*2,9,9) # 获得开始坐标
#     endx,endy = startx+w0*4-10,starty+w0*2    
#     x1,y1 = get_endchar_xy1(imgarr,endx,endy,100,100,10,10) # 获得结束坐标    
#     w,h = w1*13+10,h1*3
#     x,y = x0-15,y0-15
#     min,max =getbox_min_max(img,x,y,w,h)
#     print '甘肃省',min,max
#     setbox_255(imgarr,x,y,w,h,101)
#     doline(imgarr,x,y,w,h)
#     
#     print pytesseract.image_to_string(img,lang='chi_sim') 
#     img = Image.fromarray(imgarr) # 二维数组转换成图像
#     return HttpResponse(img.show(),"GIF")

# #矩形中两种算法，获得两种平均值，相减取绝对值 
# def box_Average_threshold(img,x,y,w,h):
#     min,max = box_min_max(img,x,y,w,h)           
#     return abs(Average(array(img),x,y,w,h)-(min+max)/2) > BOX_AVERAGE_THRESHOLD


# def box_abs_minmax_threshold1(img,x,y,w,h,MIN_MAX_THRESHOLD):
#     min,max = box_min_max(img,x,y,w,h)           
#     return abs(min-max) > MIN_MAX_THRESHOLD


