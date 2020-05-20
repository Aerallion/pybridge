# pybridge
tkinter based bridge emulator
You can start the emulator either with a predifined deal, with a random deal, or a random deal with predefined seed. 

The idea is that you can multiple instances on a server in such a way that information flows from one instance (N, Z, O, W) to the other instances. (note that the tool is in Dutch, Z-->south, O--->east)).

You start the (4) instances on a unix-based server (e.g. with 4 different users):

> bridge_v1.py N 1123 &

> bridge_v1.py O 1123 &

> bridge_v1.py Z 1123 &

> bridge_v1.py W 1123 &

with 1123 the common random seed.

Alternatively you can define a file like "may182020", specifying predefined games.

> bridge_v1.py N f9 may182020

This looks for "Spel" number 9, and reads dealer, vulnarability, and card distribution (refer to the code to see how).

Lastly, you can play "alone":

> bridge_v1.py A 

This simply generates a random deal, and allows you to view and play from all hands.




