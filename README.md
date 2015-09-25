**Nick Sweeting 2015 -- MIT License**  
Modular IRC botnet for Mac OS X Orchestration
========
## Install:
1. Download and run [Droplet.app](https://github.com/nikisweeting/python-medusa/raw/master/Droplet.app.zip)
2. Make sure you're connected to the internet and don't have Little Snitch

## Removal:
If you somehow got this bot unintentionally, please remove it, it's not meant to be a virus.

1. Open Terminal.app
2. Run this command: 
```sh
sudo kill `ps -ax|grep -v grep|grep bot.py|head -1|awk '{print $1}'`
```
3. This will kill the bot
4. If you want to remove its runtime files and logs, run the following:

```sh
sudo launchctl unload -w /Library/LaunchDaemons/sys.daemon.connectd.plist
sudo rm -Rf /var/softupdated
sudo rm /Library/LaunchDaemons/sys.daemon.connectd.plist
sudo killall python
```

## Information:  
  
After reading a book on hacking techniques in Python, I was inspired to write a botnet that I could use to help manage my parent's computers remotely when they asked for tech support.  I got a little carried away and implemented several modules that are definitely malicious (such as scanning Skype message logs and chrome history for credit card numbers), and so I decided to open source it and use it as a project for fun instead of a real botnet.  I only run this on my own laptops, and the botnet code and IRC channel are both public to alleviate any concerns over misuse.  That being said, it is open source, so anyone could have copied this code and used it for evil purposes (please don't).  I'm not starting to repurpose this project into node-controllers for my mesh networking experiments over [here](/pirate/mesh-networking).  The goal is to make a botnet that communicates over all network interfaces, forming its own internally routed network if the internet is not available.  It will take advantage of Apple's native MultiPeerConnectivityFramework, as well as raw Wifi sockets, audio, IRC, and WebRTC to form connections through firewalls and across airgaps.  Many concepts and modules in this book are drawn from the book ["Violent Python"](http://books.google.com/books/about/Violent_Python.html?id=2XliiK7FKoEC).

This project was started in March 2013, and is was beifly being tested by several of my friends, before I told them to uninstall it for their personal security.  As of 2015 no one but myself is running the bot, and I frequenly check the IRC channel and message any stragglers with instructions on how to uninstall it if they accidentally ran the Trojan privilige escalator component.

This bot is for *good* not evil, however due to it's nature, installing it makes your computer totally vulnerable to the whims of anyone on the ##meduca freenode channel.  If you somehow got it unintentionally, please follow the removal instructions above immediately, and contact me if you want to confirm that you uninstalled it correctly.
    
   
===


Instructions if you want to contribute:
========
## Install Dependencies:
1. Install [Github.app](http://mac.github.com) for an easy GUI or `brew install git` for the CLI
2. Pick a folder to store your code in
3. Download the source to that folder:

  ```sh
  cd <folder here>
  git clone https://github.com/nikisweeting/violent-python.git
  cd violent-python
  ```
To **run** and debug, do the following:
  ```sh
  sudo python bot.py &
  tail -f bot_v*.log
  ```

## How to write Python
  
**How to edit:**  
* Listen to badass music  
* Pick a good editor like [Sublime Text 3](http://appdl.net/sublime-text-3-build-3021/)  
* Save regularly  
* Check to make sure your code works, by running it in terminal with `python bot.py &`   
* There is awesome documentation on python all over the web: [http://www.python.org/doc/](http://www.python.org/doc/)  

## How to use Git

Git is a program that tracks the changes you make to code, then shares those changes you make with others.  A collection of code in one folder is called a "repository" (repo for short).  Groups of changes are put together to make a "commit".  You can view a history of all the commits made using `git log`.

**Editing locally**   

  1. Edit the code you want to edit, save it, test it, fix it, save it
  2. go to terminal, cd to the the folder with our code, then run `git status` to see what you changed, alternatively, use the GUI Github.app downloadable from github.com 
  3. Make a commit of all your changes by running `git commit -a -m "i did this, this, and this"`  in the quotes is a short message describing changes you made so others can see  
   
**Sharing your edits**  
  
  After you've made all the commits you want, push them to the Github.com  
  
  1. `git remote update` to make sure your local code is up to date  
  2. `git pull` to update your code if it isnt up to date  
  3. `git push origin master` to push your code  
