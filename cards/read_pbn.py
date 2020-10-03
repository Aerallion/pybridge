import numpy as np
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
        allcards =  ['2R','3R','4R','5R','6R','7R','8R','9R','10R','JR','QR','KR','AR', 
                     '2K','3K','4K','5K','6K','7K','8K','9K','10K','JK','QK','KK','AK',
                     '2H','3H','4H','5H','6H','7H','8H','9H','10H','JH','QH','KH','AH',
                     '2S','3S','4S','5S','6S','7S','8S','9S','10S','JS','QS','KS','AS']
        vcards = range(52)
        self.dicards = dict(zip(allcards,vcards))    # library that links value to allcards
        self.dcards = dict(zip(vcards,allcards))    # library that links value to allcards
def read_pbn(play):
    play = play[3:]
    with open('test.pbn','rb') as f:
        lines = f.read().decode(errors='replace').split('\r\n')
    i = 0
    for i,line in enumerate(lines):
        if line.count('Board ') == 1: 
            board = get_value(line)
            if board == play:
                for j,line in enumerate(lines[i:]):
                    if line.count('Dealer ') == 1: 
                       dealer = get_value(line)
                       if dealer == 'S': dealer = 'Z'
                       if dealer == 'E': dealer = 'O'
                       play_info.dealer = dealer
                    if line.count('Vulnerable ') == 1: 
                       vuln = get_value(line)
                       if vuln == 'None': vuln = '--'
                       if vuln == 'All': vuln = 'allen'
                       if vuln == 'NS': vuln = 'NZ'
                       if vuln == 'EW': vuln = 'OW'
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
                           play_info.comment.append(lines[i+j+k])
                    if line.count('[FreqTable ') == 1:
                       play_info.freqtable = []
                       for k in range(1,40):
                           if (lines[i+j+k].count('}') == 1): break
                           play_info.freqtable.append(lines[i+j+k])
                       return


def get_value(line):
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
                vv.append(play_info.dicards[card])
    vv = np.array(vv)
    if hand == 'N': play_info.deal = vv.tolist()
    if hand == 'E': play_info.deal = np.roll(vv,13).tolist()
    if hand == 'S': play_info.deal = np.roll(vv,26).tolist()
    if hand == 'W': play_info.deal = np.roll(vv,39).tolist()



    


play_info = logistics()
read_pbn('pbn10')
