#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2009/09/17


'''

import os


from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from webapi import twitter
from google.appengine.api import memcache

OAUTH_KEY = 'YOUR OAUTH KEY'
OAUTH_SECRET = 'YOUR SECRET KEY'
class InitHandler(webapp.RequestHandler):
  def post(self):
       client = twitter.Client(OAUTH_KEY, OAUTH_SECRET)
       client.setAccessToken(OAUTH_TOKEN)
       client.setTokenSeacret(OAUTH_TOKEN_SECRET)
       client.setRequest("url_fetch_api")
       text=unicode(self.request.get('text'))
       status,result=client.statuses.update(status=text).send()
       if status:
           template_values={'result':u'OK'}
       else:
           template_values={'result':result.content}
       path = os.path.join(os.path.dirname(__file__), 'index.html')
       self.response.out.write(template.render(path, template_values))
  def get(self):
     
      client = twitter.Client(OAUTH_KEY, OAUTH_SECRET)
      result=client.prepareLogin()
      if result:
          self.response.out.write("<a href="+result["xoauth_request_auth_url"]+">twitterでログイン</a>")
          key=result["oauth_token"]
          value=result["oauth_token_secret"]
          memcache.add(key,value,3600)    
      
class  ExchangeHandler(webapp.RequestHandler):
    def get(self):
       oauth_token=self.request.get("oauth_token")
       oauth_verifier=self.request.get("oauth_verifier")
       request_token_secret=memcache.get(oauth_token)
       client=twitter.Client(OAUTH_KEY,OAUTH_SECRET)
       result=client.exchangeTokens(request_token_secret, oauth_token, oauth_verifier)
       if result:
           status,result=client.account.verify_credentials().send()
           if status:
               self.response.out.write(result)
application = webapp.WSGIApplication([('/', InitHandler),('/callback',ExchangeHandler)],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()