#!/usr/bin/env python3
from tkinter import *
from tkinter import messagebox
import tkinter.font as tkFont
import random
import sys
import os
import numpy as np
from PIL import Image
from PIL import ImageTk

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
        if (play_info.to_play == 'N') or (play_info.to_play == 'Z'):
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
        play_info.lead = ' '
        set_player(play_info.to_play)
        # render play box again...
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
        elif play_info.dummy == 'O':
            evis.set(1)
        elif play_info.dummy == 'Z':
            svis.set(1)
        else:
            wvis.set(1)
        set_visibility()
    history.actions.append([1,card,card.xpos,card.ypos,play_info.to_play,play_info.lead])
    if play_info.ncards == 0:
        play_info.lead = card.cardname[-1:]   # set color to follow for the other players 'K','R','H','S'
    # We will play: update logistics:
    # write to playinfo:
    with open('testinfo','w') as f:
        f.write(play_info.to_play+card.cardname)
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
    history.took_back = []   # no longer allow history

def set_player(playerx):
        play_info.bigtext['text']=playerx
        if   playerx == 'N':
            play_info.bigtext.place(x=playfield.nxpos,y=playfield.nypos)
        elif playerx == 'O':
            play_info.bigtext.place(x=playfield.expos,y=playfield.eypos)
        elif playerx == 'Z':
            play_info.bigtext.place(x=playfield.sxpos,y=playfield.sypos)
        else:
            play_info.bigtext.place(x=playfield.wxpos,y=playfield.wypos)

def who_wins():
    # get color and values of cards..
    hands=['N','O','Z','W']
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
    if play_info.play_started:
        played = [north.played,south.played,east.played,west.played]
        if played.count(None) == 0:
            play_stroke()
            # write to playinfo:
            with open('testinfo','w') as f:
                f.write('play_stroke')

def readinfo():
    with open('testinfo', 'r') as f:
        line = f.readline()
        if line.startswith('contract'):
            contract = line[9:line.find(' player')]
            play_info.tcontract.set(contract)
            player = line[line.find('player ')+7:]
            play_info.tplayer.set(player)
            play_info.start_play()
        else:   # events after play has started:
            if line.startswith('play_stroke'):
                play_stroke()
            elif line.startswith('N') or line.startswith('O') or line.startswith('Z') or line.startswith('W'):
                rhand = line[0:1]
                rcard = line[1:]
                if rhand == 'N':
                    play_hand(north,rcard,True)
                elif rhand == 'O':
                    play_hand(east,rcard,True)
                elif rhand == 'Z':
                    play_hand(south,rcard,True)
                else:
                    play_hand(west,rcard,True)
            elif line.startswith('result '):
                contract_result = line[line.find(' ')+1:]
                play_info.tcontract.set(contract_result)
            elif line.startswith('claim'):
                play_info.claim.set(1)
                play_info.claim_tricks()

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
    ''' play card xplayed from hand xhand. force overrides checks for leader whn playing dummy '''
    if hasattr(play_info, 'to_play'):
        if (xhand.played == None) and (play_info.to_play == xhand.hand):   
            # now if hand is dummy, it should be player by the player opposite: detect by visibility:
            opp =(((play_info.player == 'N') and (nvis.get() == 1)) or  \
                  ((play_info.player == 'O') and (evis.get() == 1)) or \
                  ((play_info.player == 'Z') and (svis.get() == 1)) or \
                  ((play_info.player == 'W') and (wvis.get() == 1)) )
            if (play_info.to_play != play_info.dummy) or (opp == True) or (force == True):
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


class undo_redo:
    ''' set up undo-redo routines that take back actions '''
    def __init__(self,c):
        self.took_back = []
        self.actions   = []
        undo = Button(c,text="Undo", command=self.take_back)
        undo.place(x = 1350, y = 20)
        redo = Button(c,text="Redo",command=self.forward)
        redo.place(x = 1350, y = 40)

    def take_back(self):
        if len(self.actions) > 0:
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
                elif btn.hand == 'Z': 
                    south.played = None
                elif btn.hand == 'O': 
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
                print(None)
            self.took_back.append(raction)
        else:
            messagebox.showerror("Error", "Nothing to take back")
        # finally set visibility according to togglebuttons:
        set_visibility()

    def forward(self):
        ''' roll forward in time, whihc is only possible right after undo actions'''
        if len(self.took_back) > 0:
            action = self.took_back.pop()
            if action[0] == 1:    # replay the card:
                btn = action[1]
                raction = [1,btn,btn.xpos,btn.ypos,play_info.to_play,play_info.lead]
                btn.place(x = action[2],y = action[3])
                btn.xpos = action[2]
                btn.ypos = action[3]
                if btn.hand == 'N': north.played = btn
                if btn.hand == 'Z': south.played = btn
                if btn.hand == 'O': east.played = btn
                if btn.hand == 'W': west.played = btn
                play_info.to_play = action[4]
                play_info.lead    = action[5]
                play_info.ncards   += 1
                play_info.allcards += 1
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
                print(None)
            self.actions.append(raction)
        else:
            messagebox.showerror("Error", "Nothing to redo")
        #print(play_info.ncards,play_info.allcards)
        # finally set visibility according to togglebuttons:
        set_visibility()
        set_player(play_info.to_play)

class hand:
    def __init__(self, c, cards, cardnames, x0, y0, dx, cdx, dy, cdy, playx, playy, hand, visible):
        ''' '''
        self.x0=x0
        self.y0=y0
        self.dx=dx
        self.dy=dy
        self.playx = playx
        self.playy = playy
        self.played = None
        self.hand = hand
        self.buttons = []  # generates a list of button-ids
        ddx = 0   # extra spacing between colors:
        ddy = 0
        oldcolor=cardnames[0][-1]
        for i,card in enumerate(cards):
           newcolor = cardnames[i][-1]
           if (newcolor != oldcolor):
               if ((hand == 'N') or (hand == 'Z')): 
                   ddx+=cdx
                   ddy = 0
               else:
                   ddx = -i*self.dx  # back to base
                   ddy +=cdy 
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
            if (self.played) == None and (play_info.to_play == self.hand):
                # if dummy, should be played by leader
                opp =(((play_info.player == 'N') and (nvis.get() == 1)) or  \
                      ((play_info.player == 'O') and (evis.get() == 1)) or \
                      ((play_info.player == 'Z') and (svis.get() == 1)) or \
                      ((play_info.player == 'W') and (wvis.get() == 1)) )
                if (play_info.to_play != play_info.dummy) or (opp == True):
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


class select_card:
    def __init__(self, c, diamonds, clubs, hearts, spades):

        xpos = 1300; dx = 30; ypos = 140
        listbox_diamonds = Listbox(c,height=13,width=4,borderwidth=1,exportselection=False)
        for entry in diamonds:
            listbox_diamonds.insert(END, entry)
        for i in range(13):
            listbox_diamonds.itemconfig(i, {'fg': 'orange red'})
            listbox_diamonds.itemconfig(i, {'bg': 'green3'})
        listbox_diamonds.place(x = xpos, y = ypos)
        listbox_diamonds.bind("<<ListboxSelect>>", self.play)

         
        listbox_clubs = Listbox(c,height=13,width=4,borderwidth=1,exportselection=False)
        for entry in clubs:
            listbox_clubs.insert(END, entry)
        for i in range(13):
            listbox_clubs.itemconfig(i, {'fg': 'grey15'})
            listbox_clubs.itemconfig(i, {'bg': 'green3'})
        listbox_clubs.place(x = xpos+dx, y = ypos)
        listbox_clubs.bind("<<ListboxSelect>>", self.play)

        listbox_hearts = Listbox(c,height=13,width=4,borderwidth=1,exportselection=False)
        for entry in hearts:
            listbox_hearts.insert(END, entry)
        for i in range(13):
            listbox_hearts.itemconfig(i, {'fg': 'red'})
            listbox_hearts.itemconfig(i, {'bg': 'green3'})
        listbox_hearts.place(x = xpos + 2*dx, y = ypos)
        listbox_hearts.bind("<<ListboxSelect>>", self.play)

        listbox_spades = Listbox(c,height=13,width=4,borderwidth=1,exportselection=False)
        for entry in spades:
            listbox_spades.insert(END, entry)
        for i in range(13):
            listbox_spades.itemconfig(i, {'fg': 'black'})
            listbox_spades.itemconfig(i, {'bg': 'green3'})
        listbox_spades.place(x = xpos + 3*dx, y = ypos)
        listbox_spades.bind("<<ListboxSelect>>", self.play)

    def play(self,event):
        w = event.widget
        if w.curselection():   # sometimes behavious is unpredictable
            check_card(w.get(w.curselection()))
        w.selection_clear(0,last=END)
        
class logistics:
    def __init__(self, c):

        fontStyle32 = tkFont.Font(family="Inconsolata", size=32)
        self.bigtext = Label(c, text = "", font = fontStyle32)  # to follow the player...
        #self.bigtext.place(x = 10, y = 10)
        fontStyle = tkFont.Font(family="Inconsolata", size=24)
        self.tcontract  = StringVar()
        self.wcontract = Entry(c,textvariable=self.tcontract,width=5,font = fontStyle)
        self.tplayer    = StringVar()
        self.wplayer   = Entry(c,textvariable=self.tplayer,width=2,font = fontStyle)
        self.wcontract.place(x=10, y=130)
        self.wplayer.place(x=150,y=130)
        self.play_started = False
        self.wstart = Button(c,text="Play",command=self.start_play)
        self.wstart.place(x=210,y=130)
        self.wfinish = Button(c,text="Finish",command=self.finish_play)
        self.wfinish.place(x=210,y=153)
        self.ew = 0
        self.tricks_ew = Label(c, text = "%2i"%self.ew, font = fontStyle, bg = 'green', fg = 'white')
        self.tricks_ew.place(x=230,y=47)
        self.ns = 0
        self.tricks_ns = Label(c, text = "%2i"%self.ns, font = fontStyle, bg = 'green', fg = 'white')
        self.tricks_ns.place(x=230,y=7)
        self.lead   = ' '   # lead color
        # some counters
        self.ncards = 0   # number of valid cards played
        self.allcards = 0 # total of the 52 cards to be played
        nesw = ['N','O','Z','W']
        eswn = ['O','Z','W','N']

        self.nextp = dict(zip(nesw,eswn))
        self.prevp = dict(zip(eswn,nesw))
        # dictionary of card values to determine trick winner:
        xval = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
        val = np.arange(13)
        self.vald = dict(zip(xval,val))
        # button to click to view all hands:

        self.afterplay = IntVar(value=0)
        self.afterplayw = Checkbutton(c, text='Nakaarten', variable=self.afterplay, command = self.after_play)
        self.afterplayw.place(x=1315,y=100)
        self.claim = IntVar(value=0)
        self.claimw = Checkbutton(c, text='Claim', variable=self.claim, command = self.claim_tricks)
        self.claimw.place(x=1315,y=80)
        self.claimed = False
        self.next_game = False
        self.wnext = Button(c,text="Volgende Spel",command=self.play_next_game)
        self.wnext.place(x=1315,y=700)
        self.wend = Button(c,text="Stop",command=self.stop_game)
        self.wend.place(x=1315,y=725)
        


    def start_play(self):
        ''' routine to prepare for play: set contract, player, and lead'''
        if self.play_started == False:
            self.play_started = True
            contract = self.tcontract.get()
            contract = contract.upper()
            try:
                ntrick = int(contract[0:1])
            except:
                messagebox.showerror("Error", contract+" not recognized")
                self.play_started = False
                self.tricks=0
                return
            if (ntrick > 7) or (ntrick < 1):
                messagebox.showerror("Error", contract+" not recognized")
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
                messagebox.showerror("Error", "contract "+contract+" not recognized")
                self.play_started = False
                return
            player = self.tplayer.get()
            player = player.upper()
            pall = 'NOZW'
            if pall.find(player) != -1:
                self.player = player
            else:    
                messagebox.showerror("Error", "player "+player+" not recognized")
                self.player = None
                self.play_started=False
            self.to_play = self.nextp[self.player]
            set_player(self.to_play)
            self.dummy   = self.nextp[self.to_play]   # set dummy
            with open('testinfo', 'w') as f:
                f.write('contract '+self.tcontract.get()+' player '+self.tplayer.get())
    def finish_play(self):
        #print(play_info.ns,play_info.ew,self.tricks)
        if (play_info.ns + play_info.ew) == 13:
            contract = self.tcontract.get()
            # strip a possible earier result through redo/undo replays:
            if contract.find('-')  != -1: contract = contract[0:contract.find('-')]
            if contract.find('+')  != -1: contract = contract[0:contract.find('+')]
            if contract.find(' C') != -1: contract = contract[0:contract.find(' C')]
            if (self.player == 'N') or (self.player == 'Z'):
                result = play_info.ns - self.tricks
            else:
                result = play_info.ew - self.tricks
            if result == 0:
                contract_result=contract+' C'
            elif result > 0:
                contract_result=contract+'+'+str(result)
            else:
                contract_result=contract+'-'+str(-result)
            self.tcontract.set(contract_result)
            with open('testinfo', 'w') as f:
                f.write('result '+contract_result)

        else:
            messagebox.showerror("Error", "Play is not yet finished")
#        self.wcontract.delete(0,END)
#        self.wcontract.insert(

    def after_play(self):
        after = self.afterplay.get()
        if after == 1:
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
                history.take_back()
        else:
            nvis.set(self.nviso)
            evis.set(self.eviso)
            svis.set(self.sviso)
            wvis.set(self.wviso)
            set_visibility()

    def claim_tricks(self):
        if not self.claimed:
            if messagebox.askyesno('Claim','Agree with claim?'):
                self.claimed = True  # avoid repeated message box
                with open('testinfo','w') as f:
                    f.write('claim')
                nvis.set(1)
                evis.set(1)
                svis.set(1)
                wvis.set(1)
                set_visibility()
                player = play_info.tplayer.get()
                remaining = 13 - (play_info.ns + play_info.ew)
                if remaining > 0:
                    if player == 'N' or player == 'Z':
                        play_info.ns += remaining
                    else:
                        play_info.ew += remaining
                    play_info.tricks_ew['text']  = "%2i"%play_info.ew
                    play_info.tricks_ns['text']  = "%2i"%play_info.ns
                #self.finish_play()
            else:
                self.claim.set(0)

    def play_next_game(self):
        self.next_game = True
        t.destroy()
    def stop_game(self):
        t.destroy()







class create_playfield:
    def __init__(self, c, pics, playnumber, dealer):
        #fontStyle = tkFont.Font(family="Lucida Grande", size=28)
        fontStyle = tkFont.Font(family="Inconsolata", size=24)
        x1 = 395; x2 = 880
        y1 = 235; y2 = 672
        c.create_rectangle(x1,y1,x2,y2, outline="green4", fill="dark green", width=0)
        dx = 100; dy = 100

        fontStyle = tkFont.Font(family="Inconsolata", size=32)
        c.create_text((x1+x2)/2,y1+dy,text='N',font=fontStyle, fill='white')
        c.create_text((x1+x2)/2,y2-dy,text='Z',font=fontStyle, fill='white')
        c.create_text(x2-dx,(y1+y2)/2,text='O',font=fontStyle, fill='white')
        c.create_text(x1+dx,(y1+y2)/2,text='W',font=fontStyle, fill='white')
        # position of the player box: 
        dd = 16
        self.nxpos =  (x1+x2)/2-dd; self.nypos = y1+dy - dd
        self.expos =  x2-dx    -dd; self.eypos = (y1+y2)/2 - dd
        self.sxpos =  (x1+x2)/2-dd; self.sypos = y2-dy - dd
        self.wxpos =  x1+dx    -dd; self.wypos = (y1+y2)/2 - dd
        c.create_image((x1+x2)/2, y1+35, image=pics[0])
        c.create_image(x2-35, (y1+y2)/2, image=pics[1])
        c.create_image((x1+x2)/2, y2-35, image=pics[2])
        c.create_image(x1+35, (y1+y2)/2, image=pics[3])
        fontStyle = tkFont.Font(family="Inconsolata", size=24)
        c.create_text(10,10,anchor=NW, text=f'Spel {playnumber}',font = fontStyle, fill='white')
        c.create_text(10,50,anchor=NW, text=dealer,font = fontStyle, fill='white')
        c.create_text(10,90,anchor=NW, text='Contract',font = fontStyle, fill='white')
        c.create_text(150,90,anchor=NW, text='Speler',font = fontStyle, fill='white')
        c.create_text(110,10,anchor=NW, text='Slagen NZ',font = fontStyle, fill='white')
        c.create_text(110,50,anchor=NW, text='Slagen OW',font = fontStyle, fill='white')
    
class Timer:
    def __init__(self, c):
        # create dummy label to call readinfo every 500 ms:
        self.label = Label(c, text="0 s", font="Arial 30", width=10)
        self.label.after(500, self.refresh_label)
        #avoid leftovers:
        f = open('testinfo','w')
        f.write('')
        f.close()
    def refresh_label(self):
        readinfo()
        self.label.after(500, self.refresh_label)

if __name__ == "__main__":
    print( 'Number of arguments:', len(sys.argv), 'arguments.')
    print( 'Argument List:', str(sys.argv))
    # allow nextplay
    nextplay  = True
    while nextplay:
        t = Tk()
        pp = "/Users/krol/bridge/kaarten_groot/"
        # deal
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
        pcards = dict(zip(playcards,allcards)) # library that links playcards to allcards
        deal = np.arange(52)
        # determine how to play: no argument: random, integer argument: random with fixed seed, 'fx file' (with x=number) read hand number x from file named file
        # e.g. ./bridge.py N f1 may18 plays N first deal from file "may182020"
        playnumber = 1
        dealer     = 'Z/OW'
        if len(sys.argv) > 2: 
            if sys.argv[2].startswith('f'):
                playnumber = int(sys.argv[2][1:])
                filen = sys.argv[3]
                if os.path.exists(filen):
                    with open(filen,'r') as f:
                        found = False
                        ix = 0
                        while not found:
                            ix += 1
                            if ix > 1000: sys.exit(f'play {playnumber} note found in file {filen}')
                            line = f.readline()
                            if line.find('Spel:') != -1:
                                xplay = int(line[6:])
                                if xplay == playnumber:   # right play found:
                                    dealer = f.readline()
                                    line = f.readline()
                                    deal = [int(i)-1 for i in line.split(',')]
                                    found = True
                                    print(dealer,playnumber)
                else:
                    print("Error", "Input for play no found "+filen)
            else:  # use seed:
                random.seed(sys.argv[2])
                random.shuffle(deal)
                deal = deal.tolist()
        else:   # no second argument: normal random
            random.shuffle(deal)
            deal = deal.tolist()

        nhand = deal[0:13]
        ehand = deal[13:26]
        shand = deal[26:39]
        whand = deal[39:52]
        nhand.sort(reverse=True)
        ehand.sort(reverse=True)
        shand.sort(reverse=True)
        whand.sort(reverse=True)
        # get card pictures:
        cardsn = []
        cardss = []
        cardsw = []
        cardse = []
        for i in range(13):
            cardsn.append(dcards[nhand[i]])
            cardse.append(dcards[ehand[i]])
            cardss.append(dcards[shand[i]])
            cardsw.append(dcards[whand[i]])
        # set visibility using tkinter IntVar
        nvis = IntVar(value=0)
        svis = IntVar(value=0)
        evis = IntVar(value=0)
        wvis = IntVar(value=0)
        xhand = '-'
        if len(sys.argv) > 1: xhand = sys.argv[1]
        if xhand == 'N': nvis.set(1)
        if xhand == 'O': evis.set(1)
        if xhand == 'Z': svis.set(1)
        if xhand == 'W': wvis.set(1)

        # create list of images of each hand to be rendered on the canvas:
        cin = []
        cis = []
        ciw = []
        cie = []
        for card in cardsn:
            img = read_resize_img(pp+card+'.jpg',0.2)
            cin.append(img)
        for card in cardss:
            img = read_resize_img(pp+card+'.jpg',0.2)
            cis.append(img)
        for card in cardsw:
            img = read_resize_img(pp+card+'.jpg',0.2)
            ciw.append(img)
        for card in cardse:
            img = read_resize_img(pp+card+'.jpg',0.2)
            cie.append(img)

        # create canvas:
        c = Canvas(t, width=1500, height=900, bg="Green")
        c.bind("<Button-1>", lambda event: clicked_canvas())
        c.pack()
        
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

        playfield = create_playfield(c,pics,playnumber,dealer)

        visn = Checkbutton(c, text='N', variable=nvis, command = set_visibility)
        if xhand == 'N' or xhand == 'A': visn.place(x = 1200, y = 180)
        vise = Checkbutton(c, text='O', variable=evis, command = set_visibility)
        if xhand == 'O' or xhand == 'A': vise.place(x = 1220, y = 200)
        viss = Checkbutton(c, text='Z', variable=svis, command = set_visibility)
        if xhand == 'Z' or xhand == 'A': viss.place(x = 1200, y = 220)
        visw = Checkbutton(c, text='W', variable=wvis, command = set_visibility)
        if xhand == 'W' or xhand == 'A': visw.place(x = 1180, y = 200)

        play_info = logistics(c)

        north = hand(c,cin,cardsn,300,10,40,20, 0,60, 570 ,235,'N',nvis)
        #add card names to the object for future better rendering:
        #def __init__(self, c, cards, cardnames, x0, y0, dx, cdx, dy, cdy, playx, playy, hand, visible):
            #c.create_rectangle(395, 235, 880, 672, outline="green4", fill="dark green", width=0)
        north.cards = cardsn
        south = hand(c,cis,cardss,300,680,40,20, 0,60, 570,457,'Z',svis)
        south.cards = cardss
        east = hand(c,cie,cardse,910,240,40,20, 0,70, 722,356,'O',evis)
        east.cards = cardse
        west = hand(c,ciw,cardsw,20,240,40, 20 ,0,70, 416,356,'W',wvis)
        west.cards = cardsw

        # setup card selector:
        card_selector = select_card(c,diamonds,clubs,hearts,spades)
        # set_up history for undo-redo
        history = undo_redo(c)

        timer = Timer(c)

        t.lift()
        t.mainloop()
        if play_info.next_game: 
            if len(sys.argv) > 2:
                if sys.argv[2].startswith('f'):
                    playnumber = int(sys.argv[2][1:]) + 1
                    sys.argv[2] = 'f'+str(playnumber)
            nextplay = True
        else:
            nextplay = False
