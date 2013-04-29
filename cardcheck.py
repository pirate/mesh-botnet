def cardLuhnChecksumIsValid(card_number):
    """ checks to make sure that a number passes a luhn mod-10 credit card checksum """
    card_number = ''.join(card_number.split())  # remove all whitespace
    sum = 0
    num_digits = len(card_number)
    oddeven = num_digits & 1
    for count in range(0, num_digits):
        digit = int(card_number[count])
        if not (( count & 1 ) ^ oddeven ):
            digit = digit * 2
        if digit > 9:
            digit = digit - 9
        sum = sum + digit
    return ( (sum % 10) == 0 )

def printit(in1, in2):
    print("[+] %s :%s" % (in1.ljust(26), in2))

numbers = [ "378282246310005",
            "4111 1111 1111 1111",
            "5500 0000 0000 0004", 
            "3400 0000 0000 009", 
            "3000 0000 0000 04", 
            "3000 0000 0000 04",
            "6011 0000 0000 0004", 
            "2014 0000 0000 009", 
            "3088 0000 0000 0009",
            "4222222222222",
            "4012888888881881",]

print("[*] -- Starting Credit Card Check -- ")
for number in numbers:
    printit(''.join(number.split()), cardLuhnChecksumIsValid(number))