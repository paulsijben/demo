#!/usr/bin/python

import rtmidi_python as rtmidi
import time
import threading
import traceback,sys

bpm=200
beats=16
lastnote=None

pattern=[]
tapmode=False

code=1
running=False
opscodes={11:"CC",9:"Note down",8:"Note UP",14:"FADER"}

WHITE=3
BLACK=0
RED=60
DARKRED=7
GREEN=123
BLUE=50

heldbuttons={}
taps=[]
cleared=None
step=None

sounds=[]
combinations={}
longestsound=0
import os
from pydub import AudioSegment
import pyaudio
p = pyaudio.PyAudio()
stream = p.open(format=p.get_format_from_width(2),
                    channels=1,
                    rate=44100,
                    output=True)
DISPLAY=None

try:
	if DISPLAY==None:
		import X_display
		myprog=os.path.basename(__file__)[:-3]
		DISPLAY=X_display.MyDisplay(myprog)
		#sleep(2)
		print "GOT DISPLAY1:",DISPLAY
except:	
	exc_type, exc_value, exc_traceback = sys.exc_info()
	lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
	print ''.join('!! ' + line for line in lines)  # Log it or whatever here


def loadSounds():
	lst=os.listdir("sounds")
	lst.sort()
	lst.reverse()
	global longestsound
	for i in lst:
		sound= AudioSegment.from_file("sounds"+os.sep+i, format="wav")
		longestsound=max(longestsound,sound.__len__())
		sounds.append(sound)

def play(sound):
	stream.write(sound)
	
def combiSounds():
	for a in [0,1]:
		for b in [0,1]:
			for c in [0,1]:
				for d in [0,1]:
					sound=AudioSegment.silent(duration=longestsound)
					if a:
						sound=sound.overlay(sounds[0],loop=False)
					if b:
						sound=sound.overlay(sounds[1],loop=False)	
					if c:
						sound=sound.overlay(sounds[2],loop=False)	
					if d:
						sound=sound.overlay(sounds[3],loop=False)	
					combinations["%s%s%s%s"%(a,b,c,d)]=sound.get_array_of_samples()

def clear():
	print "CLEAR:",running
	global step
	step=-1
	#midi_out.send_message([144, 49, BLACK])	
	for i in range(104,104+8):
		midi_out.send_message([176, i, BLACK])
	
	if not running:	
		for i in range(len(pattern)):
			del pattern[-1]
		for i in range(16):
			pattern.append([False,False,False,False])
			midi_out.send_message([145, 49, GREEN])
	else:
		v		
	for i in range(90):
		midi_out.send_message([144, i, BLACK])
		
	for i in [1,2,3,4]:
		if i<=beats/4:
			midi_out.send_message([176, 107+i, GREEN])


def callback(message, time_stamp):
	try:
		#print message,"||",
		a,b,c=message
		#print hex(a),hex(b),hex(c),
		ops,channel = divmod(a,16)
		channel+=1
		global code
		global lastnote
		global beat
		code=b
		action=None
		if c==127:
			if not heldbuttons.has_key(b):
				action="DOWN"
			else: 
				action="HOLD"        
			heldbuttons[b]=time.time()
		else:
			if heldbuttons.has_key(b):
				action="UP"   
			del heldbuttons[b]
		if ops in [8,9]:
			row,col= divmod(b,10)
			if ops==9 and lastnote!=b:#note down
				lastnote=b
				if col<9:
					if row<5:
						step2=col+8-1
						beat=pattern[step2]  
						beat[row-1]=not beat[row-1]
						new=beat[row-1]
					else:
						step2=col-1
						beat=pattern[step2]  
						beat[row-5]=not beat[row-5]
						new=beat[row-5]
					if new:
						val=DARKRED
					else:
						val=BLACK
					pattern[step2]=beat    
					midi_out.send_message([144, b, val])
				elif b==19:
					if heldbuttons.has_key(19):
						midi_out.send_message([144, 19, RED])
					else:
						midi_out.send_message([144, 19, BLACK])
				elif b==29:
					if heldbuttons.has_key(29):
						midi_out.send_message([144, 29, GREEN])
					else:
						midi_out.send_message([144, 29, BLACK])

			else:
				#print "YEAH",b,c
				row,col= divmod(b,10)
				row=row-4
				lastnote=None
				if b==49:
					if c==0:
						global cleared
						if False: #cleared:
							cleared=False
						else:	
							global running
							running=not running
							if running:
								
								global step
								drawBeat(step,False)
								step=-1
								midi_out.send_message([144, 49, GREEN])
								
							else:
								midi_out.send_message([144, 49, RED])
				elif b==19:
					if heldbuttons.has_key(19):
						midi_out.send_message([144, 19, RED])
					else:
						midi_out.send_message([144, 19, BLACK])
				elif b==29:
					if heldbuttons.has_key(19):
						midi_out.send_message([144, 29, GREEN])
					else:
						midi_out.send_message([144, 29, BLACK])

				elif heldbuttons.has_key(19) and (b in [89,79,69,59]):
					#record
					print "RECORDING", row
					midi_out.send_message([144, b, RED])

				elif heldbuttons.has_key(29) and (b in [89,79,69,59]): 
					print "PLAYING", row
					midi_out.send_message([144, b, GREEN])

				elif running and (b in [89,79,69,59]):
					step2=step
					#print "STEP=",step2
					beat=pattern[step2]
					beat[row-1]=not beat[row-1]
					new=beat[row-1]
					if new:
						val=DARKRED
					else:
						val=BLACK
					pattern[step2]=beat   
					#print step2,row
					if step2<8:
						note=51+step+10*(row-1)
					else:
						note=11+step-8+10*(row-1)
					midi_out.send_message([144, note, val])
		elif ops == 11:
			global bpm
			if heldbuttons.has_key(104) and  heldbuttons.has_key(105) and action=="DOWN":
				#toggle tapmode
				global tapmode
				tapmode=not tapmode
				if tapmode:
					val=BLUE
				else:
					val=BLACK
				midi_out.send_message([176, 104, val])
				midi_out.send_message([176, 105, val])
			elif 	heldbuttons.has_key(19) and b==104 and action=="DOWN":
				global running
				running=False
				clear()
				from subprocess import call
				call(["shutdown","-h","now"])
			elif tapmode and b in [104,105] and action=="DOWN":
				t=time.time()
				if len(taps)>0 and t-taps[0]>3:
					while len(taps)>0:
						del taps[0]

				taps.append(t)
				while len(taps)>5: del taps[0]
				avg=0
				#print taps
				if len(taps)>3:
					for i in range(len(taps)-1,0, -1): 
						tt=taps[i-1]
						delta=t-tt
						#print i,delta
						avg+=delta
						t=tt
					avg=avg/(len(taps)-1)
					#print "AVG=",avg, len(taps)
					bpm=min(2*60/avg,350)

			elif b==104 and action=="UP":
				bpm+=3
			elif b==105 and action=="UP":
				bpm-=3
			elif b in [108,109,110,111]:
				#print "b=",b,
				bars=b-107
				#print bars
				global beats
				beats=bars*4
				#print "beats=",beats
				for i in range(108,112):
					if i<=b:
						midi_out.send_message([176, i, GREEN])
					else:
						midi_out.send_message([176, i, BLACK])
			#print "BPM=",bpm        
			if DISPLAY: DISPLAY.showText("BPM:%s"%bpm)
		else:
			midi_out.send_message(message)
	except:
		exc_type, exc_value, exc_traceback = sys.exc_info()
		lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
		print ''.join('!! ' + line for line in lines)  # Log it or whatever here
		#time.sleep(1) 

midi_in = rtmidi.MidiIn()
midi_out =rtmidi.MidiOut()
midi_in.callback = callback

connected=False

def drawBeat(step,selected):
	beat=pattern[step]
	combi=''
	for i in range(4):
		a=beat[i]
		if a:
			combi+="1"
		else:
			combi+="0"

		if step<8:
			note=51+step+10*i
		else:
			note=11+step-8+10*i

		if selected:    
			if a:
				val=RED
			else: 
				val=WHITE
		else:
			if a:
				val=DARKRED
			else: 
				val=BLACK
		midi_out.send_message([144, note, val])

def playbeat(step):
	beat=pattern[step]
	combi=''
	for i in range(4):
		a=beat[i]
		if a:
			combi+="1"
		else:
			combi+="0"
	#print "A:",time.time()
	#print combi
	if combi!='0000':
		play(combinations[combi])
	#print "B:",time.time()	
def sequencer():
	try:
		prevstep=None
		global connected
		global bpm
		global beats
		global running
		global step
		while connected:
			if running:
				t=time.time()
				#print "1:",t
				prevstep=step 
				if step==None:
					step=0
				else:	
					step+=1    
				if step>=beats:
					step=0
				playbeat(step)
				#print "2:",time.time()
				if prevstep!=None:
					drawBeat(prevstep,False)
				#print "3:",time.time()	
				drawBeat(step,True)
				#print "4:",time.time()
				tdelta=60.0/bpm 
				v=tdelta-(time.time()-t)
				#print bpm,tdelta,v
				if v<=0: 
					print "WAAAAH!"
					print bpm,tdelta,v
				else: time.sleep(v)
			else:
				#print heldbuttons
				if heldbuttons.has_key(49) and  heldbuttons.has_key(39) and time.time()-(heldbuttons[39])>2:
					del heldbuttons[49]
					del heldbuttons[39]
					clear()
					global cleared
					cleared=True
					midi_out.send_message([145, 49, GREEN])
					running =False
				else:	
					time.sleep(.2)	
	except:
		exc_type, exc_value, exc_traceback = sys.exc_info()
		lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
		print ''.join('!! ' + line for line in lines)  # Log it or whatever here
		#time.sleep(1) 
loadSounds()
combiSounds()

while not midi_in.ports:
	time.sleep(1)

val=0  
direction=1
c=48+8
while 1:
	try:
		ii=0
		while midi_in.ports[ii][:9]!="Launchpad":
			ii+=1
			
		i = midi_in.ports[ii]
		if not connected:
			print "FOUND:",i[:-2]
			nm=i[:-4]
			print "reconnecting"
			midi_in.close_port()
			midi_in.open_port(i)
			#print midi_in.ports
			j = midi_out.ports.index(i[:-5]+":0")
			midi_out.close_port()
			midi_out.open_port(j)

			time.sleep(1)
			connected=True
			clear()
			arr=[]
			if not running:
				for i in "Sequencer...":
					arr.append(ord(i))
				midi_out.send_message([240, 0, 32, 41, 2, 24, 20,BLUE,0]+arr+[247])
				if DISPLAY:
					time.sleep(3)
					DISPLAY.showText("Found:"+nm)
			thread=threading.Thread(target=sequencer)
			thread.daemon=True
			thread.start()
			midi_out.send_message([145, 49, GREEN])	

	except ValueError: pass    
	except IndexError:
		if connected: print "Whoops, USB device gone!"
		connected=False
	time.sleep(.1)