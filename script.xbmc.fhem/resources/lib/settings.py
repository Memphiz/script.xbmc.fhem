'''
    Boblight for XBMC
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

import sys
import time
import xbmc
__scriptname__ = sys.modules[ "__main__" ].__scriptname__
__settings__   = sys.modules[ "__main__" ].__settings__
__cwd__        = sys.modules[ "__main__" ].__cwd__
__icon__       = sys.modules[ "__main__" ].__icon__
sys.path.append (__cwd__)

#general
global g_hostip
global g_hostport
global g_timer

#init globals with defaults
def settings_initGlobals():
  global g_hostip
  global g_hostport  
  global g_timer

  g_hostip         = "127.0.0.1"
  g_hostport       = 7072
  g_timer          = time.time()   

def settings_getHostIp():
  global g_hostip
  return g_hostip

def settings_getHostPort():
  global g_hostport
  return g_hostport 

#check for new settings and handle them if anything changed
#only checks if the last check is 5 secs old
#returns if a reconnect is needed due to settings change
def settings_checkForNewSettings():
#todo  for now impl. stat on addon.getAddonInfo('profile')/settings.xml and use mtime
#check for new settings every 5 secs
  global g_timer
  reconnect = False

  if time.time() - g_timer > 5:
    reconnect = settings_setup()
    g_timer = time.time()
  return reconnect

  
#handle all settings in the general tab according to network access
#returns true if reconnect is needed due to network changes
def settings_handleNetworkSettings():
  global g_hostip
  global g_hostport
  reconnect = False

  hostip        = __settings__.getSetting("hostip")
  hostport      = int(__settings__.getSetting("hostport"))

  #server settings
  #we need to reconnect if networkaccess bool changes
  #or if network access is enabled and ip or port have changed
  if g_hostip != hostip or g_hostport != hostport:
    if g_hostip != hostip:
      print "fhem: changed hostip to " + str(hostip)
      g_hostip = hostip
    
    if g_hostport != hostport:
      print "fhem: changed hostport to " + str(hostport)
      g_hostport = hostport
    reconnect = True
  return reconnect

#handles all settings of boblight and applies them as needed
#returns if a reconnect is needed due to settings changes
def settings_setup():  
  reconnect = False
  reconnect = settings_handleNetworkSettings()

  return reconnect
  
