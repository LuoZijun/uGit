#!/usr/bin/env python
#-*- coding:utf-8 -*-
import os,sys,time

from django.http import HttpResponse
import re
import gitlib
git = gitlib.Core('log/articles','Luo','Luo','Luo@freeweapon.org')

template = """
<html lang="zh_CN">
    <head>
        <title>log</title>
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
    <h1>Log</h1>
    <hr>
    <br>
        <p><a href="/add">添加文章</a></p>
        <p>文章列表: </p>
        <ul>
            %s
        </ul>
    """
    article = """
        <li><a href="%s">%s</a></li>\n
    """
    #tree = git.Git("/home/luozijun/文档/Git研究/gitm/gitm/blog/.git").tree()
    tree_content = git.tree()
    tlist = tree_content.split('\n')
    articles = ""
    for tree in tlist:
        t = tree.split('\t')
        if len(t) > 1:
            if int(t[0]) == 40000:
                articles += article %( '/category/' + t[2], t[1] )
            elif int(t[0]) == 100644:
                articles += article %( '/articles/' + t[1] + '/' + t[2], t[1] )
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
    title = request.POST['title'].encode('utf8')
    content = request.POST['content'].encode('utf8')
    #TODO: 阅读 Git索引文件规范 (index)
    """
        1. 创建 tree/blob 对象(得到对象Hash(sha1) )
        2. 在 索引 里面查找 该 对象编号 的信息( 文件名,大小,类型,权限 )
    """
    git.add(title, content)
    commit_tree = git.commit_tree
    print git.commit('add one article.')
    
    return HttpResponse(commit_tree)

def category(request, tree):
    "目录浏览"
    tree = tree.encode('utf8')
    return HttpResponse("你要查看的分类是: %s \n<br>\n 目前暂不支持查阅." %(tree))

def articles(request, title, sha):
    "文章阅读"
    sha = sha.encode('utf8')
    title = title.encode('utf8')
    
    content = git.blob(sha)
    article = """
    <h1>%s</h1>
    <div class="content">
    %s
    </div>
    """
    if content:
        from docutils.core import publish_string,default_description
        description = ('Generates (X)HTML documents from standalone reStructuredText '
               'sources.  ' + default_description)
        
        content = re.compile(r"^blob\s\d+\x00(.*?)$",re.DOTALL).findall(content)[0]
        try:
            response = publish_string(content, writer_name='html')
        except:
            response = "    @@不是正确的RST格式 :)) \n\n<br><br><hr>\n\n<br> <pre>%s</pre>" %( content)
        #article = article %( str(title), str(content))
        #response = template %( article )
    else:
        response = "你要查看的文章是: %s \n<br>\n 目前暂不支持查阅." %(name)
    return HttpResponse(response)
    
