# Python script to find ip addresses of the destination urls
import socket

fh = open('data/urls.txt', 'r')
L = fh.readlines()
fh.close()
with open('data/ips.txt', 'w') as fh:
    for line in L:
        ip_addr = socket.gethostbyname(line.rstrip())
        fh.write(ip_addr+'\n')
