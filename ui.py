#!/usr/bin/env python
# encoding=utf-8
from os import system
import curses
import re
import logging,os,sys
import urllib2,json
import locale
locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')
logging.basicConfig(filename = os.path.join(os.getcwd(), 'log.txt'), level = logging.DEBUG)  

class UI():
     def __init__(self,screen):
          self.screen =screen
          self.filename=''
          self.info=''
          self.lines=[]
          self.key=0
          self.show_number=True
          self.line_no=0
          self.col=0
          self.offset=0
          self.height=curses.tigetnum('lines')
          self.width = curses.tigetnum('cols')
          self.word=None
          self.mode='Command'
          self.mark=None
          self.running=True

     def display_status(self,msg):
          self.screen.addstr(self.height-1,10,msg,curses.A_REVERSE)

     def color(self,line_no,start,end='$'):
          if end!='$':text=self.lines[line_no][start:end]
          else:text=self.lines[line_no][start:]
          if text and line_no in self.view_lines:
               self.screen.addstr(line_no-self.view_lines[0],start+self.side_width,text,curses.A_REVERSE)

     def color_selection(self,y1,x1,y2,x2):
          if y1*10000+x1>y2*10000+x2:
               t1,t2=y1,x1
               y1,x1=y2,x2
               y2,x2=t1,t2
          if y1==y2:self.color(y1,x1,x2)
          else:
               self.color(y1,x1)
               for y in range(y1+1,y2):
                    self.color(y,0)
               self.color(y2,0,x2)

     def compute_view_lines(self):
          start=self.line_no-self.offset
          end=start+self.body_height
          if end>len(self.lines):end=len(self.lines)
          self.view_lines=range(start,end)

     def display_line_no(self,i,line_no):
          current_line_no_width=len(str(line_no))
          if self.show_number:
               line_header='%s%s '%(' '*(self.line_no_width-current_line_no_width),line_no)
               self.screen.addstr(i,0,line_header,curses.color_pair(1))

     def display_filter_word(self,word,line_no):
          line=self.lines[line_no]
          if word and line.find(word)>=0:
                    self.color(line_no,line.index(word),line.index(word)+len(word))

     def display_body(self):
          for i in range(0,self.body_height):
               if i<len(self.view_lines):
                    line_no=self.view_lines[i]
                    line=self.lines[line_no]
                    self.display_line_no(i,line_no)
                    self.screen.addstr(i, self.side_width, line)
                    if line and line[0]=='$':
                         self.screen.addstr(i, self.side_width, line,curses.color_pair(2))
                    self.display_filter_word(self.word,line_no)
               else:
                    self.screen.addstr(i, self.side_width, '~')
          if self.mark:
               self.color_selection(self.mark[0],self.mark[1],self.line_no,self.col)

     def display(self):
          try:
               self.screen.clear()
               #screen.border(0)
               self.height=curses.tigetnum('lines')
               self.line_no_width=len(str(len(self.lines))) #compute line no width
               self.side_width=self.line_no_width+1
               self.body_height=self.height-1
               self.compute_view_lines()
               self.display_body()
               line=self.lines[self.line_no]
               if self.col<len(line):char=ord(line[self.col])
               else:char=' '
               msg='(Mode %s)(Line %s,Column %s,offset %s,Char %s)(key %s) (%s) %s '%(self.mode,self.line_no,
                    self.col,self.offset,char,self.key,self.info,self.height)
               self.display_status(msg)
               self.screen.move(self.offset,self.col+self.side_width)
               self.screen.refresh()
          except Exception as e:
               logging.error(str(e))

     def do_insert(self,ch):
          y=self.line_no
          x=self.col
          if ch==27:
               self.mode='Command'
               self.info='esc'
               self.word=None
          elif ch==127:#backspace delete char before cursor
               if x>0:
                    self.lines[y]=self.lines[y][:x-1]+self.lines[y][x:]
                    self.col-=1
          elif ch==10:#enter break line 
               self.info=self.lines[y][x:]
               self.lines.insert(y+1,self.lines[y][x:])
               self.lines[y]=self.lines[y][:x]
               self.do_command(ord('j'))
               self.col=0
          else:
               self.lines[y]=self.lines[y][:x]+chr(ch)+self.lines[y][x:]
               self.col+=1

     def do_command(self,ch):
          #delete cursor char
          if ch==ord('x'):
               y=self.line_no
               x=self.col
               self.lines[y]=self.lines[y][:x]+self.lines[y][x+1:]
          if ch==ord('l'):
               self.col+=1
          if ch==ord('h'):
               if self.col>0:self.col-=1
          if ch==ord('j'):
               if self.line_no<len(self.lines)-1:
                    if self.offset<self.body_height-1:self.offset+=1
                    self.col=min(self.col,len(self.lines[self.line_no]))
                    self.line_no+=1
          if ch==ord('k'):
               if self.line_no>0:
                    self.line_no-=1
                    if self.offset>0:self.offset-=1
          if ch==27:
               self.mode='Command'
               self.info='esc'
               self.word=None
               self.mark=None
          if ch==ord('i'):
               self.mode='Insert'
          if ch==ord('m'):
               self.mark=[self.line_no,self.col]
               self.info='Marked'
          if ch==ord(':') or ch == ord(';'):
               curses.echo()
               input=self.screen.getstr(self.height-1, 1, 60).strip()
               curses.noecho()
               self.info='Command '+input
               if input=='q':self.quit()
               if input=='w':
                    self.save()
                    self.info='file saved'
               elif input=='wq':
                    self.save()
                    self.quit()
               elif re.match('\d+$',input):self.line_no=int(input)
               elif re.match('set\s+number',input):self.show_number=True
               elif re.match('/\w+',input):self.word=input[1:]
               else :self.complex_command(input)
          self.simple_command(ch)
     def simple_command(self,ch):
          pass
     def complex_command(self,word):
          pass
     def save(self):
          with open(self.filename,'w') as f:
               f.write('\n'.join(self.lines))
     def quit(self):
         self.running=False
     def main_loop(self):
          while self.running:
               self.display()
               ch=self.screen.getch()
               self.key=ch
               if self.mode=='Insert':
                    self.do_insert(ch)
               else: self.do_command(ch)
     def reset(self):
          self.line_no=0
          self.col=0
          self.offset=0        

def startup(_UI):
     try:
          screen=curses.initscr()
          curses.noecho()
          curses.start_color()
          curses.use_default_colors()
          curses.init_pair(1, curses.COLOR_GREEN, -1)
          curses.init_pair(2, curses.COLOR_BLUE, -1)
          _UI(screen).main_loop()
     except:
          raise
     finally:
          curses.echo()
          curses.endwin()
