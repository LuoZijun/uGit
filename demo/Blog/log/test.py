#!/usr/bin/env python
#-*- coding:utf-8 -*-

import gitlib

git = gitlib.Core('articles','Luo','Luo','Luo@freeweapon.org')

def git_add():
    "参数: 文件名, 文件内容 "
    content = """
更复杂的内容
======================

.. contents::

描述
-----------
这是一份描述哦。

来自Python Docutils Lib.

介绍
-------------
坏心情原因?

代码
------------

python
^^^^^^^^

.. code:: python

    import os
    import time
    print "hello, i'm python"

PHP
^^^^^^^^^^^

.. code:: php

    <?php
    print_r('hello, im php.....');
    
    ?>

"""
    git.add('代码.rst', content)
    print git.commit_tree
    git.commit('代码 commit')

def get_tree():
    "fetch last commit tree"
    tree = git.tree()
    print repr(tree)
    print ''
    print tree

if __name__ == '__main__':
    git_add()
    #get_tree()
