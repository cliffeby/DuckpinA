import credentials
from azure.storage.blob import BlockBlobService
import numpy as np
import collections
import time
import pandas
from collections import defaultdict, OrderedDict
import matplotlib.pyplot as plt
from operator import itemgetter


container_name = 'dpanalysis'
account_name = credentials.STORAGE_ACCOUNT_NAME
account_key = credentials.STORAGE_ACCOUNT_KEY
file_name = 'results01.csv'

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
    # pin size on figure
    circle_size = 40
    # Subplots on figure in 2 x 2 grid
    plt.subplot2grid((2,2),(int((index/2)%2),index%2))
    # create axes for subplots
    ax = plt.gca()
    ax.cla()
    ax.set_xlim(20, 1310)
    ax.set_ylim(0, 800)
    # plot ball path on figure
    ax.plot([round(g.iloc[1][4],0),round(g.iloc[1][4]+2,0)],[0,400],'--')
    # plot x location of ball.  Size is +- one standard deviation
    ax.scatter(round(g.iloc[1][4],0),0,s=2*round(g.iloc[2][4],0))
    # create table and entries
    #format of grouped.describe() 'g' - use g.iloc[row][col]
    #         epc          v1          v2      theta           x
    # count  39.0   39.000000   35.000000  35.000000   39.000000
    # mean   32.0  140.733184  118.778189  -0.056169  591.538462
    # std     0.0   45.883051   28.093312   0.222245   88.924523
    # min    32.0   10.440307    9.848858  -0.274910  452.000000
    # 25%    32.0  118.432796  108.754121  -0.151138  501.000000
    # 50%    32.0  149.214610  122.331517  -0.070803  634.000000
    # 75%    32.0  175.676504  136.434460  -0.047601  645.000000
    # max    32.0  213.527516  148.013513   1.152572  885.000000
    cells =[[int(g.iloc[1][4]),int(g.iloc[1][1]),int(g.iloc[1][2]),round(g.iloc[1][3],2)],
            ['1','1','1','1'],  #TODO for median
            [round(g.iloc[2][4],0),round(g.iloc[2][1],0),round(g.iloc[2][2],0),round(g.iloc[2][3],2)]]
    cols = ['x', 'v1','v2',r'$\theta$' ]
    rows = ['mean', 'median',r'$\sigma$' ]
    # plot filled/unfilled pin circles, title, table, and population on figure
    for idx in range(0, len(pinxy)):
        circle = plt.Circle(pinxy[idx], circle_size,
                            color='b', fill=bit_fill(idx, endingPinCount))
        plt.gcf().gca().add_artist(circle)
    plt.title('Lane 4 ' + str(endingPinCount))
    plt.table(cellText=cells,
                      rowLabels=rows,
                      colLabels=cols,
                      loc='bottom',
                      bbox=[.2, -.75, .75, 0.5])
    plt.text(400, 700, 'pop = ' +str(value))

#  Sorts the data dictionary by desired order
#  type = 'Count' sorts by most frequent
#  type = 'Downed' sorts by best result
def arrangeDict(d,type):
    if type == 'Count' or type == '':
        # type = result
        d_sorted_keys = sorted(d, key=d.get,reverse=True)
        arranged = {}
        for r in d_sorted_keys:
            arranged[r] = d[r]
        return arranged


# Get CSV data fro Blob storage - Persist in this directory with same name as in Blob Storage
# block_blob_service = BlockBlobService(
#     account_name=account_name, account_key=account_key)
# block_blob_service.get_blob_to_path(container_name, file_name, file_name)
file_name = 'small.csv'
file_name = 'results01.csv'
# endingPinCount, v1, v2, angle2, x = np.loadtxt(
#     file_name, delimiter=',', unpack=True, usecols=range(5))
# endingPinCount, v1, v2, angle2, x = np.genfromtxt(
#     file_name, delimiter=',', unpack=True, missing_values='0')
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
        plt.suptitle(time.strftime('%b %d %Y'))
    if index > 20:
        continue
    endcountGroup = result.loc[result['epc'] == key]
    if index%10 ==0:
        print('Stats for group ',index, endcountGroup.describe())    
    drawPins(key, index, value,endcountGroup.describe())
    index = index+1

plt.tight_layout(pad=4.0, w_pad=0.5, h_pad=6.0)
plt.show()


