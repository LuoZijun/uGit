#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os, time, stat
import hashlib,binascii,struct
import zlib, json
# import shutil
import sys

reload(sys)
sys.setdefaultencoding('utf8')

class utils:
    "工具函数"
    @staticmethod
    def sha1(content):
        sha1 = hashlib.sha1()
        try:
            content = content.encode('utf8')
        except:
            pass
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
        try:
            content = content.encode('utf8')
        except:
            pass
        return zlib.compress(content)
    @staticmethod
    def decompress(content):
        return zlib.decompress(content)
    @staticmethod
    def pmode(mode):
        return int(mode, 8)
    @staticmethod
    def fmode(mode):
        return int(oct(mode))
    @staticmethod
    def gmode(path):
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


class Git:
    workspace = ""
    email     = "example@example.com"
    name      = "example"
    stash     = {}

    def __init__(self, workspace="", email="example@example.com", name="example"):
        self.workspace = workspace
        self.email     = email
        self.name      = name
        self.committer = "%s <%s>" % (self.name, self.email)
        print workspace
        assert os.path.exists(self.workspace) #u"目录 \'%s\'不存在。" % self.workspace
        assert os.path.isdir(self.workspace)  #u"路径 \'%s\' 不是有效的目录。" % self.workspace

    def init(self, workspace=None, description=u"Unnamed repository; edit this file 'description' to name the repository."):
        # template       = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template'), 'git')
        root = os.path.join(self.workspace,'.git')
        assert (os.path.exists(root) == False) #u"警告： 检测到该目录 \'%s\' 是一个已存在的Git仓库。" % self.workspace

        config = """
            [core]
            repositoryformatversion = 0
            filemode = true
            bare = false
            logallrefupdates = true
        """
        os.makedirs( root )

        open( os.path.join(root, 'config'), 'w' ).write(config.encode("utf8"))
        open( os.path.join(root, 'HEAD'), 'w' ).write("ref: refs/heads/master".encode("utf8"))
        open( os.path.join(root, 'description'), 'w' ).write(description.encode("utf8"))

        os.makedirs( os.path.join(root,'hooks') )
        os.makedirs( os.path.join(root,'objects') )
        os.makedirs( os.path.join(root,'branches') )
        # os.makedirs( os.path.join(root,'logs') )
        # os.makedirs( os.path.join(root,'info') )

        refs = os.path.join(os.path.join(root,'refs'), 'heads')
        os.makedirs( refs )
        # default commit tree hash: 0000000000000000000000000000000000000000
        open( os.path.join(refs, 'master'), 'w' ).write("0"*40+"\n")
        # return shutil.copytree(template, os.path.join(self.workspace,'.git') )

    def add(self, path, content, mode=100644):
        sha1    = utils.sha1(content)
        
        # OBJECT_MODE = { 
        #     100644:'blob', 
        #     100755:'blob', 
        #     040000:'tree',      # 040000
        #     160000:'commit', 
        #     120000:'blob',      # blob 对象的符号链接
        # }
        self.stash[path] = {
            "mode": mode, 
            "path": path, 
            "sha1": sha1, 
            "content": content
        }
    def _fetch_object(self, sha1):
        path    = os.path.join(self.workspace, ".git", "objects", sha1[:2], sha1[2:] )
        assert (os.path.exists(path) and os.path.isfile(path) )
        return utils.decompress(open(path, "r").read())

    def _write_object(self, sha1, content):
        # ".git/objects/9c/d13d64f479e0126471b5326ae2c9d1b6037c94"
        root    = os.path.join(self.workspace, ".git", "objects", sha1[:2] )
        filename= os.path.join(root, sha1[2:])
        if not os.path.exists(root):
            os.makedirs(root)
        if not os.path.isdir(root):
            os.remove(root)
            os.makedirs(root)
        if os.path.exists(filename):
            return True

        open(filename, 'wb').write(utils.compress(content))
        return True
    def _fecth_last_commit_hash(self):
        head_file = os.path.join(self.workspace, '.git', 'HEAD')
        assert (os.path.exists(head_file) and os.path.isfile(head_file) )
        HEAD = open(head_file, 'r').read().split('\n')[0]
        path = os.path.join(self.workspace, '.git', os.path.split(HEAD.split(': ')[1])[0] )
        assert (os.path.exists(path) and os.path.isdir(path) )

        ref  = os.path.join(path, os.path.split(HEAD.split(': ')[1])[1])
        if not os.path.exists(ref):
            open(ref, "w").write('0'*40 + '\n')
        if not os.path.isfile(ref):
            raise ValueError(u'Git 结构已损坏 ...')
        else:
            sha1 = open(ref, 'r').read().split('\n')[0]

        assert len(sha1) == 40
        return sha1
    def _update_last_commit_hash(self, sha1):
        head_file = os.path.join(self.workspace, '.git', 'HEAD')
        assert (os.path.exists(head_file) and os.path.isfile(head_file) )
        HEAD = open(head_file, 'r').read().split('\n')[0]
        path = os.path.join(self.workspace, '.git', HEAD.split(': ')[1] )
        assert (os.path.exists(path) and os.path.isfile(path) )
        sha1 = open(path, 'w').write(sha1+"\n")
        return sha1
    def _parse_commit(self, sha1):
        """
            Commit Object:
                commit 194\x00
                tree 8805caff2d459b57bc4c08cfdcbe848fd8ab6621\n
                parent 85760890364e7dbc04aceef112cd01dd27827328\n
                author Luo <gnulinux@126.com> 1461727165 +0800\n
                committer Luo <gnulinux@126.com> 1461727165 +0800\n
                \n7\n'
        """
        data = self._fetch_object(sha1)
        assert data[0:7] == "commit "
        data = data[7:]
        size = ""
        while True:
            char = data[0:1]
            data = data[1:]
            if char == '\x00':
                break
            size += char
        size = int(size)
        data = data[0:size]
        data = data.split("\n")

        commit  = {}
        for n in range(4):
            tmp = data[0].split(" ")
            key = tmp[0]
            del tmp[0]
            value = " ".join(tmp)
            commit[key] = value
            del data[0]

        commit['comment'] = "\n".join(data)
        """
            {
                'comment': '\n7\n', 
                'committer': 'Luo <gnulinux@126.com> 1461727165 +0800', 
                'tree': '8805caff2d459b57bc4c08cfdcbe848fd8ab6621', 
                'parent': '85760890364e7dbc04aceef112cd01dd27827328', 
                'author': 'Luo <gnulinux@126.com> 1461727165 +0800'
            }
        """
        return commit
    def _parse_tree(self, sha1):
        data = self._fetch_object(sha1)
        """
            tree 123\x00
            40000 dir\x00\xf9f\x95-~\x07\x15h>\xe95\xd2\x01\xcdJ\xb2'6\xc81
            100644 h\x00\x9c\xd1=d\xf4y\xe0\x12dq\xb52j\xe2\xc9\xd1\xb6\x03|\x94
            100644 test.py\x00;vTC\xd9\xda\xafN\xbb\xa6\xd6\xe6\x94qu\xaf\xd7\xe5\x87\xaf
            100644 w\x00\xe6\x9d\xe2\x9b\xb2\xd1\xd6CK\x8b)\xaewZ\xd8\xc2\xe4\x8cS\x91
        """
        assert data[0:5] == "tree "
        data = data[5:]
        size = ""
        while True:
            char = data[0:1]
            data = data[1:]
            if char == '\x00':
                break
            size += char
        size = int(size)
        data = data[0:size]
        data = data.split("\n")

        def read(d):
            prefix   = ""
            while True:
                char = d[0:1]
                d    = d[1:]
                if char == '\x00':
                    break
                prefix += char
            tmp    = prefix.split(" ")
            record = {
                "mode": int(tmp[0]),
                "path": tmp[1],
                "sha1": binascii.b2a_hex(d[0:20])
            }
            d      = d[20:]
            return (record, d)

        tree = {}
        while True:
            record, d = read(data)
            tree[record['path']] = record
            if d == 0:break
            data = d
        """
            [
                {'path': 'dir', 'sha1': 'f966952d7e0715683ee935d201cd4ab22736c831', 'mode': 40000}, 
                {'path': 'h', 'sha1': '9cd13d64f479e0126471b5326ae2c9d1b6037c94', 'mode': 100644}, 
                {'path': 'test.py', 'sha1': '3b765443d9daaf4ebba6d6e6947175afd7e587af', 'mode': 100644}, 
                {'path': 'w', 'sha1': 'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391', 'mode': 100644}
            ]
        """
        return tree

    def _fetch_tree_hash_by_commit_hash(self, sha1=None):
        if sha1 == None:
            sha1 = self._fecth_last_commit_hash()
        commit    = self._parse_commit(sha1)
        tree_hash = commit['tree']
        return tree_hash
    def commit(self, comment=u'default commit message'):
        # fetch last commit tree
        parent = self._fecth_last_commit_hash()
        if parent != '0'*40:
            tree   = self._parse_tree(self._fetch_tree_hash_by_commit_hash(sha1=parent))
            tree   += self.stash
        else:
            tree  = self.stash

        # Make Tree Object
        records     = ""
        for p in tree:
            blob_elem  = tree[p]
            if "content" in blob_elem:
                # write blob object
                blob       = "blob %d\x00%s" % (len(blob_elem['content']), blob_elem['content'])
                self._write_object(blob_elem['sha1'], blob)
            record  = "%d %s\x00%s" % (blob_elem['mode'], blob_elem['path'], utils.hex2bin(blob_elem['sha1']) )
            records += record
        # new tree
        tree        = "tree %d\x00%s" % (len(records), records)
        # write tree
        tree_sha1   = utils.sha1(tree)
        self._write_object(tree_sha1, tree)

        # make commit object
        ntime       = time.strftime("%s %z") # format: 1405913957 +0800
        commit = {
            "parent": parent,
            "tree"  : tree_sha1,
            "author": "%s <%s> %s" %(self.name, self.email, ntime),
            "committer": "%s <%s> %s" %(self.name, self.email, ntime),
            "comment"  : comment
        }
        content = "tree %s\nparent %s\nauthor %s\ncommitter %s\n%s\n" % (\
            commit['tree'], \
            commit['parent'],\
            commit['author'],\
            commit['committer'],\
            commit['comment']\
        )
        """
            commit 194\x00
            tree 8805caff2d459b57bc4c08cfdcbe848fd8ab6621\n
            parent 85760890364e7dbc04aceef112cd01dd27827328\n
            author Luo <gnulinux@126.com> 1461727165 +0800\n
            committer Luo <gnulinux@126.com> 1461727165 +0800\n
        """
        commit = "commit %d\x00%s" %(len(content), content)
        # write commit object
        commit_sha1 = utils.sha1(commit)
        self._write_object(commit_sha1, commit)
        self._update_last_commit_hash(commit_sha1)
        return commit_sha1



class Index:
    """Git Directory Cache(DIRC, Dircache)
    https://github.com/git/git/blob/master/Documentation/technical/index-format.txt
    """
    @staticmethod
    def decode(path):
        f = open(path, 'r')
        # 4-byte signature, b"DIRC"
        signature = f.read(4)
        # 4-byte version number, 4-byte number of index entries
        version, entrieslen   = struct.unpack(">LL", f.read(8))
        entries               = []
        for n in range(entrieslen):
            entry = {}
            # 4-bit object type, 3-bit unused, 9-bit unix permission
            (ctime, ctime_nanosecond, mtime, mtime_nanosecond, dev, ino, mode, uid, gid, size, ) = struct.unpack(">LLLLLLLLLL", f.read(40))
            entry['ctime'] = ctime + ctime_nanosecond / 1000000000
            entry['mtime'] = mtime + mtime_nanosecond / 1000000000
            entry['dev']   = dev
            entry['ino']   = ino
            entry['mode']  = mode
            entry['uid']   = uid
            entry['gid']   = gid
            entry['size']  = size
            entry['sha1']  = binascii.b2a_hex(struct.unpack(">20s", f.read(20))[0])
            entry['flags'] = struct.unpack(">H", f.read(2))[0]

            # 1-bit assume-valid
            entry["assume-valid"] = bool(entry["flags"] & (0b10000000 << 8))
            # 1-bit extended, must be 0 in version 2
            entry["extended"] = bool(entry["flags"] & (0b01000000 << 8))
            # 2-bit stage (?)
            entry["stage"] = (bool(entry["flags"] & (0b00100000 << 8)), bool(entry["flags"] & (0b00010000 << 8)))
            # 12-bit name length, if the length is less than 0xFFF (else, 0xFFF)
            namelen = entry["flags"] & 0xFFF

            # 62 bytes so far
            entrylen = 62

            if entry["extended"] and (version == 3):
                entry["extra-flags"] = struct.unpack(">H", f.read(2))[0]
                # 1-bit reserved
                entry["reserved"] = bool(entry["extra-flags"] & (0b10000000 << 8))
                # 1-bit skip-worktree
                entry["skip-worktree"] = bool(entry["extra-flags"] & (0b01000000 << 8))
                # 1-bit intent-to-add
                entry["intent-to-add"] = bool(entry["extra-flags"] & (0b00100000 << 8))
                # 13-bits unused
                # used = entry["extra-flags"] & (0b11100000 << 8)
                if not used:
                    raise ValueError(u"Expected unused bits in extra-flags")
                entrylen += 2

            if namelen < 0xFFF:
                entry["name"] = f.read(namelen).decode("utf-8", "replace")
                entrylen += namelen
            else:
                # Do it the hard way
                name = []
                while True:
                    byte = f.read(1)
                    if byte == "\x00":
                        break
                    name.append(byte)
                entry["name"] = b"".join(name).decode("utf-8", "replace")
                entrylen += 1
            padlen = (8 - (entrylen % 8)) or 8
            nuls = f.read(padlen)
            if set(nuls) == {0}:
                raise ValueError(u"padding contained non-NUL")

            entries.append(entry)

        indexlen  = os.fstat(f.fileno()).st_size
        extnumber = 1

        extensions= []
        while f.tell() < (indexlen - 20):
            extension = {}
            extension["extension"] = extnumber
            extension["signature"] = f.read(4).decode("ascii")
            extension["size"]      = struct.unpack(">L", f.read(4) )[0]

            # Seems to exclude the above:
            # "src_offset += 8; src_offset += extsize;"
            extension["data"] = json.dumps(f.read(extension["size"]).decode("iso-8859-1"))
            extnumber += 1

            extensions.append(extension)

        checksum = {}
        checksum["checksum"] = True
        checksum["sha1"] = binascii.b2a_hex(struct.unpack(">20s", f.read(20))[0])

        f.close()

        result = { "entries": entries, "extensions": extensions, "checksum": checksum }

        return result


class Head:
    pass
class Refs:
    pass
class Tag:
    # https://github.com/git/git/blob/master/Documentation/git-mktag.txt
    pass
class Pack:
    # https://github.com/git/git/blob/master/Documentation/technical/pack-format.txt
    # https://github.com/git/git/blob/master/Documentation/technical/pack-protocol.txt
    pass
class Log:
    pass



# Test
def test_ls_files(git_work_tree):
    data   = open(os.path.join(git_work_tree, '.git', 'index') ,'r').read()
    data   = utils.decompress(data)
    result = Index.decode(data)
    for k in result.keys():
        print k
        if type(result[k]) != list:
            print result[k]
        else:
            for elem in result[k]:
                print elem
def test_create_git_repo(path):
    git = Git(workspace=path, email="test@test.com", name="测试")
    git.init()

def test_commit(path):
    git = Git(workspace=path, email="test@test.com", name="测试")
    git.add(path="README.rst", content="测试添加文件(rst)。")
    git.add(path="README.md", content="测试添加文件(md)。")
    print git.commit(comment="init ...")

def test():
    path = os.path.join(os.getcwd(), 'test_repo')
    test_create_git_repo(path)
    test_commit(path)
    test_ls_files(path)

if __name__ == '__main__':
    test()
    







