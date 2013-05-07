# -*- coding: utf-8 -*-
# based on this awesome dude's code: chevloschelios (http://ubuntuforums.org/showthread.php?t=1493702)
# Nick Sweeting © 2013
# share and share alike blah blah blah but for godsakes dont credit me, i dont want to get arrested if you make a botnet using this (dont)

import socket
import getpass
import random

############ Variables

server = 'irc.freenode.net'                                        # IRC server to connect to
port = 6667                                                        # you really shouldnt need these comments
channel = '#skypeupdate'                                           # duh
admin = 'thesquash'                                                # the nick of the master of bots!

hostname = socket.gethostname()
local_user = getpass.getuser()

nick = '[%s|%s]%s' % (local_user, hostname, random.randint(0, 1000))  # final format will be [username|hostname]rand, boy do i wish IRC allowed nicks with @ characters

############ IRC functions

def scan(match):                                                  # function to scan main channel messages for strings
   if data.find(channel) != -1 and not data.find(nick) != -1:     # checking to make sure its not a private message
      return data.find(match) != -1
   else:
      return False

def privscan(match):                                              # function to scan private messages to the bot for strings
   if data.find('PRIVMSG %s :%s' % (nick, match)) != -1:
      header = data.split("PRIVMSG")[0]
      return header.find(':%s!' % admin) != -1                    # checks to make sure private message is from admin

def privmsg(msg=None, to=admin):                                  # function to send a private message to a user, defaults to master of bots!
   print('PRIVMSG %s :%s\r\n' % (to, msg))
   irc.send ('PRIVMSG %s :%s\r\n' % (to, msg))

def broadcast(msg):                                               # function to send a message to the main channel
   privmsg(msg, channel)

############ Connection

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
irc.connect((server, port))
print irc.recv ( 4096 )
irc.send ('NICK %s\r\n' % nick )
irc.send ('USER %s %s %s :%s\r\n' % (nick, nick, nick, nick))
irc.send ('JOIN %s\r\n' % channel)
irc.send ('PRIVMSG %s :Reporting for duty.\r\n' % admin)

############ The beef of things

quit_status = False
while not quit_status:
   data = irc.recv ( 4096 )
   print("recieved Data")
   if data.find ('PING') != -1:                                     # im warning you, dont touch this bit
      irc.send ('PONG ' + data.split()[1] + '\r\n')

   elif scan('!quit') or privscan('quit'):                          # i suggest prefacing any commands in the main channel with ! so nobody gets hurt
      privmsg('Man down, sarge.')
      irc.send ( 'QUIT\r\n' )
      quit_status = True

   elif scan('cheese'):                                             # or you know, just screw my advice and do it your own way
      broadcast('can I have some cheese please')

   elif privscan('cheese'):                                         # private messages to the bot are obviously commands, so no need for the !
      privmsg('wielder of the great cheese, i worship you')

   elif scan('!echo >'):                                            # more complex examples
      response = data.split(">")[1]
      broadcast('You said %s' % response)

   print data

print("EXIT")