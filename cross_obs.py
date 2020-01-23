#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import wx
import sys
import os
from wx.lib.pubsub import pub
from threading import Thread
import threading

sys.path.append('shared')
sys.path.append('src')
import GetQueue
import time

import controlTK_gui as ctg
from numpy import log10

#global SOCK_STATUS_SER

class MyFrame(wx.Frame):
  def __init__(self, *args, **kwds):
    kwds["style"] = wx.DEFAULT_FRAME_STYLE
    wx.Frame.__init__(self, *args, **kwds)
    self.load_last_config()
    self.lb_src = wx.ListBox(self, wx.ID_ANY, choices=[])
    self.sizer_11_staticbox = wx.StaticBox(self, wx.ID_ANY, "Schedule")
    self.st_proj = wx.StaticText(self, wx.ID_ANY, "Project")
    self.tc_proj = wx.TextCtrl(self, wx.ID_ANY, self.proj)
    self.st_pi = wx.StaticText(self, wx.ID_ANY, "PI")
    self.tc_pi = wx.TextCtrl(self, wx.ID_ANY, self.pi)
    self.st_sched = wx.StaticText(self, wx.ID_ANY, "Schedule File")
    self.tc_sched = wx.TextCtrl(self, wx.ID_ANY, self.sched)
    self.bt_sched = wx.Button(self, wx.ID_ANY, "Browse", style=wx.BU_EXACTFIT)
    self.sizer_2_staticbox = wx.StaticBox(self, wx.ID_ANY, "Info")
    self.rbt_once = wx.RadioButton(self, wx.ID_ANY, "Once", style=wx.RB_GROUP)
    self.rbt_rpt = wx.RadioButton(self, wx.ID_ANY, "Repeat")
    self.panel_1 = wx.Panel(self, wx.ID_ANY)
    self.rbt_el0 = wx.RadioButton(self, wx.ID_ANY, "EL 5-85", style=wx.RB_GROUP)
    self.rbt_el1 = wx.RadioButton(self, wx.ID_ANY, "EL 10-80")
    self.rbt_el2 = wx.RadioButton(self, wx.ID_ANY, "EL 15-75")
    self.sizer_3_staticbox = wx.StaticBox(self, wx.ID_ANY, "Mode")
    self.bt_stop = wx.Button(self, wx.ID_ANY, "Stop", style=wx.BU_EXACTFIT)
    self.bt_restart = wx.Button(self, wx.ID_ANY, "Restart", style=wx.BU_EXACTFIT)
    self.bt_start = wx.Button(self, wx.ID_ANY, "Start", style=wx.BU_EXACTFIT)
    self.bt_status = wx.Button(self, wx.ID_ANY, "Observation Stopped")
    self.sizer_4_staticbox = wx.StaticBox(self, wx.ID_ANY, "")
    self.log = wx.TextCtrl(self, wx.ID_ANY, '', style=wx.TE_MULTILINE | wx.TE_READONLY |
        wx.HSCROLL | wx.TE_WORDWRAP | wx.TE_LINEWRAP | wx.TE_RICH2)
    self.sizer_5_staticbox = wx.StaticBox(self, wx.ID_ANY, "Logs")

    self.FS = wx.SystemSettings_GetFont(wx.SYS_OEM_FIXED_FONT).GetPointSize()
    self.Font = wx.Font(self.FS, wx.MODERN, wx.NORMAL, wx.BOLD, False)

    self.__set_properties()
    self.__do_layout()

    self.Bind(wx.EVT_BUTTON, self.on_sched, self.bt_sched)
    self.Bind(wx.EVT_BUTTON, self.on_stop, self.bt_stop)
    self.Bind(wx.EVT_BUTTON, self.on_restart, self.bt_restart)
    self.Bind(wx.EVT_BUTTON, self.on_start, self.bt_start)

    #self.Bind(wx.EVT_RADIOBUTTON, self.on_rb)
    if self.sched:
      try:
        self.lb_src.SetItems(self.load_sources())
      except:
        self.lb_src.SetItems([])
        self.sched = ''
        self.tc_sched.SetValue(self.sched)

    pub.subscribe(self.gui_update, 'update')


  def __set_properties(self):

    self.SetTitle("Cross-Scan Observation")
    self.SetSize((750, 600))
    self.status = 0

    redir = RedirectText(self.log)
    sys.stdout = redir
    sys.stderr = redir

    self.set_rbt()

    self.bt_status.SetFont(self.Font)
    self.bt_status.SetBackgroundColour('#FF0000')
    self.bt_status.SetForegroundColour('#FFFFFF')


  def __do_layout(self):
    sz0 = wx.BoxSizer(wx.HORIZONTAL)
    sizer_1 = wx.BoxSizer(wx.VERTICAL)
    self.sizer_5_staticbox.Lower()
    sizer_5 = wx.StaticBoxSizer(self.sizer_5_staticbox, wx.VERTICAL)
    self.sizer_4_staticbox.Lower()
    sizer_4 = wx.StaticBoxSizer(self.sizer_4_staticbox, wx.VERTICAL)
    sizer_10 = wx.BoxSizer(wx.HORIZONTAL)
    self.sizer_3_staticbox.Lower()
    sizer_3 = wx.StaticBoxSizer(self.sizer_3_staticbox, wx.VERTICAL)
    sizer_9 = wx.BoxSizer(wx.HORIZONTAL)
    sizer_8 = wx.BoxSizer(wx.HORIZONTAL)
    self.sizer_2_staticbox.Lower()
    sizer_2 = wx.StaticBoxSizer(self.sizer_2_staticbox, wx.VERTICAL)
    sizer_7 = wx.BoxSizer(wx.HORIZONTAL)
    sizer_6 = wx.BoxSizer(wx.HORIZONTAL)
    self.sizer_11_staticbox.Lower()
    sizer_11 = wx.StaticBoxSizer(self.sizer_11_staticbox, wx.VERTICAL)
    sizer_11.Add(self.lb_src, 1, wx.ALL | wx.EXPAND, 3)
    sz0.Add(sizer_11, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 3)
    sizer_6.Add(self.st_proj, 0, wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
    sizer_6.Add(self.tc_proj, 1, wx.ALIGN_CENTER_VERTICAL, 0)
    sizer_6.Add(self.st_pi, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 20)
    sizer_6.Add(self.tc_pi, 1, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
    sizer_2.Add(sizer_6, 1, wx.LEFT | wx.RIGHT | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 10)
    sizer_7.Add(self.st_sched, 0, wx.BOTTOM | wx.ALIGN_CENTER_VERTICAL, 5)
    sizer_7.Add(self.tc_sched, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.ALIGN_CENTER_VERTICAL, 5)
    sizer_7.Add(self.bt_sched, 0, wx.BOTTOM | wx.ALIGN_CENTER_VERTICAL, 5)
    sizer_2.Add(sizer_7, 1, wx.LEFT | wx.RIGHT | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 10)
    sizer_1.Add(sizer_2, 0, wx.EXPAND, 0)
    sizer_8.Add(self.rbt_once, 1, 0, 0)
    sizer_8.Add(self.rbt_rpt, 1, 0, 0)
    sizer_8.Add(self.panel_1, 1, wx.EXPAND, 0)
    sizer_3.Add(sizer_8, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
    sizer_9.Add(self.rbt_el0, 1, 0, 0)
    sizer_9.Add(self.rbt_el1, 1, 0, 0)
    sizer_9.Add(self.rbt_el2, 1, 0, 0)
    sizer_3.Add(sizer_9, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, 10)
    sizer_1.Add(sizer_3, 0, wx.EXPAND, 0)
    sizer_10.Add(self.bt_stop, 1, wx.LEFT | wx.RIGHT, 5)
    sizer_10.Add(self.bt_restart, 1, wx.LEFT | wx.RIGHT, 5)
    sizer_10.Add(self.bt_start, 1, wx.LEFT | wx.RIGHT, 5)
    sizer_4.Add(sizer_10, 0, wx.EXPAND, 0)
    sizer_4.Add(self.bt_status, 0, wx.ALL | wx.EXPAND, 5)
    sizer_1.Add(sizer_4, 0, wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL, 0)
    sizer_5.Add(self.log, 1, wx.ALL | wx.EXPAND, 3)
    sizer_1.Add(sizer_5, 5, wx.EXPAND, 0)
    sz0.Add(sizer_1, 3, wx.EXPAND, 0)
    self.SetSizer(sz0)
    self.Layout()

  def load_last_config(self):
    try:
      f = open('/tmp/.cross_obs.conf')
      self.sched = f.readline()[:-1]
      self.proj = f.readline()[:-1]
      self.pi = f.readline()[:-1]
      self.mode = f.readline()[:-1].split()
      self.mode = [int(e) for e in self.mode]

    except:
      self.sched = ''
      self.proj = ''
      self.pi = ''
      self.mode = [1, 2]



  def on_sched(self, event):

    dlg = wx.FileDialog(self, 'Load Schedule File', \
        defaultDir = os.environ['HOME'] + '/Schedule', \
        style=wx.OPEN|wx.CHANGE_DIR)
    if dlg.ShowModal() == wx.ID_OK:
      self.sched = dlg.GetPath()
      self.tc_sched.SetValue(self.sched)
      self.lb_src.SetItems(self.load_sources())

    dlg.Destroy()

    event.Skip()

  def _on_stop(self):

    if self.status == 1:

      self.status = 0

      self.bt_status.SetLabel('Observation Stoppped')
      self.bt_status.SetBackgroundColour('#FF0000')
      self.bt_status.SetForegroundColour('#FFFFFF')

      stcp = stop_tcp(self)
      stcp.setDaemon(True)
      stcp.start()

      #ctg.term_obs()


  def _on_start(self):

    if self.status == 0:
      self.proj, self.pi = self.tc_proj.Value, self.tc_pi.Value
      if self.proj.split() == [] or self.pi.split() == []:
        print 'Please set the name of Project and PI.'
      else:
        GetQueue.get_queue(self.sched,
                  self.tc_proj.Value,
                  self.tc_pi.Value)
        self.load_rbt()

        self.status = 1
        self.bt_status.SetLabel('Observation Running')
        self.bt_status.SetBackgroundColour('#00FF00')
        self.bt_status.SetForegroundColour('#000000')

        with open('/tmp/.cross_obs.conf', 'w') as f:
          print >> f, self.sched
          print >> f, self.proj
          print >> f, self.pi
          print >> f, '%d %d' %(self.mode[0], self.mode[1])

        #stcp = start_tcp(self)
        #ctg.main(self.p.mode, self.p.sched + '.queue')
        stcp = Thread(target=ctg.main, name='controlTK',
            args=(self.mode, self.sched+'.queue'))
        stcp.setDaemon(True)
        stcp.start()

  def _on_restart(self):

    self._on_stop()
    self._on_start()


  def on_stop(self, event):

    self._on_stop()
    event.Skip()


  def on_start(self, event):

    self._on_start()
    event.Skip()


  def on_restart(self, event):

    self._on_restart()
    event.Skip()


  def load_sources(self):

    with open(self.sched) as f:
      srcs = f.read()[:-1].split('\n')

    srcs = [e.split()[0] for e in srcs]
    N = len(srcs)
    n = int(log10(N))+1
    fmt = '%%0%dd' %n
    idxs = [fmt %e for e in range(N)]
    l = [a+'    '+b for (a, b) in zip(idxs, srcs)]

    return l


  def set_rbt(self):

    idx0, idx1 = self.mode
    rbts = [self.rbt_once, self.rbt_rpt]
    rbts[idx0].SetValue(True)

    rbts = [self.rbt_el0, self.rbt_el1, self.rbt_el2]
    rbts[idx1].SetValue(True)


  def load_rbt(self):

    tmp = [0, 0]

    rbts = [self.rbt_once, self.rbt_rpt]
    for i in range(2):
      if rbts[i].Value == True:
        tmp[0] = i
        break

    rbts = [self.rbt_el0, self.rbt_el1, self.rbt_el2]
    for i in range(3):
      if rbts[i].Value == True:
        tmp[1] = i
        break

    self.mode = tmp


  def gui_update(self, msg):

    if 'new scan' in msg:
      idx = int(msg.split()[2])
      self.lb_src.Select(idx)
    #elif msg == 'subscan done':
      # gsfit and plot
      #pass

    elif msg == 'scan done':
      wx.Bell()

    elif msg == 'obs_complete':
      self._on_stop()
      time.sleep(0.1)


class start_tcp(Thread):

  def __init__(self, parent):
    Thread.__init__(self)
    self.__name__ = 'controlTK'
    self.setName(self.__name__)
    self.p = parent

  def run(self):

    ctg.main(self.p.mode, self.p.sched + '.queue')



class stop_tcp(Thread):

  def __init__(self, parent):
    Thread.__init__(self)
    self.__name__ = 'Stop_controlTK'
    self.setName(self.__name__)
    self.p = parent

  def run(self):

    ctg.term_obs()



class RedirectText(object):

  def __init__(self, aWxTextCtrl):
    self.out = aWxTextCtrl

  def write(self, string):
    if threading.currentThread().getName() is "MainThread":
      self.out.write(string)
      self.out.Update()
    else:
      wx.CallAfter(self.out.write, string)
      wx.CallAfter(self.out.Update)


def main():

  class App(wx.App):

    def OnInit(self):

      MyFrame(None, -1).Show()
      return True

  app = App()
  app.MainLoop()


if __name__ == "__main__":

  main()
