#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os,sys,time
import hashlib,binascii,struct
import zlib
import stat,shutil

class utils:
    "工具函数"
    @staticmethod
    def sha1(content):
        sha1 = hashlib.sha1()
        sha1.update(content)
        return sha1.hexdigest()
    @staticmethod
    def sha512(content):
        sha512 = hashlib.sha512()
        sha512.update(content)
        return sha512.hexdigest()
    @staticmethod
    def hex2bin(sha1):
        return binascii.a2b_hex(sha1)
    @staticmethod
    def bin2hex(sha1):
        return binascii.b2a_hex(sha1)
    @staticmethod
    def compress(content):
        return zlib.compress(content)
    @staticmethod
    def decompress(content):
        return zlib.decompress(content)
    @staticmethod
    def read(path):
        return open(path, 'r').read()
    
    @staticmethod
    def write(path, content, mode=100644):
        path = os.path.dirname(path)
        if path and not os.path.exists(path):
            os.makedirs(path)
        open(path, 'w').write(content)
        os.chmod(path, mode)
        return True

    @staticmethod
    def pmode(mode):
        "解析八进制文件权限( GIT使用八进制来描述权限 )"
        return int(mode, 8)
    @staticmethod
    def fmode(mode):
        "转换十进制权限至八进制"
        return int(oct(mode))
    @staticmethod
    def gmode(path):
        "读取系统文件权限"
        mode = os.stat(path).st_mode
        if stat.S_ISLNK(mode):
            "Linux Link"
            return 120000
        elif stat.S_ISDIR(mode):
            "directory"
            return 40000
        elif stat.S_ISREG(mode):
            "blob"
            return 100644
        else:
            "Do Not Support"
            raise AssertionError("File Mode (Int: %d) Not Support !" % mode )

class Blob:
    #"Blob Object"
    def __init__(self):
        pass
    @staticmethod
    def decode(data):
        "unpack blob object"
        if data[:4] != 'blob':
            raise AssertionError("无效的文件对象: %r" % data[:4])
        content = data[5:]
        size = re.compile(r"(\d+)\x00",re.DOTALL).findall(content)[0]
        return content[len(str(size))+1:]
    @staticmethod
    def encode(data):
        "pack blob object"
        header = "blob %d\x00" % len(data)          # type(space)size(null byte)
        content = header + data
        #sha1       = utils.sha1(content)
        #return {'content':content, 'sha1':sha1}         # 需要 转换二进制 binascii.a2b_hex
        return content
    @staticmethod
    def write(workspace, content, sha1=None):
        "write blob object to file system"
        if sha1 == None:
            sha1 = utils.sha1(content)
        

class Tree:
    "Tree Object"
    """
    OBJECT_MODE = { 
        100644:'blob', 
        100755:'blob', 
        40000:'tree',                             # 040000
        160000:'commit', 
        120000:'blob',                          # blob 对象的符号链接
    }
    """
    @staticmethod
    def decode(data):
        "unpack object tree"
        if data[:4] != 'tree':
            raise AssertionError("无效的树对象: %r" % data[:4])
        size = int(data.split('\x00')[0][5:])
        content = data[6+len(str(size)):]
        # SHA哈希长度为 20 个比特(二进制), 40个字节(十六进制) MODE 长度 5 - 6 位
        tlist = re.compile(r"(\d{5,6})\s(\S+)\x00(.{20})",re.DOTALL).findall(content)
        tree = ''
        for t in tlist:
            t = list(t)
            if int(t[0]) == 40000:
                t[0] = '040000'
            t[2] = utils.bin2hex(t[2])
            tree += '\t'.join(t) + '\n'
        return tree
    @staticmethod
    def encode(data):
        "pack object tree"
        header = "tree %d\x00%s"
        content = ""
        for tree in data.split('\n'):
            if len(tree) != 0:
                t = tree.split('\t')
                mode = int(t[0])
                path = t[1]
                sha1 = utils.hex2bin( t[2] )
                content += "%d %s\x00%s" %( mode, path, sha1 )
        return header %( len(content), content )
    @staticmethod
    def mktree(mode, path, sha1):
        "make tree object"
        return '\t'.join( [int(mode), path, sha1] )
    @staticmethod
    def maketree(tlist):
        "make tree object from object list"
        tree = []
        for  t in tlist:
            "struct  [mode, path, sha1]"
            tree.append( '\t'.join( t ) )
        return '\n'.join( tree )

class Commit:
    "Commit Object"
    @staticmethod
    def decode(data):
        "unpack commit object data"
        #content = re.compile(r"commit\s\d+\x00(tree\s\S+)\n",re.DOTALL).findall(data)[0]
        content = re.compile(r"commit\s\d+\x00(.*?\n)$",re.DOTALL).findall(data)[0]
        
        content.reverse()
        lines = content.split('\n')
        
        commit = {'comment':[] }
        while True:
            if len(lines) == 0:
                break
            line = lines.pop()
            stage = line.split(' ')
            if stage[0] in ['tree','parent']:
                commit[stage[0]] = stage[1]
            elif stage[0] in ['author','committer']:
                """
                name = stage[1:][0]
                email = stage[1:][1]
                timestamp   = stage[1:][2:][0]
                timezone = stage[1:][2:][1]
                # ['luo', '<luo@freeweapon.org>', '1405847288', '+0800']
                """
                commit[stage[0]] = stage[1:]
            else:
                commit['comment'].append(line)
        commit['comment'] = '\n'.join( commit['comment'] )
        return commit
    @staticmethod
    def encode(data):
        "pack commit object data"
        # tree, parent, author, committer, comment
        head = "commit %d\x00"
        content = ""
        content += "tree %s\nparent %s\n" %( data['tree'], data['parent'] )
        content += "author %s\n" %( ' '.join(data['author']) )
        content += "committer %s\n" %( ' '.join(data['committer']) )
        #content += "committer %s\n" %( ' '.join(data['committer']) )
        # TODO: Need Check.
        # coment format is  "\nComment\n"? or "Comment" ?
        content += "%s" %( data['comment'] )
        return content
    
    @staticmethod
    def mkcommit(self):
        "make commit object"
        pass
    @staticmethod
    def mkcomment():
        "make comment text"
        pass
    @staticmethod
    def parent(workspace):
        "Last Commit Object"
        HEAD = open(os.path.join(workspace, '.git', 'HEAD'), 'r').read().split('\n')[0]
        path = os.path.join(workspace, '.git', os.path.split(HEAD.split(': ')[1])[0] )
        refs = os.path.join(path, os.path.split(HEAD.split(': ')[1])[1])
        if os.path.exists(path) == False:
            os.makedirs(path)
        if os.path.isfile(refs) == False:
            open(refs, 'w').write('0'*40 + '\n')
            return '0'*40
        else:
            return open(refs, 'r').read().split('\n')[0]

class Core:
    "Git Command"
    __path__      = os.path.dirname(os.path.abspath(__file__))
    __version__ = '0.1'
    def __init__(self,workspace=None, author=None, committer=None, email=None, sync=False):
        self.workspace = workspace
        self.author = author
        self.committer = committer
        self.email = email
        self.sync = sync           # 是否同步对象至工作目录 ( not git root )
        
        self.commit_tree = ''

    def init(self):
        "初始化仓库"
        return shutil.copytree( self.__path__ + '/template/git', os.path.join(self.workspace,'.git') )
    def create(self):
        "创建仓库"
        os.makedirs( os.path.join(self.workspace,'.git') )
        return shutil.copytree( self.__path__ + '/template/git', os.path.join(self.workspace,'.git'))
    def add(self, path, content, mode=100644):
        "增加文件至提交事务当中"
        sha1 = utils.sha1(content)
        Object(self.workspace).write(sha1, Blob.encode(content) )
        self.commit_tree += Tree.mktree(mode, path, sha1) + "\n"
    def rm(self, path):
        "删除操作"
        # TODO: 从 commit tree 删除 path .
        pass
    def commit(self, comment='default commit message'):
        "向仓库提交操作"
        tree = Tree.encode(self.commit_tree)
        sha1 = utils.sha1(tree)    # now commit tree sha1
        Object(self.workspace).write(sha1, tree)
        # make commit object
        parent = Commit.parent(self.workspace)
        
        commit_time = time.strftime("%s %z") # format: 1405913957 +0800
        commit_author = " ".join( " ".join(self.author, "<%s>" %self.email), commit_time)
        commit_committer = " ".join( " ".join(self.committer, "<%s>" %self.email), commit_time)
        commit_dict = {
                        'tree':sha1,                           # current commit tree sha1 hash.
                        'parent':parent,                  # parent commit tree sha1 hash.
                        'author':commit_author,  # format: MyName <MyEmail@email.net>.
                        'committer':commit_committer,  # like  commit_author.
                        'comment':comment                        # normal.
                        }
        commit_content = Commit.encode(commit_dict)
        
        self.commit_tree = ""  # empty commit_tree buffer.
        # write commit object to file system.
        return Object(self.workspace).write(utils.sha1(commit_content), commit_content)
    def diff(path):
        "diff one blob file. ( diff tree ? IDK. )"
        """
    unified_diff(a, b, fromfile='', tofile='', fromfiledate='', tofiledate='', n=3, lineterm='\n')
    Compare two sequences of lines; generate the delta as a unified diff.
    
    Unified diffs are a compact way of showing line changes and a few
    lines of context.  The number of context lines is set by 'n' which
    defaults to three.
    
    By default, the diff control lines (those with ---, +++, or @@) are
    created with a trailing newline.  This is helpful so that inputs
    created from file.readlines() result in diffs that are suitable for
    file.writelines() since both the inputs and outputs have trailing
    newlines.
    
    For inputs that do not have trailing newlines, set the lineterm
    argument to "" so that the output will be uniformly newline free.
    
    The unidiff format normally has a header for filenames and modification
    times.  Any or all of these may be specified using strings for
    'fromfile', 'tofile', 'fromfiledate', and 'tofiledate'.
    The modification times are normally expressed in the ISO 8601 format.
    
    Example:
    
    >>> for line in unified_diff('one two three four'.split(),
    ...             'zero one tree four'.split(), 'Original', 'Current',
    ...             '2005-01-26 23:30:50', '2010-04-02 10:20:52',
    ...             lineterm=''):
    ...     print line                  # doctest: +NORMALIZE_WHITESPACE
    --- Original        2005-01-26 23:30:50
    +++ Current         2010-04-02 10:20:52
    @@ -1,4 +1,4 @@
    +zero
     one
    -two
    -three
    +tree
     four

        """
        pass

    def log(path):
        "查看日志"
        pass

    def status(path):
        "查看状态"
        pass



class Object:
    "Object Directory Action"
    def __init__(self, workspace):
        self.workspace = os.path.join(workspace, '.git')
    def read(self, sha1):
        "read object from object sha1 hash."
        path = os.path.join(self.workspace, sha1[:2], sha1[2:])
        if os.path.exists(path) and os.path.isfile(path):
            return utils.decompress(open(path, 'rb').read())
        else:
            raise AssertionError("object path not exists.")
    def write(self, sha1, content):
        "write object from object sha1 hash"
        path = os.path.join(self.workspace, sha1[:2] )
        name = path + "/" + sha1[2:]
        if os.path.exists(path) == False:
            os.makedirs(path)
        return open(name, 'wb').write(utils.compress(content))

class Shorcut:
    "some command"
    @staticmethod
    def test():
        "Test Command."
        pass

class Index:
    #WARNING: 索引(index)对象功能并不是一个必需功能
    """
        Git 索引在一些旧文档里面也被称作目录缓存(DIRC, directory cache)
        Git 索引的作用仅在于实现 对索引生成的树对象 和 工作树 进行快速比较
        DOC: https://raw.githubusercontent.com/git/git/master/Documentation/technical/index-format.txt
        DOC: https://github.com/git/git/blob/master/Documentation/technical/api-in-core-index.txt
        
    """
    def __init__(self):
        pass
    @staticmethod
    def decode(data):
        "Unpack Index(Git Directory Cache, DIRC ) Object."
        """
        https://github.com/git/git/blob/master/Documentation/technical/index-format.txt
        Dircache
        """
        """
        print repr(data)
        print ''
        print ''
        """
        if data[:4] != 'DIRC':
            raise AssertionError("无效的 Dircache 文件头: %r" % data[:4])
        header = data[4:12]
        version,num_entries = struct.unpack(">LL",header[:8])
        assert version in (1, 2)  # availbe version are 2, 3 and 4.
        
        entries = {}
        content = data[12:]
        begin = 0
        for i in range(num_entries):
            try:
                icontent = content[begin:]
                # unpack
                ctime = struct.unpack('>LL', icontent[:8] )
                mtime = struct.unpack('>LL', icontent[8:16] )
                
                info = icontent[16:16+46]
                (dev, ino, mode, uid, gid, size, sha1, flags, ) = struct.unpack(">LLLLLL20sH", info)
                name = icontent[16+46:16+46+int(flags)]
                entries[name] = {    'ctime':ctime, 'mtime':mtime, 'dev':dev, 'ino':ino, \
                                                    'uid':uid, 'gid':gid, 'size':size, 'sha1':utils.bin2hex(sha1), 'flags':flags,\
                                                }
                
                real_size = 16+46+int(flags)+8
                #print ''
                #print repr(icontent[real_size:])
                begin += real_size
            except:
                pass
            #print repr(real_size)
            """
            timestamp = content[i*16:16]  # ctime and mtime (8 , 8)
            #(dev, ino, mode, uid, gid, size, sha1, flags, ) = content[(i+1)*16:46] # 4 * 6 + 20 + 2  = 46
            info = content[(i+1)*16:46]
            (dev, ino, mode, uid, gid, size, sha1, flags, ) = struct.unpack(">LLLLLL20sH", info)
            name = content[-2:]
            """

        for x in entries:
            print "\n"*3
            print repr(x)
            print entries[x]
            
        """
        while count < num_entries:
            struct.unpack(">L", data[(12+32*num):4] )[0]
            for num in range(1,num_entries+1):
                entries_sha = binascii.b2a_hex(data[(12+32*num):32])
                print entries_sha
        """
    @staticmethod
    def encode(data):
        "Pack Index(Git Directory Cache, DIRC ) Object."
        pass
    @staticmethod
    def checksum():
        pass


"""

    Old Code.

"""
class Commit_old:
    """
        Git提交对象(commit object)
    """
    def __init__(self, path, blob):
        self.workspace = './blog/.git'
        self.commit_path = path
        self.commit_blob = blob
        tree = self.read_tree()
        path_list = self.path_list(tree)
        if self.commit_path in path_list:
            # 修改
            self.modify()
        else:
            # 新增
            commit_hash = self.add(tree)
            # 记录日志
            parent_hash = self.last_commit_hash
            self.record(parent_hash, commit_hash)
            
    def read_tree(self):
        "read last write tree."
        last_commit_hash = open(self.workspace + '/refs/heads/master').read().replace('\n','')
        self.last_commit_hash = last_commit_hash
        last_commit_obj = GitIO().read(last_commit_hash)
        """
        commit 153\x00tree 5d9efd9cf5ab7b8b5b5dc674a0e00b4f3a8f59a5\nauthor luo <luo@freeweapon.org> 1406727213 +0800\ncommitter luo <luo@freeweapon.org> 1406727213 +0800\n\ninit\n
        """
        tree_hash = re.compile(r"commit\s\d+\x00tree\s(\S+)\n",re.DOTALL).findall(last_commit_obj)[0]
        tree_obj = GitIO().read(tree_hash)
        return GitTree().unpack(tree_obj)
    def path_list(self, tree):
        l = []
        for x in tree:
            l.append(x['path'])
        return l
    def modify(self):
        "修改对象"
        pass
        
    def add(self,tree):
        "新增对象"
        b_obj = GitBlob().pack(self.commit_blob)
        #写入对象
        GitIO().write(b_obj['sha'], b_obj['content'])
        tree.append( {'path':self.commit_path, 'type':'blob', 'mode':'100644', 'sha':b_obj['sha']} )
        tree = GitTree().pack(tree)
        # 写入 树对象
        tree_hash = hashlib.sha1(tree).hexdigest()
        GitIO().write(tree_hash, tree)
        
        sha = self.mk_commit_obj(tree_hash)
        # 替换 refs/heads/master
        open(self.workspace + '/refs/heads/master', 'w').write(sha+'\n')
        return sha
    def mk_commit_obj(self,sha):
        "生成 commit 对象"
        commit_date = time.strftime("%s %z")         # 格式 '1405913957 +0800'
        commit_info = "author luo <luo@freeweapon.org> %s\ncommitter luo <luo@freeweapon.org> %s\n\ncommit message\n" %(commit_date,commit_date)
        obj = "tree %s\n%s" %( sha, commit_info)
        obj = "commit %d\x00%s" %(len(obj), obj)
        commit_hash = hashlib.sha1(obj).hexdigest()
        GitIO().write(commit_hash, obj)
        # TODO: 生成 git log. ( git log 需要该文件 )
        return commit_hash

    def record(self, p_sha, c_sha):
        "add one record"
        committer_name = 'luo'                               # 提交人名称
        committer_email = 'luo@freeweapon.org'               # 提交人电邮
        parent_hash = p_sha                                           # 上次提交对象散列值
        commit_hash = c_sha                                         # 当前提交对象散列值
        
        commit_time = time.strftime("%s %z")         # 格式 '1405913957 +0800'
        comment = "commit message(log)"                      # 提交描述
        # in first commit parent_hash="0"*40
        record = [ parent_hash, commit_hash, committer_name, \
                            '<%s>' %committer_email , commit_time ]
        record = ' '.join(record)
        # 首次提交 commit (initial):  , 其它: commit: 
        record += "\tcommit: %s\n" % comment

        log1 = self.workspace + "/logs/HEAD"
        log2 = self.workspace + "/logs/refs/heads/master"
        open(log1,'a').write(record)
        open(log2,'a').write(record)
        return True



class Tag:
    #WARNING: 因为标签对象功能并不是一个必需功能
    #                       所以暂时不打算实现该功能的打算
    #                       标签对象一般用在 分支/提交对象的引用/签名 上
    #                       DOC: https://github.com/git/git/blob/master/Documentation/git-mktag.txt
    def __init__(self):
        "标签对象"
        pass


                
class Pack:
    #WARNING: 因为pack对象功能并不是一个必需功能
    #                       所以暂时不打算实现该功能的打算
    #                       DOC: https://github.com/git/git/blob/master/Documentation/technical/pack-format.txt
    #                                  https://github.com/git/git/blob/master/Documentation/technical/pack-protocol.txt
    def __init__(self):
        pass


class IO:
    "Git Object Read/Write"
    def __init__(self,workspace =  None):
        if workspace == None:
            self.workspace = './blog/.git'
        else:
            self.workspace = workspace
    def read(self,sha):
        path = self.workspace + '/objects/' + sha[:2] + '/'
        name = sha[2:]
        return zlib.decompress(open(path+name,'r').read())
    def write(self,sha,data):
        path = self.workspace + '/objects/' + sha[:2] + '/'
        name = sha[2:]
        if os.path.exists(path) == False:
            os.makedirs( path )
        return open(path+name,'w').write(zlib.compress(data))

if __name__ == '__main__':
    data = open('index','rb').read()
    #data = utils.decompress(data)
    Index.decode(data)







