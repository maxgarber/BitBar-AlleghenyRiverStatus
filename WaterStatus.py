#!/Library/Frameworks/Python.framework/Versions/2.7/bin/python
# -*- coding: utf-8 -*-

#
#	WaterStatus
#	a BitBar plugin for rowers on the Allegheny river in Pittsburgh, PA
#	v1.0 by Max Garber <max.garber+dev@gmail.com>
#	[√] tested on 2017/04/23
#


#
#	Libraries
#

import sys, os, re, urllib2
import xml.dom.minidom, xml.etree.ElementTree
import datetime, pytz
from xml.dom.minidom import parseString
from xml.etree.ElementTree import tostring


#
#	Functions
#

#	retrieve water flow rate
def getFlow():
	datum = {}
	url = "https://waterservices.usgs.gov/nwis/iv/?format=waterml,2&sites=03049500&parameterCd=00060&period=P1D"
	dom = parseString(urllib2.urlopen(url).read())
	n = dom.getElementsByTagName("wml2:MeasurementTimeseries").length - 1
	l = dom.getElementsByTagName("wml2:MeasurementTVP").length
	
	if n >= l:
		return "n/a"
	else:
		node = dom.getElementsByTagName("wml2:MeasurementTVP")[-1]
		datum['value'] = float(node.getElementsByTagName("wml2:value")[0].toxml().replace('<wml2:value>','').replace('</wml2:value>',''))/1000
		datum['date'] = node.getElementsByTagName("wml2:time")[0].toxml().replace('<wml2:time>','').replace('</wml2:time>','')
		datum['units'] = "kcfs"
		return datum
	#end-ifelse
#END-def

#	retrieve water temperature
def getTemp():
	datum = {}
	url = "https://waterservices.usgs.gov/nwis/iv/?format=waterml,2&sites=03049640&&parameterCd=00010&period=P1D"
	dom = parseString(urllib2.urlopen(url).read())
	n = dom.getElementsByTagName("wml2:MeasurementTimeseries").length - 1
	l = dom.getElementsByTagName("wml2:MeasurementTVP").length
	
	if n >= l:
		return "n/a"
	else:
		node = dom.getElementsByTagName("wml2:MeasurementTVP")[-1]
		datum['value'] = float(node.getElementsByTagName("wml2:value")[0].toxml().replace('<wml2:value>','').replace('</wml2:value>',''))
		datum['date'] = node.getElementsByTagName("wml2:time")[0].toxml().replace('<wml2:time>','').replace('</wml2:time>','')
		datum['units'] = "˚C"
		return datum
	#end-ifelse
#END-def

#	safety matrix notes
def getSafetyNotes(zone):
	safetyString = ""
	if (zone == 1):
		safetyString = "All boats"
	elif (zone == 2):
		safetyString = "All boats\n1x, 2x, & 2- without launch must have ≥1 yr rowing experience at TRRA\nIf zone 3 daylight need 1 launch to 2 every shells of equal speed\nProtected cell phone required"
	elif (zone == 3):
		safetyString = "8+, 4+,4x & 2x; adaptive LTA racing: 2x only\n1 launch to every 2 shells of equal speed\ncoach must be USRA level ≥2\nPFDs worn by all rowers and coxswains\nProtected cell phone required"
	elif (zone == 4):
		safetyString = "8+, 4+, & 4x\n1 launch to every 2 shells of equal speed\ncoach must be USRA level ≥2\nPFDs worn by all rowers and coxswains\nProtected cell phone required"
	else:
		safetyString = "unsafe?"
	#END-ifelse
	return safetyString
#END-def


#
#	main()
#

flow = getFlow()
temp = getTemp()

if flow == "n/a":
	flowValue = "n/a"
	flowZone = "n/a"
else:
	flowValue = flow['value']
	flowZone = 0
	if flowValue < 28:
	    flowZone = 1
	elif flowValue < 35:
	    flowZone = 2
	elif flowValue < 40:
	    flowZone = 3
	elif flowValue < 45:
	    flowZone = 4
	elif flowValue < 50:
	    flowZone = 5
	elif flowValue < 60:
	    flowZone = 6
	else:
	    flowZone = -1
	#end-ifelse
#END-ifelse

if temp == "n/a":
	tempValue = "n/a"
	tempZone = "n/a"
else:
	tempValue = temp['value']
	tempZone = 0
	if (tempValue > 10):
		tempZone = 1
	elif (tempValue <= 10 and tempValue >= 4.5):
		tempZone = 3
	elif (tempValue < 4.5 and tempValue > 0):
		tempZone = 4
	else:
		tempZone = -1
	#end-ifelse
#END-ifelse

#error check here
if ((flowValue == "n/a") and (tempValue == "n/a")):
	safetyZone = "n/a"
	color = "gray"
else:
	safetyZone = max(flowZone, tempZone)
	color = "white"
	if (safetyZone == 1):
		color = "lime"
	elif (safetyZone == 2):
		color = "green"
	elif (safetyZone == 3):
		color = "olive"
	elif (safetyZone == 4):
		color = "yellow"
	elif (safetyZone == 5):
		color = "orange"
	else:
		color = "red"
	#end-ifelse
#end-ifelse

print(str(flowValue)+ flow['units']+ ", " +str(tempValue) + temp['units'] + "|dropdown=true, color=" + color)
print("---")
#need measurement dates
print("zone: " + str(safetyZone))
print(getSafetyNotes(safetyZone))

#EOF
