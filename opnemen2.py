#!/usr/bin/python

import requests
import time
import json
import datetime
import xml.etree.ElementTree as ET
tree = ET.parse('output.xml')
root = tree.getroot()

favorites=[ "Top 2000",
 "Only Connect",
 "All together now",
"The Repair shop",
"Salvage hunters",
 "Formula 1",
 "Death in paradise",
 "De Nationale Wetenschapsquiz",
 "Gardeners' world",
 "Wheeler Dealers",
 "grand tours of schotland's lochs",
]
channels=['spike']
skipchannels=['zappelin','bbc first','tv5','nickelodeon','eurosport','2m']

months=['jan','feb','mrt','apr','mei','jun','jul','aug','sept','okt','nov','dec']

def prettyDate(d):
   yr=d[:4]
   mon=months[int(d[4:6])-1]
   day=d[6:8]
   hr=d[8:10]
   mn=d[10:12]
   
   return "%s %s %s:%s"%(mon,day,hr,mn)

def inFavorites(title):
   for i in favorites:
      if title.lower().find(i.lower())>-1:
         return i
   return False   



import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# me == my email address
# you == recipient's email address
me = "paul@XXXXXXXXXXXXXXX"
you = "we@XXXXXXXXXXXXXXXX"

# Create message container - the correct MIME type is multipart/alternative.
msg = MIMEMultipart('alternative')
msg['Subject'] = "Opnemen"
msg['From'] = me
msg['To'] = you


now = datetime.datetime.now()
today="%s-%02d-%02dT%02d:%02d"%(now.year,now.month, now.day,now.hour,now.minute)
end_date = now + datetime.timedelta(days=3)
end="%s-%02d-%02d"%(end_date.year,end_date.month, end_date.day)

result=[]
channels={}
for child in root.iter('channel'):
   cid=child.attrib['id']
   channels[cid]=child.find('display-name').text

for child in root.iter('programme'):
   title=child.find('title').text
   term=inFavorites(title)
   if term:
      try:
         desc=child.find('desc').text
         start=prettyDate(child.attrib['start'])
         stop=prettyDate(child.attrib['stop'])
         cid=child.attrib['channel']
         channel=channels[cid]
         try:
            e=child.find('episode-num').text.split(" . ")
            episode="serie %s episode %s"%(e[0],e[1])
         except:
            episode=''
         if not channel.lower() in skipchannels:
            result.append(((title, episode,channel, start, stop,desc),term))
      except AttributeError:
         print child
result.sort()

oddeven=0
col=["#cccccc","#70bbd9"]
ht=""
text=""
for r in result:
   text+="%s,%s\n"%r
   #print r
   line='<TR bgcolor="%s">'%col[oddeven]
   oddeven=1-oddeven
   count=0
   for e in r[0]:
      if count==0:
         ef=e.replace(" ","%20")
         ee='<a href="https://televisie.xs4all.nl/zoekresultaten/%s">%s</a>'%(ef,e)
      else: ee=e   
      line+="<TD>%s</TD>"%ee
      count+=1
   line+="<TD>%s</TD>"%r[1]   
   line+="</TR>\n"
   ht+=line


# Create the body of the message (a plain-text and an HTML version).

html = """\
<html>
  <head></head>
  <body>
<TABLE>

<TR bgcolor="#ee4c50"><TD>Titel</TD><TD>Episode</TD><TD>Kanaal</TD><TD>Start</TD><TD>Einde</TD><TD>Omschrijving</TD><TD>zoekterm</TD></TR>

%s
</TABLE>
  </body>
</html>
"""%ht

# Record the MIME types of both parts - text/plain and text/html.
part1 = MIMEText(text, 'plain')
part2 = MIMEText(html.encode('ascii', 'xmlcharrefreplace'), 'html')

# Attach parts into message container.
# According to RFC 2046, the last part of a multipart message, in this case
# the HTML message, is best and preferred.
msg.attach(part1)
msg.attach(part2)

# Send the message via local SMTP server.
s = smtplib.SMTP('10.100.0.249')
# sendmail function takes 3 arguments: sender's address, recipient's address
# and message to send - here it is sent as one string.
s.sendmail(me, you, msg.as_string())
s.quit()
