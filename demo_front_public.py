# -*- coding: utf-8 -*-
# python demo_front_public.py -log_file_prefix=/opt/ossapp/demo.log

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

import shutil
import os
import json
from boto3.session import Session
import boto3
import uuid
import time
import sys
import re
from urllib import quote

reload(sys)
sys.setdefaultencoding("utf-8")

from tornado.options import define, options
define("port", default=8081, help="run on the given port", type=int)

def gets3session():
    access_key = ""
    secret_key = ""
    url = ""
    session = Session(access_key, secret_key)
    s3_client = session.client('s3', endpoint_url=url)
    return s3_client

class VideoHandler(tornado.web.RequestHandler):
    def get(self):
        Key = self.get_argument('Key')
        Key_quote = quote(Key)
        link = 'http://{host}/test1-bucket1/'.format(host=host)+Key_quote
        self.render("video.html",title=Key_quote,link=link)
        
class FileDelHandler(tornado.web.RequestHandler):
    def get(self):
        Key = self.get_argument('Key')
        log_result = 'accepted'
        try:
            s3_client.delete_object(Bucket="test1-bucket1", Key=Key)
            log_result = 'delete ok'
        except Exception,e:
            log_result = str(e)
        self.redirect("/list")


class FileListHandler(tornado.web.RequestHandler):
    def get(self):
        rj = []
        resp = s3_client.list_objects(Bucket='test1-bucket1')
        if resp.has_key("Contents"):
            for obj in resp['Contents']:
                j = {"Key":"","link":"","type":"","download":"","quote":""}
                if re.match("(.+?)(\.gif|\.jpg|\.jpeg|\.GIF|\.JPG|\.JPEG|\.png)",obj["Key"]):
                    j["type"] = "img"
                elif re.match(".+?\.mp4.*",obj["Key"]):
                    j["type"] = "vdo"
                j["Key"] = obj["Key"]
                j["quote"] = quote(obj["Key"].encode('utf8'))
                j["link"] = 'http://{host}/test1-bucket1/'.format(host=host)+j['quote']
                j["download"] = "'http://{host}/test1-bucket1/{Key}'".format(host=host,Key=j['quote'])
                rj.append(j)

        self.render('index.html',rj=rj)

    def post(self):
        log_result = 'accepted'
        #try:
        file_metas = self.request.files.get('file', None)  
        #except Exception,e:
        #    log_result = str(e)
        #    return log_result
        if not file_metas:
            log_result = 'error or empty file'
            self.redirect("/list")
            return 

        for meta in file_metas:
            localtime = time.localtime()
            filename = meta['filename'] + '-' + "{hour}:{min}:{sec}".format(hour=localtime.tm_hour,min=localtime.tm_min,sec=localtime.tm_sec)
            filename = meta['filename']
            try:
                s3_client.put_object(Bucket="test1-bucket1", Key=filename, Body=meta['body'])
                s3_client.put_object_acl(Bucket="test1-bucket1", Key=filename, ACL='public-read')
            except Exception,e:
                log_result = str(e)
                self.redirect("/list")
                return 

        self.redirect("/list")
        

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [(r"/list", FileListHandler),
                    (r"/del", FileDelHandler),
                    (r"/video", VideoHandler),
        ]
        
        settings = {  
            'template_path':os.path.join(os.path.dirname(__file__), 'templates'),  
            'static_path':os.path.join(os.path.dirname(__file__), 'static'),
            #'static_path':os.path.join(os.path.dirname(__file__), 'static'),  
            'debug':True
        }  
    
        tornado.web.Application.__init__(self, handlers, **settings)


if __name__ == '__main__':
    s3_client = gets3session()
    host = ''
    tornado.options.parse_command_line()
    #logging.debug("debug ...")
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
