#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Copyright 2010, Hagiwara Takayuki.
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
 
import rest
from auth import oauth
from parser_obj import URLParser

 
class Client(rest.Client):
  auth_class=oauth.OAuth
  sub_client_class=rest.Client
  sign_header=True
  def __init__(self, consumer_key, consumer_secret,req_token_url=None,request_auth_url=None,access_token_url=None):
    self.auth=self.auth_class(consumer_key, consumer_secret)   
    self.sub_client=self.sub_client_class(auth=self.auth)
    self.sub_client.setParser(URLParser.ParserObject())
    self.initiarise()
    if request_auth_url!=None:
        self.request_auth_url=request_auth_url
    if req_token_url!=None:
        self.req_token_url=req_token_url
    if access_token_url!= None:
        self.access_token_url=access_token_url
    self.realm=None

  def setEndpoint(self,endpoint,parser_obj=None,parser_option=None):
      rest.Client.setEndpoint(self, endpoint, parser_obj, parser_option)
      if self.realm != None:
          self.setHeader('realm', self.realm)
  def setRealm(self,realm):
        if self.cursor==-1:
            self.realm=realm
        else:
            self.setHeader('realm', self.realm)
  def prepareLogin(self,callback_url=None,additional_param={},method=rest.POST,sign_header=True):
    '''
    ログイン準備
    '''
   
    if callback_url:
         additional_param['oauth_callback']=callback_url
        
    self.sub_client.setEndpoint(endpoint=self.request_token_url)
    self.sub_client.setQueryParam(additional_param)
    self.sub_client.setMethod(method)
    status,result=self.sub_client.send(clear=True)
    self.last_response = result
    if not status:
      raise Exception('OAuth Request Token Error: ' + str(result))
      
    if not result.has_key('xoauth_request_auth_url'):
        oauth_token=result['oauth_token']
        result['xoauth_request_auth_url']=self.sub_client.getURL(endpoint=self.request_auth_url,queryparam={'oauth_token':oauth_token},headerparam={})
        
    return result
 
 
  def exchangeTokens(self, request_token_secret,oauth_token,oauth_verifier,additional_param={},method=rest.POST):
    self.sub_client.auth.setTokenSecret(request_token_secret)
    self.sub_client.auth.setAccessToken(oauth_token)
    additional_param["oauth_verifier"]=oauth_verifier
    
    self.sub_client.setEndpoint(endpoint=self.exchange_token_url)
    self.sub_client.setQueryParam(additional_param)
    self.sub_client.setMethod(method)
    status,result=self.sub_client.send(clear=True)
    self.last_response = result
    if not status:
      raise Exception('OAuth Request Token Error: ' + str(result))
    
    self.auth.setTokenSecret(result['oauth_token_secret'])
    self.auth.setAccessToken(result['oauth_token'])
    return result
  

  
  