# -*- coding: utf-8 -*-

def addition(in1):
	return str(int(in1.split("+")[0])+int(in1.split("+")[1]))

def echo(text):
	return text

source_checking_enabled = True
allowed_sources = ["thesquash"]

channel = "#skypeupdate"
nick = "thesquashbot"


commands = {
"add "  			: {"do": addition, 	"type":"public", "help":"lists the version"},
"echo " 			: {"do": echo, 		"type":"public", "help":"lists the version"},
"$" 				: {"do": echo, 		"type":"public", "help":"lists the version"},
}


def parse(data):
	if data.find("PRIVMSG") != -1:
		from_nick 	= data.split("PRIVMSG ",1)[0].split("!")[0][1:] # who sent the PRIVMSG
		to 			= data.split("PRIVMSG ",1)[1].split(" :",1)[0]	# where did they send it
		text 		= data.split("PRIVMSG ",1)[1].split(" :",1)[1]	# what did it contain
		if source_checking_enabled and from_nick not in allowed_sources:
			return (False,)											# break and return nothing if message is invalid
		if to == channel:
			return_to = "public"
		elif to != channel:
			return_to = from_nick
		for command, directive in commands.iteritems():				# iterate through the list of possible commands to find a match
			if text[:len(command)].find(command) != -1:				# strict length checking
				arguments = text[len(command):]						# arguments are everything after the command keyword
				return 	(directive["do"],arguments,return_to)		# return the function to run, the arguments to pass it, and where the output should go

	elif data.find("PING :",0,6) != -1:								# was it just a ping?
		from_srv = data.split("PING :")[1] 							# the source of the PING
		return ("PING", from_srv)
	return (False,)													# break and return nothing if message is invalid




data = ":thesquash!~nick@116.231.75.214 PRIVMSG #skypeupdate :'´´ç≈$ƒ∑´ƒƒ"
#data = "PING :wright.freenode.net"

valid_parsed_input = parse(data)
if not valid_parsed_input[0]:
	pass
elif valid_parsed_input[0] == "PING":	
	print "Pong",valid_parsed_input[1]
else:
	output = valid_parsed_input[0](valid_parsed_input[1])
	print "return output: "+output+" to: "+valid_parsed_input[2]

# if data.find("echo >") != -1:
# 	text = data.split(">")[1]
# 	function = 'echo'
# 	params = {'text':text}
# 	print commands[function]["do"](**params)

# data = "add >2+2"

# if data.find("add >") != -1:
# 	math = data.split(">")[1]
# 	function = 'add'
# 	params = {'in1':math.split("+")[0],'in2':math.split("+")[1]}
# 	print commands[function]["do"](**params)

# data = "sub >21-2"

# if data.find("sub >") != -1:
# 	math = data.split(">")[1]
# 	params = {'in1':int(math.split("-")[0]),'in2':-int(math.split("-")[1])}
# 	print commands['add']["do"](**params)

# for key, line in commands.iteritems():
# 	print(key.ljust(20)+"-- "+line["help"])