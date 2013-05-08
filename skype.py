

import sqlite3
def printProfile(skypeDB):
	conn = sqlite3.connect(skypeDB)
	c = conn.cursor()
	c.execute("SELECT fullname, skypename, city, country, \
		datetime(profile_timestamp,'unixepoch') FROM Accounts;") 
	for row in c:
		yield '[*] -- Found Account --'
		yield '[+] User: '+str(row[0])
		yield '[+] Skype Username: '+str(row[1])
		yield '[+] Location: '+str(row[2])+','+str(row[3])
		yield '[+] Profile Date: '+str(row[4])

def printContacts(skypeDB):
	conn = sqlite3.connect(skypeDB)
	c = conn.cursor()
	c.execute("SELECT displayname, skypename, city, country,\
		phone_mobile, birthday FROM Contacts;") 
	for row in c:
		print('\n[*] -- Found Contact --')
		print('[+] User                : %s' % row[0])
		print('[+] Skype Username      : %s' % row[1])

		if str(row[2]) != '' and str(row[2]) != 'None':
			print('[+] Location            : %s,%s' % (row[2],row[3]))

		if str(row[4]) != 'None':
			print('[+] Mobile Number       : %s' % row[4])

		if str(row[5]) != 'None':
			print('[+] Birthday            : %s' % row[5])


def printCallLog(skypeDB):
	conn = sqlite3.connect(skypeDB)
	c = conn.cursor()
	c.execute("SELECT * FROM calls, conversations;")

	print('\n[*] -- Found Calls --')
	for row in c:
		print('[+] Time: %s' % row[0])
		print('[+] Partner %s' % row[1])
		
def printMessages(skypeDB):
	conn = sqlite3.connect(skypeDB)
	c = conn.cursor()
	c.execute("SELECT datetime(timestamp,'unixepoch'), \
		dialog_partner, author, body_xml FROM Messages;")
	messages = ['BEGIN'];
	print '\n[*] -- Found Messages --'
	print '[+] Saving into messages array'
	for row in c:
		try:
			if 'partlist' not in str(row[3]):
				if str(row[1]) != str(row[2]):
					msgDirection = 'To ' + str(row[1]) + ': '
				else:
					msgDirection = 'From ' + str(row[2]) + ': '

				messages.append('Time: ' + str(row[0]) + ' ' \
					+ msgDirection + str(row[3]))
		except:
			pass

def purgeMessages(skypeDB):
	conn = sqlite3.connect(skypeDB)
	c = conn.cursor()
	c.execute("SELECT datetime(timestamp,'unixepoch'), dialog_partner, author, body_xml FROM Messages WHERE dialog_partner = '<SKYPE-PARTNER>'")
	c.execute("DELETE FROM messages WHERE skypename = '<SKYPE-PARTNER>'")


def main():
	skypeDB = "main.db" 
	printProfile(skypeDB)
	printContacts(skypeDB)
	printCallLog(skypeDB)
	printMessages(skypeDB)
if __name__ == "__main__": 
	main()