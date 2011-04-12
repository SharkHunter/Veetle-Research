#!/usr/bin/python

import urllib2
import socket
import binascii
import sys

#grab ip and port info
response = urllib2.urlopen('http://www.veetle.com/channelHostPort/'+sys.argv[1])
payload = response.read()
print payload

if payload.startswith('ok'):
   ip, d, ports = payload[3:].partition(':')
   ports = [int(p) for p in ports.split(',')]
   print 'ip: ' + ip, 'ports:', ports
else:
   print payload

s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s2.connect((ip, ports[2]))

s22 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s22.connect((ip, ports[2]))

s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s1.connect((ip, ports[1]))

s0 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s0.connect((ip, ports[0]))

#handshake part 1
p2_question = binascii.unhexlify('3002000000000000')  #version no?
print 'p2 question: ' + binascii.hexlify(p2_question)
s2.send(p2_question)
s22.send(p2_question)
p1_answer = s1.recv(1024)
p0_answer = s0.recv(1024)
p2_answer = s2.recv(1024)
p22_answer = s22.recv(1024)
print 'p1 answer: ' + binascii.hexlify(p1_answer)
print 'p0 answer: ' + binascii.hexlify(p0_answer)
print 'p2 answer: ' + binascii.hexlify(p2_answer)
print 'p22 answer: ' + binascii.hexlify(p22_answer)

#handshake part 2
p1_question = chr(16) + chr(01) + p22_answer[2:] + p2_answer[-2:]
print 'p1 question: ' + binascii.hexlify(p1_question)
s1.send(p1_question)
s0.send(p1_question)
#p1_answer = s1.recv(1024)
#print 'p1 answer: ' + binascii.hexlify(p1_answer)

#handshake part 3
p0_question = binascii.unhexlify('78010439a912') + p1_question[2:] + 'breadboyy' + chr(8)
print len(binascii.unhexlify('78010439a913')),len(p22_answer),len('breadboyy')
print 'p0 question: ' + binascii.hexlify(p0_question)
s0.send(p0_question)
p1_answer = s1.recv(1024)
print 'p1 answer: ' + binascii.hexlify(p1_answer)


# remove first 35 bytes
print 'discarding: ' + binascii.hexlify(s0.recv(35))
   
print 'grabbing first 4k to test.stream'

f = open('test.stream', 'w')
mid='79040015a5'
base=32
i=0
b=0
while True:
   stream = s0.recv(4096)
   #print binascii.hexlify(stream)
   i=i+1
   
   b=b+len(stream)
   print 'received', b, 'bytes','cnt',i
   if(not stream):
      break
   if(i==25):
      base=(base+1) % 256
      b=0
      x=binascii.unhexlify(mid)+chr(base)
      print 'send '+ binascii.hexlify(x)
      s0.send(x)
      i=0
   f.write(stream)

