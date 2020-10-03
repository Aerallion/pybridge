#!/usr/bin/env python3

import sys
import socket
import selectors
import traceback

import libclient

sel = selectors.DefaultSelector()

valid_actions = ['get','card','stroke','contract','leader','player','claim','spel','laad','spelen','nakaarten','nextgame','result','seed','bid','clean']

def create_request(action, value, player):
  if valid_actions.count(action) == 1:
      return dict(
          type="text/json",
          encoding="utf-8",
          content=dict(action=action, value=value, player=player),
      )
  else:
      return dict(
          type="binary/custom-client-binary-type",
          encoding="binary",
          content=bytes(action + value, encoding="utf-8"),
      )


def start_connection(host, port, request):
  addr = (host, port)
  print("starting connection to", addr)
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.setblocking(False)
  sock.connect_ex(addr)
  events = selectors.EVENT_READ | selectors.EVENT_WRITE
  message = libclient.Message(sel, sock, addr, request)
  sel.register(sock, events, data=message)

def doit(action,value):
  request = create_request(action, value)
  start_connection(host, port, request)
  try:
      while True:
          events = sel.select(timeout=1)
          for key, mask in events:
              message = key.data
              try:
                  message.process_events(mask)
                  print('answer....xx',message.response)
              except Exception:
                  print(
                      "main: error: exception for",
                      f"{message.addr}:\n{traceback.format_exc()}",
                  )
                  message.close()
          # Check for a socket being monitored to continue.
          if not sel.get_map():
              break
  except KeyboardInterrupt:
      print("caught keyboard interrupt, exiting")
  finally:
      print('close')
      sel.close()

if len(sys.argv) != 6:
  print("usage:", sys.argv[0], "<host> <port> <action> <value> <...>")
  sys.exit(1)

host, port = sys.argv[1], int(sys.argv[2])
action, value, player = sys.argv[3], sys.argv[4], sys.argv[5]
request = create_request(action, value, player)
start_connection(host, port, request)
try:
  while True:
      events = sel.select(timeout=1)
      for key, mask in events:
          message = key.data
          try:
              message.process_events(mask)
              print('answer....xx',message.response)
          except Exception:
              print(
                  "main: error: exception for",
                  f"{message.addr}:\n{traceback.format_exc()}",
              )
              message.close()
      # Check for a socket being monitored to continue.
      if not sel.get_map():
          break
except KeyboardInterrupt:
  print("caught keyboard interrupt, exiting")
finally:
  print('close')
  sel.close()
print(message)
