#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2009/09/14

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
import rest
import oauth
"""
HOW To

client= twitter.Client()
status,result=client.status.update(status='foo').send()

foo/bar params = a,b,c-> client.foo.bar(a='a',b='b',c='c').send()
foo paras=a,b,c  ->client.foo(a='a',b='b',c='c')

"""

API_MAP={}

K="search"
API_MAP[K]={u"pattern":"search"}
K="trends"
API_MAP[K]={u"pattern":"search"}


K="statuses"
API_MAP[K]={u"exception":{u"update":{u"method":rest.POST},
                          u"show":{u"pattern":u"id"},
                          u"destroy":{u"pattern":u"id"},
                          u"user_timeline":{u"pattern":"id"},                        
                          u"retweet":{u"pattern":"id",u"method":rest.POST},
                          u"retweets":{u"method":rest.POST},
                          }
            }

K=u"friendships"
API_MAP[K]={u"pattern":"create_destroy"}

K=u"direct_messages"
API_MAP[K]={u"exception":{u"destroy":{u"pattern":u"id"},
                          u"new":{"method":rest.POST}
                          }
            }


K=u"friends"
API_MAP[K]={u"pattern":"id",
            u"exception":{u"exists":{u"pattern":u"short"},
                          u"ids":{u"pattern":u"ids"}}            
            }

K=u"followers"
API_MAP[K]={u"pattern":"ids"}
K="favorites"
API_MAP[K]={u"pattern":"create_destroy"}
K="blocks"
API_MAP[K]={u"pattern":"create_destroy"}

K="account"
API_MAP[K]={"method":rest.POST,
            u"exception":{u"verify_credentials":{u"method":rest.GET},
                          u"rate_limit_status":{u"method":rest.GET},
                          u"end_session":{u"method":rest.GET}
                          }
            }
K="friendships"
API_MAP[K]={u"method":rest.POST,
            u"pattern":u"id",
            u"exception":{u"show":{u"method":rest.GET}}
            }

K="saved_searches"
API_MAP[K]={u"pattern":"create_destroy"}   
PATTERN_MAP={}
PATTERN_ID={u"path":"http://api.twitter.com/1/%(controller_name)s/%(api_name)s/%(id)s.json",
                   u"key_pathparam":[u"id"]}
PATTERN_MAP["id"]=PATTERN_ID.copy()
PATTERN_MAP["short"]={u"path":"http://api.twitter.com/1/%(controller_name)s/%(api_name)s.json"}
PATTERN_MAP["ids"]={u"path":"http://api.twitter.com/1/%(controller_name)s/%(api_name)s/ids.json"}
PATTERN_CREATE_DESTROY=PATTERN_ID.copy()
PATTERN_CREATE_DESTROY["method"]=rest.POST
PATTERN_MAP["create_destroy"]={u"exception":{u"create":PATTERN_CREATE_DESTROY,
                                           u"destroy":PATTERN_CREATE_DESTROY}
                            }  
PATTERN_MAP["search"]={u"path":u"http://search.twitter.com/%(controller_name)s/(api_name)s.json",
                       u"omit":u"http://search.twitter.com/%(controller_name)s.json"}
                        
class Client(oauth.Client,rest.PretyURL):
    request_token_url="http://api.twitter.com/oauth/request_token"
    request_auth_url="https://api.twitter.com/oauth/authorize"
    exchange_token_url="https://api.twitter.com/oauth/access_token"
    def __init__(self,consumer_key,consumer_secrt,gae=True,debug=False):
        oauth.Client.__init__(self,consumer_key,consumer_secrt)
        
        self.setParser("JSON",{"gae":gae,"debug":debug})
        
        self.default_setting={"path":"http://api.twitter.com/1/%(controller_name)s/%(api_name)s.json",
                              "omit":"http://api.twitter.com/1/%(controller_name)s.json"}
        
        self.map=API_MAP
        self.pattern=PATTERN_MAP
     
                