#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" 
11.6.2019 New version to have 8 channels /JA
"""

import tkinter as tk
import tkinter.font
from tkinter import *
import time
import random
import socket
import sys
import select
#import digipot_test as d
import digipot_2 as d
from functools import partial

# import RPi.GPIO as GPIO

# Function to run LAN communication
def count_looper(label):
    def looper():
        # Web server here
        # Wait for a connection
        readable, writable, errored = select.select(read_list, [], [], 0.5)
        # print('waiting for a connection ', readable)

        for s in readable:
            # This is used to prevent freezing to accept()
            if s is sock:
                connection, client_address = sock.accept()
                read_list.append(connection)
                print("Connection from", client_address)
            else:
                data = s.recv(1024)
                if data:
                    com = data.decode("ISO-8859-1")
                    # print(com.split(","))
                    kom = com.strip()
                    kom = kom.lower()
                    lkom = kom.split(",")
                    # print(lkom)
                    # for n in range(len(com)):
                    # com[n]=com[n].strip()
                    # com[n]=com[n].lower()
                    if (lkom[0] == 'virta'):
                        Rv = round(8.85222e-4 * float(lkom[2]) ** 2 + 2.209 * float(lkom[2]) - 0.138969)
                        if Rv < 0:
                            Rv = -1 #-1 puts on zero current and shorts the channel

                        print("Rv=" + str(Rv))
                        apply_ETH_com(int(lkom[1]), Rv)
                        s.send(data)
                    else:
                        s.send(data)
                else:
                    s.close()
                    read_list.remove(s)

        label.after(1000, looper)

    looper()


def apply_ETH_com(chan, Rv):
    if chan >= 0 and chan <= 3:
        if Rv!=-1:
            CH[chan].res = Rv
            CH[chan].updateCurrent()
            dpot.write(chan, Rv)
            GND[chan].set("ON")
            app.CHLabel[chan].config(state="normal")
        if Rv==-1:
            GND[chan].set("OFF")
            app.CHLabel[chan].config(state="disabled")
            dpot.write(chan, Rv)

    else:
        print(chan)
        # dpot.read()
        # dpot.close()


root = tk.Tk()
root.attributes('-zoomed', True)
# Destroy window titlebar
#root.overrideredirect(1)


# Extra variable for changes
class ChannelVar(tk.StringVar):
    channel = 0
    relay = 0
    # chIOparam=[("000","0"),("000","1"),("100","0"),("100","1")]
    res = 0

    def updateCurrent(self):  # Aseta resistanssista laskettu virta lukemaksi
        if self.channel == 0: self.set(("%.3f" % (-(self.res) ** 2 * 3.49753e-5 + self.res * 0.444314 + 0.333751))[0:5])
        if self.channel == 1: self.set(("%.3f" % (-(self.res) ** 2 * 3.49753e-5 + self.res * 0.444314 + 0.333751))[0:5])
        if self.channel == 2: self.set(("%.3f" % (-(self.res) ** 2 * 3.49753e-5 + self.res * 0.444314 + 0.333751))[0:5])
        if self.channel == 3: self.set(("%.3f" % (-(self.res) ** 2 * 3.49753e-5 + self.res * 0.444314 + 0.333751))[0:5])
        if self.channel == 4: self.set(("%.3f" % (-(self.res) ** 2 * 3.49753e-5 + self.res * 0.444314 + 0.333751))[0:5])
        if self.channel == 5: self.set(("%.3f" % (-(self.res) ** 2 * 3.49753e-5 + self.res * 0.444314 + 0.333751))[0:5])
        if self.channel == 6: self.set(("%.3f" % (-(self.res) ** 2 * 3.49753e-5 + self.res * 0.444314 + 0.333751))[0:5])
        if self.channel == 7: self.set(("%.3f" % (-(self.res) ** 2 * 3.49753e-5 + self.res * 0.444314 + 0.333751))[0:5])

#    def updateGND(self):
#       if self.relay==0: self.set(fg="red")
#      if self.relay==1: self.set(fg="black")

# ChannelVar are holding the current values
# These should be red continuously from the digipots in later versions
# Reset to zero
mod = ChannelVar()
mod.set("0")
CH = [ChannelVar(), ChannelVar(), ChannelVar(), ChannelVar(), ChannelVar(), ChannelVar(), ChannelVar(), ChannelVar()]
GND = [tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar()]
for i in range(0, len(CH)):
    CH[i].res = 0
    CH[i].channel = i
    CH[i].relay = 1
    CH[i].updateCurrent()
for i in range(0, len(GND)):
    GND[i].set("OFF")


def apply_ETH_com(chan, Rv):
    if Rv!=-1:
        CH[chan].res = Rv
        CH[chan].updateCurrent()
        GND[chan].set("ON")
        GND[chan].relay=0
        app.CHLabel[chan].config(state="normal")
    else:
        GND[chan].set("OFF")
        GND[chan].relay=1
        app.CHLabel[chan].config(state="disabled")


    # dpot=d.digipot(13, 11, mod.chIOparam[chan][0])

    dpot.write(chan, Rv)
    dpot.read(chan)

    # dpot.close()


# Change current value according to arrows
def chcurrent(event):
    caller = event.widget.cget("text")
    if caller == "<<": mod.res += -10
    if caller == ">>": mod.res += 10
    if caller == "<": mod.res += -1
    if caller == ">": mod.res += 1
    if caller == "0": mod.res = 0
    if caller == "50": mod.res = 128
    if caller == "100": mod.res = 255
    if mod.res < 0: mod.res = 0
    if mod.res > 255: mod.res = 255
    mod.updateCurrent()


def changeGND(channel):
    if channel.relay == 0: #Turns channel off
        dpot.write(channel.channel, -1)
        channel.relay = 1
        GND[channel.channel].set("OFF")
        app.CHLabel[channel.channel].config(state="disabled")
        #channel.updateGND()
    elif channel.relay == 1: #Turns channel on
        dpot.write(channel.channel, channel.res) #channel.res sets the relay to the last value it previously had
        channel.relay = 0
        GND[channel.channel].set("ON")
        app.CHLabel[channel.channel].config(state="normal")
        #channel.updateGND()
        
def ONOFF(onoff, channels):
    if onoff == "off":
        for channel in channels:
            dpot.write(channel.channel,-1)
            channel.relay = 1
            GND[channel.channel].set("OFF")
            app.CHLabel[channel.channel].config(state="disabled")
    elif onoff == "on":
        for channel in channels:
            dpot.write(channel.channel,channel.res)
            channel.relay = 0
            GND[channel.channel].set("ON")
            app.CHLabel[channel.channel].config(state="normal")
            
# Pop-up window to change the channel current
def changePopup(event):
    caller = int(event.widget.cget("text").split("H")[1]) - 1  # Strips channel number from the button text
    mod.channel = caller
    mod.res = CH[caller].res
    mod.updateCurrent()
    toplevel = Toplevel()
    toplevel.attributes('-zoomed', True)
    toplevel.title("Channel 1")
    toplevel.columnconfigure(0, minsize=150)
    toplevel.columnconfigure(1, minsize=160)
    toplevel.columnconfigure(2, minsize=160)
    toplevel.columnconfigure(3, minsize=160)
    toplevel.rowconfigure(0, minsize=90)
    toplevel.rowconfigure(1, minsize=90)
    toplevel.rowconfigure(2, minsize=70)
    toplevel.rowconfigure(3, minsize=70)
    toplevel.overrideredirect(1)
    # toplevel.rowconfigure(4, minsize = 70)

    # Apply changes to the channel memory but gnd is not changed
    def apply(event):
        CH[caller].res = mod.res
        CH[caller].updateCurrent()
        if CH[caller].relay==0:
            dpot.write(caller, mod.res)

    # dpot.close()
    # Popup buttons
    topLabel = Label(toplevel, font=('Helvetica', 30), text="CH" + str(caller + 1))
    topLabel.grid(column=1, row=0, sticky=N + S + E + W)
    fastDec = Button(toplevel, font=('Helvetica', 30), text="<<")
    fastDec.grid(column=0, row=0, sticky=N + S + E + W)
    fastDec.bind('<Button-1>', chcurrent)
    fastInc = Button(toplevel, font=('Helvetica', 30), text=">>")
    fastInc.grid(column=2, row=0, sticky=N + S + E + W)
    fastInc.bind('<Button-1>', chcurrent)
    label1 = Label(toplevel, font=('Helvetica', 30), textvariable=mod)
    label1.grid(column=1, row=1, sticky=N + S + E + W)
    slowDec = Button(toplevel, font=('Helvetica', 30), text="<")
    slowDec.grid(column=0, row=1, sticky=N + S + E + W);
    slowDec.bind('<Button-1>', chcurrent)
    buttonZero = Button(toplevel, font=('Helvetica', 30), text="0")
    buttonZero.grid(column=1, row=2, sticky=N + S + E + W)
    buttonZero.bind('<Button-1>', chcurrent)
    button50 = Button(toplevel, font=('Helvetica', 30), text="50")
    button50.grid(column=2, row=2, sticky=N + S + E + W)
    button50.bind('<Button-1>', chcurrent)
    button100 = Button(toplevel, font=('Helvetica', 30), text="100")
    button100.grid(column=0, row=2, sticky=N + S + E + W)
    button100.bind('<Button-1>', chcurrent)
    slowInc = Button(toplevel, font=('Helvetica', 30), text=">")
    slowInc.grid(column=2, row=1, sticky=N + S + E + W);
    slowInc.bind('<Button-1>', chcurrent)
    applyBut = Button(toplevel, font=('Helvetica', 30), text="APPLY", command=toplevel.destroy)
    applyBut.grid(column=2, row=3, sticky=N + S + E + W)
    applyBut.bind('<Button-1>', apply)
    exitBut = Button(toplevel, font=('Helvetica', 30), text="CLOSE", command=toplevel.destroy)
    exitBut.grid(column=0, row=3, sticky=N + S + E + W)


# Main screen
class Application(tk.Frame):
    #fonsize1=36
    #fontsize2=32
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.columnconfigure(0, minsize=110)
        self.columnconfigure(1, minsize=160)
        self.columnconfigure(2, minsize=90)
        self.columnconfigure(3, minsize=110)
        self.columnconfigure(4, minsize=160)
        self.columnconfigure(5, minsize=90)
        self.rowconfigure(0, minsize=74)
        self.rowconfigure(1, minsize=74)
        self.rowconfigure(2, minsize=74)
        self.rowconfigure(3, minsize=74)
        self.rowconfigure(4, minsize=74) 
        self.createWidgets()
        

    def createWidgets(self):
        global fonsize1
        global fontsize2
        fontsize1= 34
        fontsize2= 30
        self.CHLabel=[tk.Label, tk.Label, tk.Label, tk.Label, tk.Label, tk.Label, tk.Label, tk.Label] #JA
        self.CH1Button = tk.Button(self, font=('Helvetica', fontsize1), text='CH1')
        self.CH1Button.grid(column=0, row=0)
        self.CH1Button.bind('<Button-1>', changePopup)
        self.CH1Gnd = tk.Button(self, font=('Helvetica', fontsize1), textvariable=GND[0],command=partial( changeGND, CH[0]) )
        self.CH1Gnd.grid(column=2, row=0)
        self.CHLabel[0] = tk.Label(self, font=('Helvetica', fontsize2), textvariable=CH[0], anchor='e', state='disabled')
        self.CHLabel[0].grid(column=1, row=0)

        self.CH2Button = tk.Button(self, font=('Helvetica', fontsize1), text='CH2')
        self.CH2Button.grid(column=0, row=1)
        self.CH2Button.bind('<Button-1>', changePopup)
        self.CH2Gnd = tk.Button(self, font=('Helvetica', fontsize1), textvariable=GND[1], anchor='e',command=partial( changeGND, CH[1]) )
        self.CH2Gnd.grid(column=2, row=1)
        self.CHLabel[1] = tk.Label(self, font=('Helvetica', fontsize2), textvariable=CH[1], anchor='e', state='disabled')
        self.CHLabel[1].grid(column=1, row=1)

        self.CH3Button = tk.Button(self, font=('Helvetica', fontsize1), text='CH3')
        self.CH3Button.grid(column=0, row=2)
        self.CH3Button.bind('<Button-1>', changePopup)
        self.CH3Gnd = tk.Button(self, font=('Helvetica', fontsize1), textvariable=GND[2], anchor='e',command=partial( changeGND, CH[2]) )
        self.CH3Gnd.grid(column=2, row=2)
        self.CHLabel[2] = tk.Label(self, font=('Helvetica', fontsize2), textvariable=CH[2], anchor='e', state='disabled')
        self.CHLabel[2].grid(column=1, row=2)

        self.CH4Button = tk.Button(self, font=('Helvetica', fontsize1), text='CH4')
        self.CH4Button.grid(column=0, row=3)
        self.CH4Button.bind('<Button-1>', changePopup)
        self.CH4Gnd = tk.Button(self, font=('Helvetica', fontsize1), textvariable=GND[3], anchor='e',command=partial( changeGND, CH[3]) )
        self.CH4Gnd.grid(column=2, row=3)
        self.CHLabel[3] = tk.Label(self, font=('Helvetica', fontsize2), textvariable=CH[3], anchor='e', state='disabled')
        self.CHLabel[3].grid(column=1, row=3)

        self.CH5Button = tk.Button(self, font=('Helvetica', fontsize1), text='CH5')
        self.CH5Button.grid(column=3, row=0)
        self.CH5Button.bind('<Button-1>', changePopup)
        self.CH5Gnd = tk.Button(self, font=('Helvetica', fontsize1), textvariable=GND[4],command=partial( changeGND, CH[4]) )
        self.CH5Gnd.grid(column=5, row=0)
        self.CHLabel[4] = tk.Label(self, font=('Helvetica', fontsize2), textvariable=CH[4], anchor='e', state='disabled')
        self.CHLabel[4].grid(column=4, row=0)

        self.CH6Button = tk.Button(self, font=('Helvetica', fontsize1), text='CH6')
        self.CH6Button.grid(column=3, row=1)
        self.CH6Button.bind('<Button-1>', changePopup)
        self.CH6Gnd = tk.Button(self, font=('Helvetica', fontsize1), textvariable=GND[5], anchor='e',command=partial( changeGND, CH[5]) )
        self.CH6Gnd.grid(column=5, row=1)
        self.CHLabel[5] = tk.Label(self, font=('Helvetica', fontsize2), textvariable=CH[5], anchor='e', state='disabled')
        self.CHLabel[5].grid(column=4, row=1)

        self.CH7Button = tk.Button(self, font=('Helvetica', fontsize1), text='CH7')
        self.CH7Button.grid(column=3, row=2)
        self.CH7Button.bind('<Button-1>', changePopup)
        self.CH7Gnd = tk.Button(self, font=('Helvetica', fontsize1), textvariable=GND[6], anchor='e',command=partial( changeGND, CH[6]) )
        self.CH7Gnd.grid(column=5, row=2)
        self.CHLabel[6] = tk.Label(self, font=('Helvetica', fontsize2), textvariable=CH[6], anchor='e', state='disabled')
        self.CHLabel[6].grid(column=4, row=2)

        self.CH8Button = tk.Button(self, font=('Helvetica', fontsize1), text='CH8')
        self.CH8Button.grid(column=3, row=3)
        self.CH8Button.bind('<Button-1>', changePopup)
        self.CH8Gnd = tk.Button(self, font=('Helvetica', fontsize1), textvariable=GND[7], anchor='e',command=partial( changeGND, CH[7]) )
        self.CH8Gnd.grid(column=5, row=3)
        self.CHLabel[7] = tk.Label(self, font=('Helvetica', fontsize2), textvariable=CH[7], anchor='e', state='disabled')
        self.CHLabel[7].grid(column=4, row=3)

        self.Label1to4 = tk.Button(self, font=('Helvetica', fontsize2-5), text='CH1-4')
        self.Label1to4.grid(column=0, row=4)
        self.On14 = tk.Button(self, font=('Helvetica', fontsize1), text="ON",activebackground="#3BBA3B",bg="#3BBA3B",command=partial( ONOFF, "on", [CH[0],CH[1],CH[2],CH[3]]) )
        self.On14.grid(column=1, row=4)
        self.Off14 = tk.Button(self, font=('Helvetica', fontsize1), text="OFF",activebackground="#B7282C",bg="#B7282C",command=partial( ONOFF, "off", [CH[0],CH[1],CH[2],CH[3]]) )
        self.Off14.grid(column=2, row=4)
        
        self.Label5to8 = tk.Button(self, font=('Helvetica', fontsize2-5), text='CH5-8')
        self.Label5to8.grid(column=3, row=4)
        self.On58 = tk.Button(self, font=('Helvetica', fontsize1), text="ON",activebackground="#3BBA3B",bg="#3BBA3B",command=partial( ONOFF, "on", [CH[4],CH[5],CH[6],CH[7]]) )
        self.On58.grid(column=4, row=4)
        self.Off58 = tk.Button(self, font=('Helvetica', fontsize1), text="OFF",activebackground="#B7282C",bg="#B7282C",command=partial( ONOFF, "off", [CH[4],CH[5],CH[6],CH[7]]) )
        self.Off58.grid(column=5, row=4)

# Define proper channels, digipots and relays
jj = [["000", 0, 15], ["000", 1, 12], ["111", 0, 18], ["111", 1, 16]]
ja = [["000", 0, 12], ["000", 1, 15], ["100", 0, 18], ["100", 1, 16]]
jj_new = [["000", 0, 0], ["000", 1, 1], ["001", 0, 2], ["001", 1, 3], ["010", 0, 4], ["010", 1, 5], ["011", 0, 6], ["011", 1, 7]]

dpot = d.digipot(jj_new)

app = Application()
app.master.title('RPi current source 8 channel 06/2019')

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# Bind the socket to the port
#server_address = ('192.168.1.20', 15000)
server_address = (socket.gethostbyname(socket.gethostname()),15000)
#server_address = ('127.0.0.1', 15000)
sock.bind(server_address)
# sock.settimeout(1000)
# Listen for incoming connections
sock.listen(1)
read_list = [sock]
count_looper(app.CHLabel[0])
app.mainloop()
