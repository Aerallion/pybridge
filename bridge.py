#!/usr/bin/env python3
from tkinter import *
from tkinter import messagebox
import tkinter.font as tkFont
import random
import sys
import os
import sys
import socket
import selectors
import libclient
import traceback
import numpy as np
from PIL import Image
from PIL import ImageTk
from datetime import datetime
from socket_communication import *
import math
import time


class hand:
    def __init__(self, x0, y0, dx, cdx, dy, cdy, playx, playy, hand):
        ''' '''
        self.x0=x0
        self.y0=y0
        self.dx=dx
        self.dy=dy
        self.cdx = cdx
        self.cdy = cdy
        self.playx = playx
        self.playy = playy
        self.played = None
        self.hand = hand
        self.buttons = []  # generates a list of button-ids

    def display_hand(self, c, cards, cardnames, visible):
        ddx = 0   # extra spacing between colors:
        ddy = 0
        oldcolor=cardnames[0][-1]
        for i,card in enumerate(cards):
           newcolor = cardnames[i][-1]
           if (newcolor != oldcolor):
               if ((self.hand == 'N') or (self.hand == 'S')): 
                   ddx+=self.cdx
                   ddy = 0
               else:
                   ddx = -i*self.dx  # back to base
                   ddy +=self.cdy 
               oldcolor=newcolor
           b = Button(c,image=card,borderwidth=0)
           # attach some useful information:
           b.hand = self.hand
           b.cardname = cardnames[i]
           b.xpos =  self.x0 + i*self.dx + ddx
           b.ypos =  self.y0 + i*self.dy + ddy
           b.place(x = b.xpos, y = b.ypos)
           if visible.get() == 0: b.place_forget()
           b.bind("<Button-1>", self.eventh)
           self.buttons.append(b)
    def eventh(self,event):
        ''' one of the cards in one of the hands has been cicked'''    
        pressed = event.widget   # pressed is the pressed card
        if hasattr(play_info, 'to_play'):   
            if (self.played) == None and (play_info.to_play == self.hand) and (play_info.stage != 'bidding') and (play_info.player != play_info.dummy):
                # if dummy, should be played by leader
                opp =   (play_info.player == play_info.leader) or (play_info.player == 'A') or (play_info.player == 'M')
                if (play_info.to_play != play_info.dummy) or (opp) or (play_info.stage == 'nakaarten') or (play_info.stage == 'finished'): 
                    ok = True
                    if pressed.cardname[-1:] != play_info.lead:   # check the color
                        ok = check_hand(self,play_info.lead)
                    if ok:
                        self.played = pressed  # gather the button-id
                        play_card(pressed,self.playx,self.playy)
                    else:
                        messagebox.showerror("Error", "Player should follow lead")
        else:
            messagebox.showerror("Error", "Contract and player have to be defined")
class bidding_box:
    def __init__(self):
        ''' '''
        self.played = False
        self.bids    = [ '1KBB', '1RBB', '1HBB', '1SBB', '1NBB',
                         '2KBB', '2RBB', '2HBB', '2SBB', '2NBB',
                         '3KBB', '3RBB', '3HBB', '3SBB', '3NBB',
                         '4KBB', '4RBB', '4HBB', '4SBB', '4NBB',
                         '5KBB', '5RBB', '5HBB', '5SBB', '5NBB',
                         '6KBB', '6RBB', '6HBB', '6SBB', '6NBB',
                         '7KBB', '7RBB', '7HBB', '7SBB', '7NBB']
        self.restbids = ['ALERTBB', 'STOPBB', 'XXBB', 'XBB','PASSBB']
        self.buttons = []  # generates a list of button-ids
        self.bid_img=[]
        self.dx = 30
        self.dy = 30
        self.bidlist = []
        self.redo = []
        self.redoit = False
        self.bidbut =  [] # list of button_ids!
        self.finished = False

    def display_bidbox(self,c, pp, north, east, south, west, xpos, ypos):
        self.nx = north.playx-15
        self.ny = north.playy
        self.ex = east.playx+110
        self.ey = east.playy-9
        self.sx = south.playx-15
        self.sy = south.playy+124
        self.wx = west.playx-32
        self.wy = west.playy-9
        self.north = []   #  list of North bids (in from of pressed buttons_
        self.east  = []   
        self.south = []   
        self.west  = []   
        self.bid_img=[]
        for bid in self.bids:
            img = read_resize_img(pp+bid+'.png',0.08)
            self.bid_img.append(img)
        dx = 30
        dy = 55
        startx = xpos + 5*dx
        starty = ypos
        ix = 0
        iy = 0
        bidid = 1   # start from 1 (somehow gave problems)
        for i,bid in enumerate(self.bid_img):
           b = Button(c,image=bid,borderwidth=0)
           b.bidid = bidid
           bidid += 1
           b.bidname = self.bids[i]
           b.xpos =  [startx - ix*dx]   # list to keep track of position
           b.ypos =  [starty + iy*dy]
           b.played = False   # to track if bid has been played
           b.place(x = b.xpos[0], y = b.ypos[0])
           b.bind("<Button-1>", self.bid)
           self.buttons.append(b)
           ix += 1
           if ix == 5:
               ix = 0
               iy += 1
        self.restbid_img=[]
        for bid in self.restbids:
            img = read_resize_img(pp+bid+'.png',0.06)
            self.restbid_img.append(img)
        startx = xpos + 5*dx
        starty = ypos
        ix = 0
        iy = 7
        reps = [8,8,8,8,30]   # provide multiple realisations:
        for i,bid in enumerate(self.restbid_img):
           for j in range(reps[i]):
               b = Button(c,image=bid,borderwidth=0)
               b.bidid = bidid
               bidid += 1
               b.bidname = self.restbids[i]
               b.xpos =  [startx - ix*dx]
               b.ypos =  [starty + iy*dy]
               b.played = False   # to track if bid has been played
               b.place(x = b.xpos[0], y = b.ypos[0])
               b.bind("<Button-1>", self.bid)
               self.buttons.append(b)
           ix += 1

    
    def start_bid(self):
        # avoid bid still in buffer:
        # first determine dealer position and put ??
        play_info.to_play = play_info.dealer
        set_player(play_info.to_play)
        play_info.stage = 'bidding'
           
    def bid(self,event):
        ''' one of the bid cards is pressed '''
        pressed = event.widget   # pressed is the pressed card
        if not self.finished: 
            # is the bid allowed?
            if pressed.bidname in ['XBB', 'XXBB', 'ALERTBB', 'STOPBB']:
                if not self.catch_nonbid(pressed.bidname): 
                    messagebox.showerror("Error", pressed.bidname+' not allowed')
                    return
            # was bid already placed?
            if not pressed.played:
                # is the person allowed to bid?
                if play_info.to_play == play_info.player or play_info.player == 'A' or play_info.player == 'M':
                    comm.comm_info('bid',pressed.bidid,play_info.player)
                    self.play_bid(pressed.bidid)

    def play_bid(self,bidid):
        # find the correct pressed button:
        for pressed in self.buttons:
            if pressed.bidid == bidid:
                if not pressed.played:
                    pressed.played = True
                    if play_info.to_play == 'N':
                        self.place_bid(pressed,self.north,self.nx,self.ny,-self.dx)
                    elif play_info.to_play == 'E':
                        self.place_bid(pressed,self.east,self.ex,self.ey,-self.dx)
                    elif play_info.to_play == 'S':
                        self.place_bid(pressed,self.south,self.sx,self.sy,-self.dx)
                    elif play_info.to_play == 'W':
                        self.place_bid(pressed,self.west,self.wx,self.wy,self.dx)
                    else:
                        None
                    xbid = pressed.bidname
                    # remove previous possible bids if not Pass etc., but only if not already on the board! 
                    if self.bids.count(xbid) == 1:
                        for i in range(self.bids.index(xbid)):
                            if not self.buttons[i].played: 
                                if self.buttons[i].xpos[-1] != -999:   # remove only once!
                                    self.buttons[i].xpos.append(-999)
                                    self.buttons[i].ypos.append(-999)
                                    self.buttons[i].place(x = self.buttons[i].xpos[-1], y = self.buttons[i].ypos[-1])
                    # bring to front:
                    pressed.lift()
                    # add to bid-list:
                    bidname = pressed.bidname[:pressed.bidname.find('BB')]
                    if bidname != 'ALERT' and bidname != 'STOP':
                        self.bidlist.append(bidname)
                        if self.redoit: 
                            self.redoit = False
                        else:
                            self.redo = []
                        self.bidbut.append(pressed)
                        self.check_bid()
                        # move to next player if not finished:
                        if not self.finished:
                            play_info.to_play = play_info.nextp[play_info.to_play]
                            set_player(play_info.to_play)
                            self.last_bidder = play_info.to_play

    def place_bid(self,pressed,hand,x,y,dx):
        # shift existing bids and place new bid:
        pressed.xpos.append(x)
        pressed.ypos.append(y)
        for xbid in hand:
            xpos = xbid.xpos[-1]+dx
            xbid.xpos.append(xpos)
            xbid.ypos.append(xbid.ypos[-1])
            xbid.place(x=xbid.xpos[-1],y=xbid.ypos[-1])
        pressed.place(x=x,y=y)
        hand.append(pressed)

    def check_bid(self):
        double = False
        redouble = False
        bl = self.bidlist
        if len(bl) > 3:
            if bl[-4:].count('PASS') == 4:
                # rondpas
                contract = 'rondpas'
                play_info.tcontract.set(contract)
                xplayer = '-'
                play_info.tplayer.set(xplayer)
                self.finished = True   # signal to stop looking for bids

            if bl[-3:].count('PASS') == 3:
                # determine the last color bid:
                for i in range(len(bl), 0, -1):
                    if not bl[i-1] in ['PASS', 'X', 'XX']:
                        contract = bl[i-1]
                        color = contract[1:]  # S, R, H, K, N
                        break
                # who playes?
                # color = contract[1:]   # S,R,H,K,N
                bidnr = bl.index(contract) # the last time color was called
                winbid = bidnr
                while bidnr > 0:
                    bidnr -= 2
                    if bl[bidnr][1:] == color: winbid = bidnr
                xplayer = play_info.dealer
                for i in range(winbid): xplayer = play_info.nextp[xplayer]

                if contract[1:2] == 'N': contract = contract[0:1]+'SA'

                if bl[-4] == 'X':
                    double = True
                    contract = contract + ' X'
                elif bl[-4] == 'XX':
                    redouble = True
                    contract = contract + ' XX'

                play_info.tcontract.set(contract)
                play_info.tplayer.set(xplayer)
                self.finished = True   # signal to stop looking for bids
                # propress player to avoid redo/undo problems
                self.last_bidder = play_info.to_play
                play_info.to_play = play_info.nextp[play_info.to_play]
                set_player(play_info.to_play)

    def finish_bid(self): 
        # clear bidding box:
        for b in self.buttons:
            b.xpos.append(-999)
            b.ypos.append(-999)
            b.place(x = b.xpos[-1], y = b.ypos[-1])
        play_info.stage = 'playing'
        play_info.start_play()

    def catch_nonbid(self, pb):
        # to catch non-color bid and prepare action
        sl = self.bidlist
        if len(sl) == 0:
            alw = False
        if len(sl) == 1:
            if pb == 'XBB' and sl[-1] != 'PASS':
                alw = True
            else:
                alw = False
        if len(sl) == 2:
            if pb == 'XBB':
                alw = True
                if sl[-1] in ['X', 'XX', 'PASS']:
                    alw = False
            if pb == 'XXBB':
                if sl[-1] == 'X':
                    alw = True
                else:
                    alw = False
        if len(sl) > 2:
            if pb == 'XBB':
                alw = True
                if sl[-1] in ['X', 'XX', 'PASS']:
                    alw = False
                if sl[-1] == 'PASS' and sl[-2] == 'PASS':
                    if not sl[-3] in ['X', 'XX', 'PASS']:
                        alw = True
            if pb == 'XXBB':
                if sl[-1] == 'X' or (sl[-3] == 'X' and not sl[-2] == 'XX'):
                    alw = True
                else:
                    alw = False
        # future use?
        if pb == 'ALERTBB':
            alw = True
        if pb == 'STOPBB':
            alw = True
 
        return alw

    def take_back(self):
        if self.finished:    # 3xPass but not yet clicked on Canvas to finalize bidding
            play_info.tcontract.set('')
            play_info.tplayer.set('')
            self.finished = False
        if len(self.bidbut) > 0:
            b = self.bidbut[-1]
            b.played = False
            play_info.to_play = play_info.prevp[play_info.to_play]
            set_player(play_info.to_play)
            if play_info.to_play == 'N':
                b,self.north = self.unplace_bid(b,self.north,self.dx)
            elif play_info.to_play == 'E':
                b,self.east = self.unplace_bid(b,self.east,self.dx)
            elif play_info.to_play == 'S':
                b,self.south = self.unplace_bid(b,self.south,self.dx)
            elif play_info.to_play == 'W':
                b,self.west = self.unplace_bid(b,self.west,-self.dx)
            else:
                None
            self.redo.append(self.bidbut[-1].bidid)
            self.bidbut = self.bidbut[:len(self.bidbut)-1]
            self.bidlist = self.bidlist[:len(self.bidlist)-1]
            # replace bidbox values
            xbid = b.bidname
            if self.bids.count(xbid) == 1:   # is it 1K-->7Ha?
                for i in range(self.bids.index(xbid)-1,-1,-1):
                    if len(self.buttons[i].xpos) > 1:    # bid was moved
                        if self.buttons[i].xpos[-1] == -999:    # bid is outside field
                            xpos = self.buttons[i].xpos[-2]
                            ypos = self.buttons[i].ypos[-2]
                            self.buttons[i].place(x = xpos,y=ypos)
                            self.buttons[i].lower()
                            self.buttons[i].xpos = self.buttons[i].xpos[:len(self.buttons[i].xpos)-1]
                            self.buttons[i].ypos = self.buttons[i].ypos[:len(self.buttons[i].ypos)-1]
                        else:
                            break


    def unplace_bid(self,pressed,hand,dx):
        # shift existing bids and place new bid:
        xpos = pressed.xpos[-2]
        ypos = pressed.ypos[-2]
        pressed.place(x = xpos,y=ypos)
        pressed.lower()
        pressed.xpos = pressed.xpos[:len(pressed.xpos)-1]
        pressed.ypos = pressed.ypos[:len(pressed.ypos)-1]
        for xbid in hand[:-1]: 
            xpos = xbid.xpos[-2]
            ypos = xbid.ypos[-2]
            xbid.place(x=xpos,y=ypos)
            xbid.xpos = xbid.xpos[:len(xbid.xpos)-1]
            xbid.ypos = xbid.ypos[:len(xbid.ypos)-1]
        hand = hand[:len(hand)-1]
        return pressed,hand

    def resume_bidding(self):
        play_info.stage = 'bidding' 
        play_info.tcontract.set('')
        play_info.tplayer.set('')
        play_info.play_started = False
        self.finished = False
        play_info.to_play = play_info.nextp[self.last_bidder]
        set_player(play_info.to_play)
        for b in self.buttons:
            xpos = b.xpos[-2]
            ypos = b.ypos[-2]
            b.place(x = xpos,y=ypos)
            #buttons[i].lower()
            b.xpos = b.xpos[:len(b.xpos)-1]
            b.ypos = b.ypos[:len(b.ypos)-1]
        self.take_back()



class logistics:
    def __init__(self):
        self.passcount = 0
        self.highrank = -1
        self.dblok = False
        self.rdblok = False
        self.bidready = False
        self.xbid = 0
        self.ybid = 0
        # to read in:
        self.player = '-'
        self.vuln = '---'
        self.dealer = "---"
        self.dealerpos = 1
        self.leader = "---"
        self.contract = "---"
        self.game = "-"
        self.master = False
        self.deal = []
        self.play_started = False
        self.seed = 0
        self.dread = False
        self.stage = 'getplay'   
        self.lead   = ' '   # lead color
        self.next_game = False
        self.to_play = '-'
        self.dummy = '-'
        self.score = 0
        self.follow_action = False

    
    def draw_info(self, c):
        fontStyle32 = tkFont.Font(family="Inconsolata", size=32)
        self.bigtext = Label(c, text = "", font = fontStyle32, bg = 'deep sky blue')  # to follow the player...
        #self.bigtext.place(x = 10, y = 10)
        fontStyle = tkFont.Font(family="Inconsolata", size=10)
        self.tcontract  = StringVar()
        self.wcontract = Entry(c,textvariable=self.tcontract,width=8,font = fontStyle)
        self.tplayer    = StringVar()
        self.wplayer   = Entry(c,textvariable=self.tplayer,width=2,font = fontStyle)
        self.wcontract.place(x=10, y=130)
        self.wplayer.place(x=150,y=130)
        self.ew = 0
        self.tricks_ew = Label(c, text = "%2i"%self.ew, font = fontStyle, bg = 'green', fg = 'white')
        self.tricks_ew.place(x=220,y=47)
        self.ns = 0
        self.tricks_ns = Label(c, text = "%2i"%self.ns, font = fontStyle, bg = 'green', fg = 'white')
        self.tricks_ns.place(x=220,y=7)
        # some counters
        self.ncards = 0   # number of valid cards played
        self.allcards = 0 # total of the 52 cards to be played
        nesw = ['N','E','S','W']
        eswn = ['E','S','W','N']
        self.nextp = dict(zip(nesw,eswn))
        self.prevp = dict(zip(eswn,nesw))
        # dictionary of card values to determine trick winner:
        xval = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
        val = np.arange(13)
        self.vald = dict(zip(xval,val))
        # button to click to view all hands:
        self.claimed   = False
        self.next_game = False
        self.redid     = False
        self.finished  = False
        if self.master:
            fontStyle = tkFont.Font(family="Inconsolata", size=10)
            self.afterplay = IntVar(value=0)
            self.afterplayw = Checkbutton(c, text='Nakaarten', font = fontStyle, variable=self.afterplay, command = self.after_play)
            self.afterplayw.place(x=950,y=150)
            self.claim = IntVar(value=0)
            self.claimw = Checkbutton(c, text='Claim', font = fontStyle, variable=self.claim, command= self.claim_tricks)
            self.claimw.place(x=950,y=125)
            self.wnext = Button(c,text="Next game",font = fontStyle, command=self.play_next_game)
            self.wnext.place(x=950,y=60)
            self.wend = Button(c,text="Stop",font = fontStyle, command=self.stop_game)
            self.wend.place(x=950,y=90)
            self.hand   = '-'     # will contain the hand that plays


    def start_play(self):
        ''' routine to prepare for play: set contract, player, and lead'''
        if self.play_started == False:
            self.play_started = True
            contract = self.tcontract.get()
            try:
                ntrick = int(contract[0:1])
            except:
                if self.master: messagebox.showerror("Error", contract+" not recognized")
                self.play_started = False
                self.tricks=0
                return
            if (ntrick > 7) or (ntrick < 1):
                if self.master: messagebox.showerror("Error", contract+" not recognized")
                self.play_started = False
                self.tricks=0
                return
            else:
                self.tricks = 6+ntrick
            if contract.find('SA') >= 0:
                self.contract='SA'
            elif contract.find('R') >= 0:
                self.contract='R'
            elif contract.find('S') >= 0:
                self.contract='S'
            elif contract.find('H') >= 0:
                self.contract='H'
            elif contract.find('K') >= 0:
                self.contract='K'
            else:
                if self.master: messagebox.showerror("Error", "contract "+contract+" not recognized")
                self.play_started = False
                return
            leader = self.tplayer.get()
            leader = leader.upper()
            pall = 'NESW'
            if pall.find(leader) != -1:
                self.leader = leader
            else:    
                if self.master: messagebox.showerror("Error", "player "+player+" not recognized")
                self.leader = None
                self.play_started=False
                return
            self.to_play = self.nextp[self.leader]
            set_player(self.to_play)
            self.dummy   = self.nextp[self.to_play]   # set dummy
            if self.player == self.dummy:    # allow dummy to see all hands
                if self.player != 'N':
                   visn = Checkbutton(c, text='N', font = labelfont, variable=nvis, command = set_visibility)
                   visn.place(x = 1170, y = 105)
                if self.player != 'E':
                   vise = Checkbutton(c, text='E', font = labelfont, variable=evis, command = set_visibility)
                   vise.place(x = 1190, y = 130)
                if self.player != 'S':
                   viss = Checkbutton(c, text='S', font = labelfont, variable=svis, command = set_visibility)
                   viss.place(x = 1170, y = 155)
                if self.player != 'W':
                   visw = Checkbutton(c, text='W', font = labelfont, variable=wvis, command = set_visibility)
                   visw.place(x = 1150, y = 130)
            #if play_info.master: comm.comm_info('clean','finishbid',play_info.player)
            #if play_info.master:    # normally north writes...
            #    comm.comm_info('contract',self.tcontract.get())
            #    comm.comm_info('leader',self.tplayer.get())

    def finish_play(self):
        if not self.finished:
            self.finished = True
            if (self.ns + self.ew) == 13:
                contract = self.tcontract.get()
                # strip a possible earier result through redo/undo replays:
                if contract.find('-')  != -1: contract = contract[0:contract.find('-')]
                if contract.find('+')  != -1: contract = contract[0:contract.find('+')]
                if contract.find(' C') != -1: contract = contract[0:contract.find(' C')]
                if (self.leader == 'N') or (self.leader == 'S'):
                    result = self.ns - self.tricks
                else:
                    result = self.ew - self.tricks
                if result == 0:
                    contract_result=contract+' C'
                elif result > 0:
                    contract_result=contract+'+'+str(result)
                else:
                    contract_result=contract+'-'+str(-result)
                self.tcontract.set(contract_result)
                self.stage = 'finished'
                self.score = self.score_play(contract_result, self.vuln, self.leader)
                fontStyle = tkFont.Font(family="Inconsolata", size=10)
                c.create_text(10 ,170,anchor='nw',text= 'Score: %4i'%(self.score),font=fontStyle, fill='white')
                if hasattr(self,'perc_ns'):
                    c.create_text(110 ,170,anchor='nw',text= f'%NS {self.perc_ns} %EW {self.perc_ew}',font=fontStyle, fill='white')
                    c.create_text(10 ,190,anchor='nw',text= f'Datum: {self.datumscore} IMP NS {self.imp_ns} IMP EW {self.imp_ew}',font=fontStyle, fill='white')

            else:
                if self.master: messagebox.showerror("Error", "Play is not yet finished")
#        self.wcontract.delete(0,END)
#        self.wcontract.insert(

    def score_play(self, cn, vu, le):
        # setup booleans and down scores
        nt = False
        mi = False
        ma = False
        dbl = False
        rdbl = False
        dblist = [100, 300, 500, 800, 1100, 1400, 1700, 2000, 2300, 2600, 2900, 3200, 3500]
        xscore = 0

        # parse result in usable elements
        cnx = cn                # contract
        lvl = int(cnx[0])     # bidlevel
        trs = cnx[-2:]          # over/under tricks (string)
        if 'C' in trs:
            trx = 0
        else:
            trx = int(trs)

        if 'X' in cnx: dbl = True  # double or redouble?
        if 'XX' in cnx:
            rdbl = True
            dbl = False
        vux = vu[0:2]           # vulnerability (first 2 chars)

        # determine vulnerability of contract
        if le.upper() in vux.upper() or 'AL' in vux.upper():
            vub = 1
        else:
            vub = 0

        # determine NT, major or minor
        if 'SA' in cnx: nt = True
        if 'S' in cnx or 'H' in cnx: ma = True
        if 'K' in cnx or 'R' in cnx: mi = True

        # calculate leader score
        if trx >= 0:
            if not dbl and not rdbl:
                if mi:
                    xscore = lvl * 20 + 50 + trx * 20
                    if lvl >= 5: xscore += 250 + 200 * vub
                if ma:
                    xscore = lvl * 30 + 50 + trx * 30
                    if lvl >= 4: xscore += 250 + 200 * vub
                if nt:
                    xscore = lvl * 30 + 60 + trx * 30
                    if lvl >= 3: xscore += 250 + 200 * vub
                if lvl == 6: xscore += 500 + 250 * vub
                if lvl == 7: xscore += 1000 + 500 * vub

            if dbl:
                if mi: xscore = 2 * (lvl * 20)
                if ma: xscore = 2 * (lvl * 30)
                if nt: xscore = 2 * (lvl * 30 + 10)
                if xscore > 100:
                    xscore += 350 + 200 * vub
                else:
                    xscore += 100
                xscore += trx * (100 + 100 * vub)
                if lvl == 6: xscore += 500 + 250 * vub
                if lvl == 7: xscore += 1000 + 500 * vub

            if rdbl:
                if mi: xscore = 4 * (lvl * 20)
                if ma: xscore = 4 * (lvl * 30)
                if nt: xscore = 4 * (lvl * 30 + 10)
                if xscore > 100:
                    xscore += 400 + 200 * vub
                else:
                    xscore += 150
                xscore += trx * (200 + 200 * vub)
                if lvl == 6: xscore += 500 + 250 * vub
                if lvl == 7: xscore += 1000 + 500 * vub
        else:
            if not dbl and not rdbl:
                xscore = trx * (50 + 50 * vub)
            else:
                xscore = - dblist[abs(trx)-1]
                if abs(trx) == 1: xscore -= 100 * vub
                if abs(trx) == 2: xscore -= 200 * vub
                if abs(trx) >= 3: xscore -= 300 * vub
                if rdbl:
                    xscore = 2 * xscore
        if hasattr(self,'freq_data'):    # we can compare to available information: (to be improved!)
            implist = [0, 20, 50, 90, 130, 170, 220, 270, 320, 370, 430, 500, 600, 750, 900, 1100, 1300, 1500, 1750, 2000, 2250, 2500, 3000, 3500, 4000]
            info = self.freq_data
            #datum-score bepalen en opzoeken
            imp = 0
            gespeeld = info.T[0].sum(axis=1)
            datumtotaal = (info.T[0]*(info.T[1]-info.T[2]).T)            
            gespeeld -= info[0,0] + info[-1,0] #hoogste en laagste eraf
            datumtotaal -= info[0,0]*(info[0,1]-info[0,2]) + info[-1,0]*(info[-1,1]-info[-1,2])
            datumscore = datumtotaal/gespeeld
            datumscore = int(datumscore/10)*10 #naar beneden afronden op 10
            if le.upper() == 'N' or le.upper() == 'S':
                ns_score = xscore
            else:
                ns_score = -xscore
            if abs(ns_score - datumscore) >= 4000:
                imp = 24
            else:
                for i in range(1, len(implist)):
                    if implist[i - 1] <= abs(ns_score - datumscore) < implist[i]:
                        imp = i - 1
                        if imp < 0: imp = 0
                        break
            if (ns_score - datumscore) < 0: imp = -imp
            self.datumscore = datumscore
            self.imp_ns = imp
            self.imp_ew = - self.imp_ns

            #print(info)
            #print(gespeeld)
            #print(ns_score)
            #print(ns_score - datumscore)
            #print(self.imp_ns)
             
            if ns_score > 0:
                a = info[:,1]
                idx = np.where( a == ns_score)[0]
                if len(idx) == 1:
                    self.perc_ns = float(info[idx[0],3])
                    self.perc_ew = 100.0 - self.perc_ns
                else:
                    for i,val in enumerate(a):
                        if val < ns_score: break
                    if i == 0:
                        # 100 %
                        self.perc_ns = 100.0
                        self.perc_ew = 0.0
                    else: 
                        idx = i
                        self.perc_ns = (info[idx,3] + info[idx-1,3])*0.5
                        self.perc_ew = (info[idx,4] + info[idx-1,4])*0.5
            else:
                b = info[:,2]
                idx = np.where(b == -ns_score)[0]
                if len(idx) == 1:
                    self.perc_ns = float(info[idx[0],3])
                    self.perc_ew = 100. - self.perc_ns
                else:
                    for i,val in enumerate(b):
                        if val > -ns_score: break
                    if -ns_score > b[-1]:
                        self.perc_ns = 0.0
                        self.perc_ew = 100.0
                    else:
                        idx = i
                        self.perc_ns = (info[idx,3] + info[idx-1,3])*0.5
                        self.perc_ew = (info[idx,4] + info[idx-1,4])*0.5
        return xscore




    def after_play(self):
        if play_info.stage != 'bidding' and play_info.stage != 'playing':
 
            if not self.redid:    # quick and dirty solution till undo-redo is fixed
                after = 1
                if self.master: 
                    if self.finished:
                        after = self.afterplay.get()
                        if after == 1:
                            comm.comm_info('nakaarten','1',self.player)
                        else:
                            comm.comm_info('nakaarten','0',self.player)
                    else:
                        messagebox.showerror("Error", "Play is not yet finished")
                        self.nakaarten.set(0)
                        return
                if after == 1:
                    self.redid = True
                    # save old value:
                    self.nviso = nvis.get()
                    self.eviso = evis.get()
                    self.sviso = svis.get()
                    self.wviso = wvis.get()
                    nvis.set(1)
                    evis.set(1)
                    svis.set(1)
                    wvis.set(1)
                    set_visibility()
                    # roll back history:
                    naction = len(history.actions)
                    for i in range(naction):
                        history.do_take_back()
                    # print information on the screen:
                    if self.game.get().count('pbn') == 1:
                        self.stage = 'nakaarten'
                        fontStyle = tkFont.Font(family="Courier", size=14)
                        # create window with inofrmation!
                        self.nw = Toplevel(t,background="bisque")
                        self.nw.geometry("1200x600")
                        self.text = Text(self.nw,font=fontStyle,width=120,height=40)
                        self.text.insert(INSERT,'Contract: '+self.xcontract+' Player: '+self.declarer+'\n')
                        self.text.insert(INSERT,'Result (# tricks): '+self.xresult+'\n')
                        self.text.insert(INSERT,'First bidder: '+self.xfirstbidder+'\n')
                        for ft in self.auction:
                            self.text.insert(INSERT,ft+'\n')
                        self.text.insert(INSERT,'Outcome by '+self.xplayer+': '+self.xlead+'\n')
                        self.text.insert(INSERT,'\n')
                        for ft in self.comment:
                            self.text.insert(INSERT,ft+'\n')
                        for ft in self.freqtable:
                            self.text.insert(INSERT,ft+'\n')
                        self.text.pack()
                else:
                    nvis.set(self.nviso)
                    evis.set(self.eviso)
                    svis.set(self.sviso)
                    wvis.set(self.wviso)
                    set_visibility()
        else:
            self.afterplay.set(0)

    def claim_tricks(self):
        if play_info.stage == 'playing':
            if not self.claimed:
                if self.master:
                    if messagebox.askyesno('Claim','Agree with claim?'): 
                        comm.comm_info('claim','1',self.player)
                    else:
                        self.claim.set(0)
                        return
                self.claimed = True  # avoid repeated message box
                nvis.set(1)
                evis.set(1)
                svis.set(1)
                wvis.set(1)
                set_visibility()
                player = self.tplayer.get()
                remaining = 13 - (self.ns + self.ew)
                if remaining > 0:
                    if player == 'N' or player == 'S':
                        self.ns += remaining
                    else:
                        self.ew += remaining
                    self.tricks_ew['text']  = "%2i"%self.ew
                    self.tricks_ns['text']  = "%2i"%self.ns
                self.stage = 'afterplay'
        else:
            self.claim.set(0)

    def play_next_game(self):
        if self.master: 
            comm.comm_info('nextgame','1',self.player)
            time.sleep(1)
        time.sleep(1)
        self.next_game = True
        t.destroy()
    def stop_game(self):
        t.destroy()

def read_game():
    # master triggers this routine for other instances:
    # Allow x,X to trigger random game. Make sure you do this only once!
    if play_info.dread == False:
        play_info.dread = True
        if play_info.master:
            xplay = play_info.game.get()
            if str(xplay).upper() == 'X': 
                xx = datetime.now()
                play_info.seed = xx.microsecond
                comm.comm_info('seed',play_info.seed,play_info.player)
            comm.comm_info('spel',xplay,play_info.player)
        if play_info.seed == 0:
            xplay = str(play_info.game.get())
            if xplay.startswith('pbn'): 
                read_pbn(xplay)
            else:
                filen = ps + "Spel " + xplay + ".txt"
                if os.path.exists(filen):
                    with open(filen, "r") as g:
                        line = g.readline()
                        if line.find('Spel:') != -1:
                            play_info.game.set(line[6:])
                            dealer = g.readline()
                            play_info.info   = dealer 
                            play_info.dealer = dealer[:1]
                            play_info.vuln   = dealer[2:]
                            line = g.readline()
                            play_info.deal = [int(i)-1 for i in line.split(',')]
                else:
                    if play_info.master : messagebox.showerror("Error", f"File {filen} not found")
                    play_info.dread = False
                    return
        else:   # random game stirred by seed != 0:
            options = ['E/NS','N/--','S/EW','W/allen']
            #enforce same seed based on microseconds time
            random.seed(play_info.seed)
            dealer = options[random.randint(0,3)]
            play_info.info   = dealer 
            play_info.dealer = dealer[:1]
            play_info.vuln   = dealer[2:]
            deal = np.arange(52)
            random.shuffle(deal)
            play_info.deal = deal.tolist()
        # create and show deal:
        card_info.create_deal(play_info.deal,pp)
        north.display_hand(c,card_info.cin,card_info.cardsn,nvis)
        north.cards = card_info.cardsn
        south.display_hand(c,card_info.cis,card_info.cardss,svis)
        south.cards = card_info.cardss
        east.display_hand(c,card_info.cie,card_info.cardse,evis)
        east.cards = card_info.cardse
        west.display_hand(c,card_info.ciw,card_info.cardsw,wvis)
        west.cards = card_info.cardsw
        # set_up bidding box
        play_info.draw_info(c)
        bidbox.display_bidbox(c,pp,north,east,south,west, 1145, 190)
        playfield.set_contract(play_info.game.get(),play_info.dealer+'/'+play_info.vuln)
        playfield.indicate_vuln(play_info.vuln)
        bidbox.start_bid()

def read_pbn(play):
    play = play[3:]
    with open(ps+'test.pbn','rb') as f:
        lines = f.read().decode(errors='replace').split('\r\n')
    diamond = '◆'
    club    = '♣'
    spade   = '♠'
    heart   = '♥'
    i = 0
    for i,line in enumerate(lines):
        print(line)
        if line.count('Board ') == 1: 
            board = get_value(line)
            if board == play:
                for j,line in enumerate(lines[i:]):
                    if line.count('Dealer ') == 1: 
                       dealer = get_value(line)
                       if dealer == 'S': dealer = 'S'
                       if dealer == 'E': dealer = 'E'
                       play_info.dealer = dealer
                    if line.count('Vulnerable ') == 1: 
                       vuln = get_value(line)
                       if vuln == 'None': vuln = '--'
                       if vuln == 'All': vuln = 'allen'
                       if vuln == 'NS': vuln = 'NS'
                       if vuln == 'EW': vuln = 'EW'
                       play_info.vuln = vuln
                    if line.count('Deal ') == 1: 
                       xplay = get_value(line)
                       decode_play(xplay)
                    if line.count('Declarer ') == 1:
                       play_info.declarer = get_value(line)
                    if line.count('Contract ') == 1:
                       play_info.xcontract = get_value(line)
                    if line.count('Result ') == 1:
                       play_info.xresult = get_value(line)
                    if line.count('Auction ') == 1:
                       play_info.xfirstbidder = get_value(line)
                       play_info.auction = []
                       for k in range(1,30):
                           if (lines[i+j+k].count('Play ') == 1): break
                           play_info.auction.append(lines[i+j+k])
                    if line.count('Play ') == 1:
                       play_info.xplayer = get_value(line)
                       play_info.xlead = lines[i+j+1]
                    if line.count('{Comment:') == 1:
                       play_info.comment = []
                       for k in range(1,30):
                           if (lines[i+j+k].count('}') == 1): break
                           xxline = lines[i+j+k].replace('\D',diamond).replace('\C',club).replace('\H',heart).replace('\S',spade)
                           play_info.comment.append(xxline)
                    if line.count('[FreqTable ') == 1:
                       play_info.freqtable = []
                       info = []
                       for k in range(1,40):
                           if (lines[i+j+k].count('}') == 1): break
                           play_info.freqtable.append(lines[i+j+k])
                           if k > 1: 
                               vals = lines[i+j+k].split(' ')
                               infoline = []
                               for val in vals:
                                   if val != '': infoline.append(int(val))
                               info.append(infoline)
                       info = np.asmatrix(info)
                       play_info.freq_data = info
                       return


def get_value(line):
    print(line)
    idx = line.index('"') 
    idx2 = line.index('"',idx+1)
    return line[idx+1:idx2]

def decode_play(xplay):
    col = ['S','H','R','K']
    hand = xplay[0:1]
    xplay = xplay[2:]
    vv = []
    dh = xplay.split(' ')
    for hh in dh:
        xh = hh.split('.')
        for c,xx in zip(col,xh):
            for i in xx:
                if i == 'T':
                    card = '10'+c
                else:
                    card = i+c
                vv.append(card_info.dicards[card])
    vv = np.array(vv)
    if hand == 'N': play_info.deal = vv.tolist()
    if hand == 'E': play_info.deal = np.roll(vv,13).tolist()
    if hand == 'S': play_info.deal = np.roll(vv,26).tolist()
    if hand == 'W': play_info.deal = np.roll(vv,39).tolist()

class create_playfield:
    def __init__(self, c, pics):
        #fontStyle = tkFont.Font(family="Lucida Grande", size=28)
        fontStyle = tkFont.Font(family="Inconsolata", size=10)
        x1 = 362; x2 = 842
        y1 = 212; y2 = 614
        c.create_rectangle(x1,y1,x2,y2, outline="green4", fill="dark green", width=0)
        dx = 100; dy = 100

        fontStyle = tkFont.Font(family="Inconsolata", size=32)
        c.create_text((x1+x2)/2,y1+dy,text='N',font=fontStyle, fill='white')
        c.create_text((x1+x2)/2,y2-dy,text='S',font=fontStyle, fill='white')
        c.create_text(x2-dx,(y1+y2)/2,text='E',font=fontStyle, fill='white')
        c.create_text(x1+dx,(y1+y2)/2,text='W',font=fontStyle, fill='white')
        # position of the player box: 
        dd = 24
        ddx = 16
        self.nxpos =  (x1+x2)/2-ddx; self.nypos = y1+dy - dd
        self.expos =  x2-dx    -ddx; self.eypos = (y1+y2)/2 - dd
        self.sxpos =  (x1+x2)/2-ddx; self.sypos = y2-dy - dd
        self.wxpos =  x1+dx    -ddx; self.wypos = (y1+y2)/2 - dd
        c.create_image((x1+x2)/2, y1+35, image=pics[0])
        c.create_image(x2-35, (y1+y2)/2, image=pics[1])
        c.create_image((x1+x2)/2, y2-35, image=pics[2])
        c.create_image(x1+35, (y1+y2)/2, image=pics[3])

    def write_dummy(self,hand):
        fontStyle = tkFont.Font(family="Inconsolata", size=20, weight=tkFont.BOLD)
        if hand == 'N':
            c.create_text(self.nxpos+55,self.nypos-75,anchor=NW, text='DUMMY',font = fontStyle, fill = 'white')
        elif hand == 'E':
            c.create_text(self.expos+25,self.eypos-40,anchor=NW, text='DUMMY',font = fontStyle, fill = 'white')
        elif hand == 'S':
            c.create_text(self.sxpos+55,self.sypos+90,anchor=NW, text='DUMMY',font = fontStyle, fill = 'white')
        elif hand == 'W':
            c.create_text(self.wxpos-80,self.wypos-40,anchor=NW, text='DUMMY',font = fontStyle, fill = 'white')
        else:
            None


    def set_contract(self,playnumber,dealer):
        fontStyle = tkFont.Font(family="Inconsolata", size=10)
        c.create_text(10,10,anchor=NW, text=f'Game {playnumber}',font = fontStyle, fill='white')
        c.create_text(10,50,anchor=NW, text=dealer,font = fontStyle, fill='white')
        c.create_text(10,90,anchor=NW, text='Contract',font = fontStyle, fill='white')
        c.create_text(150,90,anchor=NW, text='Player',font = fontStyle, fill='white')
        c.create_text(105,10,anchor=NW, text='Success NS',font = fontStyle, fill='white')
        c.create_text(105,50,anchor=NW, text='Success EW',font = fontStyle, fill='white')

    def indicate_vuln(self,vuln):
        x1 = 362; x2 = 842
        y1 = 212; y2 = 614
        dx = 100; dy = 100
        fontStyle = tkFont.Font(family="Inconsolata", size=32)
        if vuln == 'allen':
            c.create_text((x1+x2)/2,y1+dy,text='N',font=fontStyle, fill='orange red')
            c.create_text((x1+x2)/2,y2-dy,text='S',font=fontStyle, fill='orange red')
            c.create_text(x2-dx,(y1+y2)/2,text='E',font=fontStyle, fill='orange red')
            c.create_text(x1+dx,(y1+y2)/2,text='W',font=fontStyle, fill='orange red')
        elif vuln == 'NS':
            c.create_text((x1+x2)/2,y1+dy,text='N',font=fontStyle, fill='orange red')
            c.create_text((x1+x2)/2,y2-dy,text='S',font=fontStyle, fill='orange red')
        elif vuln == 'EW':
            c.create_text(x2-dx,(y1+y2)/2,text='E',font=fontStyle, fill='orange red')
            c.create_text(x1+dx,(y1+y2)/2,text='W',font=fontStyle, fill='orange red')
        else:
            None

    

    def play(self,event):
        w = event.widget
        if w.curselection():   # sometimes behavious is unpredictable
            check_card(w.get(w.curselection()))
        w.selection_clear(0,last=END)
        


class undo_redo:
    ''' set up undo-redo routines that take back actions '''
    def __init__(self,c):
        self.took_back = []
        self.actions   = []

        fontStyle = tkFont.Font(family="Inconsolata", size=10)
        undo = Button(c,text="Undo", font = fontStyle, command=self.take_back)
        undo.place(x = 1150, y = 10)
        redo = Button(c,text="Redo",font = fontStyle, command=self.forward)
        redo.place(x = 1150, y = 40)
        systemk = Button(c,text="Systeemkaart",font = fontStyle, command=self.systeemkaart)
        systemk.place(x = 1150, y = 70)

    def take_back(self):
        comm.comm_info('undo','1',play_info.player)
        self.do_take_back()

    def forward(self):
        comm.comm_info('redo','1',play_info.player)
        self.do_forward()

    def do_take_back(self):
        if play_info.stage == "bidding":
            bidbox.take_back()
            return
        if play_info.stage == 'playing' or play_info.stage == 'nakaarten' or play_info.stage == 'finished':
            if len(self.actions) > 0:
                if play_info.allcards == 1 and play_info.stage != 'nakaarten' and play_info.stage != 'finished':    # take back dummy
                    fontStyle = tkFont.Font(family="Inconsolata", size=20)
                    if play_info.dummy == 'N':
                        nvis.set(0)
                        c.create_text(playfield.nxpos+55,playfield.nypos-75,anchor=NW, text='DUMMY',font = fontStyle, fill = 'dark green')
                    elif play_info.dummy == 'E':
                        evis.set(0)
                        c.create_text(playfield.expos+25,playfield.eypos-40,anchor=NW, text='DUMMY',font = fontStyle, fill = 'dark green')
                    elif play_info.dummy == 'S':
                        svis.set(0)
                        c.create_text(playfield.sxpos+55,playfield.sypos+90,anchor=NW, text='DUMMY',font = fontStyle, fill = 'dark green')
                    else:
                        wvis.set(0)
                        c.create_text(playfield.wxpos-80,playfield.wypos-40,anchor=NW, text='DUMMY',font = fontStyle, fill = 'dark green')
                    set_visibility()

                action = self.actions.pop()
                if action[0] == 1:    # take back played card and reset played
                    btn = action[1]
                    raction = [1, btn, btn.xpos, btn.ypos, play_info.to_play, play_info.lead]  # command fo redo action
                    btn.place(x = action[2],y = action[3])
                    btn.xpos = action[2]
                    btn.ypos = action[3]
                    # update the player to the previous player
                    play_info.to_play = action[4]
                    play_info.lead    = action[5]
                    set_player(play_info.to_play)
                    play_info.ncards   -= 1
                    play_info.allcards -= 1
                    if btn.hand == 'N': 
                        north.played = None
                    elif btn.hand == 'S': 
                        south.played = None
                    elif btn.hand == 'E': 
                        east.played = None
                    else:  # @btn.hand == 'west': 
                        west.played = None
                elif action[0] == 2:  # replace removed trick
                    btns = action[1]
                    xpos = action[2]
                    ypos = action[3]
                    oxpos = []
                    oypos = []
                    for i,btn in enumerate(btns):
                        oxpos.append(btn.xpos)
                        oypos.append(btn.ypos)
                        btn.place(x = xpos[i], y = ypos[i])
                        btn.xpos = xpos[i]
                        btn.ypos = ypos[i]
                    raction = [2, btns, oxpos, oypos, play_info.ew,play_info.ns,play_info.lead]
                    play_info.ew = action[4]
                    play_info.ns = action[5]
                    play_info.lead =  action[6]
                    play_info.ncards   += 4
                    play_info.tricks_ew['text']  = "%2i"%play_info.ew
                    play_info.tricks_ns['text']  = "%2i"%play_info.ns
                    [north.played, south.played, east.played,  west.played] = btns
                else:
                    None
                self.took_back.append(raction)
            else:
                # go back into bidding mode, replace bidbox and take back one bid...
                if play_info.allcards == 0:
                    bidbox.resume_bidding()

    def do_forward(self):
        ''' roll forward in time, whihc is only possible right after undo actions'''
        if play_info.stage == "bidding":
            if len(bidbox.redo) > 0:
                bidid = bidbox.redo.pop()
                bidbox.redoit = True
                bidbox.play_bid(bidid)
        if play_info.stage == 'playing' or play_info.stage == 'nakaarten' or play_info.stage == 'finished':
            if len(self.took_back) > 0:
                action = self.took_back.pop()
                if action[0] == 1:    # replay the card:
                    btn = action[1]
                    raction = [1,btn,btn.xpos,btn.ypos,play_info.to_play,play_info.lead]
                    btn.place(x = action[2],y = action[3])
                    btn.xpos = action[2]
                    btn.ypos = action[3]
                    if btn.hand == 'N': north.played = btn
                    if btn.hand == 'S': south.played = btn
                    if btn.hand == 'E': east.played = btn
                    if btn.hand == 'W': west.played = btn
                    play_info.to_play = action[4]
                    play_info.lead    = action[5]
                    play_info.ncards   += 1
                    play_info.allcards += 1
                    if play_info.allcards == 1:
                        if play_info.dummy == 'N':
                            nvis.set(1)
                            playfield.write_dummy('N')
                        elif play_info.dummy == 'E':
                            evis.set(1)
                            playfield.write_dummy('E')
                        elif play_info.dummy == 'S':
                            svis.set(1)
                            playfield.write_dummy('S')
                        else:
                            wvis.set(1)
                            playfield.write_dummy('W')
                        set_visibility()
                elif action[0] == 2:  # remove trick
                    btns = action[1]
                    xpos = action[2]
                    ypos = action[3]
                    oxpos = []
                    oypos = []
                    for i,btn in enumerate(btns):
                        oxpos.append(btn.xpos)
                        oypos.append(btn.ypos)
                        btn.place(x = xpos[i], y = ypos[i])
                        btn.xpos = xpos[i]
                        btn.ypos = ypos[i]
                    [north.played, south.played, east.played,  west.played] = [None, None, None, None]
                    raction = [2,btns,oxpos,oypos,play_info.ew,play_info.ns,play_info.lead]
                    play_info.ew = action[4]
                    play_info.ns = action[5]
                    play_info.tricks_ew['text']  = "%2i"%play_info.ew
                    play_info.tricks_ns['text']  = "%2i"%play_info.ns
                    play_info.lead = action[6]
                    play_info.ncards   -= 4
                else:
                    None
                self.actions.append(raction)
            else:
                None
            #messagebox.showerror("Error", "Nothing to redo")
        #print(play_info.ncards,play_info.allcards)
        # finally set visibility according to togglebuttons:
        set_visibility()
        set_player(play_info.to_play)

    def systeemkaart(self):
        import subprocess
        cmd = ['xpdf','Systeemkaart']
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        


def read_resize_img(picfile,frac):
    img = Image.open(picfile)
    width,height = img.size
    img = img.resize((int(width*frac),int(height*frac)), Image.ANTIALIAS)
    return ImageTk.PhotoImage(img)

def play_stroke():
    played = [north.played,south.played,east.played,west.played]
    if (played.count(None) == 0) and (play_info.ncards == 4):  # double check:
        xpos = []
        ypos = []
        for card in played:
            # set to distant location: -999, keep alife for roll-back, and interferes with toggle routine
            xpos.append(card.xpos)
            ypos.append(card.ypos)
            card.xpos = -999
            card.ypos = -999
            card.place_forget()
        # store action 2: move trick and forget
        history.actions.append([2,played,xpos,ypos,play_info.ew,play_info.ns,play_info.lead])
        # account for play statistics:
        if (play_info.to_play == 'N') or (play_info.to_play == 'S'):
            play_info.ns += 1
        else:
            play_info.ew += 1
        play_info.ncards = 0
        # reset for new trick
        north.played = None
        south.played = None
        west.played = None
        east.played = None
        # update trick information:
        play_info.tricks_ew['text']  = "%2i"%play_info.ew
        play_info.tricks_ns['text']  = "%2i"%play_info.ns
        if (play_info.ns + play_info.ew) == 13 and play_info.allcards == 52:
            play_info.stage = "afterplay"
        play_info.lead = ' '
        set_player(play_info.to_play)
        history.took_back = []   # no longer allow history
    else:
        None
        #messagebox.showerror("Error", "Not all cards of this stroke are played")


def set_visibility():
    ''' use routine to set ALL visibilities; helps in undo-redo 
    routine gets the state of the toggle buttons and sets the visibility accordingly'''
    vis = [nvis.get(),evis.get(),svis.get(),wvis.get()]
    #print(vis)
    for i,hand in enumerate([north,east,south,west]):
        if vis[i] == 0: #make invisible
            for btn in hand.buttons:  # forget, unless in play position:
#                if btn.xpos != hand.playx and btn.ypos != hand.playy:
                btn.place_forget()
                if (btn.xpos == hand.playx) and (btn.ypos == hand.playy):    
                    btn.place(x=btn.xpos,y=btn.ypos)
        else:         # make visible if not played yet (otherwise -999)
            for btn in hand.buttons:
                btn.place(x=btn.xpos,y=btn.ypos)

def play_card(card,to_x,to_y):
    if play_info.allcards == 0:   # lead has been played, open dummy
        if play_info.dummy == 'N':
            nvis.set(1)
            playfield.write_dummy('N')
        elif play_info.dummy == 'E':
            evis.set(1)
            playfield.write_dummy('E')
        elif play_info.dummy == 'S':
            svis.set(1)
            playfield.write_dummy('S')
        else:
            wvis.set(1)
            playfield.write_dummy('W')
        set_visibility()
    history.actions.append([1,card,card.xpos,card.ypos,play_info.to_play,play_info.lead])
    if play_info.ncards == 0:
        play_info.lead = card.cardname[-1:]   # set color to follow for the other players 'K','R','H','S'
    # We will play: update logistics:
    # write to playinfo:
    if play_info.to_play == play_info.dummy:
        to_play =  play_info.nextp[play_info.nextp[play_info.dummy]]
    else:
        to_play = play_info.to_play

    if play_info.stage == 'nakaarten' or play_info.stage == 'finished':
        if not play_info.follow_action:   # only true player writes:
            comm.comm_info('card',card.cardname,play_info.player)
        else:
            play_info.follow_action = False
    else:
        if play_info.player == to_play or play_info.player == 'A' or play_info.player == 'M':
            comm.comm_info('card',card.cardname,play_info.player)

    play_info.ncards   += 1
    play_info.allcards += 1
    # store action type 1: move card. button & old position, the player itself, and the lead color
    card.xpos = to_x
    card.ypos = to_y
    card.place(x = to_x, y = to_y)
    if play_info.ncards == 4:   # now decide who wins the trick, update the statistics, and give winner the lead:
        play_info.to_play = who_wins()
    else:     # up to the next player:
        play_info.to_play = play_info.nextp[play_info.to_play]
        set_player(play_info.to_play)
    history.took_back = []   # no longer allow history since a new card is played

def set_player(playerx):
    play_info.bigtext['text']=playerx
    if   playerx == 'N':
        play_info.bigtext.place(x=playfield.nxpos,y=playfield.nypos)
    elif playerx == 'E':
        play_info.bigtext.place(x=playfield.expos,y=playfield.eypos)
    elif playerx == 'S':
        play_info.bigtext.place(x=playfield.sxpos,y=playfield.sypos)
    else:
        play_info.bigtext.place(x=playfield.wxpos,y=playfield.wypos)
    play_info.bigtext.lower()

def who_wins():
    # get color and values of cards..
    hands=['N','E','S','W']
    cards=[north.played.cardname,east.played.cardname,south.played.cardname,west.played.cardname]
    value = []
    for card in cards:
        color = card[-1:]
        xval  = play_info.vald[card[:-1]]
        if color == play_info.contract: 
            xval +=13   # in trump contracts
        elif color != play_info.lead:
            xval -=13   # not following and no trump played
        value.append(xval)
    return hands[np.array(value).argmax()]

def check_hand(xhand,color):
    ''' checks if a non-played card in the hand is of color: if this is the case, return False (should follow) else True'''
    ok = True
    for card in xhand.buttons:
        if (card.xpos != -999) and (card.cardname[-1:] == color): ok = False
    return ok


def clicked_canvas():     # also play trick when you click canvas (RSI prevention)
    if play_info.stage == 'playing':
        played = [north.played,south.played,east.played,west.played]
        if played.count(None) == 0:
            ## allow all players if play_info.master:
            play_stroke()
            comm.comm_info('stroke','1',play_info.player)
    elif play_info.stage == 'bidding':   # after bidding and three times PASS, we wait for canvas click to start playing
        if bidbox.finished:
            bidbox.finish_bid() 
            comm.comm_info('finishbid','1',play_info.player)
    elif play_info.stage == "afterplay":
        comm.comm_info('result','1',play_info.player)
        play_info.finish_play()
    elif play_info.stage == 'nakaarten' or play_info.stage == 'finished':
        # allow replaying:
        played = [north.played,south.played,east.played,west.played]
        if played.count(None) == 0:
            play_stroke()
            comm.comm_info('stroke','1',play_info.player)
    else:
        None
        

def readinfo():
    # general call:
    answer = comm.comm_info('get','-',play_info.player)
    action = answer['action']
    value  = answer['value']
    if action != '-':
        if action == 'seed': 
            play_info.seed =  answer['value']
        if action == 'spel': 
            play_info.game.set(value)  # put in field
            read_game()
        elif action == 'bid':
            bidbox.play_bid(value)
        elif action == 'finishbid':
            bidbox.finish_bid() 
        elif action == 'card':
            rcard = value
            if rcard != '-':
                if play_info.stage == 'nakaarten' or play_info.stage == 'finished': play_info.follow_action = True
                if north.cards.count(rcard) == 1: play_hand(north,rcard,True)
                if east.cards.count(rcard) == 1: play_hand(east,rcard,True)
                if south.cards.count(rcard) == 1: play_hand(south,rcard,True)
                if west.cards.count(rcard) == 1: play_hand(west,rcard,True)
        elif action == 'stroke':
            if value == '1': play_stroke()
        elif action == 'claim':
            if value == '1': play_info.claim_tricks()
        elif action == 'result':
            if value != '-': play_info.finish_play()
        elif action == 'nakaarten':
            if value == '1': play_info.after_play()
        elif action == 'nextgame':
            if value == '1': play_info.play_next_game()
        elif action == 'undo':
            if value == '1': history.do_take_back()
        elif action == 'redo':
            if value == '1': history.do_forward()
        else:
            None


def check_card(card):    # routine to check whether card is in hand 
    played = pcards[card]  # links to card in dealt hand
    if (north.cards.count(played) == 1):
        #print(played,card, 'north')
        play_hand(north,played,True)
    elif ( east.cards.count(played) == 1):
        #print(played,card, 'east')
        play_hand(east,played,True)
    elif (south.cards.count(played) == 1): 
        #print(played,card, 'south')
        play_hand(south,played,True)
    else: # ( west.cards.count(played) == 1):  
        #print(played,card, 'west')
        play_hand(west,played,True)

def play_hand(xhand,xplayed,force):
    ''' play card xplayed from hand xhand. force overrides checks for leader when playing dummy '''
    if hasattr(play_info, 'to_play'):
        if (xhand.played == None) and (play_info.to_play == xhand.hand) and (play_info.stage != 'bidding'):   
            # now if hand is dummy, it should be player by the player opposite: detect by visibility:
            opp =  (play_info.player == play_info.leader) or (play_info.player == 'A') or (play_info.player == 'M')
            if (play_info.to_play != play_info.dummy) or (opp) or (force == True):
                idx = xhand.cards.index(xplayed)
                # is the card still in the hand?
                if xhand.buttons[idx].xpos != -999:
                    # is the selected card in lead color if possible?
                    ok = True
                    if xhand.buttons[idx].cardname[-1:] != play_info.lead:
                        ok = check_hand(xhand,play_info.lead)
                    if ok:
                        xhand.played = xhand.buttons[idx]
                        play_card(xhand.buttons[idx],xhand.playx,xhand.playy)
                    else:
                        messagebox.showerror("Error", "Player should follow lead")
        else:
            None
        #messagebox.showerror("Error", "Card is no longer in the hand")
    else:
        messagebox.showerror("Error", "Contract and player have to be defined")

class Cards:
    ''' class to generate deal'''
    def __init__(self):
        self.test = 0

    def create_deal(self,deal,pp):
        ''' routine to transfer a deal to a list of cards and images'''
        nhand = deal[0:13]
        ehand = deal[13:26]
        shand = deal[26:39]
        whand = deal[39:52]
        nhand.sort(reverse=True)
        ehand.sort(reverse=True)
        shand.sort(reverse=True)
        whand.sort(reverse=True)
        # get card pictures:
        self.cardsn = []
        self.cardss = []
        self.cardsw = []
        self.cardse = []
        for i in range(13):
            self.cardsn.append(self.dcards[nhand[i]])
            self.cardse.append(self.dcards[ehand[i]])
            self.cardss.append(self.dcards[shand[i]])
            self.cardsw.append(self.dcards[whand[i]])
        self.cin = []
        self.cis = []
        self.ciw = []
        self.cie = []
        for card in self.cardsn:
            img = read_resize_img(pp+card+'.png',0.18)
            self.cin.append(img)
        for card in self.cardss:
            img = read_resize_img(pp+card+'.png',0.18)
            self.cis.append(img)
        for card in self.cardsw:
            img = read_resize_img(pp+card+'.png',0.18)
            self.ciw.append(img)
        for card in self.cardse:
            img = read_resize_img(pp+card+'.png',0.18)
            self.cie.append(img)


class Timer:
    def __init__(self, c):
        # create dummy label to call readinfo every 500 ms:
        self.label = Label(c, text="0 s", font="Arial 30", width=10)
        self.label.after(1000, self.refresh_label)
        comm.comm_info('clear','-','N')
    def refresh_label(self):
        readinfo()
        self.label.after(500, self.refresh_label)

def close_windows():
    print('ok')

if __name__ == "__main__":
    print( 'Number of arguments:', len(sys.argv), 'arguments.')
    print( 'Argument List:', str(sys.argv))
    allcards =  ['2R','3R','4R','5R','6R','7R','8R','9R','10R','JR','QR','KR','AR', 
                 '2K','3K','4K','5K','6K','7K','8K','9K','10K','JK','QK','KK','AK',
                 '2H','3H','4H','5H','6H','7H','8H','9H','10H','JH','QH','KH','AH',
                 '2S','3S','4S','5S','6S','7S','8S','9S','10S','JS','QS','KS','AS']
    diamonds = ['◆2','◆3','◆4','◆5','◆6','◆7','◆8','◆9','◆10','◆J','◆Q','◆K','◆A']
    clubs    = ['♣2','♣3','♣4','♣5','♣6','♣7','♣8','♣9','♣10','♣J','♣Q','♣K','♣A']
    spades   = ['♠2','♠3','♠4','♠5','♠6','♠7','♠8','♠9','♠10','♠J','♠Q','♠K','♠A']
    hearts   = ['♥2','♥3','♥4','♥5','♥6','♥7','♥8','♥9','♥10','♥J','♥Q','♥K','♥A']
    playcards = diamonds+clubs+hearts+spades
    vcards = range(52)
    dcards = dict(zip(vcards,allcards))    # library that links value to allcards
    dicards = dict(zip(allcards,vcards))    # library that links value to allcards
    pcards = dict(zip(playcards,allcards)) # library that links playcards to allcards
    # setup communication channel with other players:
    # directory of cards/bids etc.
    pp = './cards/'
    ps = './spellen/'
    # determine players for tonight, get pictures later:
    width = 70
    height = 70
    with open(os.path.expanduser('~')+'/pybridge/players.txt','r') as f:
        players = []
        for i in range(4):
            line = f.readline().split()
            players.append(line[1])

    # add to info
    card_info = Cards()
    card_info.dcards = dcards
    card_info.pcards = pcards
    card_info.dicards = dicards
    # allow nextplay
    nextplay  = True
    contracts = []
    spel = []
    vuls = []
    players = []
    scores = []
    perc_ns = []
    perc_ew = []
    imp_ns = []
    imp_ew = []
    comm = socket_communication()
    while nextplay:
        # get play information, create deal:
        t = Tk()
        # create canvas:
        play_info = logistics()
        play_info.player = sys.argv[1]
        if play_info.player == 'M': play_info.master = True
        if len(sys.argv) == 3:
            if play_info.player == sys.argv[2]: play_info.master = True
        else:
            if play_info.player == 'N' : play_info.master = True

        # set visibility using tkinter IntVar
        nvis = IntVar(value=0)
        svis = IntVar(value=0)
        evis = IntVar(value=0)
        wvis = IntVar(value=0)
        xhand = '-'
        if len(sys.argv) > 1: xhand = sys.argv[1]
        if xhand == 'N': nvis.set(1)
        if xhand == 'E': evis.set(1)
        if xhand == 'S': svis.set(1)
        if xhand == 'W': wvis.set(1)


        labelfont = tkFont.Font(family="Arial", size=10)
        # create canvas:
        c = Canvas(t, width=1350, height=820, bg="Green")
        c.bind("<Button-1>", lambda event: clicked_canvas())
        c.pack()

        # window to load game (by master only)
        if play_info.master:
            laadspel = Button(c, text=" Load game ", command=lambda: read_game())
            laadspel.place(x=950, y=10)
            laadspel.config(font=labelfont, foreground="Black", background="#DDEBF7")
        play_info.game = StringVar()
        entry1 = Entry(t,textvariable=play_info.game, font = labelfont)
        if play_info.master:
            c.create_window(1100, 20, width=50, window=entry1)

        width = 70
        height = 70
        with open('players.txt','r') as f:
            pics = []
            for i in range(4):
                line = f.readline().split()
                picfile = pp+line[1].lower()+'.png'
                img = Image.open(picfile)
                img = img.resize((width,height), Image.ANTIALIAS)
                pics.append(ImageTk.PhotoImage(img))

        playfield = create_playfield(c,pics)

        visn = Checkbutton(c, text='N', font = labelfont, variable=nvis, command = set_visibility)
        if xhand == 'N' or xhand == 'A' or xhand == 'M': visn.place(x = 1170, y = 105)
        vise = Checkbutton(c, text='E', font = labelfont, variable=evis, command = set_visibility)
        if xhand == 'E' or xhand == 'A' or xhand == 'M': vise.place(x = 1190, y = 130)
        viss = Checkbutton(c, text='S', font = labelfont, variable=svis, command = set_visibility)
        if xhand == 'S' or xhand == 'A' or xhand == 'M': viss.place(x = 1170, y = 155)
        visw = Checkbutton(c, text='W', font = labelfont, variable=wvis, command = set_visibility)
        if xhand == 'W' or xhand == 'A' or xhand == 'M': visw.place(x = 1150, y = 130)

        hand.hand = xhand 



        # setup hands:
        north = hand(250,10,40,20, 0,60, 539 ,212,'N')
        south = hand(250,620,40,20, 0,60, 539,420,'S')
        east = hand(850,210,40,20, 0,70, 679,324,'E')
        west = hand(10,210,40, 20 ,0,70, 397,324,'W')
        # set_up bidding box
        bidbox = bidding_box()

        # setup card selector:
        # set_up history for undo-redo
        history = undo_redo(c)

        timer = Timer(c)

        t.lift()
        t.mainloop()
        if hasattr(play_info,'tcontract'): 
            contracts.append(play_info.tcontract.get())
        else:
            contracts.append(' ')
        spel.append(play_info.game.get())
        vuls.append(play_info.dealer+'/'+play_info.vuln)
        players.append(play_info.leader)
        scores.append(play_info.score)
        if hasattr(play_info,'perc_ns'):
            perc_ns.append(play_info.perc_ns)
            perc_ew.append(play_info.perc_ew)
            imp_ns.append(play_info.imp_ns)
            imp_ew.append(play_info.imp_ew)
        else:
            perc_ns.append(50.0)
            perc_ew.append(50.0)
            imp_ns.append(0.0)
            imp_ew.append(0.0)
        print('Results')
        print('Game     Dealer/Vulnerable  Leader Contract+result  Score    NS%   EW%   IMP(NS) IMP(EW)')
        print('-----------------------------------------------------------------------------------------')
        for i,contract in enumerate(contracts):
            print('%6a    %14a   %2a     %8a          %5i  %4.0f  %4.0f  %4i  %4i'%(spel[i],vuls[i],players[i],contract,scores[i],perc_ns[i],perc_ew[i],imp_ns[i],imp_ew[i]))
        print('-----------------------------------------------------------------------------------------')
        ewp = np.array(perc_ew).mean()
        nsp = np.array(perc_ns).mean()
        ewimp = np.array(imp_ew).sum()
        nsimp = np.array(imp_ns).sum()
        print('Stand                                                        %4.0f  %4.0f  %4i  %4i'%(nsp,ewp,nsimp,ewimp))

        if play_info.next_game: 
            nextplay = True
        else:
            nextplay = False

    comm.close_communication()
