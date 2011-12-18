'''
    FHEM for XBMC
    Copyright (C) 2011 Team XBMC

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import platform
import xbmc
import xbmcgui
import sys
import os
import re
import telnetlib

from elementtree import ElementTree as xmltree

__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__settings__ = sys.modules[ "__main__" ].__settings__
__cwd__ = sys.modules[ "__main__" ].__cwd__
__icon__ = sys.modules[ "__main__" ].__icon__

global g_fht_list
global g_fhttk_list
global g_fs20_list
global g_infoWindow

#heating control object
class FHTObj():
  name = ""
  temperature = ""
  setTemp = ""
  room = ""
  actuator = ""
  battery = ""
  mode = ""
  windowSensor = ""

#window contact object
class FHTTKObj():
  name = ""
  room = ""
  battery = ""
  window = ""

#switches object
class FS20Obj():
  name = ""
  room = ""
  state = ""

def fhem_initGlobals():
  global g_fht_list
  global g_fhttk_list  
  global g_fs20_list  
  global g_infoWindow
  
  g_fht_list = list()
  g_fhttk_list = list()
  g_fs20_list = list()
  g_infoWindow = xbmcgui.Window(10000)

def fhem_fetch(ip, port):
  ret = True
  fhem_clearLists()
  xmlstr = fhem_get_xml(ip, port)
  if xmlstr != "":
    ret = fhem_parseXML(xmlstr)
  else:
    ret = False

#  fhem_printFhtList()
#  fhem_printFhttkList()
#  fhem_printFs20List()
  return ret

def fhem_clearLists():
  global g_fht_list
  global g_fhttk_list
  global g_fs20_list

  g_fht_list = list()
  g_fhttk_list = list()
  g_fs20_list = list()
#g_fht_list.clear()

def fhem_printFhtList():
  for obj in g_fht_list:
    print "fhem: FHT " + obj.name + " temp: " + obj.temperature + " room: " + obj.room + " act: " + obj.actuator + " bat: " + obj.battery + " mode: " + obj.mode + " setTemp: " + obj.setTemp + " winSens: " + obj.windowSensor

def fhem_printFhttkList():
  for obj in g_fhttk_list:
    print "fhem: FHTTK " + obj.name + " room: " + obj.room + " bat: " + obj.battery + " window: " + obj.window

def fhem_printFs20List():
  for obj in g_fs20_list:
    print "fhem: FS20 " + obj.name + " room: " + obj.room + " state: " + obj.state

def fhem_parseXML(xmlstr):
  global g_fht_list
  global g_fhttk_list
  global g_fs20_list

  ret = True
  fhemcontents = xmltree.fromstring(xmlstr)
  for element in fhemcontents.getiterator():
    #PARSE FHT infos heating control
    if element.tag == "FHT_LIST":
      for child in element:
        if child.tag == "FHT":
          fhtobj = FHTObj()
          fhtobj.name = child.attrib.get('name')
          for subchild in child:
            if subchild.tag == "ATTR" and subchild.attrib.get('key') == "room":
			  fhtobj.room = subchild.attrib.get('value')
            if subchild.tag == "STATE" and subchild.attrib.get('key') == "measured-temp":
              fhtobj.temperature = subchild.attrib.get('value')
            if subchild.tag == "STATE" and subchild.attrib.get('key') == "actuator":
			  fhtobj.actuator = subchild.attrib.get('value')
            if subchild.tag == "STATE" and subchild.attrib.get('key') == "battery":
			  fhtobj.battery = subchild.attrib.get('value')		
            if subchild.tag == "STATE" and subchild.attrib.get('key') == "mode":
			  fhtobj.mode = subchild.attrib.get('value')	
            if subchild.tag == "STATE" and subchild.attrib.get('key') == "desired-temp":
			  fhtobj.setTemp = subchild.attrib.get('value')
            if subchild.tag == "STATE" and subchild.attrib.get('key') == "windowsensor":
			  fhtobj.windowSensor = subchild.attrib.get('value')			    
        g_fht_list.append(fhtobj)

    #PARSE FHTTK infos window sensors
    if element.tag == "CUL_FHTTK_LIST":
      for child in element:
        if child.tag == "CUL_FHTTK":
          fhttkobj = FHTTKObj()
          fhttkobj.name = child.attrib.get('name')
          for subchild in child:
            if subchild.tag == "ATTR" and subchild.attrib.get('key') == "room":
	          fhttkobj.room = subchild.attrib.get('value')
            if subchild.tag == "STATE" and subchild.attrib.get('key') == "Battery":
              fhttkobj.battery = subchild.attrib.get('value')
            if subchild.tag == "STATE" and subchild.attrib.get('key') == "Window":
              fhttkobj.window = subchild.attrib.get('value')
        g_fhttk_list.append(fhttkobj)

    #PARSE FS20 infos switches
    if element.tag == "FS20_LIST":
      for child in element:
        if child.tag == "FS20":
          fs20obj = FS20Obj()
          fs20obj.name = child.attrib.get('name')
          for subchild in child:
            if subchild.tag == "ATTR" and subchild.attrib.get('key') == "room":
	          fs20obj.room = subchild.attrib.get('value')
            if subchild.tag == "STATE" and subchild.attrib.get('key') == "state":
              fs20obj.state = subchild.attrib.get('value')

        g_fs20_list.append(fs20obj)        

  return ret

def fhem_get_xml(ip,port):
  ret = ""
  try:
    tn = telnetlib.Telnet()
    print "fhem: open " + str(ip) + ":" + str(port)
    tn.open(ip, port)
    tn.write("xmllist\n")
    tn.write("quit\n")
    ret = tn.read_all()
    tn.close()
  except:
    print "fhem: telnet exception."
  return ret
  
  
#WINDOW for presenting the FHEM data
def fhem_updateInfoWindow():
  global g_infoWindow

  counter = 0
  g_infoWindow.setProperty("FHT1", "")
  g_infoWindow.setProperty("FHT2", "")
  for obj in g_fht_list:
    counter = counter + 1
    prefix = "FHT" + str(counter)
    g_infoWindow.setProperty(prefix, obj.name)
    g_infoWindow.setProperty(prefix + "room", obj.room)
    g_infoWindow.setProperty(prefix + "destemp", obj.setTemp + " (Celsius)")
    g_infoWindow.setProperty(prefix + "meastemp", obj.temperature)
    g_infoWindow.setProperty(prefix + "act", obj.actuator)
    g_infoWindow.setProperty(prefix + "bat", obj.battery)
    g_infoWindow.setProperty(prefix + "mode", obj.mode)
 
  counter = 0
  g_infoWindow.setProperty("FHTTK1", "")
  for obj in g_fhttk_list:
    counter = counter + 1
    prefix = "FHTTK" + str(counter)
    g_infoWindow.setProperty(prefix, obj.name)
    g_infoWindow.setProperty(prefix + "room", obj.room)
    g_infoWindow.setProperty(prefix + "bat", obj.battery)
    g_infoWindow.setProperty(prefix + "window", obj.window)
