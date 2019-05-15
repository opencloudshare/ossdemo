# -*- coding: utf-8 -*-

from boto3.session import Session
import boto3

#get connect session from oss for other method
def getS3session():
    access_key = ""
    secret_key = ""
    url = ""
    session = Session(access_key, secret_key)
    s3_client = session.client('s3', endpoint_url=url)
    return s3_client

#remove specified object in specified bucket        
def removeObject(bucket,key):
    log_result = 'delete require accepted'
    try:
        s3_client.delete_object(Bucket=bucket, Key=key)
        log_result = 'delete ok'
        return 1
    except Exception,e:
        log_result = str(e)
        return 0

# list all object belong to a specified bucket
def listObject(bucket):
    resp = s3_client.list_objects(Bucket=bucket)
    return resp

# upload object to a specified bucket and name it as the original file name, then set it readable for public
def uploadObject(bucket):
    log_result = 'upload require accepted'
    # warning,  here file should be transferred by http requests, see detail in demo_front_public.py
    file_metas = self.request.files.get('file', None)  
    if not file_metas:
        log_result = 'error or empty file'
        self.redirect("/list")
        return 0

    for meta in file_metas:
        localtime = time.localtime()
        filename = meta['filename']
        try:
            s3_client.put_object(Bucket=bucket, Key=filename, Body=meta['body'])
            # acl means access control , here the object is set for everyone reading
            s3_client.put_object_acl(Bucket=bucket, Key=filename, ACL='public-read')
            return 1
        except Exception,e:
            log_result = str(e)
            return 0

# for public-read object, get/download is easy enough
