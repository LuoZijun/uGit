#!/usr/bin/env python
#-*- coding:utf-8 -*-

import gitlib

git = gitlib.Core('articles','Luo','Luo','Luo@freeweapon.org')

def git_add():
    "参数: 文件名, 文件内容 "
    git.add('TEST3.rst','这是测试文章 test3.rst\n')
    print git.commit_tree
    git.commit('test3 commit')

def get_tree():
    "fetch last commit tree"
    tree = git.tree()
    print repr(tree)
    print ''
    print tree

if __name__ == '__main__':
    #git_add()
    get_tree()
