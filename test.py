import string

def help():
    print "help"

def identify():
    print "identifying..."

def quit():
    print "quitting."

public_commands = {
"!help":help,
"!identify":identify, 
"!quit":quit,
}

private_commands = {
"help":help,
"identify":identify, 
"quit":quit,
}

data = ["!help do","help","identify","!identify"]

for line in data:
    # lookup the function to call for each line
    try:
    	functionToCall = public_commands[line]
    except:
    	try:
    		functionToCall = private_commands[line]
    	except:
    		functionToCall = exit

    # and call it
    functionToCall()