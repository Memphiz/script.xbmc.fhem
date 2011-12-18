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
import xbmc
import xbmcaddon
import xbmcgui
import time
import os

__settings__   = xbmcaddon.Addon(id='script.xbmc.fhem')
__cwd__        = __settings__.getAddonInfo('path')
__icon__       = os.path.join(__cwd__,"icon.png")
__scriptname__ = "XBMC FHEM"

BASE_RESOURCE_PATH = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'lib' ) )
sys.path.append (BASE_RESOURCE_PATH)

from settings import *
from fhem import *

global g_failedConnectionNotified


def initGlobals():
  global g_failedConnectionNotified

  g_failedConnectionNotified = False   
  settings_initGlobals()
  fhem_initGlobals()

def process_fhem():
  while not xbmc.abortRequested:
    fetchFhem()
    fhem_updateInfoWindow()    
    for i in range(1,30):
      time.sleep(1)
      if xbmc.abortRequested:
        break

def fetchFhem():
  global g_failedConnectionNotified
  
  hostip   = settings_getHostIp()
  hostport = settings_getHostPort()
  
  while not xbmc.abortRequested:
    #check for new settings
    if settings_checkForNewSettings():    #networksettings changed?
      g_failedConnectionNotified = False  #reset notification flag
    hostip   = settings_getHostIp()
    hostport = settings_getHostPort()    
    ret = fhem_fetch(hostip, hostport)

    if not ret:
      print "fhem: connection to fhem failed"
      count = 10
      while (not xbmc.abortRequested) and (count > 0):
        time.sleep(1)
        count -= 1
      if not g_failedConnectionNotified:
        g_failedConnectionNotified = True
        text = __settings__.getLocalizedString(500)
        xbmc.executebuiltin("XBMC.Notification(%s,%s,%s,%s)" % (__scriptname__,text,10,__icon__))
    else:
      text = __settings__.getLocalizedString(501)
      if not g_failedConnectionNotified:
        xbmc.executebuiltin("XBMC.Notification(%s,%s,%s,%s)" % (__scriptname__,text,10,__icon__))
        g_failedConnectionNotified = True
      print "fhem: connected to fhem and fetched data"
      break
  return True

#MAIN - entry point
initGlobals()

#main loop
while not xbmc.abortRequested:
  settings_setup()
  process_fhem()    #fhem loop

fhem_initGlobals() #clears lists - for skin doesn't show the old values
fhem_updateInfoWindow() #push cleared values to the skin
