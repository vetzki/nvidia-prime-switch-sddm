#!/usr/bin/python

import os
import sys

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator

intel_active = True

def switch(_, switch_menu):
  global intel_active

  ret = os.WEXITSTATUS(os.system('pkexec prime-switch -d ' + ('nvidia' if intel_active else 'intel')))
  if ret not in [0,1]:
    dialog = gtk.MessageDialog(parent=None, flags=0, message_type=gtk.MessageType.ERROR, buttons=gtk.ButtonsType.OK, text='pkexec might not be installed or privilege is not given, it\'s required to execute prime-switch as root')
  else:
    intel_active = not intel_active
    switch_menu.set_label(label='Switch to ' + ('Nvidia' if intel_active else 'Intel'))
    msg = 'Switching successful, please relogin/reboot' if ret == 0 else 'Switching failed, check if switching manually via terminal works'
    dialog = gtk.MessageDialog(parent=None, flags=0, message_type=gtk.MessageType.INFO, buttons=gtk.ButtonsType.OK, text=msg)

  dialog.run()
  dialog.destroy()

def quit(_):
  gtk.main_quit()

def build_menu():
  menu = gtk.Menu()

  switch_menu = gtk.MenuItem(label='Switch to ' + ('Nvidia' if intel_active else 'Intel'))
  switch_menu.connect('activate', switch, switch_menu)
  menu.append(switch_menu)

  quit_menu = gtk.MenuItem(label='Quit')
  quit_menu.connect('activate', quit)
  menu.append(quit_menu)

  menu.show_all()
  return menu

def is_intel_active():
  ret = os.WEXITSTATUS(os.system("glxinfo | grep 'Vendor: Intel'"))
  if ret not in [0,1]:
    dialog = gtk.MessageDialog(parent=None, flags=0, message_type=gtk.MessageType.ERROR, buttons=gtk.ButtonsType.OK, text='glxinfo might not be installed, it\'s required to check currently active card')
    dialog.run()
    dialog.destroy()
    sys.exit()

  return ret == 0

def main():
  global intel_active
  intel_active = is_intel_active()

  indicator = appindicator.Indicator.new('Nvidia PRIME Switch', 'applications-games-symbolic', appindicator.IndicatorCategory.APPLICATION_STATUS)
  indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
  indicator.set_menu(build_menu())
  gtk.main()

if __name__ == "__main__":
  main()