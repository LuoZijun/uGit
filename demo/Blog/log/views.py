#!/usr/bin/env python
#-*- coding:utf-8 -*-
import os,sys,time

from django.http import HttpResponse

import git

template = """
<html lang="zh_CN">
    <head>
        <title>My Blog</title>
        <meta charset="utf8">
    </head>
    <body>
        %s
    </body>
    
    <footer>
        <hr>
        <p>Python 2.7 / Django</p>
    </footer>
</html>
"""

def index(request):
    "首页"
    body = """
    <h1>It Work!</h1>
        <p><a href="/add">添加文章</a></p>
        <p>文章列表: </p>
        <ul>
            %s
        </ul>
    """
    article = """
        <li><a href="%s">%s</a></li>\n
    """
    tree = git.Git("/home/luozijun/文档/Git研究/gitm/gitm/blog/.git").tree()
    articles = ""
    for p in tree:
        if p['type'] == 'blob':
            articles += article %( '/blog/' + p['path'], p['path'] )
        else:
            articles += article %( '/blog/' + p['path'] + '/', p['path'] + '/' )
    return HttpResponse(template % (body% articles ) )



def init(request):
    "初始化仓库"
    #NOTE: 已转移至 git.py

def add(request):
    "添加文章视图"
    body = """
        <h1>添加文章</h1>
        <form action="/commit" method="post">
            标题: <input type="text" name="title" /> <br><br>
            内容: <textarea rows="10" cols="30" name='content'></textarea>
            <br><br><br>
            <input type="submit" value="提交" /> <br>
        </form>
    """
    return HttpResponse(template % body)
    
def commit(request):
    "向仓库提交内容"
    title = request.POST['title']
    content = request.POST['content']
    #TODO: 阅读 Git索引文件规范 (index)
    """
        1. 创建 tree/blob 对象(得到对象Hash(sha1) )
        2. 在 索引 里面查找 该 对象编号 的信息( 文件名,大小,类型,权限 )
    """
    return HttpResponse('ok')

def category(request, tree):
    "目录浏览"
    tree = tree.encode('utf8')
    return HttpResponse("你要查看的分类是: %s \n<br>\n 目前暂不支持查阅." %(tree))

def articles(request,name):
    "文章阅读"
    name = name.encode('utf8')
    
    return HttpResponse("你要查看的文章是: %s \n<br>\n 目前暂不支持查阅." %(name))
    
