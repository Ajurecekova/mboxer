#!/usr/bin/env python3
import socket
import os
import sys
import signal
import re
import hashlib

def send_status(f,status_num,status_txt):

    f.write(f'{status_num} {status_txt}\n'.encode('UTF-8'))
    if status_num != '100':
        f.write('\n'.encode('UTF-8'))
        f.flush()

def write_method(f):

    head1 = f.readline().decode('UTF-8')
    head2 = f.readline().decode('UTF-8')
    a = head1.split(':')
    b = head2.split(':')
    a[1] = a[1].replace("\n", "")
    b[1] = b[1].replace("\n", "")
    n = b[1].isnumeric()
    c = f.readline().decode('UTF-8')
    
    if a[0]!='Mailbox' or b[0]!= 'Content-length' or not n or '/' in a[1] or '/' in b[1]:
        send_status(f,'200','Bad request')
        f.readline()

    if not os.path.exists('./'+a[1]):
        send_status(f,'203','No such mailbox')
        f.readline()
        
    if c=='\n' :
        send_status(f,'100','Ok')
        f.write(('\n').encode('UTF-8'))
        m = hashlib.md5()
        line = f.read(int(b[1]))
        m.update(line)
        file = open(a[1]+'/'+str(m.hexdigest()), 'wb')
        file.write(line)
        
    else:
        send_status(f,'200','Bad request')
        return
    f.flush()

def read_method(f):

    head1 = f.readline().decode('utf-8')
    head2 = f.readline().decode('utf-8')
    a = head1.split(':')
    b = head2.split(':')
    a[1] = a[1].replace("\n", "")
    b[1] = b[1].replace("\n", "")
    c = f.readline()
    if a[0]!='Mailbox' or b[0]!= 'Message' or '/' in a[1]:
        send_status(f,'200','Bad request')
        return
    
    elif not os.path.exists('./'+a[1]) or not os.path.exists('./'+a[1]+'/'+b[1]):
        send_status(f,'201','No such message')
        return
        
    try:
        mes = open('./'+a[1]+'/'+b[1],'rb').read()
    except error:
        send_status(f,'203','Read error')
        return

    send_status(f,'100','Ok')
    with open(a[1]+'/'+b[1],'rb') as file:
        content = file.read()
    f.write(('Content-length:'+str(len(content))).encode('utf-8'))
    f.write('\n\n'.encode('utf-8'))
    f.write((content))

    f.flush()

def LS_method(f):
    head1 = f.readline().decode('utf-8')
    a = head1.split(':')
    a[1] = a[1].replace("\n", "")
    c = f.readline().decode('utf-8')
    if a[0]!='Mailbox' or '/' in a[1]:
        send_status(f,'200','Bad request')
        return
   
    elif not os.path.exists('./'+a[1]):
        send_status(f,'203','No such mailbox')
        return

    send_status(f,'100','Ok')
    zoz = os.listdir(a[1])
    length = len(zoz)
    f.write(('Number-of-messages:'+str(length)).encode('UTF-8'))
    f.write(('\n\n').encode('UTF-8'))
    for i in zoz:
        f.write(i.encode('UTF-8'))
        f.write('\n'.encode('UTF-8'))
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
                send_status(f,'204','Unknown method')
        f.close()
        sys.exit(0)
    else:
        connected_socket.close()
