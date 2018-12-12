import credentials
from azure.storage.blob import BlockBlobService
import numpy as np
import collections
from collections import defaultdict, OrderedDict
import matplotlib.pyplot as plt
from operator import itemgetter


container_name = 'dpanalysis'
account_name = credentials.STORAGE_ACCOUNT_NAME
account_key = credentials.STORAGE_ACCOUNT_KEY
file_name = 'results01.csv'


def bit_fill(pin, pinCount):
    bits = "{0:b}".format(pinCount)
    while len(bits) < 10:
        bits = "0"+bits
    if(bits[pin] == "1"):
        return True
    else:
        return False


def drawPins(endingPinCount):
    pinxy = [(5, 1), (4, 2), (6, 2), (3, 3), (5, 3),
             (7, 3), (2, 4), (4, 4), (6, 4), (8, 4)]
    circle_size = 0.25
    ax = plt.gca()
    ax.cla()
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    for idx in range(0, len(pinxy)):
        circle = plt.Circle(pinxy[idx], circle_size,
                            color='b', fill=bit_fill(idx, endingPinCount))
        plt.gcf().gca().add_artist(circle)
    plt.show()


# Get CSV data fro Blob storage - Persist in this directory with same name as in Blob Storage
# block_blob_service = BlockBlobService(
#     account_name=account_name, account_key=account_key)
# block_blob_service.get_blob_to_path(container_name, file_name, file_name)
file_name = 'small.csv'
file_name = 'results01.csv'
# endingPinCount, v1, v2, angle2, x = np.loadtxt(
#     file_name, delimiter=',', unpack=True, usecols=range(5))
endingPinCount, v1, v2, angle2, x = np.genfromtxt(
    file_name, delimiter=',', unpack=True, missing_values='0')
csv = np.recfromcsv(file_name)
# plt.plot(v1, x, label='v1,x')
# circle = plt.Circle((5, 1), 5, color='black', fill=True)

print('EPClen', len(endingPinCount), endingPinCount[1])
print('CSV', csv)
csv1 = np.sort(csv)
print('CSV1', csv1)
endCount = []
for row in csv1:
    endCount.append(row[0])
print('EC', endCount)
unique, counts = np.unique(endCount, return_counts=True)
print('UC', unique, counts)
ecDict = dict(zip(unique, counts))
print('DICT', ecDict)
for key, value in sorted(ecDict.items(), key=itemgetter(1), reverse=True):
    print('Sorted', key, value)
    drawPins(key)
