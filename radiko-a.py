#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request, urllib.error, urllib.parse
import os, sys, datetime, argparse, re
import subprocess
import base64
import shlex
import logging
from sys import argv

auth_token = ""
auth_key = "bcd151073c03b352e1ef2fd66c32209da9ca0afa"
key_offset = 0

"""
"         channel_name list in Tokyo"
"           TBS Radio: TBS"
"           Nippon Cultural Broadcasting: QRR"
"           Nippon Broadcasting: LFR"
"           Radio Nippon: JORF"
"           Inter FM: INT"
"           Tokyo FM: FMT"
"           J-WAVE: FMJ"
"           bayfm 78.0MHz: BAYFM78"
"           NACK5: NACK5"
"           FM yokohama 84.7: YFM"
"""

def auth1():
    url = "https://radiko.jp/v2/api/auth1"
    headers = {}
    auth_response = {}

    headers = {
        "User-Agent": "curl/7.56.1",
        "Accept": "*/*",
        "X-Radiko-App":"pc_html5" ,
        "X-Radiko-App-Version":"0.0.1" ,
        "X-Radiko-User":"dummy_user" ,
        "X-Radiko-Device":"pc" 
    }
    req = urllib.request.Request( url, None, headers  )
    res = urllib.request.urlopen(req)
    auth_response["body"] = res.read()
    auth_response["headers"] = res.info()
    #print('auth_response='+str( auth_response))
    #print('auth_response_headers='+str( auth_response['headers']))
    return auth_response

def get_partial_key(auth_response):
    authtoken = auth_response["headers"]["x-radiko-authtoken"]
    offset    = auth_response["headers"]["x-radiko-keyoffset"]
    length    = auth_response["headers"]["x-radiko-keylength"]
    offset = int(offset)
    length = int(length)
    print('pkey_offset='+str(offset)+' length='+str(length))
    #partialkey= auth_key[offset:offset+length]
    partialkey= auth_key[offset:offset+length]
    print('pkey='+partialkey)
    partialkey = base64.b64encode(partialkey.encode())
    print('pkeyB64='+ str(partialkey))
    partialkey = partialkey.decode()
    print('pkeyB64d='+ str(partialkey))

    return [partialkey,authtoken]

def auth2( partialkey, auth_token ) :
    url = "https://radiko.jp/v2/api/auth2"
    headers =  {
        "X-Radiko-AuthToken": auth_token,
        "pragma": "no-cache" ,
        "X-Radiko-Partialkey": partialkey,
        #"X-Radiko-User": "dummy_user",
        "X-Radiko-User": "test-stream" , 
        "X-Radiko-Device": 'pc'
    }
    print('auth2 headers='+str(headers))
    req  = urllib.request.Request( url, None, headers  )
    #print('req='+str(req))
    res  = urllib.request.urlopen(req)
    txt = res.read()
    area = txt.decode()
    print(txt)
    return area


def gen_temp_chunk_m3u8_url( url, auth_token ):
    headers =  {
        "X-Radiko-AuthToken": auth_token,
    }
    req  = urllib.request.Request( url, None, headers  )
    res  = urllib.request.urlopen(req)
    body = res.read().decode()
    #print('gen_temp body='+ body)
    #lines = re.findall( '^https?://.+m3u8$' , body, flags=(re.MULTILINE) )
    lines = re.findall( 'http://.+m3u8' , body)
    print('gen_temp lines='+ str(lines))
    #return 'http://c-radiko.smartstream.ne.jp/FMT/_definst_/simul-stream.stream/playlist.m3u8'
    return lines[0]


if len(argv) < 2:
    print('usage : {} Station'.format(argv[0]))
    exit(0)

res = auth1()
ret = get_partial_key(res)
token = ret[1]
partialkey = str(ret[0])
print('ret[1](token)='+str(token)+' ret[0](partkey)='+partialkey)

area=auth2( partialkey, token )
print('area='+ str(area))

#url = 'http://f-radiko.smartstream.ne.jp/{argv[1]}/_definst_/simul-stream.stream/playlist.m3u8'
#url=  "http://radiko.jp/v2/station/stream_smh_multi/FMT.xml"
url=  'http://radiko.jp/v2/station/stream_smh_multi/'+argv[1]+'.xml'

print('url='+url)

m3u8 = gen_temp_chunk_m3u8_url( url ,token)
print('m3u8='+m3u8)

#cmd="ffplay  -headers 'X-Radiko-Authtoken:"+token+ "' -i " + m3u8

#cmd="mpv --really-quiet --no-cache --http-header-fields='X-Radiko-Authtoken: {0}' --end='{1}' '{2}'".format(token, argv[2], m3u8) 

cmd="mpv  --no-cache --http-header-fields='X-Radiko-Authtoken: {0}'  '{1}'".format(token,  m3u8) 

print('cmd='+cmd)

#os.system( "ffplay -nodisp -loglevel quiet -headers 'X-Radiko-Authtoken:{token}' -i '{m3u8}'")

os.system(cmd)

### EOF
