# imports of external packages to use in our code
import sys
from random import shuffle

# main function for our card game Python code
if __name__ == "__main__":
    # if the user includes the flag -h or --help print the options
    if '-h' in sys.argv or '--help' in sys.argv:
        print ("Usage: %s [-options]" % sys.argv[0])
        print ("  options:")
        print ("   --help(-h)          print options")
        print ("   -Ncards [number]    choose number of cards in deck")
        print ("   -gimme [number]     choose number of cards to cheat with")
        print ("   -Ngames [number]    choose number of games to play each set")
        print ("   -Nsets [number]     choose number of sets to play")
        print ("   -output [text]      name of file for output data")
        sys.exit(1)
  
    # default gimme
    gimme = 0
    
    # default number of cards
    Ncards = 20
    
    # default number of players
    n_players = 2

    # default number of games
    Ngames = 10
    
    # default number of sets
    Nsets = 10
    
    # output file defaults
    doOutputFile = False

    # read the user-provided seed from the command line (if there)
    if '-gimme' in sys.argv:
        p = sys.argv.index('-gimme')
        gm = int(sys.argv[p+1])
        if gm >= 0 and gm < Ncards+1:
            gimme = gm
    if '-Ncards' in sys.argv:
        p = sys.argv.index('-Ncards')
        nc = int(sys.argv[p+1])
        if (nc % 2) == 0:
            Ncards = nc
    if '-Ngames' in sys.argv:
        p = sys.argv.index('-Ngames')
        Ng = int(sys.argv[p+1])
        if Ng > 0:
            Ngames = Ng
    if '-Nsets' in sys.argv:
        p = sys.argv.index('-Nsets')
        Ns = int(sys.argv[p+1])
        if Ns > 0:
            Nsets = Ns
    if '-output' in sys.argv:
        p = sys.argv.index('-output')
        OutputFileName = sys.argv[p+1]
        Rulesname = "rules_" + str(OutputFileName)
        doOutputFile = True
        
# N card deck takes value input by user
class Cards:
    def __init__(self):
        n = Ncards
        values = list(range(1,n+1))
        self.deck = values

    def shuffle(self):
        shuffle(self.deck)
 
# Creates parameters for play and defines cheating
class Gameplay:
    def __init__(self):
        self.cards = Cards() 
    
    # deals deck to each player, alternating players
    def deal(self, n_players):
        self.hands = [self.cards.deck[i::n_players] for i in range(0, n_players)]
    
    # takes gimme value and gives player0 access to a deck of unusually high values
    # guaranteed to exceed any cards in deck
    def cheat(self, gimme):
        n = Ncards
        pcheat = list(range(n+2, (n+2)+(n//2)))
        p0 = self.hands[0]
        cheatCards = pcheat[:gimme]
        p0_new = p0[gimme:]
        p0_new = p0_new + cheatCards
        shuffle(p0_new)
        return p0_new
        
    # gives players hands
    def outcome(self):     
        n = Ncards
        if gimme > 0 and gimme < n+1:
            p0 = self.cheat(gimme)
        else: 
            p0 = self.hands[0]
            
        p1 = self.hands[1]
        self.difference = []
        self.winResult = 0
        
        # subtracts list p0 - p1 over all items in list to determine winner
        zip_object = zip(p0, p1)
        for p0_i, p1_i in zip_object:
            self.difference.append(p0_i-p1_i)
        for num in self.difference: 
            if num > 0: 
                self.winResult += 1
        return self.winResult
        
    def rungame(self):
        self.cards.shuffle()
        self.deal(2)
        return self.outcome()
    
    # writes to txt file from user input
    # txt file shows games in rows and sets in columns
if doOutputFile:
    outfile = open(OutputFileName, 'w')
    outfilerules = open(Rulesname, 'w')
    # records rules in separate text file for use in analysis
    outfilerules.write(str(Ncards) + "\n" + str(Ngames) + "\n" + str(Nsets) + "\n" + str(gimme))
    # outfilerules.write("Ncards[" + str(Ncards) + "]; Ngames[" + str(Ngames) + "]; Nsets[" + str(Nsets) + "]; gimme[" + str(gimme) + "]")
    for ns in range(0,Nsets):
        for ng in range(0,Ngames):
            g = Gameplay()
            outfile.write(str(g.rungame()))
            outfile.write(",")
        outfile.write("\n")
else:
    for e in range(0,Ngames):
        g = Gameplay()
        print(str(g.rungame()))
