**Nick Sweeting 2013 -- MIT License**  
Violent Python: Nefarious python targeted towards Mac OS X
========

## Install:
1. Install Github http://mac.github.com
2. Pick a folder to store your code in

```
cd <folder here>
git clone https://github.com/nikisweeting/violent-python.git
cd violent-python
nano readme.md
```
## How to write Python
  
**How to edit:**  
* Pick a good editor like Sublime Text 3 (http://appdl.net/sublime-text-3-build-3021/)  
* Save regularly  
* Check to make sure your code works, by running it in terminal with `$ python filename.py`   
* There is awesome documentation on python all over the web: [http://www.python.org/doc/](http://www.python.org/doc/)  
* Book on hacking using python that this project is based off [http://books.google.com/books/about/Violent_Python.html?id=2XliiK7FKoEC](http://books.google.com/books/about/Violent_Python.html?id=2XliiK7FKoEC), ask me for a copy

## How to use Github

Github is a program that lets you track the changes you make to code, then share those changes you make with others.  A collection of code in one folder is called a "repository" (repo for short).  Groups of changes are put together to make a "commit".  You can view a history of all the commits made using `git log`.

**Editing locally**   

  1. Edit the code you want to edit, save it, test it, fix it, save it
  2. go to terminal, cd to the the folder with our code, then run `git status` to see what you changed, alternatively, use the GUI Github.app  
  3. Make a commit of all your changes by running `git commit -a -m "i did this, this, and this"`  whats in the quotes is a short messages describing changes you made so others can see  
   
**Sharing your edits**  
  
  After you've made all the commits you want, push them to the Github.com  
  
  1. `git remote update` to make sure your local code is up to date  
  2. `git pull` to update your code if it isnt up to date  
  3. `git push origin master` to push your code  
