# pybridge
## tkinter based bridge emulator

### Maarten Krol, 2020

This is a python-based multi-player bridge program, intended for playing bridge in home setting.
Each player starts an own instance of the bridge program, and communication is performed through **sockets**.
Currently, we play this on a unix-based server with a Anaconda python installation (3.6).

Each player logs into the server. Here the communication is started by:

cd bridge (this is the folder where you store the files)
./app-server 127.0.0.1 2376 &

The system should respond with: listening on ('127.0.0.1', 2376)

Subsequently, each player starts its own instance of the program:

_North_: ./bridge.py N N

_East_: ./bridge.py O N   

_South_: ./bridge.py Z N

_West_: ./bridge.py W N


So, the first argument is the player (currently, we have Dutch setting, Z = south/zuid, O = east/oost).
The second argument is the player that has control over the game, meaning that now **N** can load plays, claim tricks, etc.

To play alone, you can type:

./bridge.py M

With M = Master. To be kibitzer, you can type ./bridge.py A, which is only useful when other players are active.

Once everybody has a green screen, the "Master" (M, and in this case N) can load a game next to the button "Laad spel". There are three options.

- type a number. The program will look at predefined games named "Spel 1", when you type "1". 
- type x or X. A random deal will be generated.
- type pbnx, with "x" a number, normally between 1 and 40. This loads tournement games, retrieved from "www.vijnberg.nl".

The next step is to press the "Laad spel" button.

The rest should be self-explanatory! A few tips:

> To remove a trick, or to proceed, click on the green canvas.

> Once you want to claim all tricks as playing team, ask the "Master" to press "Claim"

> After the game finsihed, you can click "Nakaarten".

> With undo/redo you can undo or redo actions (mind the bugs!).


A next game is started by pressing: "Volgende spel" (Master only).
This will kill the existing windows and create fresh windows in which a new game can be played.
Note that in mode "pbn" the scores will appear in the unix window. This allows you to play tournements.

Happy bridge! Feedback welcome.




