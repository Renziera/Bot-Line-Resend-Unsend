# -*- coding: utf-8 -*-
from linepy import *
from akad.ttypes import Message
import json,sys,atexit,datetime

cl = LineClient(authToken="Input your token")
tracer = LinePoll(cl)
hello = "I'm Message resend bot.\nI resend message when deleted.\nI'm glad to meet you.\n(I don't have any commands)"
admin = "Input your mid"
my_mid = cl.getProfile().mid
msg_dict = {}
bl = ["Put user's mid here to deny resend specific user's message"]

try:
    with open("Log_data.json","r",encoding="utf_8_sig") as f:
        msg_dict = json.loads(f.read())
except:
    print("Couldn't read Log data")

#message.createdTime -> 00:00:00
def cTime_to_datetime(unixtime):
    return datetime.datetime.fromtimestamp(int(str(unixtime)[:len(str(unixtime))-3]))
def dt_to_str(dt):
    return dt.strftime('%H:%M:%S')

#delete log if pass more than 24 hours
def delete_log():
    ndt = datetime.datetime.now()
    for data in msg_dict:
        if (datetime.datetime.utcnow() - cTime_to_datetime(msg_dict[data]["createdTime"])) > datetime.timedelta(1):
            del msg_dict[msg_id]


def RECEIVE_MESSAGE(op):
    try:
        msg = op.message
        if msg.toType == 0:
            cl.log("[%s]"%(msg._from)+msg.text)
        else:
            cl.log("[%s]"%(msg.to)+msg.text)
        if msg.contentType == 0:
            #Save message to dict
            msg_dict[msg.id] = {"text":msg.text,"from":msg._from,"createdTime":msg.createdTime}
    except Exception as e:
        print(e)
tracer.addOpInterrupt(26, RECEIVE_MESSAGE)

def NOTIFIED_DESTROY_MESSAGE(op):
    try:
        at = op.param1
        msg_id = op.param2
        if msg_id in msg_dict:
            if msg_dict[msg_id]["from"] not in bl:
                cl.sendMessage(at,"SentMessage cancelled.\n\n[Sender]\n %s\n[SentAt]\n %s\n[Detail]\n %s"%(cl.getContact(msg_dict[msg_id]["from"]).displayName,dt_to_str(cTime_to_datetime(msg_dict[msg_id]["createdTime"])),msg_dict[msg_id]["text"]))
            del msg_dict[msg_id]
        else:
            cl.sendMessage(at,"SentMessage cancelled,But I didn't have log data.\nSorry > <")
    except Exception as e:
        print(e)
tracer.addOpInterrupt(65, NOTIFIED_DESTROY_MESSAGE)

def NOTIFIED_INVITE_INTO_GROUP(op):
    try:
        #Accept invitation only when from an admin
        if my_mid in op.param3:
            if op.param2 == admin:
                cl.acceptGroupInvitation(op.param1)
                cl.sendMessage(op.param1,hello)
            else:
                cl.rejectGroupInvitation(op.param1)
    except Exception as e:
        print(e)
tracer.addOpInterrupt(13, NOTIFIED_INVITE_INTO_GROUP)

def atend():
    print("Saving")
    with open("Log_data.json","w",encoding='utf8') as f:
        json.dump(msg_dict, f, ensure_ascii=False, indent=4,separators=(',', ': '))
    print("BYE")
atexit.register(atend)

while True:
    tracer.trace()