#!/usr/bin/env python3
import socket
import os
import sys
import signal
import re
import hashlib



def write_method(f):

    head1 = f.readline().decode('UTF-8')
    head2 = f.readline().decode('UTF-8')
    a = head1.split(':')
    b = head2.split(':')
    a[1] = a[1].replace("\n", "")
    b[1] = b[1].replace("\n", "")
    n = b[1].isnumeric()
    
    if a[0]!='Mailbox' or b[0]!= 'Content-length' or not n or '/' in a[1] or '/' in b[1]:
        f.write('200 Bad request'.encode('UTF-8'))
        f.close()
        
    c = f.readline().decode('UTF-8')

    if not os.path.exists('./'+a[1]):
        f.write('203 No such mailbox'.encode('UTF-8'))
        f.close()
        
    if c == '\n':
        f.write('100 Ok'.encode('UTF-8'))
        m = hashlib.md5()
        byte_list = []
        whole = []

        while True:
            line = f.read(1).decode('UTF-8').strip()
            whole.append(line)
            if line == '':
                break
            
        if len(whole) < int(b[1]):
            r = len(whole)
        else:
            r = int(b[1])
        for i in range(r):
            line =whole[i]
            m.update(line.encode('UTF-8'))
            byte_list.append(line)
        m.hexdigest()
        a[1] = a[1].replace("\n", "")
        file = open(a[1]+'/'+str(m), 'w')
        for i in byte_list:
            file.write(i)
        
    else:
        f.write('200 Bad request'.encode('UTF-8'))
        f.close()
    f.flush()

def read_method(f):

    head1 = f.readline().decode('UTF-8')
    head2 = f.readline().decode('UTF-8')
    a = head1.split(':')
    b = head2.split(':')
    if a[0]!='Mailbox' or b[0]!= 'Message' or '/' in a[1]:
        f.write('200 Bad request'.encode('UTF-8'))
        f.close()
        sys.exit(0)
    a[1] = a[1].replace("\n", "")
    b[1] = b[1].replace("\n", "")
    if not os.path.exists('./'+a[1]) or not os.path.exists('./'+a[1]+'/'+b[1]):
        f.write('202 No such message'.encode('UTF-8'))
        f.close()
    try:
        mes = open('./'+a[1]+'/'+b[1],'rb').read()
    except error:
        f.write('203 Read error'.encode('UTF-8'))
        f.close()

    f.write('100 Ok\n'.encode('UTF-8'))
    with open(a[1]+'/'+b[1]) as file:
        content = file. read()
    f.write(('Content-length:'+str(len(content))).encode('UTF-8'))
    f.write('\n'.encode('UTF-8'))
    f.write(content.encode('UTF-8'))

    f.flush()

def LS_method(f):
    head1 = f.readline().decode('UTF-8')
    a = head1.split(':')
    if a[0]!='Mailbox' or '/' in a[1]:
        f.write(',200 Bad request'.encode('UTF-8'))
        f.close()
    a[1] = a[1].replace("\n", "")
   
    if not os.path.exists('./'+a[1]):
        f.write('203 No such mailbox'.encode('UTF-8'))
        f.close()

    f.write('100 Ok\n'.encode('UTF-8'))
    zoz = os.listdir(a[1])
    length = len(zoz)
    f.write(('Number-of-messages:'+str(length)).encode('UTF-8'))
    for i in range(length):
        f.write(zoz[i].encode('UTF-8'))
    f.flush()

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
s.bind(('',9999))
signal.signal(signal.SIGCHLD,signal.SIG_IGN)
s.listen(5)

while True:
    connected_socket,address=s.accept()
    print(f'spojenie z {address}')
    pid_chld=os.fork()
    if pid_chld==0:
        s.close()
        f=connected_socket.makefile('rwb')
        while True:
            request=f.readline().decode('UTF-8')
            if not request:
                # spojenie ukoncene
                break
            request.upper()
            print(request)
            if str(request) == 'READ\n':
                read_method(f)
            elif str(request) == 'WRITE\n':
                write_method(f)
            elif str(request) == 'LS\n':
                LS_method(f)
            else:
                f.write('204 Unknown method'.encode('UTF-8'))
                f.close()
        f.close()
        sys.exit(0)
    else:
        connected_socket.close()
