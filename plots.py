import credentials
from azure.storage.blob import BlockBlobService
import numpy as np
import collections
import time
import pandas, math
from collections import defaultdict, OrderedDict
import matplotlib.pyplot as plt
from operator import itemgetter


container_name = 'dpanalysis'
account_name = credentials.STORAGE_ACCOUNT_NAME
account_key = credentials.STORAGE_ACCOUNT_KEY
file_name = 'results02.csv'

# Determine which pins are up(filled) or down(unfilled)
# pinCount is decimal value of 1111111111 = 1023 or 0000000000 = 0
# A pin value of 1 is up and 0 is down.
# Pin 1 = decimal 512; pin 10 = decimal 1
# bit_fill returns True when pin is up(filled)
def bit_fill(pin, pinCount):
    bits = "{0:b}".format(pinCount)
    while len(bits) < 10:
        bits = "0"+bits
    if(bits[pin] == "1"):
        return True
    else:
        return False

        
def drawPins(endingPinCount, index, value, g):
    # xy pairs for pins on figure
    pinxy = [(570, 200), (405, 300), (725, 300), (240, 400), (570, 400),
             (880, 400), (80, 500), (400, 500), (720, 500), (1040, 500)]
    circle_size = 40 # pin size on figure
    center = 570  # xy  coordinates are x from the left lane edge.  center is xlocation in pixels
    # Subplots on figure in 2 x 2 grid
    plt.subplot2grid((2,2),(int((index/2)%2),index%2))
    # create axes for subplots
    ax = plt.gca()
    ax.cla()
    # ax.set_xlim(20, 1310)
    ax.set_xlim(-center,center)
    ax.set_ylim(0, 800)
    offset = math.tan(math.radians(g.iloc[1][4]))*400

    # plot ball path on figure
    ax.plot([round(g.iloc[5][5]-center,0),round(g.iloc[5][5]-center+offset,0)],[0,400],'--')
    # plot x location of ball.  Size is +- one standard deviation
    ax.scatter(round(g.iloc[5][5]-center,10),0,s=2*round(g.iloc[2][5],0))
    # create table and entries
    #format of grouped.describe() 'g' - use g.iloc[row][col]
#          epc    up          v1          v2      theta           x
# count   54.0  54.0   54.000000   54.000000   54.000000  54.000000   54.000000   54.000000
# mean   832.0   3.0  243.000000  137.884240  122.308169   0.039974  762.148148  200.148148
# std      0.0   0.0   55.422562   33.159582   19.883357   0.068052   42.807779   42.807779
# min    832.0   3.0  120.000000   47.010637   55.901699  -0.160988  688.000000  126.000000
# 25%    832.0   3.0  204.000000  118.735935  112.631173  -0.004934  726.250000  164.250000
# 50%    832.0   3.0  239.500000  141.851328  124.008064   0.036108  766.000000  204.000000  #--median
# 75%    832.0   3.0  284.500000  160.333228  135.058465   0.087142  792.000000  230.000000
# max    832.0   3.0  373.000000  201.486972  163.248277   0.179853  850.000000  288.000000
    cells =[[int(g.iloc[1][5]-center),int(g.iloc[1][2]),int(g.iloc[1][3]),round(g.iloc[1][4],2)],              #Row 1
            [round(g.iloc[5][5]-center,0),round(g.iloc[5][2],0),round(g.iloc[5][3],0),round(g.iloc[5][4],2)],  #Row 5
            [round(g.iloc[2][5],0),round(g.iloc[2][2],0),round(g.iloc[2][3],0),round(g.iloc[2][4],2)]]  #Row 2
    cols = ['x', 'v1','v2',r'$\theta$' ]
    rows = ['mean', 'median',r'$\sigma$' ]
    # plot filled/unfilled pin circles, title, table, and population on figure
    for idx in range(0, len(pinxy)):
        circle = plt.Circle((pinxy[idx][0]-center, pinxy[idx][1]), circle_size,
                            color='b', fill=bit_fill(idx, endingPinCount))
        plt.gcf().gca().add_artist(circle)
    plt.title('Lane 4 ' + str(endingPinCount))
    plt.table(cellText=cells,
                      rowLabels=rows,
                      colLabels=cols,
                      loc='bottom',
                      bbox=[.2, -.75, .75, 0.5])
    plt.text(-100, 700, 'pop = ' +str(value))

#  Sorts the data dictionary by desired order
#  type = 'Count' sorts by most frequent
#  type = 'Up' sorts by best result
def arrangeDict(d,type):
    if type == 'Count' or type == '':
        # type = result
        d_sorted_keys = sorted(d, key=d.get,reverse=True)
        arranged = {}
        for r in d_sorted_keys:
            arranged[r] = d[r]
        return arranged
    if type == 'Up':
        #TODO
        return d    


# Get CSV data fro Blob storage - Persist in this directory with same name as in Blob Storage
block_blob_service = BlockBlobService(
    account_name=account_name, account_key=account_key)
block_blob_service.get_blob_to_path(container_name, file_name, file_name)
# file_name = 'small.csv'  #Testing data subset - small
# file_name = 'results01.csv' #Testing data subset - large
# Format is epc,up,v1,v2,theta,x, absx
csv = np.recfromcsv(file_name)
csv1 = np.sort(csv)
endCount = []
for row in csv1:
    endCount.append(row[0])
unique, counts = np.unique(endCount, return_counts=True)
ecDict = dict(zip(unique, counts))
print('Dictionary length: ',len(ecDict))
print('First three dict pairs', {k: ecDict[k] for k in list(ecDict)[:3]})
print('Final dict pairs', {k: ecDict[k] for k in list(ecDict)[(len(ecDict)-4):len(ecDict)]})

result = pandas.DataFrame(csv1)
index = 0
for (key, value) in sorted(arrangeDict(ecDict,'Count').items(), key=itemgetter(1), reverse=True):
    if index%4 ==0:
        plt.tight_layout(pad=4.0, w_pad=0.5, h_pad=6.0)
        plt.figure(index/4 +1)
        plt.suptitle('Page '+str(index//4+1) +'  '+time.strftime('%b %d %Y'))
    if index > 19:
        continue
    endcountGroup = result.loc[result['epc'] == key]
    if index%10 ==0:
        print('Stats for group ',index, endcountGroup.describe())   
    if key==832:
            print('832 records ', endcountGroup)    
    drawPins(key, index, value,endcountGroup.describe())
    index = index+1

plt.tight_layout(pad=4.0, w_pad=0.5, h_pad=6.0)
plt.show()


