#! /usr/bin/env python3 

import wx
import threading
import time

COLOR_RED = wx.Colour(190, 20, 20)
COLOR_BLACK = wx.Colour(0,0,0)
COLOR_GREY = wx.Colour(200, 200, 200) 
EVT_FINISH = "FINISH"

EVT_COLOR_ID = wx.NewIdRef()

def EVT_COLOR_RESULT (win, func):
    win.Connect(-1, -1, EVT_COLOR_ID.GetId(), func)

class ColorEvent (wx.PyEvent):
    def __init__(self, data):
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_COLOR_ID.GetId())
        self.data = data

class ColorThread(threading.Thread):
    def __init__ (self, notifyWindow, events):
        threading.Thread.__init__(self)
        self._notifyWindow = notifyWindow
        self._events = events

        self.start()

    def run (self): 
        for e in self._events: 
            wx.PostEvent(self._notifyWindow, ColorEvent(COLOR_GREY))
            time.sleep(0.5)

            wx.PostEvent(self._notifyWindow, ColorEvent(e))
            time.sleep(1)
        wx.PostEvent(self._notifyWindow, ColorEvent(EVT_FINISH))




class GamePanel (wx.Panel):
    def __init__ (self, parent=None):
        super().__init__(parent=parent)

        mySizer = wx.BoxSizer(wx.VERTICAL)

        self._colorPanel = wx.Panel (parent=self, size= (200, 100))
        mySizer.Add(self._colorPanel, 0, wx.ALL | wx.CENTER, 10)

        self._colorPanel.SetBackgroundColour(COLOR_GREY)

        startBtn = wx.Button(self, label='Empezar')
        startBtn.Bind(wx.EVT_BUTTON, self._start)
        mySizer.Add(startBtn, 0, wx.ALL | wx.CENTER, 10)
        self.SetSizerAndFit(mySizer)

        EVT_COLOR_RESULT(self, self._OnColorEvent)
        self._colorThread = None

    def _start(self, event):
        if self._colorThread is None:
            self._colorThread = ColorThread (self, [COLOR_RED, COLOR_BLACK])

    def _OnColorEvent (self, event):
        if str(event.data) == EVT_FINISH:
            self._colorThread = None
            self._colorPanel.SetBackgroundColour(COLOR_GREY)
        else:
            self._colorPanel.SetBackgroundColour(event.data)

class MainFrame (wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Rojo o Negro')

        panel = GamePanel(self)

        self.SetClientSize(panel.GetSize())

        self.Show()



if __name__ == '__main__':
    app = wx.App()
    frame = MainFrame()
    app.MainLoop()
