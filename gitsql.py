#!/usr/bin/env python
#-*- coding:utf-8 -*-


class GSQL:
    "GIT 数据结构查询抽象"
    def __init__(self, workspace, author , user, email):
        self.workspace = workspace
        self.author = author
        self.user = user
        self.email = email
    
    @staticmethod
    def connect(self, \
                workspace=os.getcwd(), \
                author='Python', \
                user='PyGit', \
                email='PyGit@localhost',\
                ):
        return GSQL(workspace, author , user, email)
    def check(self):
        "检查仓库参数是否正确"
        
        
    def execute(self, sql):
        "Git 数据库查询"
        pass
    def cursor(self):
        "游标"
        pass
    def commit(self):
        "提交操作"
        pass
    def fetch(self):
        "提取查询结果"
        pass