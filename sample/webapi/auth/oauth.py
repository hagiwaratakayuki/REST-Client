#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2010/04/02


'''
import hmac
import urllib
from hashlib import sha1
from random import getrandbits
from time import time
from google.appengine.api import urlfetch 
 
class OAuth(object):
  version="1.0"
  encode='utf-8'
  sign_header=True
  def __init__(self, consumer_key, consumer_secret, access_token='', token_secret='',sign_header=True):
    self._consumer_key =consumer_key
    self._consumer_secret = consumer_secret
    self._access_token = access_token
    self._token_secret = token_secret
    self.sign_header=sign_header
    

  def setAccessToken(self,token):
      self._access_token=token
  def setTokenSecret(self,token_secret):
      self._token_secret=token_secret
  def sign(self,url,query,header,method):
     params=self.addSignature(url, query.copy(), method)
     if self.sign_header:    

         query=[]
         for key in params:
             value=key+'="'+self._quote(params[key])+'"'
             query.append(value)
         Authorization='OAuth '+','.join(query)
         header['Authorization']=Authorization  
     else:
         query.update(params) 
         
     return query,header
  
  def addSignature(self, url, params, method='GET'):
    oauth_params = {u'oauth_consumer_key': self._consumer_key,
                    u'oauth_signature_method': 'HMAC-SHA1',
                    u'oauth_timestamp': int(time()),
                    u'oauth_nonce': getrandbits(64),
                    u'oauth_version': self.version}
    if self._access_token!= None:
      oauth_params['oauth_token'] = self._access_token
       
    params.update(oauth_params)
    message=method+'&'+self._quote(url)+'&'
    signature_params = []
    for key in sorted(params):
      kv=self._quote(key) + self._quote("=")  + self._quote(params[key])
      signature_params.append(kv) 
    message+=self._quote("&").join(signature_params)
    hash_key = self._quote(self._consumer_secret) + '&' + self._quote(self._token_secret)
 
    digest = hmac.new(hash_key, message, sha1).digest()
    params['oauth_signature'] = digest.encode('base64')[:-1]
 
    return params
 
 
  def _quote(self, query):
    return urllib.quote(unicode(query).encode(self.encode), '')
 
 
  
