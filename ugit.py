#!/usr/bin/env python
#-*- coding:utf-8 -*-


import os,sys,time,shutil

import difflib,zlib,re
import hashlib,binascii,struct
import stat

class Setting:
    "Git Setting"
    WORKSPACE = ''
    GIT_DIR = '.git'
    REPO_DIR = ''

class Repository:
    "Git 仓库"
    def __init__(self,workspace=None, author=None, user=None, email=None):
        self.workspace = workspace
        self.author = author
        self.user = user #committer
        self.email = email
    @staticmethod
    def init(workspace):
        "初始化仓库"
        libroot = os.path.dirname(os.path.abspath(__file__))
        return shutil.copytree( libroot + '/template/.git', workspace + '/.git')
    @staticmethod
    def create(workspace):
        "创建仓库"
        libroot = os.path.dirname(os.path.abspath(__file__))
        return shutil.copytree( libroot + '/template', workspace)
    
    def add(path):
        "增加文件至提交事务当中"
        pass
        
    def commit(path):
        "向仓库提交操作"
        pass
    
    def delete(path):
        "删除操作"
        pass

    def diff(path):
        "查看"
        pass

    def log(path):
        "提取仓库日志"
        pass

    def status(path):
        "仓库状态"
        pass

    
    
class Git:
    def __init__(self,workspace=None):
        "初始化Git"
        self.workspace = workspace
    def commit(self):
        "向仓库提交文件"
        pass
    def remove(self):
        "删除文件对象"
        pass
    def add(self, path = './', file = None):
        "增加文件对象"
        if file == None: AssertionError("无效的文件")
        
    def get(self, sha = None):
        "提取文件对象"
        pass
    def tree(self):
        "获取当前树"
        last_commit_hash = open(self.workspace + '/refs/heads/master').read().replace('\n','')
        last_commit_obj = GitIO(self.workspace).read(last_commit_hash)
        tree_hash = re.compile(r"commit\s\d+\x00tree\s(\S+)\n",re.DOTALL).findall(last_commit_obj)[0]
        tree_obj = GitIO(self.workspace).read(tree_hash)
        return GitTree().unpack(tree_obj)
    def query(self, tree , name):
        "查询文件对象散列值"
        pass
    


if __name__ == '__main__':
    print ":: Git Lib Project Status:      **Building**"


