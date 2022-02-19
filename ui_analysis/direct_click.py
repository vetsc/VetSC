
#coding:utf-8
import  requests
import threading
from bs4 import BeautifulSoup
import re
import os
import time
import sys
req_header={
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding':'gzip, deflate',
    'Accept-Language':'zh-CN,zh;q=0.8',
    'Cookie':'__cfduid=d577ccecf4016421b5e2375c5b446d74c1499765327; UM_distinctid=15d30fac6beb80-0bdcc291c89c17-9383666-13c680-15d30fac6bfa28; CNZZDATA1261736110=1277741675-1499763139-null%7C1499763139; tanwanhf_9821=1; Hm_lvt_5ee23c2731c7127c7ad800272fdd85ba=1499612614,1499672399,1499761334,1499765328; Hm_lpvt_5ee23c2731c7127c7ad800272fdd85ba=1499765328; tanwanpf_9817=1; bdshare_firstime=1499765328088',
    'Host':'www.173kt.net',
    'Proxy-Connection':'keep-alive',
    'Referer':'http://www.173kt.net/book',
    'Upgrade-Insecure-Requests':'1',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.104 Safari/537.36'
}


req_url_base='http://www.173kt.net/book'           #小说主地址

#小说下载函数
#txt_id：小说编号
#txt字典项介绍
#id：小说编号
# title：小说题目
# first_page：第一章页面
# txt_section：章节地址
# section_name：章节名称
# section_text：章节正文
# section_ct：章节页数
def get_txt(txt_id):
    txt={}
    txt['title']=''
    txt['id']=str(txt_id)
    try:
        #print("请输入需要下载的小说编号：")
        #txt['id']=input()
        req_url=req_url_base+ txt['id']+'/'                        #根据小说编号获取小说URL
        print("小说编号："+txt['id'])
        res=requests.get(req_url,params=req_header)             #获取小说目录界面
        soups=BeautifulSoup(res.text,"html.parser")           #soup转化
        #获取小说题目
        txt['title']=soups.select('#wrapper .box_con #maininfo #info h1')[0].text
        txt['author']=soups.select('#wrapper .box_con #maininfo #info p')
        #获取小说最近更新时间
        txt['update']=txt['author'][2].text
        #获取最近更新章节名称
        txt['lately'] = txt['author'][3].text
        #获取小说作者
        txt['author']=txt['author'][0].text
        #获取小说简介
        txt['intro']=soups.select('#wrapper .box_con #maininfo #intro')[0].text.strip()
        print("编号："+'{0:0>8}   '.format(txt['id'])+  "小说名：《"+txt['title']+"》  开始下载。")
        print("正在获取所有章节地址。。。")
        #获取小说所有章节信息
        all_page_address=soups.select('#wrapper .box_con #list dl dd a')
        #获取小说总章页面数
        section_ct=len(all_page_address)
        print("小说章节页数："+str(section_ct))
        #打开小说文件写入小说相关信息
        fo = open('{0:0>8}-{1}.txt.download'.format(txt['id'],txt['title']), "ab+")
        fo.write((txt['title']+"\r\n").encode('UTF-8'))
        fo.write((txt['author'] + "\r\n").encode('UTF-8'))
        fo.write((txt['update'] + "\r\n").encode('UTF-8'))
        fo.write((txt['lately'] + "\r\n").encode('UTF-8'))
        fo.write(("*******简介*******\r\n").encode('UTF-8'))
        fo.write(("\t"+txt['intro'] + "\r\n").encode('UTF-8'))
        fo.write(("******************\r\n").encode('UTF-8'))
        #获取每一章节信息
        for one_page_info in all_page_address:
            try:
                #请求当前章节页面
                r=requests.get(req_url+str(one_page_info['href']),params=req_header)
                #soup转换
                soup=BeautifulSoup(r.text,"html.parser")
                #获取章节名称
                section_name=soup.select('#wrapper .content_read .box_con .bookname h1')[0]
                section_text=soup.select('#wrapper .content_read .box_con #content')[0]
                for ss in section_text.select("script"):   #删除无用项
                    ss.decompose()
                #获取章节文本
                section_text=re.sub( '\s+', '\r\n\t', section_text.text).strip('\r\n')#
                #以二进制写入章节题目
                fo.write(('\r'+section_name.text+'\r\n').encode('UTF-8'))
                #以二进制写入章节内容
                fo.write((section_text).encode('UTF-8'))
                print(txt['title']+' 章节：'+section_name.text+'     已下载')
                #print(section_text.text.encode('UTF-8'))
            except:
                print("编号："+'{0:0>8}   '.format(txt['id'])+  "小说名：《"+txt['title']+"》 章节下载失败，正在重新下载。")
        fo.close()
        os.rename('{0:0>8}-{1}.txt.download'.format(txt['id'],txt['title']), '{0:0>8}-{1}.txt'.format(txt['id'],txt['title']))
    except:     #出现错误会将错误信息写入dowload.log文件，同时答应出来
        fo_err = open('dowload.log', "ab+")
        try:
            fo_err.write(('['+time.strftime('%Y-%m-%d %X', time.localtime())+"]：编号：" + '{0:0>8}   '.format(txt['id']) + "小说名：《" + txt['title'] + "》 下载失败。\r\n").encode('UTF-8'))
            print('['+time.strftime('%Y-%m-%d %X', time.localtime())+"]：编号："+'{0:0>8}   '.format(txt['id'])+  "小说名：《"+txt['title']+"》 下载失败。")
            os.rename('{0:0>8}'.format(txt['id']) + '-' + txt['title'] + '.txt.download',
                      '{0:0>8}'.format(txt['id']) + '-' + txt['title'] + '.txt.error')
        except:
            fo_err.write(('['+time.strftime('%Y-%m-%d %X', time.localtime())+"]：编号："+'{0:0>8}   '.format(txt['id'])+"下载失败。\r\n").encode('UTF-8'))
            print('['+time.strftime('%Y-%m-%d %X', time.localtime())+"]：编号："+'{0:0>8}   '.format(txt['id'])+"下载失败。")
        finally: #关闭文件
            fo_err.close()

#此处为需要下载小说的编号，编号获取方法在上文中已经讲过。
get_txt(1566)
