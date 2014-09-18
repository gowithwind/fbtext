#!/usr/bin/env python
# encoding=utf-8
import re
import logging,os,sys
import urllib2,json
import locale
from ui import UI,startup

logging.basicConfig(filename = os.path.join(os.getcwd(), 'log.txt'), level = logging.DEBUG)  

host='https://www.v2ex.com'
def api_call(api):
     f=urllib2.urlopen(host+api)
     logging.info(host+api)
     return json.loads(f.read())

class V2EX(object):
     def __init__(self):
          self.lines=[]
          self.node='hot'
          self.status='nodes'
          self.nodes=['hot','latest','programmer','python','idev','linux','nodejs','create','design','ideas','share','jobs']
     def get_nodes(self):
          self.status='nodes'
          #self.nodes=api_call('/api/nodes/all.json')
          #lines=[node['title'].encode('utf-8') for node in self.nodes]
          return self.nodes
     def get_topics(self):
          self.status='topics'
          if self.node=='hot':
               self.topics=api_call('/api/topics/hot.json')
          elif self.node=='latest':
               self.topics=api_call('/api/topics/latest.json')
          else:
               self.topics=api_call('/api/topics/show.json?page=0&page_size=40&node_name='+self.node)
          lines= ['%s: %s (%s)'%(t['member']['username'].encode('utf-8'),t['title'].encode('utf-8') ,t['replies'])for t in self.topics ]
          lines.append('')
          lines.append('$ you can type :node to your node! :tech :python :shadowsocks')
          return lines

     def get_topic(self,id):
          self.status='topic'
          self.topic=api_call('/api/topics/show.json?id=%s'%id)[0]
          lines= ['$ '+self.topic['member']['username'].encode('utf-8'),self.topic['title'].encode('utf-8')]
          lines.append('-'*20)
          lines+=self.convert(self.topic['content'])
          lines.append('-'*20)
          self.replies=api_call('/api/replies/show.json?topic_id=%s'%id)
          for r in self.replies:
               lines.append('$ '+r['member']['username'].encode('utf-8'))
               lines+=self.convert(r['content'])
          return lines
     def convert(self,content):
          lines=content.encode('utf-8').split('\n')
          r=[]
          for line in lines:
               i=0
               while i<len(line):
                    r.append(line[i:i+80])
                    i+=80
          return r

import threading
def event(ui,process,args):
     threading.Thread(target = ui.call,args=[ui,process,args]).start()
class V2EXUI(UI):
     def __init__(self,screen):
          UI.__init__(self,screen)
          self.v2ex=V2EX()
          self.lines = self.v2ex.get_nodes()
     def call(self,ui,target,args):
          ui.lines=target(*args)
          ui.info=''
          ui.reset()
          ui.display()
     def simple_command(self,ch):
          if ch==10:#enter
               self.info='.......loading......'
               if self.v2ex.status=='nodes':
                    self.v2ex.node=self.v2ex.nodes[self.line_no]
                    event(self,self.v2ex.get_topics,[])
               else:
                    id=self.v2ex.topics[self.line_no]['id']
                    event(self,self.v2ex.get_topic,[id])
          if ch==ord('q'):
               self.info='.......loading......'
               if self.v2ex.status=='topics':
                    self.lines=self.v2ex.get_nodes()
                    self.info=''
               else:
                    event(self,self.v2ex.get_topics,[])


     def complex_command(self,word):
          self.v2ex.node=input
          self.info=self.v2ex.node
          self.lines=self.v2ex.get_topics()
          self.reset()

startup(V2EXUI)