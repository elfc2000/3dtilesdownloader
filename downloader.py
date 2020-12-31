#!/usr/bin/env python
# coding:utf-8

import sys 
import traceback
import json
import os
import time 
import getopt
import urllib
from urlparse import urlparse
from urllib   import urlretrieve 
import codecs
import socket
socket.setdefaulttimeout(300)

import gzip
from cStringIO import StringIO



def getContents(contents, n):

    #下载content url里的东西
    print "keys are:" + list_to_str(n.keys())
    if n.has_key('content'):
        print "got key content"
        c = n['content']
        if c.has_key('uri'):
            contents.append(c['uri'])
        else c.has_key('url'):
            contents.append(c['url'])
    else:
        pass #print "no key content in" + json.dumps(n) 


    if n.has_key('children'):
        print "got key children"
        children = n['children']
        for i in range(len(children)):
            c = children[i]
            print "processing: "
            print c
            getContents(contents,c)
    else:
        pass #print "no key children" + json.dumps(n)
    
    print "current contents:" + list_to_str(contents)


    return

def gzdecode(data):  
    #with patch_gzip_for_partial():
    compressedStream = StringIO(data)  
    gziper = gzip.GzipFile(fileobj=compressedStream)    
    data2 = gziper.read()  

    #print len(data)
    return data2 

def autoDownLoad(url,add):
    
    try:
        #a表示地址， b表示返回头
        a, b = urllib.urlretrieve(url, add)
        keyMap = dict(b)
        if 'content-encoding' in keyMap and keyMap['content-encoding'] == 'gzip':
            #print 'need2be decode'
            objectFile = open(add, 'rb+')#以读写模式打开
            data = objectFile.read()
            data = gzdecode(data)
            objectFile.seek(0, 0)
            objectFile.write(data)
            objectFile.close()

        return True
  
    except urllib.ContentTooShortError:
        print 'Network conditions is not good.Reloading.'
        autoDownLoad(url,add)
    except socket.timeout:
        print 'fetch ', url,' exceedTime '
        try:
            urllib.urlretrieve(url,add)
        except:
            print 'reload failed'
    except Exception,e:
        traceback.print_exc()


    return False


def unicode_convert(input):
    if isinstance(input, dict):
        return {unicode_convert(key): unicode_convert(value) for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [unicode_convert(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input

def str_to_list(t_str):
    a_list = []
    for c in str(t_str):
        a_list.append(c)
    return a_list


def list_to_str(a_list):
    return "".join(list(map(str, a_list)))

def process_file(savedir, thefile):
    #解析
    tilesetfile = savedir+"/"+thefile
    tileset = None
    try:
        f = codecs.open(tilesetfile,'r','utf-8')
        s = f.read()
        f.close()
        #print s
        tileset = json.loads(s)
        tileset=unicode_convert(tileset)
        #print tileset
    except Exception as e:
        print e    

    contents = []
    getContents(contents,tileset['root'])


    for i in range(start,len(contents)):
        c = contents[i]

        file = savedir+'/' + c

        dirname =  os.path.dirname(file)
        if not os.path.exists(dirname):
            os.makedirs(dirname) 

        url = baseurl + c + '?' + uu.query
        if autoDownLoad(url,file):
            print  c + ' download success: '  + str(i+1) + '/' + str(len(contents))
            if c.endswith('.json'):
                process_file(savedir, c)
        else:
            print  c + ' download failed: '  + str(i+1) + '/' + str(len(contents))

    return contents
    #下载tilesetjson

if __name__ == "__main__":

    baseurl = ''
    savedir = ''
    start = 0

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hu:d:s:", ["url=","dir=","start="])
    except getopt.GetoptError:
        print 'param error'
        sys.exit(2)


    for opt, arg in opts:
        if opt == '-h':
            print 'python downloader.py  url  dir'
            sys.exit()
        elif opt in ("-u", "--url"):
            baseurl = arg
        elif opt in ("-d", "--dir"):
            savedir = arg
        elif opt in ("-s", "--start"):
            start = int(arg)

    if baseurl == '':
        print 'please input url param'
        sys.exit(2)
    if savedir == '':
        print 'please input dir param'
        sys.exit(2)

    if os.path.isfile(savedir):
        print 'savedir can not be a file ',savedir
        sys.exit(2)

    if not os.path.exists(savedir):
        os.makedirs(savedir)

    

    #print baseurl
    uu = urlparse(baseurl)
    #print uu
    #print uu.path,uu.query
    #解析url

    tileseturl = uu.scheme + "://" + uu.netloc  + uu.path
    if not tileseturl.endswith('tileset.json'):
        tileseturl +=  '/tileset.json'

    baseurl = tileseturl[0:tileseturl.find('tileset.json')]
    #print baseurl
    #sys.exit(2)

    tileseturl += '?' + uu.query


    print tileseturl

    urllib.URLopener.version = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36 SE 2.X MetaSr 1.0'

    tilesetfile = savedir+'/tileset.json'
    if not autoDownLoad(tileseturl,tilesetfile):
        sys.exit(2)
    


    print 'download tileset.json success'

    process_file(savedir, '/tileset.json')

