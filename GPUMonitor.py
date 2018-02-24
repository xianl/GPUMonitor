#! /usr/bin/env python
# -*- coding:utf-8 -*-

import urllib
import urllib2
import time
import json
import random
import hmac
import hashlib
from pynvml import *

class NwsSender:
        def init(self):
                self.url='http://receiver.monitor.tencentyun.com:8080/v2/index.php'
                self.timeout=10
        def send_data(self,data):
                try:
                        req=urllib2.Request(url=self.url+ "?" + data)
                        timeout=self.timeout
                        http_ret=urllib2.urlopen(req, timeout = timeout)
                        response=http_ret.read()
                        try:
                                json_resp=json.loads(response)
                                retcode=int(json_resp["code"])
                                if retcode!=0:
                                        print "send error,retcode:%d,msg:%s,data:%s" % (retcode,json_resp['message'],data)
                                else:
                                        print "send succ,data:%s" % response
                        except ValueError,e:
                                print 'value error:%s' % response
                except urllib2.URLError,e:
                        print "send error"+str(e)+data

def getGpuUtilization(handle):
    try:
        util = nvmlDeviceGetUtilizationRates(handle)
        gpu_util = int(util.gpu)
    except NVMLError as err:
        error = handleError(err)
        gpu_util = error
    return gpu_util


def main():
        secretId="xxxxxxxxxxxxxx"  #change to your own secret_id
        secretKey="xxxxxxxxxxxxxx" #change to your own secret_key
        region='gz'
        data={
		"Action":"PutMonitorData",
                "SecretId":secretId,
                "Namespace":"gputest",
                "Region":region,
                }
        sender=NwsSender()
        sender.init()

        nvmlInit()
        deviceCount = nvmlDeviceGetCount()

        while True:
                ts=int(time.time())
                nonce=random.randint(10000,100000)
                text="GETreceiver.monitor.tencentyun.com/v2/index.php?Action=PutMonitorData&Nonce=%d&Region=%s&SecretId=%s&Timestamp=%d" % (nonce,region,secretId,ts)
                data['Timestamp']=ts
                data['Nonce']=nonce
                data['Signature']=hmac.new(secretKey,text,hashlib.sha1).digest().encode("base64").rstrip('\n')

                for i in range(deviceCount):

                        handle = nvmlDeviceGetHandleByIndex(i)
                        gpu_util = getGpuUtilization(handle)
                        Data=[
                             {
                              "dimensions": {"gpu_id": str(i) ,"server_name": 'testserver'},
                              "metricName": "gpu_util",
                              "value": gpu_util,
                              }
                              ]
                        data["Data"]=json.dumps(Data)
                        xx = urllib.urlencode(data)
                        sender.send_data(xx)

                time.sleep(20)

if __name__=='__main__':
        main()
