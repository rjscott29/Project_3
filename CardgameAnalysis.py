# imports of external packages to use in our code
import sys
import math
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter

# gets rules from the text file associated with input files
def GetRules(InputFile):
    RulesFile = "rules_" + InputFile
    rules = []
    with open(RulesFile, "r") as rulesfile:
        for rule in rulesfile:
            rules.append(int(rule))
        # print("Ncards: " + str(rules[0]))
        # print("Ngames: " + str(rules[1]))
        # print("Nsets: " + str(rules[2]))
        # print("gimme: " + str(rules[3]))
    return rules

# get theoretical probability distribution based on gimme and Ncards
def TrueProbability(gimme,n):
    pdist = []
    g = np.linspace(0,gimme-1,gimme)
    x = np.linspace(gimme,n,n+1-gimme)
    # probabilities for the fair games
    p = .5
    q = 1-p
    # add 0 to pdist for number of cheating games; you'll never lose
    for i in g:
        pdist.append(0.0)
    # establish the pdist for remaining games, offset by gimme
    for i in x:
        N = n-gimme
        I = i-gimme
        # print(N)
        # print(I)
        nchoose = math.comb(int(N),int(I))
        a = (p**I)*(q**(N-I))
        pdist.append(nchoose*a)
    return pdist

# Reorganizes inputfile data for our use, outputs as tuple
def DataResults(InputFile):
    with open(InputFile,'r') as sets:
        # organizes data into tuple where each item is a set
        # removes information that is not a digit
        data = [[int(x) for x in line.split(',') if x.isdigit()] for line in sets]
        return data
    
# just gets all of the values from the tuple and compiles it
def TotalResults(DataResults):
    results = []
    for data in DataResults:
        for x in data:
            results.append(x)
    return results

# gets probability distribution of data for density plot
def GetProbability(data,n):
    x = np.linspace(0,n,n+1)
    y = []
    p_y = []
    countdict = Counter(data)
    counts = countdict.items()
    counts = sorted(counts)
    i,j = zip(*counts)
    for x_i in x:
        if x_i not in i:
            y.append(0)
        if x_i in i:
            y_i = i.index(x_i)
            y.append(j[y_i])
    Y = sum(y)
    for y_i in y:
        y_i = y_i/Y
        p_y.append(y_i)
    return x,p_y

# Gets likelihood from one set (input as list), returns single float value
def Likelihood(data,probability_true):
    L = []
    for value in data:
        # take each value from data and multiply by the probability of getting
        # that value from prob
        # data value corresponds to index of probability distribution
        l = probability_true[value]
        L.append(l)
    likelihood = np.product(L)
    return likelihood

# Input unnormalized data as list, output list of data normalized [0,1]
def NormalizeData(data):
    return (data - np.min(data)) / (np.max(data) - np.min(data))        

# main function for our coin toss Python code
if __name__ == "__main__":
    # not making any assumptions about what is provided by user
    haveH = False
            
    # available options for user input
    if '-input' in sys.argv:
        p = sys.argv.index('-input')
        InputFile = sys.argv[p+1]
        haveH = True
    # if the user includes the flag -h or --help print the options
    if '-h' in sys.argv or '--help' in sys.argv or not haveH:
        print ("Usage: %s [options]" % sys.argv[0])
        print ("  options:")
        print ("   --help(-h)          print options")
        print ("   -input [filename]  name of file for data")
        sys.exit(1)
    
    # get data from the input file rules so we know what we are working with
    rules = GetRules(InputFile)
    Ncards = rules[0]
    n = Ncards//2
    Ngames = rules[1]
    Nsets = rules[2]
    g_true = rules[3]
    # acquire list of possible g values, knowing number of cards
    g_list = np.linspace(0,n,n+1)
        
    # use our definitions to get data, tuple [[set1],[set2],[set3],...]
    data_sets = DataResults(InputFile)
    
    # compiles all sets of data into one list (tuple --> list)
    data_list = TotalResults(data_sets)
    
    # gets probability of occurrence from outcome
    prob = GetProbability(data_list,n)
    
    # gets true probability distribution of occurrence for each g
    prob_true = TrueProbability(g_true, n)
    
    # gives tuple of probability distributions where probdist[g] is
    # the probability distribution for any particular g value
    probdist_true = []
    for g in g_list:
        probdist_i = TrueProbability(int(g), n)
        probdist_true.append(probdist_i)
    
    # define some lists for collecting data
    g_exp = []
    pull = []
    sigma = []
    # we take each set of data and find associated likelihood from each possible
    # g value and then place those in a list
    for data_set_i in data_sets:
        likelihood_dist = []
        for g in probdist_true:
            likelihood_i = Likelihood(data_set_i,g)
            likelihood_dist.append(likelihood_i)
        g_maxes_L_value = max(likelihood_dist)
        g_maxes_L = likelihood_dist.index(max(likelihood_dist))
        g_exp.append(g_maxes_L)
        
        # find stdev of data
        LLR = []
        for l_value in likelihood_dist:
            # record very large negative number to avoid log(0) = -inf
            if l_value == 0:
                LLR.append(-1e32)
            else:
                LLR_i = np.log(l_value) - np.log(likelihood_dist[g_maxes_L])
                LLR.append(LLR_i)
        # add .5 to all values to find where LLR exceeds .5
        LLR_math = [x+.5 for x in LLR]
        # look for the sign change in the data and get the index location
        where = (np.diff(np.sign(LLR_math)) != 0)*1
        if sum(where) < 2:
            L_sigma = 0 - [i for i, n in enumerate(where) if n == 1][0]
        else:
            L_sigma = ([i for i, n in enumerate(where) if n == 1][1] - [i for i, n in enumerate(where) if n == 1][0])
        sigma.append(L_sigma)
        # error when L_sigma = 0, use 0 as pull value
        if L_sigma != 0:
            pull.append((g_maxes_L-g_true)/L_sigma)
        else:
            pull.append(0)
        
##########################            
    # Set binwidth for plots
    binwidth = 1
    
    # plt.figure()
    # plt.hist2d(x_g_true,y_g_best,bins=[n,n*2],range=[[0,n],[0,n]],
    #            cmap=plt.cm.Reds)
    # plt.colorbar()
    # plt.show()
    
##########################                    
# # PLOT 1: Frequency plot
#     title1 = "Frequency Table for Number of Games Won"
                
#     # make figure
#     plt.figure()
#     plt.hist(data_list, binwidth, facecolor='deepskyblue',
#               alpha=0.5, align = 'left', label="$\\mathbb{H}$")
      
#     plt.xlabel('$N_{wins}$ per game')
#     plt.ylabel('Frequency')
#     plt.legend(loc = 2)
#     plt.xlim(-.5 , n+.5)
#     plt.tick_params(axis='both')
#     plt.title(title1)
#     plt.grid(True)

#     plt.show()

##########################     
# # PLOT 2: Density plot
#     title2 = "Density Table for Number of Games Won"
                
#     # make figure
#     plt.figure()
#     plt.bar(prob[0], prob[1], width=binwidth, facecolor='deepskyblue',
#               alpha=0.5, label="$\\mathbb{H}$")
      
#     plt.xlabel('$N_{wins}$ per game')
#     plt.ylabel('Probability')
#     plt.legend(loc = 2)
#     plt.xlim(-.5 , n+.5)
#     plt.tick_params(axis='both')
#     plt.title(title2)
#     plt.grid(True)

#     plt.show()
    
# ########################## 
# # PLOT 3: Combined G and Pull plots
    title3 = str(Nsets) + " sets; " + str(Ngames) + " games / set; " + str(Ncards) + " cards / game; $G$ = " + str(g_true) 
                 
     # make figure
    fig, (ax1, ax2) = plt.subplots(1,2,figsize = [12.8, 4.8])
    fig.suptitle(title3)
    ax1.hist(g_exp, bins=max(g_exp)-min(g_exp), align = 'left',
              facecolor='deepskyblue', edgecolor = 'black', density = True, alpha=0.5)
    ax2.hist(pull, bins=8, range=[-2,2],
              facecolor='deepskyblue', density = True, edgecolor = 'black', alpha=0.5, align = 'left')
        
    ax1.set_title("Predicted G Plot")
    ax2.set_title("Pull Plot")
    ax1.set(xlabel='G', ylabel="Probability")
    ax2.set(xlabel='Pull', ylabel="Probability")
    ax1.tick_params(axis='both')
    ax1.set_xticks(range(min(g_exp),max(g_exp)))
    ax2.tick_params(axis='both')
    ax1.grid(True)
    ax2.grid(True)
    
    plt.show()
    
# ########################## 
# # PLOT 4: Predicted g plot
#     title4 = "Predicted G Plot (actual value: G = " + str(g_true) + ")"
                
#     # make figure data, bins=np.arange(min(data), max(data) + binwidth, binwidth)
#     plt.figure(figsize=[10,8])
#     plt.hist(g_exp, bins=max(g_exp)-min(g_exp), align = 'left',
#               facecolor='deepskyblue', edgecolor = 'black', density = True, alpha=0.5)
      
#     plt.xlabel('G')
#     plt.ylabel('Probability')
#     plt.xlim()
#     plt.tick_params(axis='both')
#     plt.xticks(range(min(g_exp),max(g_exp)))
#     plt.title(title4)
#     plt.grid(True)

#     plt.show()
    
# ########################## 
# # PLOT 5: Pull plot
#     title4 = "Pull Plot"
                
#     # make figure data, bins=np.arange(min(data), max(data) + binwidth, binwidth)
#     plt.figure()
#     plt.hist(pull, bins=8, range=[-2,2],
#               facecolor='deepskyblue', density = True, alpha=0.5, align = 'left')
      
#     plt.xlabel('Pull')
#     plt.ylabel('Probability')
#     plt.xlim()
#     plt.tick_params(axis='both')
#     plt.title(title5)
#     plt.grid(True)

#     plt.show()