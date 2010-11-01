#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2009/09/06

Copyright 2009, Hagiwara Takayuki.
All rights reserved.

 Redistribution and use in source and binary forms, with or without
 modification, are permitted provided that the following conditions are
 met:

     * Redistributions of source code must retain the above copyright
 notice, this list of conditions and the following disclaimer.
     * Redistributions in binary form must reproduce the above
 copyright notice, this list of conditions and the following disclaimer
 in the documentation and/or other materials provided with the
 distribution.
     * Neither the name of Google Inc. nor the names of its
 contributors may be used to endorse or promote products derived from
 this software without specific prior written permission.

 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE
'''

from google.appengine.api import urlfetch
class RequestObject:
    callback=None
    failer=None
    def __init__(self,callback=None):
        self.callback=callback
    def send(self,url,method,data,header,unsinc,parser_func):
    
        if unsinc:
            return self.__sendUnSinc(url, method, data,header, parser_func)
        else:
            return self.__sendSinc(url, method, data,header, parser_func)
    def __sendUnSinc(self,url,method,data,header,parser_func):
       rpc = urlfetch.create_rpc()
       rpc.callback = self.__create_callback(rpc,parser_func) 
       if header is None:
           header={}
       if data==None:
           data={}
       urlfetch.make_fetch_call(rpc=rpc,
                                url=url,
                                method=getattr(urlfetch,method),
                                payload=data,
                                headers=header
                                )
       return rpc
    def __create_callback(self,rpc,parser_func):
        callback=self.callback
        def unsinc_callback(rpc):
           r=rpc.get_result()
           if r.status_code==200:
               response=r.content
               result=parser_func(response)
               callback(result)
           elif self.failer:
               self.failer(r)
                      
        return lambda: unsinc_callback(rpc)
    def __sendSinc(self,url,method,data,header,parser_func):
       if header is None:
           header={}
       if data==None:
           data={}
      
       response=urlfetch.fetch(url=url,
                                method=getattr(urlfetch,method),
                                payload=data,
                                headers=header
                                )
       if response.status_code==200:
           
           result=parser_func(response.content)
           return True,result
       
       return False,response
    