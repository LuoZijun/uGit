#!/usr/bin/env python
#-*- coding:utf-8 -*-

import gitlib

"参数: 文件名, 文件内容 "
git = gitlib.Core('articles','Luo','Luo','Luo@freeweapon.org')
git.add('TEST.rst','这是测试文章 test.rst\n')
print git.commit_tree
git.commit('test commit')
