import sys
import struct
import os

def readInt32(file):
    value = file.read(4)
    if not value:
        return
    return struct.unpack('>i', value)[0]

def readInt64(file):
    value = file.read(8)
    if not value:
        return
    return struct.unpack('>q', value)[0]

def readByte(file):
    return struct.unpack('>B', file.read(1))[0]

def readString(file):
    length = readInt32(file)
    return struct.unpack('%ds' % length, file.read(length))[0].decode('utf-8')

def printList(values):
    for v in values:
        print(v, end = ',', file = fileOut)
    print("", file = fileOut)

def parseClan(file):
    values = []
    values.append(readInt64(file))  # Clan ID
    values.append(readString(file)) # Clan Name
    values.append(readInt32(file))  
    values.append(readInt32(file))  # Clan level
    warSize = readInt32(file)       # War size
    values.append(warSize)
    print(clanLabel, file = fileOut)
    printList(values)

    print(memberLabel, file = fileOut)
    for i in range(0, warSize):
        parseMember(file)

def parseMember(file):
    values = []
    values.append(readInt64(file))  # Clan ID
    values.append(readInt64(file))  # Member ID
    values.append(readInt64(file))  # Member ID
    values.append(readString(file)) # Member Name
    values.append(readInt32(file))  # Stars given up
    values.append(readInt32(file))  # Damage
    values.append(readInt32(file))  
    values.append(readInt32(file))  # Attacks used
    numDefenses = readInt32(file)   # Number of defenses
    values.append(numDefenses)
    values.append(readInt32(file))  # Gold gained
    values.append(readInt32(file))  # Elixir gained
    values.append(readInt32(file))  # DE gained
    values.append(readInt32(file))  # Gold available
    values.append(readInt32(file))  # Elixir available
    values.append(readInt32(file))  # DE available
    values.append(readInt32(file))  # Offense weight
    values.append(readInt32(file))  # Defense weight
    values.append(readInt32(file))
    values.append(readInt32(file))  # TH level ID
    values.append(readByte(file))
    values.append(readInt32(file))
    values.append(readInt32(file))
    values.append(readByte(file))
    values.append(readInt32(file))
    values.append(readByte(file))
    values.append(readInt32(file)) 
    values.append(readInt32(file)) 
    values.append(readInt32(file))
    if numDefenses:
        values.append(readInt32(file)) 
        values.append(readInt32(file))
    else:
        values.append(0) 
        values.append(0)
    values.append(readInt32(file))  # CC level ID
    values.append(readInt32(file))  # CC capacity
    values.append('"' + readString(file) + '"') # CC request message
    values.append(readInt32(file))  # CC capacity

    # Unknown variable length data
    sizeI = readInt32(file)
    values.append(sizeI)
    for i in range(0, sizeI):
        values.append(readInt64(file))
        sizeJ = readInt32(file)
        values.append(sizeJ)
        for j in range(0, sizeJ):
            values.append(readInt64(file))
    printList(values)

def parseAttacks(file):
    print(readInt32(fileIn), end = ',', file = fileOut)
    print(readInt32(fileIn), end = ',', file = fileOut)
    numAttacks = readInt32(fileIn)
    print(numAttacks, file = fileOut)

    print(attackLabel, file = fileOut)
    for i in range (0, numAttacks):
        parseAttackEntry(fileIn)

def parseAttackEntry(file):
    values = []
    values.append(readInt32(file))
    values.append(readInt32(file))
    values.append(readInt32(file))  # Replay ID
    values.append(readInt32(file))  # Time remaining
    values.append(readInt64(file))  # Attacker ID
    values.append(readInt64(file))  # Attacker clan ID
    values.append(readInt64(file))  # Defender ID
    values.append(readInt64(file))  # Defender clan ID
    values.append(readString(file)) # Attacker name
    values.append(readString(file)) # Defender name
    values.append(readInt32(file))  # Stars won
    values.append(readInt32(file))  # Stars earned
    values.append(readInt32(file))  # Damage
    values.append(readInt32(file))
    values.append(readInt32(file))
    values.append(readInt32(file))
    values.append(readInt32(file))
    values.append(readByte(file))
    values.append(readInt32(file))
    values.append(readInt32(file))
    values.append(readInt32(file))
    values.append(readInt32(file))
    printList(values)

def parsePadding(file):
    values = []
    values.append(readByte(file))
    length = readInt32(file)
    values.append(length)
    #printList(values)
    #del values[:]
    for i in range(0, length):
        values.append(readInt32(file))
    #printList(values)
    #del values[:]
    values.append(readInt32(file))
    values.append(readInt32(file))
    values.append(readInt32(file))
    values.append(readInt32(file))
    values.append(readInt32(file))
    values.append(readByte(file))
    printList(values)


clanLabel = "ClanID,ClanName,,ClanLevel,WarSize"
memberLabel = "ClanID,MemberID,MemberID,Name,StarsGiven,Damage,,AttacksUsed,"
"TotalDefenses,GoldGained,ElixirGained,DEGained,GoldAvailable,ElixirAvailable,"
"DEAvailable,OffenseWeight,DefenseWeight,,THID,,,,,,,,,,,,"
"CCID,CCSize,CCRequestMessage,CCSize"
attackLabel = ",,ReplayID,TimeLeft,AttackerClanID,AttackerID,DefenderClanID,"
"DefenderID,AttackerName,DefenderName,StarsWon,StarsEarned,Damage"

fileIn = open(sys.argv[1], 'rb')
fileOut = open(sys.argv[1] + ".csv", 'w', encoding = 'utf8')

print(readInt32(fileIn), end = ',', file = fileOut)
print(readInt32(fileIn), file = fileOut)

for i in range(0, 2):
    parseClan(fileIn)
    parsePadding(fileIn)
parseAttacks(fileIn)
