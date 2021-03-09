Mesh-Networking Demonstration: IRC Botnet App (Mac)
========

python-medusa is a demo of simple intrusion and virus building concepts introduced in
the book "Violent Python", to be run on the test bed provided by mesh-networking.
The book is a a funny overview of Python & system security by
a US Military Paratrooper, and I highly recommend checking it out. This is an ideal demonstration
of the mesh-networking project because it needs a large, organic, networked app to show off its true capability.

It would be incredibly difficult to install or get away with using this for malicious purposes
in the real world. It makes no attempts to shield communications or evade filesystem detection in any way because the
mesh-networking hosts are not adversarial and do not have any of the protection measures like SIP or Gatekeeper.

This is not a "real"/malicious botnet that you can use off-the-shelf, it's just an educational example of of a botnet-style program that can run on the [`mesh-networking`](https://github.com/pirate/mesh-networking) network simulation library.

**Book: ["Violent Python"](http://books.google.com/books/about/Violent_Python.html?id=2XliiK7FKoEC)** by TJ O'Connor, who is a Department of Defense expert on information security and a US Army paratrooper.  
**Modules: [Violent-Python-Examples](https://github.com/shadow-box/Violent-Python-Examples)**


## Developer Install:
```bash
git clone https://github.com/pirate/python-medusa.git
cd python-medusa
nano bot.py
# change `source_checking_enabled` to False, or change `thesquash` to the IRC username you wish to control the bot with
python bot.py
# Log into your test IRC channel on irc.freenode.net and type a command (e.g. `!status`)
```

## Uninstall:

1. Open Terminal.app
2. Run this command to kill the bot: 
```sh
sudo kill `ps -ax|grep -v grep|grep bot.py|head -1|awk '{print $1}'`
```
3. Remove its runtime files, logs, and boot persistence with the following:

```sh
sudo launchctl unload -w /Library/LaunchDaemons/sys.daemon.connectd.plist
sudo rm -Rf /var/softupdated
sudo rm /Library/LaunchDaemons/sys.daemon.connectd.plist
sudo kill `ps -ax|grep -v grep|grep bot.py|head -1|awk '{print $1}'`
```

## Information:  
2015 -- MIT License  

After reading a [book](http://books.google.com/books/about/Violent_Python.html?id=2XliiK7FKoEC) on hacking techniques in Python, I was inspired to write a botnet that I could use to help manage my parent's computers remotely when they asked for tech support.  I followed along while reading the book and implemented some of the more fun modules (such as [scanning Skype message logs](https://github.com/pirate/python-medusa/blob/master/modules/skype.py) and network traffic for [credit card numbers](https://github.com/pirate/python-medusa/blob/master/modules/cardcheck.py)), and so I decided to open source it and use it as a project, (and no... of course it's not running on my parents computers, nice try).  I only run this on VMs for my mesh-networking project, and it's highly inneffective in the real world, there are plenty of better open source botnets out there.  That being said, it is open source, and I am not responsible for anyone who has copied the (already freely available in the book) exploit code and used it for evil purposes.

For my [mesh-networking](https://github.com/pirate/mesh-networking) project, this botnet communicates over all network interfaces in a test subnet, forming its own internally routed network by finding the minimum spanning trees between infected nodes.  I can then visualize its growth and use the botnet code to run arbitrary programs for testing on all the network simulated nodes.

Screenshots:  
========
**1. Trojan impersonates Google Chrome and unwitting victim types in their password*:**  
![](http://i.imgur.com/200NfKl.png)  
**2. Bot installs installs itself with boot hook and connects to the C&C IRC channel:**  
![](http://i.imgur.com/FEIRtR3.png)  
**3. Host can be controlled by sending a privmsg to the bot:**  
![](http://i.imgur.com/KJnwaGU.png)  
**4. Bots can be controlled en-masse by sending commands to the whole C&C channel:**
![](http://imgur.com/tu8y9ym.png)

\* I removed the Google Chrome trojan from Github because I don't want script kiddies finding 
this and attempting to use it on people.

Development Guide:  
========

1. Install the [Github App](http://mac.github.com) or [GitUp](http://gitup.co/) for an easy GUI
2. Pick a folder to store your code in
3. Download the source to that folder:

  ```bash
  cd ~/Desktop/
  git clone https://github.com/pirate/python-medusa.git
  cd python-medusa
  ```
4. To run it and debug, do the following:
  ```bash
  sudo ./test.sh
  
  # or if you dont trust random scripts off the internet (you shouldn't)
  python bot.py & tail -f bot_v*.log
  ```

  
* Listen to badass music, you're a real hacker now!  
* Pick a good editor like [Sublime Text 3](http://appdl.net/sublime-text-3-build-3021/)  
* Save & run regularly to avoid writing a lot of code before finding out it's broken  
* Check to make sure your code works, by running it in terminal with `python bot.py &`   
* There is great documentation on Python all over the web: [http://www.python.org/doc/](http://www.python.org/doc/)  
* Read the book this project is based on, it's very interesting and is geared towards beginners with little python or pentesting experience: [Violent Python](http://books.google.com/books/about/Violent_Python.html?id=2XliiK7FKoEC)

## How to use Git

Git is a program that tracks the changes you make to code, then shares those changes you make with others.  A collection of code in one folder is called a "repository" (repo for short).  Groups of changes are put together to make a "commit".  You can view a history of all the commits made using `git log`.

**Editing locally**   

  1. Edit the code you want to edit, save it, test it, fix it, save it
  2. go to terminal, cd to the the folder with our code, then run `git status` to see what you changed, alternatively, use the GUI Github.app downloadable from github.com 
  3. Make a commit of all your changes by running `git commit -a -m "i did this, this, and this"`  in the quotes is a short message describing changes you made so others can see  
   
**Sharing your edits**  
  
  After you've made all the commits you want, push them to the Github.com  
  
  1. `git remote update` to make sure your local code is up to date  
  2. `git pull --rebase` to update your code if it isnt up to date  
  3. `git push origin master` to push your code  
