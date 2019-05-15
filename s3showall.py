# coding: utf-8

from boto3.session import Session
import boto3

import uuid
import re

access_key = ""
secret_key = ""
url = "" 
session = Session(access_key, secret_key)
s3_client = session.client('s3', endpoint_url=url)

for bucket in s3_client.list_buckets()['Buckets']:
    print bucket['Name']
    resp = s3_client.list_objects(Bucket=bucket['Name'])
    try:
        for obj in resp['Contents']:
            print '-',obj['Key']
	    if re.match("(.+?)(\.gif|\.jpg|\.jpeg|\.GIF|\.JPG|\.JPEG|\.png)",obj["Key"]):
		print "  (image)"
	    else:
		print "  (not image)"
            resp2 = s3_client.get_object_acl(Bucket=bucket['Name'], Key=obj['Key'])
            print '  -[Grants]',resp2['Grants']
            print '  -[Owner]',resp2['Owner']

    except Exception,e:
        print '! no object in this bucket'

