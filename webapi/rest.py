# -*- coding: utf-8 -*-
"""
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

"""


import urllib


import sys
import base64
import re
import traceback
DEFAULT_PARSER="EtreeParser"
DEFAULT_REQUEST="fetch_urllib"
#モジュールのディレクトリ定義
if __name__ != "__main__":
   path=__name__.split(".")
   path.pop()
   MOD_NAME=".".join(path)+"."         
else:
   MOD_NAME=None
QUERY_SINGLE="single"
QUERY_ADD="add"
KEY_DUPLICATE="duplicate"
GET="GET"
POST="POST"
PUT="PUT"
DELETE="DELETE"

class Client(object):
    def __init__(self,endpoint=None,auth=None):
        self.initiarise()
        if endpoint != None:
           self.setEndpoint(endpoint)
        if auth:
            self.auth=auth
    def setEndpoint(self,endpoint,parser_obj=None,parser_option=None):
       
        """
        リクエストの起点となるURLを設定する
        """
        
        self.endpoint=endpoint
        
        url={"endpoint":endpoint,
             "method":self.method,
             "queryparam":self.queryparam.copy(),
             "headerparam":self.headerparam.copy(),
             "pathparam":self.pathparam.copy()}
        
   
        self.cursor=self.cursor+1
        self.urls.append(url)
        if parser_obj is None:
            
            if not self.parser_init:
                parser_obj=DEFAULT_PARSER
            else:
                
                parser_obj=self.parser_init["name"]
                if self.parser_init.has_key("option"):
                    parser_option=self.parser_init["option"]
             
      
        self.setParser(parser_obj,parser_option)
       
    def initiarise(self):
        self.urls=[]
        self.namespace=None
        self.pathparam={}
        self.queryparam={}
        self.headerparam={}
        self.glue=','
        self.gluemap=None
        self.request=None
        self.dump=False
        self.parser_init={}
        self.unsinc=False
        self.cursor=-1
        self.method=GET
        self.modemap={} 
       
    def setMethod(self,method):
        if self.cursor==-1:
            self.method=method
        else:
            self.urls[self.cursor]["method"]=method 
    def setPathParam(self,key,value=None):
        """
        Twitterのようなパス形式のパラメーターを追加
   
        """
        value=urllib.quote_plus(value.encode('utf-8'))
        self.__addParams('pathparam',key,value,False)
    
    def setQueryParam(self,key,value=None,add=False):
        """
        一般的なクエリーを追加
                追加モード(addがTrue)または複製モードならば、リストへの追加。
        AmazonのWebサービスのような、キーに対して複数の値を許容するような場合に対応
        """
    
        
        self.__addParams('queryparam',key,value,add)
      
    def setHeader(self,key,value=None):
        """
        ヘッダの追加
        """
        self.__addParams("headerparam", key, value,False)
    def setBasicAuth(self, user,pwd):
        """
        基本認証を追加
        """
        str64 = base64.encodestring('%s:%s' % (user,pwd))[:-1]
        self.setHeader("Authorization",u'Basic '+str64)       
    def __addParams(self,name,key,value,add):
        """
        辞書形式のパラメーターを追加

        """
        if self.cursor == -1:
            target=getattr(self,name,None)
        else:
            target=self.urls[self.cursor][name]   
        if target==None:
            target={}
        if value==None or key==None:
            
            if value==None:
                value=key
            for key in value:
                param=value[key]
                target=self.__addPair(target,key,param,add)
        else:
            target=self.__addPair(target,key,value,add)
        if self.cursor == -1:
            setattr(self,name,target)
        else:
            self.urls[self.cursor][name]=target            
    def __addPair(self,target,key,value,add=False):
        """
            キーと値のペアを生成。
            追加モード(addがTrue)ならば、リストへの追加。
      AmazonのWebサービスのような、キーに対して複数の値を許容するような場合に対応
        """
        if not target.has_key(key):
            if add:
                 
                 self.modemap[key]=add
                 target[key]=[value]
                 
            else:
                target[key]=value
        elif add:
            self.modemap[key]=add
            if isinstance(value,list):
               target=target[key]+value
            else:
               target[key]=target[key]+[value]
        else:
             target[key]=value
        return target
    def unsetEndpoint(self,endpoint):
        self.urls.pop(endpoint)
    def send(self,clear=False):
        """
                リクエストする
        """
        ret=[]
        count=0
      
        while  count<len(self.urls):
             args=self.urls[count]
           
             result=self.__sendRequest(endpoint=args["endpoint"],
                                        method=args["method"],
                                        queryparam=args["queryparam"],
                                        headerparam=args["headerparam"],
                                        pathparam=args["pathparam"],
                                        parser_obj=args["parser_obj"])
             ret.append(result)
             count=count+1
        if len(self.urls)==1 and len(ret)==1:
             ret=ret[0]
        
        if clear:
            self.urls=[]
            self.cursor=-1
        return ret
         
    def __sendRequest(self,endpoint,method,queryparam,headerparam,pathparam,parser_obj):
        """
        リクエストする
        """
        
        if method == GET:
           url=self.getURL(endpoint, pathparam, queryparam,headerparam,method)
        else:
           
            url=self.getURL(endpoint, pathparam, {},headerparam,method)
            if hasattr(self, 'auth'):
                self.auth.sign(url,queryparam,headerparam,method) 
            for key in queryparam:
                
               queryparam[key]=queryparam[key].encode("utf-8")
            
            queryparam=urllib.urlencode(queryparam)
        if self.request==None:
            self.setRequest()
        request=self.request
        if parser_obj is None:
            if self.parser_obj==None:
                self.setParser()
            parser_obj=self.parser_obj
        elif isinstance(parser_obj, str):
            self.setParser(parser_obj)
            parser_obj=self.parser_obj
        elif isinstance(parser_obj,dict):
            self.setParser(**paser_obj)
            parser_obj=self.parser_obj
        parser_func=parser_obj.execute
     
        return request.send(url,method,queryparam,headerparam,self.unsinc,parser_func)
               
        """
        if self.parser==None:
            self.parser=self.loadParser("EtreeParser")
        return self.parser(result)
        """
    def getURL(self,endpoint=None,pathparam=None,queryparam=None,headerparam=None,method=GET):
        """
        今のパラメーターを元に実際にアクセスするurlを生成する
    アクセス時の下請け兼キャッシュキー生成
        """
        if self.cursor>-1:
            cursor=self.urls[self.cursor]
            if endpoint is None:
                endpoint=cursor["endpoint"]
               
            if pathparam is None:
                pathparam=cursor["pathparam"]
            if queryparam is None:
                queryparam=cursor["queryparam"]
        
            if headerparam is None:
                headerparam=cursor["headerparam"]
        url=endpoint
       
         
        if pathparam:
             url=url % pathparam
      
        
        
        if method==GET and hasattr(self, 'auth'):
            self.auth.sign(url,queryparam,headerparam,method)
            
        if queryparam:
            querys=[]
            dup={}
            for key,value in queryparam.iteritems():
                          
                if self.modemap.has_key(key):
                    
                    if self.modemap[key] is QUERY_ADD:
                        value=u','.join(value)
                    if self.modemap[key] is KEY_DUPLICATE:
                        dup[key]=value
                        continue
       
                qs=key+"="+urllib.quote_plus(value.encode('utf-8'))
                querys.append(qs)
           
            if dup:
                
                for key,values in dup.iteritems():
                    for value in value:
                        qs=key+"="+urllib.quote_plus(value.encode('utf-8'))
                        querys.append(qs)
            query_string="&".join(querys)
            if url.count('?')==0:
                url=url+'?'
            url=url+query_string
        
        if self.dump:
            print url
        return url
 
    def setParser(self,name=None,options=None):
        """
                パーサーをセット。文字列で与えると自動的にロード。
        """
        if self.cursor ==-1:
            self.parser_init["name"]=name
            self.parser_init["option"]=options
            return
        
            
        if isinstance(name, str):
            
            obj=self.__loadParser(name,options)
        else:
            obj=name
                   
        url=self.urls[self.cursor]
        url["parser_obj"]=obj
        self.urls[self.cursor]=url
        
        
    def __loadParser(self,name,options):
         """
         命名規則に基づいてpaser_objパッケージ下にあるパーサーをロード
         """
         
         name="parser_obj."+name
         mod =self._load(name)
         
         
         if options is None:
             
            ret=mod.ParserObject()
         else:
             ret=mod.ParserObject(**options)
       
         return ret
         
    def setRequest(self,name=DEFAULT_REQUEST,options=None):
        """
                   命名規則に基づいてrequets_objパッケージ下にあるリクエストをロード
        """
        if isinstance(name, str):
           self.request=self.__loadRequst(name, options)
        else:
           self.request=name
      
    def __loadRequst(self,name,options):
         """
         命名規則に基づいてrequest_objパッケージ下にあるリクエストをロード
         """
         name="request_obj."+name
         mod =self._load(name)
         if options is None:
             return mod.RequestObject()
         else:
             return mod.RequestObject(**options)          
    def _load(self,name):

          if MOD_NAME != None:
              name=MOD_NAME+name
          mod = __import__(name,{},())
          components=name.split(".")
          for comp in components[1:]:
              mod = getattr(mod, comp)
         
          return mod

class PretyURL(Client):
    """
    RonR型のURL構成をしているAPI用。 
    　　ｈｔｔｐ：//test.example.com/foo/bar/がfooコントローラーのbarAPIへのアクセスになるタイプのもの。ex　Ｔｗｉｔｔｅｒ
    　　 sendでリクエスト送信。
    　　パスの設定方法
                メンバー変数　default_urlがパスの設定。モジュロでパターン設定して、コンントローラー名.API名(**クエリー)でデータ書き込み
                パスの予約語　コントローラーを表す%(controller_name)sとメソッドを表す%(api_name)s。
    　　　     なおｈｔｔｐ：//test.example.com/foo/bar/?hoge=fugaであれば、 ｈｔｔｐ：//test.example.com/のみで省略可能
   　 　
       ｈｔｔｐ：//test.example.com/foo/bar/?hoge=fugaへのアクセス
   　　　    from webapi.rest improt PrettyURL
       cleint=PrettyURL
       client.default_url="ｈｔｔｐ：//test.example.com/"
       client.foo.bar(hoge="fuga")
       result=client.send()
    
       ｈｔｔｐ：//test.example.com/foo/ｂａｒ.json?hoge=fugaへのアクセス
   
       　　　 from webapi.rest improt PrettyURL
       cleint=PrettyURL
       client.default_url="ｈｔｔｐ：//test.example.com/%(controller_name)s/"
       client.foo.bar(hoge="fuga")
       result=client.send()
      
         
        設定用のハッシュ
            
            　コントローラー名をキーとしたハッシュを使って、さらに複雑な設定が可能。
    　　　　           
            path このコントローラーにアクセスする場合のURL設定          
            method GET以外のメソッドでアクセスする場合に設定
            key_pathparam　パスに設定するキーのリスト　ex:[id]
             pattern　共通するパターン(後述)  　　　　　　　　　　　　　
                                                   
            omit　アクセスするメソッドが省略された場合に。この場合、コントローラー名をメンバ関数のようにアクセス可能
            extra　例外的な処理をするメソッド
          hogeコントローラーにアクセスする場合はｈｔｔｐ：//test.example.com/foo/ｂａｒ.json?hoge=fuga形式。
                    ただし、 ｈｔｔｐ：//test.example.com/foo.json?hoge=fugaがありうる場合
   
       　　　         from webapi.rest improt PrettyURL
            client=PrettyURL()
            client.map={"hoge":{"path":"ｈｔｔｐ：//test.example.com/%(controller_name)s/(api_name)s.json"
                                "omit":"ｈｔｔｐ：//test.example.com/%(controller_name)s.json"}
                        }
           
           client.foo.bar(hoge="fuga")
           result=client.send()#ｈｔｔｐ：//test.example.com/foo/ｂａｒ.json?hoge=fuga
           
           client.foo(hoge="fuga")#ｈｔｔｐ：//test.example.com/foo.json?hoge=fuga
           
        　　　
        　　　　　メソッド単位の例外
                
                        キー"exception"に設定を書くことでメソッド単位で「異なるケース」を設定することができる
             　　　　　キー"exception"にはメソッド名をキーとして設定          
           　　　　　　
           　　　　　　path このメソッドに特有のURL設定          
            method このメソッドにGET以外のアクセスメソッドでアクセスする場合に設定
            key_pathparam　パスに設定するキーのリスト　ex:[id]
      　　　　　　     omit　パスに設定するキーが省略された場合
            pattern　共通するパターン(後述)       
    　　　　　　　hogeコントローラーにアクセスする場合はｈｔｔｐ：//test.example.com/foo/ｂａｒ.json?hoge=fuga形式。
                    ただし、 showメソッドにはｈｔｔｐ：//test.example.com/foo/hoe/{id}.jsonでアクセス
        　　　　　
   
       　　　         from webapi.rest improt PrettyURL
            client=PrettyURL()
            client.map={"hoge":{"path":"ｈｔｔｐ：//test.example.com/%(controller_name)s/(api_name)s.json"
                                "omit":"ｈｔｔｐ：//test.example.com/%(controller_name)s.json"}
                        }
           
           client.foo.bar(hoge="fuga")
           result=client.send()#ｈｔｔｐ：//test.example.com/foo/ｂａｒ.json?hoge=fuga
           
           client.foo(hoge="fuga")#ｈｔｔｐ：//test.example.com/foo.json?hoge=fuga       
        
　　"""
    default_url=""
    default_setting={}
    map={}#設定用のハッシュをつける
    pattern={}#共通パターンを設定
    def __getattr__(self,controller_name):
        m=None
        api={}
        if self.default_setting:
            api=self.default_setting.copy()
        api_name=None
        origin={}
        path_param=[]
       
        if self.map.has_key(controller_name):
           
           origin=self.map[controller_name]
           api.update(origin.copy())
        
        self.checkPattern(api)               
        if not api.has_key("path"):
            api["path"]=self.default_url
        return self._returnClass(api, controller_name)
    def checkPattern(self,target):
        if target.has_key("pattern"):
            
            url_pattern=target["pattern"]
            if self.pattern.has_key(url_pattern):
                origin=self.pattern[url_pattern]
                target.update(origin.copy()) 
    def _returnClass(self,api,controller_name):
        target=self
        class CallbackClass:
            def setPath(self,path,api_name=None):
                use_controller_name=path.count('%(controller_name)s')
                use_api_name=path.count('%(api_name)s')
                if use_controller_name == 0 and use_api_name == 0:
                  
                   if re.match(r'/$', path) is None:
                       path=path+"/"
                   path=path+controller_name+"/"+attr_name+"/"
                   target.setEndpoint(path)
                else:
                  
                   target.setEndpoint(path)
                   if use_controller_name >0:
                       target.setPathParam("controller_name",controller_name)
                   if use_api_name >0:
                       target.setPathParam("api_name",api_name)
  
            def setParam(self,setting,params):
               
                if setting.has_key("key_pathparam"):
                   for key in api["key_pathparam"]:
                       target.setPathParam(key,params[key])
                       del params[key]
                if params:
                    
                    for key in params:
                         value=params[key]
                         
                         
                         target.setQueryParam(key,value)
                if setting.has_key("method"):
                       
                       target.setMethod(setting["method"])
            def __call__(self,**kwargs):
                if api.has_key("omit"):
                    path=api["omit"]
                
                self.setPath(path)
                self.setParam(api,kwargs)  
                return target
               
            def __getattr__(self,api_name):
                target_api=api           
                
                if target_api.has_key("exception"):
                    if target_api["exception"].has_key(api_name):
                       target.checkPattern(target_api["exception"][api_name])
                       target_api.update(target_api["exception"][api_name])
                  
               
                temp_path=target_api["path"]        
                myobj=self
                
                def callback(**kwargs):

                    target_path=temp_path
                    
                    if target_api.has_key("key_pathparam"):
                        for key in target_api["key_pathparam"]:
                            if not kwargs.has_key(key):
                                target_path=target_api["omit"]
                                break
                    
                    myobj.setPath(target_path,api_name)
                    myobj.setParam(target_api,kwargs)
                    return target                     
                return callback
        ret=CallbackClass()
        return ret
                                           
                    
                    









