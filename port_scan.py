import socket
import sys
import threading
import time
import Queue
import struct
import json

#############
# config
TIMEOUT = 1
THREAD = 1
COMMON_PORT = ['80','443','3306','23']
############


RESULT = {}
q = Queue.Queue()


def ip_to_long(ip):
    return socket.ntohl(struct.unpack("I",socket.inet_aton(str(ip)))[0])


def long_to_ip(long):
    return socket.inet_ntoa(struct.pack('I',socket.htonl(long)))


def args_parse(ip_range,port_range):
    def split_ip(ip_range):
        print 'split ip'
        result = set()
        ips = ip_range.split('-')
        if len(ips) == 1:
            result.add(ip_to_long(ips[0]))
        elif len(ips) == 2:
            for i in range(ip_to_long(ips[0]), ip_to_long(ips[1])+1):
                result.add(i)
        return result

    def split_port(port_range):
        print 'split port'
        result = set()
        ports = port_range.split('-')
        if len(ports) == 1:
            result.add(ports[0])
        elif len(ports) == 2:
            for i in range(int(ports[0]), int(ports[1])):
                result.add(i)
        for p in COMMON_PORT:
            result.add(p)
        return result
    ips = split_ip(ip_range)
    ports = split_port(port_range)
    for ip in ips:
        for port in ports:
            q.put((ip,port))
    print 'the number of task is %d'% q.qsize()


def ping(task, timeout=TIMEOUT):
    ip = long_to_ip(task[0])
    port = task[1]
    try:
        if not RESULT or not RESULT[ip]:
            RESULT[ip] = []
        cs=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        cs.settimeout(float(timeout))
        address=(str(ip),int(port))
        status = cs.connect_ex((address))
        if status == 0 :
            RESULT[ip].append(port)
            print "%s is NORMAL" %port
        else:
            print '{0}:{1} is unavailable'.format(ip,port)
    except Exception as e:
        print e
    else:
        cs.close()


class Scan(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while not q.empty():
            task = q.get()
            ping(task)


if __name__ == '__main__':
    ip_range = sys.argv[1]
    port_range = sys.argv[2]
    args_parse(ip_range,port_range)
    threads = []
    for i in range(THREAD):
        t = Scan()
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    with open('ports.txt','w+') as f:
        f.write(json.dumps(RESULT))