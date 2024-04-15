#! /usr/bin/env python3 

import wx
import threading
import time
import random
import qrcode
import os

COLOR_RED = wx.Colour(190, 20, 20)
COLOR_BLACK = wx.Colour(0,0,0)
COLOR_GREY = wx.Colour(200, 200, 200) 
EVT_FINISH = "FINISH"
TMP_FILE = "qr.png"

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

def generateQr ():
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=20,
        border=4)

    qr.add_data("2 20'S 34 34'E")
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="red")
    img.save(TMP_FILE)


class ResultPanel (wx.Panel):

    def __init__ (self, parent=None):
        super().__init__(parent=parent)

        mySizer = wx.BoxSizer(wx.VERTICAL)
        text = wx.StaticText (self, -1, style = wx.ALIGN_CENTER)
        text.SetLabel ('Lo verás al despertar (77).')
        mySizer.Add (text, 0, wx.ALL | wx.CENTER, 10)

        generateQr ()
        png = wx.Image(TMP_FILE, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        bitmap = wx.StaticBitmap (self, -1, png, (10,5), (png.GetWidth(), png.GetHeight()))
        mySizer.Add (bitmap, 0, wx.ALL | wx.CENTER, 10)

        self.SetSizerAndFit(mySizer)
        os.unlink (TMP_FILE)

class ResultFrame(wx.Frame):
    def __init__ (self, parent=None):
        wx.Frame.__init__(self, parent, title='Lo verás al desperta (77).') 
        panel = ResultPanel (self)
        self.SetWindowStyle(wx.STAY_ON_TOP)
        self.SetClientSize(panel.GetSize())
        self.Show()


class GamePanel (wx.Panel):

    NO_OF_PHASES = 1
    PHASE_MIN = 2

    def __init__ (self, parent=None):
        super().__init__(parent=parent)

        self._currentPhase = None
        self._currentSequence = None

        mySizer = wx.BoxSizer(wx.VERTICAL)

        self._colorPanel = wx.Panel (parent=self, size= (400, 300))
        mySizer.Add(self._colorPanel, 0, wx.ALL | wx.CENTER, 10)

        self._colorPanel.SetBackgroundColour(COLOR_GREY)

        self._startBtn = wx.Button(self, label='Empezar')
        self._startBtn.Bind(wx.EVT_BUTTON, self._start)
        mySizer.Add(self._startBtn, 0, wx.ALL | wx.CENTER, 10)

        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self._blackButton = wx.Button(self, label='Negro')
        self._blackButton.Bind(wx.EVT_BUTTON, self._pressBlack)
        buttonSizer.Add (self._blackButton, 0, wx.ALL, 10)
        self._redButton = wx.Button(self, label='Rojo')
        self._redButton.Bind(wx.EVT_BUTTON, self._pressRed)
        buttonSizer.Add (self._redButton, 0, wx.ALL, 10)
        mySizer.Add (buttonSizer, 0, wx.ALIGN_CENTER)

        self._redButton.Disable()
        self._blackButton.Disable()

        self.SetSizerAndFit(mySizer)

        EVT_COLOR_RESULT(self, self._OnColorEvent)
        self._colorThread = None


    def _getSize (self):
        return self._currentPhase + self.PHASE_MIN

    def _launchThread (self):
        size = self._getSize()
        self._currentSequence = []
        events = []
        self._currentGuess = 0
        for i in range(size):
            if random.choice ([True, False]):
                self._currentSequence.append (True)
                events.append (COLOR_RED)
            else:
                self._currentSequence.append (False)
                events.append (COLOR_BLACK)

        if self._colorThread is None:
            self._colorThread = ColorThread (self, events)
        else:
            raise ValueError
            

    def _start(self, event):
        self._startBtn.Disable()
        self._currentPhase = 0
        self._launchThread ()

    def _failGame (self): 
        self._redButton.Disable ()
        self._blackButton.Disable ()
        self._startBtn.Enable ()

    def _correctGuess (self):
        self._currentGuess += 1
        size = self._getSize ()
        if self._currentGuess >= size:
            self._currentPhase += 1
            if self._currentPhase >= self.NO_OF_PHASES:
                self._redButton.Disable()
                self._blackButton.Disable()
                rFrame = ResultFrame ()
            else:
                self._launchThread ()

    def _pressRed (self, event):
        if self._currentSequence [self._currentGuess]:
            self._correctGuess ()
        else:
            self._failGame ()

    def _pressBlack (self, event):
        if not self._currentSequence [self._currentGuess]:
            self._correctGuess ()
        else:
            self._failGame ()

    def _OnColorEvent (self, event):
        if str(event.data) == EVT_FINISH:
            self._colorThread = None
            self._colorPanel.SetBackgroundColour(COLOR_GREY)
            self._redButton.Enable ()
            self._blackButton.Enable ()
        else:
            self._colorPanel.SetBackgroundColour(event.data)

def getIcon ():
    icon = wx.Icon ()
    icon.CopyFromBitmap(wx.Bitmap("LS46.png", wx.BITMAP_TYPE_ANY))
    return icon

class MainFrame (wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='Rojo o Negro')

        self.SetIcon(getIcon())
        panel = GamePanel(self)

        self.SetClientSize(panel.GetSize())

        self.Show()



if __name__ == '__main__':
    app = wx.App()
    frame = MainFrame()
    app.MainLoop()
