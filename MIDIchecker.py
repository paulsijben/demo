#!/usr/bin/python

import rtmidi_python as rtmidi
import time

code=0

opscodes={11:"CC",9:"Note down",8:"Note UP",14:"FADER",12:"PC"}
def callback(message, time_stamp):
    print message,"||",
    if len(message)==3:
        a,b,c=message
        print hex(a),hex(b),hex(c),
        ops,channel = divmod(a,16)
        channel+=1
        global code
        code=b
        if ops==14:
            print "channel:",channel, opscodes[ops],"   value=",c*128+b
        else:    
            print "channel:",channel, opscodes[ops], b,"   value=",c #, time_stamp
        
        #midi_out.send_message(message)
    elif len(message)==2:
        a,b=message
        print hex(a),hex(b),
        ops,channel = divmod(a,16)
        channel+=1
        global code
        code=b

        print "channel:",channel, opscodes[ops],"   value=",b 
midi_in = rtmidi.MidiIn()
midi_out =rtmidi.MidiOut()
midi_in.callback = callback

notconnected=True

while not midi_in.ports:
    time.sleep(1)

val=0  
direction=1
c=48+8
while 1:
    try:
        ii=0
        while midi_in.ports[ii][:7]=="Automap":
            ii+=1
        i = midi_in.ports[ii]
        if notconnected:
            print "FOUND:",i[:-2]
            print "reconnecting"
            midi_in.close_port()
            midi_in.open_port(i)
            #print midi_in.ports
            j = midi_out.ports.index(i[:-2])
            midi_out.close_port()
            midi_out.open_port(j)
            time.sleep(1)
            notconnected=False
            #midi_out.send_message([224, 0, 0])
        
        ##code=c
        print "sending",[0xb2,code,val]   
        midi_out.send_message([0xb1,code,val])  
        val+=direction
        if val>=127 or val<=0:
            direction=-direction
            ###val=0
            ###c+=1
            
        
    except IndexError:
        if not notconnected: print "Whoops, USB device gone!"
        notconnected=True   
    time.sleep(.2)
