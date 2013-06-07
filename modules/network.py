# -*- coding: utf-8 -*-
 
def portscan(host, max_port=10000):
    print 'Starting Singlethread Scan.'
    benchmark = time.time()
    remoteServerIP  = socket.gethostbyname(host)

    ports = []
    for port in range(1,max_port):  
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if s.connect_ex((remoteServerIP, port)) == 0:
            ports.append(port)
            print port
        s.close()

    print ports
    print 'Finished Scan.'
    print time.time() - benchmark


def multiportscan(host, max_port=10000):
    print 'Starting Multithread Scan.'
    benchmark = time.time()
    remoteServerIP  = socket.gethostbyname(host)
    ports = []
    def check_port(ip,port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if s.connect_ex((ip,port)) == 0:
            ports.append(port)
            print port
        s.close()

    threads = []
    increment = 0
    for port in range(1,max_port):
        if increment < 200:
            t = threading.Thread(target=check_port,args=(remoteServerIP,port))
            t.start()
            threads.append(t)
            increment += 1
        else:
            for t in threads:
                t.join()
            increment = 0

    print ports
    print 'Finished Scan.'
    print time.time() - benchmark
 

if __name__=="__main__":
    import threading
    import socket
    import time

    print "Starting Race"
    portscan(host='127.0.0.1',max_port=100000)
    multiportscan(host='127.0.0.1',max_port=100000)


        # except socket.gaierror:
        #     print 'Hostname could not be resolved. Exiting'
        # except socket.error:
        #     print "Couldn't connect to server"