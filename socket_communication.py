#!/usr/bin/env python3
import sys
import time
import socket
import selectors
import libclient

class socket_communication:
    def __init__(self):
        #self.host   = '145.100.57.192'    
        self.host   = '127.0.0.1'
        self.port   = 2376
        self.valid_actions = ['get','card','stroke','contract','leader','player','claim','spel','laad','finishbid','nakaarten','nextgame', \
                              'result','seed','bid','clear','undo','redo','check']

    def create_request(self,action, value,player):
        if self.valid_actions.count(action) == 1:
            return dict( type="text/json", encoding="utf-8", content=dict(action=action, value=value, player=player),)
        else:
            return dict( type="binary/custom-client-binary-type", encoding="binary", content=bytes(action + value, encoding="utf-8"),)

    def start_connection(self,request):
        self.sel = selectors.DefaultSelector()
        self.addr = (self.host, self.port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(False)
        self.sock.connect_ex(self.addr)
        self.events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.message = libclient.Message(self.sel, self.sock, self.addr, request)
        self.sel.register(self.sock, self.events, data=self.message)


    def comm_info(self,action,value,player):
        request = self.create_request(action, value, player)
        self.start_connection(request )
        try:
            while True:
                self.events = self.sel.select(timeout=1)
                for key, mask in self.events:
                    self.message = key.data
                    try:
                        self.message.process_events(mask)
                    except Exception:
                        print( "main: error: exception for", f"{self.message.addr}:\n{traceback.format_exc()}",)
                        self.message.close()
                # Check for a socket being monitored to continue.
                if not self.sel.get_map():
                    break
        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")
        self.sel.close()
        response = self.message.response
        if player != 'M' and action != 'clear' and action != 'get' and action != 'check':   # we should check if the action is read by "all" others:
            #print('action',action,'player',player)
            value = 1
            icount = 0
            while value != 0:
               time.sleep(0.3)
               self.comm_info('check',value,player)
               #print('check',self.message.response['value'])
               value =  self.message.response['value']
               icount += 1
               # force quit after 6 second...to avoid "hanging"
               if icount > 20: value = 0
        return response

    def close_communication(self):
            self.sel.close()

# setup communication channel with other players:
#master = 'N'
#player = 'N'
#comm = socket_communication()
#for i in range(10):
#    spel = i
#    if player == master: 
#        answer = comm.comm_info('spel',spel,player)
#        print('Player',player,'put value to',answer)
#        answer = comm.comm_info('seed',123,player)
#        print('Player',player,'put value to',answer)
#    for xplayer in ['Z','O','W']:
#        answer = comm.comm_info('get','-',xplayer)
#        print(xplayer,answer)
#    for xplayer in ['Z','O','W']:
#        answer = comm.comm_info('get','-',xplayer)
#        print(xplayer,answer)
#    for xplayer in ['Z','O','W']:
#        answer = comm.comm_info('get','-',xplayer)
#        print(xplayer,answer)
#comm.close_communication()




