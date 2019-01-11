from linepy import *
from datetime import datetime

#authToken dari LINE() trus nanti scan qr atau LINE('email', 'pass') trus verify di HP, token tiap 30 hari harus renew
line = LINE("EAcBeeOeBHgwKGbMemj1./krU4S9VPkDA3A/FvNyPeq.lyG2OZ8Co+08b2TIAvraQVtNodjztTySAqI1U1oVUeE=")
tracer = OEPoll(line)
log = {}

# msg.createdTime -> 00:00:00
def cTime_to_Text(unixtime):
    dt = datetime.fromtimestamp(int(unixtime[:-3]))
    return dt.strftime('%H:%M:%S')
# make response text
def mk_resp(msg_id):
    return '\n'.join([
    line.getContact(log[msg_id]["from"]).displayName,
    'Unsent:',
    log[msg_id]["text"],
    cTime_to_Text(str(log[msg_id]["createdTime"]))
    ])

# Receive messages from OEPoll
def RECEIVE_MESSAGE(op):
    msg = op.message
    line.log(msg)
    text = msg.text
    msg_id = msg.id
    receiver = msg.to
    sender = msg._from
    
    # Check content only text message
    if msg.contentType == 0:
        # Personal chat
        if msg.toType == 0:
            # Add to log
            log[msg_id] = {"text":text,"from":sender,"createdTime":msg.createdTime}
        # Group chat
        if msg.toType == 2:
            # Chat checked request
            line.sendChatChecked(receiver, msg_id)
            # Add to log
            log[msg_id] = {"text":text,"from":receiver,"createdTime":msg.createdTime}

        # Get sender contact
        contact = line.getContact(sender)
        txt = '[%s] %s' % (contact.displayName, text)
        # Print log
        line.log(txt)

# Load from Log when message cancelled
def NOTIFIED_DESTROY_MESSAGE(op):
    line.log(op)
    try:
        at = op.param1
        msg_id = op.param2
        if msg_id in log:
            line.sendMessage(log[msg_id]["from"],mk_resp(msg_id))
    except Exception as e:
        print(e)

# Auto join if BOT invited to group
def NOTIFIED_INVITE_INTO_GROUP(op):
    try:
        group_id=op.param1
        # Accept group invitation
        line.acceptGroupInvitation(group_id)
    except Exception as e:
        line.log("[NOTIFIED_INVITE_INTO_GROUP] ERROR : " + str(e))

# Add function to OEPoll
tracer.addOpInterruptWithDict({
    OpType.RECEIVE_MESSAGE: RECEIVE_MESSAGE,
    OpType.NOTIFIED_DESTROY_MESSAGE : NOTIFIED_DESTROY_MESSAGE,
    OpType.NOTIFIED_INVITE_INTO_GROUP : NOTIFIED_INVITE_INTO_GROUP
})

while True:
    tracer.trace()
