﻿import sys
import struct
import os
import argparse
import json
import re

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

def secondsToString(seconds):
    hours = int(seconds / 3600)
    seconds %= 3600
    minutes = int(seconds / 60)
    seconds %= 60

    str = ""
    if hours > 0:
        str += "%dh " % hours
    if hours == 0 and minutes == 0:
        str += "%ds" % seconds
    else:
        str += "%dm" % minutes

    return str

def searchPlayer(id, clan):
    return [player for player in clan['roster'] if player['id'] == id][0]

def swapAttackOrder(clan):
    for player in clan['roster']:
        if player['attacksUsed'] == 1:
            temp = player['attack1']
            player['attack1'] = player['attack2']
            player['attack2'] = temp

# Print raw output
def printList(values):
    for v in values:
        print(v, end = ',', file = fileOut)
    print("", file = fileOut)

def parseClan(file):
    values = []
    clan = {}

    clan['totalOffenseWeight'] = 0
    clan['totalDefenseWeight'] = 0

    values.append(readInt64(file))  # Clan ID
    clan['id'] = values[-1]

    values.append(readString(file)) # Clan name
    clan['name'] = values[-1]

    values.append(readInt32(file))  # Clan badge
     
    values.append(readInt32(file))  # Clan level
    clan['level'] = values[-1]

    values.append(readInt32(file))  # War size
    clan['size'] = values[-1]
    warSize = values[-1]

    print(clanLabel, file = fileOut)
    printList(values)

    print(memberLabel, file = fileOut)

    roster = []
    for i in range(0, warSize):
        player = parseMember(file)
        player['position'] = i + 1
        roster.append(player)
        clan['totalOffenseWeight'] += player['offenseWeight']
        clan['totalDefenseWeight'] += player['defenseWeight']

    clan['roster'] = roster
    return clan

def parseMember(file):
    values = [] # raw output
    player = {} # formatted output

    player['attacksUsed'] = 0
    player['attacksWon'] = 0
    player['attack1'] = {'starsWon': 0, 'starsEarned': 0, 'damage': 0, 'target': "", 'targetPosition': 0}
    player['attack2'] = {'starsWon': 0, 'starsEarned': 0, 'damage': 0, 'target': "", 'targetPosition': 0}
    player['enemyBestAttack'] = {'starsWon': 0, 'starsEarned': 0, 'damage': 0, 'target': "", 'targetPosition': 0}

    values.append(readInt64(file))  # Clan ID

    values.append(readInt64(file))  # Member ID
    player['id'] = values[-1]

    values.append(readInt64(file))  # Member ID

    values.append(readString(file)) # Member Name
    player['name'] = values[-1]
    values[-1] = '"' + values[-1] + '"'

    values.append(readInt32(file))  # Stars given up
    player['starsGiven'] = values[-1]

    values.append(readInt32(file))  # Damage
    player['damageTaken'] = values[-1]

    values.append(readInt32(file))
    values.append(readInt32(file))  # Attacks used

    values.append(readInt32(file))  # Number of defenses
    player['totalDefenses'] = values[-1]
    numDefenses = values[-1]

    values.append(readInt32(file))  # Gold gained
    values.append(readInt32(file))  # Elixir gained
    values.append(readInt32(file))  # DE gained

    values.append(readInt32(file))  # Gold available
    values.append(readInt32(file))  # Elixir available
    player['goldAndElixir'] = values[-1]

    values.append(readInt32(file))  # DE available
    player['darkElixir'] = values[-1]

    values.append(readInt32(file))  # Offense weight
    player['offenseWeight'] = values[-1]

    values.append(readInt32(file))  # Defense weight
    player['defenseWeight'] = values[-1]

    values.append(readInt32(file))

    values.append(readInt32(file))  # TH level ID
    player['townHall'] = values[-1] + 1

    values.append(readByte(file))
    values.append(readInt32(file))
    values.append(readInt32(file))
    values.append(readInt32(file))
   
    values.append(readByte(file))
    battleDay = values[-1]
    
    if battleDay:
        values.append(readInt32(file))
        values.append(readInt32(file))

        values.append(readByte(file))
        values.append(readInt32(file) if numDefenses else 0)
        values.append(readInt32(file) if numDefenses else 0) # Best attack replay ID

    values.append(readInt32(file))

    values.append(readInt32(file))  # CC level ID
    values.append(readInt32(file))  # CC capacity
    values.append('"' + readString(file) + '"') # CC request message
    values.append(readInt32(file))  # CC number of troops

    # CC Troops
    sizeI = readInt32(file)
    values.append(sizeI)
    for i in range(0, sizeI):
        values.append(readInt64(file))
        sizeJ = readInt32(file)
        values.append(sizeJ)
        for j in range(0, sizeJ):
            values.append(readInt64(file))
    printList(values)
    return player

def parseAttacks(file, homeClan, enemyClan):
    print(readInt32(fileIn), end = ',', file = fileOut)
    print(readInt32(fileIn), end = ',', file = fileOut)
    numAttacks = readInt32(fileIn)
    print(numAttacks, file = fileOut)

    print(attackLabel, file = fileOut)

    warEvents = []
    for i in range (0, numAttacks):
        entry = parseAttackEntry(fileIn)
        entry['id'] = numAttacks - i
        warEvents.append(entry)

    return warEvents

def parseAttackEntry(file):
    values = []
    event = {}

    values.append(readInt32(file))
    values.append(readInt32(file))

    values.append(readInt32(file))  # Replay ID
 
    values.append(readInt32(file))  # Time remaining
    event['timeLeftDisplay'] = secondsToString(values[-1])
    event['timeLeftSeconds'] = values[-1]

    values.append(readInt64(file))  # Attacker clan ID
    attackerClanId = values[-1]

    values.append(readInt64(file))  # Attacker ID
    attackerId = values[-1]

    values.append(readInt64(file))  # Defender clan ID

    values.append(readInt64(file))  # Defender ID
    defenderId = values[-1]

    values.append(readString(file)) # Attacker name
    attackerName = values[-1]

    values.append(readString(file)) # Defender name
    defenderName = values[-1]

    values.append(readInt32(file))  # Stars won
    event['starsWon'] = values[-1]

    values.append(readInt32(file))  # Stars earned
    event['starsEarned'] = values[-1]
    
    values.append(readInt32(file))  # Damage
    event['damage'] = values[-1]

    values.append(readInt32(file)) # Time taken
    event['timeTaken'] = values[-1] + 1

    values.append(readInt32(file))
    values.append(readInt32(file))
    values.append(readInt32(file))

    values.append(readByte(file))
    values.append(readInt32(file))
    values.append(readInt32(file))
    values.append(readInt32(file))
    values.append(readInt32(file))
    printList(values)

    isHomeAttack = attackerClanId == homeClanId
    event['isHomeAttack'] = isHomeAttack

    homePlayer = searchPlayer(attackerId if isHomeAttack else defenderId, homeClan)
    enemyPlayer = searchPlayer(defenderId if isHomeAttack else attackerId, enemyClan)

    event['homePlayer'] = homePlayer['name']
    event['homePlayerPosition'] = homePlayer['position']
    event['enemyPlayer'] = enemyPlayer['name']
    event['enemyPlayerPosition'] = enemyPlayer['position']

    defender = searchPlayer(defenderId, enemyClan if isHomeAttack else homeClan)
    defenderPosition = defender['position']
    attackResult = {'starsWon': event['starsWon'], 'starsEarned': event['starsEarned'], 'damage': event['damage'], 'target': defenderName, 'targetPosition': defenderPosition}        

    player = searchPlayer(attackerId, homeClan if isHomeAttack else enemyClan)
    player['attacksUsed'] += 1
    if player['attacksUsed'] == 1:
        player['attack2'] = attackResult
    else:
        player['attack1'] = attackResult

    if event['starsWon'] > 0:
        player['attacksWon'] += 1

    if (event['starsEarned'] > 0  and event['starsWon'] > defender['enemyBestAttack']['starsWon']) or \
        (event['starsEarned'] == 0 and event['damage'] > defender['enemyBestAttack']['damage']):
        defender['enemyBestAttack'] = {'starsWon': event['starsWon'], 'starsEarned': event['starsEarned'], 'damage': event['damage'], 'target': player['name'], 'targetPosition': player['position']}

    return event

def parsePadding(file):
    values = []
    values.append(readByte(file))
    length = readInt32(file)
    values.append(length)
    for i in range(0, length + 5):
        values.append(readInt32(file))
    values.append(readByte(file))
    printList(values)

def createStats(home, enemy):
    stats = {}
    warSize = home['size']

    stats['attacksUsed'] = 0
    stats['attacksWon'] = 0
    for player in home['roster']:
        stats['attacksUsed'] += player['attacksUsed']
        stats['attacksWon'] += player['attacksWon']
    stats['attacksRemaining'] = warSize * 2 - stats['attacksUsed']
    stats['attacksLost'] = stats['attacksUsed'] - stats['attacksWon']

    stats['3Star'] = 0
    stats['2Star'] = 0
    stats['1Star'] = 0
    destruction = 0
    for player in enemy['roster']:
        destruction += player['damageTaken']
        if player['starsGiven'] == 3:
            stats['3Star'] += 1
        elif player['starsGiven'] == 2:
            stats['2Star'] += 1
        elif player['starsGiven'] == 1:
            stats['1Star'] += 1
    
    stats['totalStars'] = stats['3Star'] * 3 + stats['2Star'] * 2 + stats['1Star']
    stats['totalDestruction'] = float(destruction) / warSize

    return stats

def createSummary(homeClan, enemyClan, events):
    home = createStats(homeClan, enemyClan)
    enemy = createStats(enemyClan, homeClan)
    if home['totalStars'] > enemy['totalStars']:
        result = "Victory"
    elif home['totalStars'] < enemy['totalStars']:
        result = "Loss"
    else:
        if home['totalDestruction'] > enemy['totalDestruction']:
            result = "Victory"
        elif home['totalDestruction'] < enemy['totalDestruction']:
            result = "Loss"
        else:
            result = "Draw"
    return {'home': home, 'enemy': enemy, 'result': result}
    
# Labels do not display properly for war packet during preparation day
clanLabel = "ClanID,ClanName,,ClanLevel,WarSize"
memberLabel = "ClanID,MemberID,MemberID,Name,StarsGiven,Damage,,AttacksUsed,TotalDefenses,GoldGained,ElixirGained,DEGained,GoldAvailable,ElixirAvailable,DEAvailable,OffenseWeight,DefenseWeight,,TH,,,,,,,,,,BestAttackReplayID,,CC,CCSize,CCRequestMessage,CCFilled"
attackLabel = ",,ReplayID,TimeLeft,AttackerClanID,AttackerID,DefenderClanID,DefenderID,AttackerName,DefenderName,StarsWon,StarsEarned,Damage"

parser = argparse.ArgumentParser()
parser.add_argument("filepath", help = "decrypted LastClanWarData packet file path")
parser.add_argument("-r", "--raw", action = "store_false", help = "create raw decoded output")
parser.add_argument("-p", "--pretty", action = "store_true", help = "pretty print json")
parser.add_argument("-o", "--output", action = 'store', help = "specify output path, ending with /")
args = parser.parse_args()

fileIn = open(args.filepath, 'rb')
fileOut =  open(args.filepath + "-raw.csv", 'w', encoding = 'utf8')

print(readInt32(fileIn), end = ',', file = fileOut) # Clan war stage
print(readInt32(fileIn), file = fileOut)            # Time left

homeClan = parseClan(fileIn)
parsePadding(fileIn)
enemyClan = parseClan(fileIn)
parsePadding(fileIn)

homeClanId = homeClan['id']
enemyClanId = enemyClan['id']

warEvents = parseAttacks(fileIn, homeClan, enemyClan)
warSummary = createSummary(homeClan, enemyClan, warEvents)

if args.raw:
    fileOut.close()
    os.remove(args.filepath + "-raw.csv") # Should be a better way to do this

# Swap attack order if only attacked once
swapAttackOrder(homeClan)
swapAttackOrder(enemyClan)

m = re.search("[^\\\/]+$", args.filepath)
#warId = int(m.group(0)) if isinstance(m.group(0), int) else 0
warData = {'id': int(m.group(0)), 'summary': warSummary, 'home': homeClan, 'enemy': enemyClan, 'events': warEvents}
if args.pretty:
    jsonOutput = json.dumps(warData, indent = 2, ensure_ascii = False)
else:
    jsonOutput = json.dumps(warData, ensure_ascii = False)

if args.output:
    jsonFileOut = open(args.output + m.group(0) + ".json", 'w', encoding = 'utf8')
else:
    jsonFileOut = open(m.group(0) + ".json", 'w', encoding = 'utf8')

print(jsonOutput, file = jsonFileOut)

if not fileIn.read(1):
    print("done parsing")
else:
    print("error: parsing incomplete")