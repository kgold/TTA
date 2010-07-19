import csv
import random
import math
from collections import deque

# TODO:
# Code repository
# Air force tactics effect
# Joan of Arc culture ability
# Columbus colonization
# Antiquated tactics
# Leader Age II
# Leader Age III
# *AI, rudimentary (random-ish moves, or behavior tree)
# Military deck - Events, Age II and III
# Raid - building loss
# Military deck - Aggressions, Age II and III
# Military deck - Defense/Bonus
# Military deck - Pacts
# Military deck - Wars
# Undo command
# Game end
# GUI front end
# Multiplayer server
# AI, search-based
# AI, learning
# *General debugging!

ageMap = {"A":0, "I":1, "II":2, "III":3}
farmCost = [2, 4, 6, 8]
mineCost = [2,5,8,11]
resourceValue = [1,2,3,5]
templeCost = [3,5,7]
templeCulture = [1,1,1]
templeHappy = [1,2,3]
labCost = [3,6,8,10]
labScience = [1,2,3,5]
arenaCost = [1000, 4, 6, 8]
arenaStrength = [0,1,2,3]
arenaHappy = [2,3,4]
libraryCost = [1000,4,8,11]
libraryCulture = [0,1,2,3]
libraryScience = [0,1,2,3]
theaterCost = [1000,5,9,12]
theaterCulture = [0,2,3,4]
theaterHappy = [0,1,1,1]
milCost = [2,3,5,7]
milStrength = [1,2,3,5]
techRowCost = [1, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3]


def getResource(a):
	return a[0] + a[1] * 2 + a[2] * 3 + a[3] * 5

def showCard(card):
	if card == "-":
		print(self.leader["Card Name"] + " wept, for there was no more tech to conquer in that slot.")
		return
	for key in card:
		if key[1:] == "er" or key == "isNew" : # skip card counts,  flags
			continue
		val = card[key]
		if len(val) > 0:
			print(key + ":" + val)

def totalBuildings(array):
	total = 0
	for x in array:
		if x > 0:
			total += x
	return total

def buildingsToString(name, array):
		discovered = False
		for x in array:
			if x > -1:
				discovered = True
		if not discovered:
			return ""
		result = name + ": " 
		for x in array:
			result += " "
			if x < 0:
				result += "-"
			else:
				result += str(x)
		return result + "\n"

def resourceToString(array):
		result = str(array[0]) + "x1 "
		for x in range(1,3):
			if array[x] > 0:
				result += "+ " + str(array[x]) + "x" + str(resourceValue[x])
		result += "= " + str(getResource(array))
		return result
		

class MatState:

	def __init__(self, player):
		# -1 is code for "not invented yet"
		self.playerNum = player-1 # for purpose of player array index
		self.labs = [1,-1,-1,-1]
		self.temples = [0, -1, -1, -1]
		self.farms = [2, -1, -1, -1]
		self.food = [0, 0, 0, 0]
		self.mines = [2, -1, -1, -1]
		self.rocks = [0, 0, 0, 0]
		self.libraries = [-1, -1, -1, -1]
		self.theaters = [-1, -1, -1, -1]
		self.arenas = [-1, -1, -1, -1]
		self.infantry = [1, -1, -1, -1]
		self.cavalry = [-1, -1, -1, -1]
		self.artillery = [-1,-1,-1,-1]
		self.airForce = [-1, -1, -1, -1]
		self.workerPool = 1
		self.civilActions = player 
		self.milActions = 0 
		self.milResource = 0
		self.government = {"CA":4, "MA":2}
		self.urbanMax = 2
		self.resourceReserve = 18
		self.populationBank = 18
		self.wonders = []
		self.wonderRemaining = []
		self.guysOnWonder = 0
		self.wonderRate = 1
		self.buildDiscount = [0, 0, 0, 0]
		self.leader = {}
		self.tactics = {}
		self.discardMilThisTurn = True
		self.territories = []
		self.techsInPlay = []
		self.science = 0
		self.culture = 0
		self.civilHand = []
		self.milHand = []
		self.techsTaken = []
		self.myTurn = (player == 1)
		self.leaderTaken = [False, False, False, False]
		self.colonizeBonus = 0
		self.techDict = {'s':self.labs, 'r':self.temples, 'f':self.farms, 'm':self.mines, 'g':self.arenas, 'l':self.libraries, 'i':self.infantry, 'c': self.cavalry, 'a':self.artillery, 'p':self.airForce}
	
	def getFood(self):
		return getResource(self.food)

	def getRocks(self):
		return getResource(self.rocks)

	def dScience(self):
		dSci = 0
		for i in range(4):
			if self.labs[i] > 0:
				dSci += self.labs[i] * labScience[i]
		for w in self.builtWonders():
			if "Science" in w and w["Science"].isdigit():
				dSci += int(w["Science"])
		if self.leaderIs("Leonardo da Vinci"):
			for level in [3,2,1]:
				# Libs act as labs of one lower level;
				# Leo can't be alive in Age III
				if self.labs[level-1] > 0 or self.libraries[level] > 0:
					dSci += labScience[level-1]
					break
		return dSci

	def getMilitary(self):
		mil = 0
		for i in range(4):
			if self.infantry[i] >0:
				mil += milStrength[i] * self.infantry[i]
			if self.cavalry[i] > 0:
				mil += milStrength[i] * self.cavalry[i]
			if self.artillery[i] > 0:
				mil += milStrength[i] * self.artillery[i]
			if self.airForce[i] > 0:
				mil += milStrength[i] * self.airForce[i]
		for w in self.builtWonders():
			if "Strength" in w and w["Strength"].isdigit():
				mil += int(w["Strength"])
			if w["Card Name"] == "Great Wall":
				for j in range(4):
					mil += self.infantry[j]
					mil += self.artillery[j]
		for t in self.techsInPlay:
			if t["Type"] == "Military" or t["Type"] == "Colonization":
				mil += int(t["Strength"])
		if "Strength" in self.government:
			mil += int(self.government["Strength"])
		for t in self.territories:
			if t["Card Name"] == "Strategic Territory":
				if t["Age"] == "I":
					mil += 2
				else:
					mil += 4
		if self.leaderIs("Alexander the Great"):
			mil += totalBuildings(self.infantry)
			mil += totalBuildings(self.cavalry)
			mil += totalBuildings(self.artillery)
		if self.leaderIs("Joan of Arc"):
			for i in range(4):
				if self.temples > 0:
					mil += templeHappy[i] * self.temples[i]
		if self.leaderIs("Julius Caesar"):
			mil += 1 # only straight str leader
		if self.leaderIs("Genghis Khan"):
			for i in range(4):
				if self.cavalry[i] > 0:
					mil += self.cavalry[i]
		elif "Card Name" in self.tactics:
			# Tactics bonus
			[infNeeded, cavNeeded, artNeeded] = figureTacticsReqs(self.tactics)
			infWeHave = totalBuildings(self.infantry)
			cavWeHave = totalBuildings(self.cavalry)
			artWeHave = totalBuildings(self.artillery)
			totalArmies = 0
			print ("Calculating tactics: ")
			print (str(infWeHave) + "/" + str(infNeeded))
			print (str(cavWeHave) + "/" + str(cavNeeded))
			print (str(artWeHave) + "/" + str(artNeeded))
			while infWeHave >= infNeeded and cavWeHave >= cavNeeded and artWeHave >= artNeeded:
				totalArmies += 1
				infWeHave -= infNeeded
				cavWeHave -= cavNeeded
				artWeHave -= artNeeded
			print ("armies: " + str(totalArmies))
			# Ignoring antiquated unit stuff for now
			bonus = int(self.tactics["Army bonus"])
			mil += bonus * totalArmies

		return mil

	def leaderIs(self, name):
		return "Card Name" in self.leader and self.leader["Card Name"] == name

	def getUnhappy(self):
		if self.populationBank <= 0:
			u = 8
		elif self.populationBank <= 2:
			u = 7
		elif self.populationBank <= 4:
			u = 6
		elif self.populationBank <= 6:
			u = 5
		elif self.populationBank <= 8:
			u = 4
		elif self.populationBank <= 10:
			u = 3
		elif self.populationBank <= 12:
			u = 2
		elif self.populationBank <= 16:
			u = 1
		else:
			u = 0
		return max(u - self.happiness(), 0)

	def happiness(self):
		h = 0
		neg_h = 0 # keep separate for St. Pete's Basilica
		weHavePete = False
		for i in range(4):
			if self.temples[i] > 0:
				h += templeHappy[i] * self.temples[i]
			if self.theaters[i] > 0:
				h += theaterHappy[i] * self.libraries[i]
		for w in self.builtWonders():
			if "Happy" in w:
				happyVal = w["Happy"]
				if happyVal.isdigit():
					h += int(happyVal)
				elif len(happyVal) > 1 and happyVal[0] == '-' and happyVal[1:].isdigit():
					neg_h += int(happyVal[1:])
			if ("Card Name" in w and w["Card Name"] == "St. Peter's Basilica"):
				weHavePete = True
		if "Happy" in self.government:
			happyVal = self.government["Happy"]
			if happyVal.isdigit():
				h+=int(happyVal)
			elif happyVal[0] == '-' and happyVal[1:].isdigit():
				neg_h += int(happyVal[1:])
		for t in self.territories:
			if t["Card Name"] == "Historic Territory":
				if t["Age"] == "I":
					h += 1
				else:
					h += 2
				
		if (weHavePete):
			h *= 2
		h -= neg_h
		h = min(h, 8)
		return h

	def dCulture(self):
		dc = 0
		for i in range(4):
			if self.temples[i] > 0:
				dc += templeCulture[i] * self.temples[i]
			if self.libraries[i] > 0:
				dc += libraryCulture[i] * self.libraries[i]
			if self.theaters[i] > 0:
				dc += theaterCulture[i] * self.theaters[i]
		for w in self.builtWonders():
			if "Culture" in w and w["Culture"].isdigit():
				dc += int(w["Culture"])
		if "Culture" in self.government:
			dc += self.government["Culture"]
		if self.leaderIs("Homer"):
			dc += min(2, self.infantry[0])
		if self.leaderIs("Michelangelo"):
			for i in range(4):
				if self.temples[i] > 0:
					dc += templeHappy[i] * self.temples[i]
				if self.theaters[i] > 0:
					dc += theaterHappy[i] * self.theaters[i]
			for w in self.builtWonders():
				if w["Happy"].isdigit():  # ie, nonnegative
					dc += int(w["Happy"])
		if self.leaderIs("Genghis Khan"):
			for i in range(4):
				if self.cavalry[i] > 0:
					dc += self.cavalry[i]
		return dc

	# Returns amount lost
	def loseResource(self, a, isRocks):
		# Can't do check here for affording it, because some effects
		# may just take as much as possible.
		toLose = a
		i = 3
		if (isRocks):
			resourceArray = self.rocks
		else:
			resourceArray = self.food
		value = [1, 2, 3, 5]
		while (toLose > 0 and i >= 0):
			if resourceArray[i] * value[i] > 0:
				resourceArray[i]-=1
				toLose -= value[i]
				self.resourceReserve += 1
			else:
				i-=1
		# Make change in 1's.  Larger change is TODO.
		if (toLose < 0):
			resourceArray[0] -= toLose
			self.resourceReserve -= toLose
		if (toLose > 0):
			return a - toLose
		else:
			return a
	
	def gainResource(self, a, isRocks):
		toGain = a
		i = 3
		if isRocks:
			rArray = self.rocks
			buildArray = self.mines
		else:
			rArray = self.food
			buildArray = self.farms
		value = [1,2,3,5]
		while toGain > 0 and i >= 0 and self.resourceReserve > 0:
			if buildArray[i] > -1 and value[i] <= toGain:
				rArray[i] += 1
				toGain -= value[i]
				self.resourceReserve -= 1
			else:
				i -= 1

	def growCost(self):
		if self.populationBank <= 4:
			cost = 7
		elif self.populationBank <= 8:
			cost = 5
		elif self.populationBank <= 12:
			cost = 4
		elif self.populationBank <= 16:
			cost = 3
		else:
			cost = 2
		if self.leaderIs("Moses"):
			cost -= 1
		return cost
		
	# tryBuild: now handles both upgrading and building (build prevLevel = -1), since many effects are the same for each
	def tryBuild(self, buildArray, costArray, level, urban, civil, discount=0, prevLevel = -1):
		if (civil):
			if self.civilActions <= 0:
				return "no - out of civil actions"
		else:
			if self.milActions <= 0:
				return "no - out of mil actions"
		if (prevLevel >= 0):
			if buildArray[prevLevel] < 1:
				return "no - no units at level " + str(prevLevel)
			else:
				if (urban):
					cost = costArray[level] - self.buildDiscount[level] - (costArray[prevLevel] - self.buildDiscount[prevLevel])
				else:
					cost = costArray[level] - costArray[prevLevel]
		else:
			if (urban):
				cost = costArray[level] - self.buildDiscount[level]
			else:
				cost = costArray[level]
		cost -= discount # from a tech card, for example
		if (not civil):
			milResourceSupplied = min(self.milResource, cost)
			cost -= milResourceSupplied
		if (cost > self.getRocks()):
			return "no - not enough resources"
		elif (buildArray[level] == -1):
			return "no - not invented yet.  cheater."
		elif (urban and prevLevel == -1 and totalBuildings(buildArray) >= self.urbanMax):
			return "no - urban building max reached"
		else:
			self.loseResource(cost, True)
			buildArray[level]+=1
			if (civil):
				self.civilActions -= 1
			else:
				self.milActions -= 1
				self.milResource -= milResourceSupplied
		if (prevLevel == -1):
			self.workerPool -= 1
		else:
			buildArray[prevLevel] -= 1
		return "ok"

	def handLimit(self, civil):
		if (civil):
			limit = self.getCivilActionsMax()
		else:
			limit = self.getMilActionsMax()
		for w in self.builtWonders():
			if (w["Card Name"] == "Library of Alexandria"):
				limit += 1
		return limit

	def parseCommand(self, commandString, techRow, allMats, discount = 0):
		if (len(commandString) <= 0):
			return "no - received empty input"
		if (commandString[0] == 'h'):
			print ("Commands:")
			print ("b[t][#] -- (b)uild")
			print ("\tvalues for [t]: (s)cience, (r)eligion, (f)arm, (m)ine, (l)ibrary, (d)rama, (g)ladiators (= arena), (i)nfantry, (c)avalry, (a)rtillery, (w)onder, (p) = planes (air force)")
			print ("\t# = level to build (default 0=ancient) or number of stages of wonder to build (with appropriate Construction tech; default 1")
			print ("\texamples:  bw2, bm, bp, bw, bi3, bi0, bi")
			print ("u[t][#1][#2] -- upgrade [t] from [#1] to [#2]")
			print ("\t...same values for [t], defaults 0 and #1+1")
			print ("d[t][#] -- disband [t] of level [#] (default L0)")
			print ("g[o/b#] -- (g)row population")
			print ("\toptional o: use Ocean Liner Service")
			print ("\toptional b[i/c/a][#]: grow with Barbarossa (ex: gbi2, gbc)")
			print ("t[#] -- (t)ake a card from the tech row")
			print ("\texample: t0")
			print ("p# -- (p)lay a card from your civil hand")
			print ("pt# -- (p)lay (t)actics (only kind of mil card allowed)")
			print ("f -- (f)inish the turn")
			print ("x[r/h/p/l/w]# -- e(x)amine a card from the (r)ow, your civil (h)and, your (m)ilitary hand, a tech in (p)lay, a (l)eader in play, or a (w)onder in play (default is tech row)")
			print ("\texamples: xr0, xh2,xl,x5")
			print ("h -- this (h)elp")
			return("ok")
		if (commandString[0] == 'x'):
			if len(commandString) < 2:
				return("no - I understood you as far as wanting to examine something.")
			if commandString[1] == 'l':
				if not "Card Name" in self.leader:
					return("no - You can't see any such thing.")
				showCard(self.leader)
				return
			if commandString[1] == '5':
				if not "Card Name" in self.tactics:
					return("no - You can't see any such thing.")
				showCard(self.tactics)
				return
			if len(commandString) < 3 or not commandString[2:].isdigit() or commandString[1].isdigit():
				if(commandString[1].isdigit()):
					# assume tech row
					commandString = "xr" + commandString[1:]
				else:
					return ("no - check help for format")
			cardNum = int(commandString[2:])
			if commandString[1] == 'r':
				if cardNum > 12:
					return("no - You can't see any such thing.")
				showCard(techRow[cardNum])
			if commandString[1] == 'h':
				if cardNum > len(self.civilHand):
					return("no - You can't see any such thing.")
				showCard(self.civilHand[cardNum])
			if commandString[1] == 'p':
				if cardNum > len(self.techsInPlay):
					return("no - You can't see any such thing.")
				showCard(self.techsInPlay[cardNum])
			if commandString[1] == 'w':
				if cardNum > len(self.wonders):
					return("no - You can't see any such thing.")
				showCard(self.wonders[cardNum])
			if commandString[1] == 'm':
				if cardNum > len(self.milHand):
					return("no - You can't see any such thing.")
				showCard(self.milHand[cardNum])
			return "ok"
			
		if (commandString[0] == 'p'):
			# Play (a civil card)
			if len(commandString) < 2 or (not commandString[1] == 't' and not commandString[1].isdigit()):
				return "no - need to specify number of card"
			if commandString[1] == 't':
				if len(commandString) < 3 or not commandString[2].isdigit():
					return "no - need to specify card number in mil hand"
				cardNum = int(commandString[2])
				if len(self.milHand) <= cardNum:
					return "no - invalid mil card number"
				card = self.milHand[cardNum]
				if not card["Type"] == "Tactics":
					return "no - only tactics cards can be played after political action"
				if self.milActions <= 0:
					return "no - not enough mil actions"
				self.milActions -= 1
				self.tactics = card
				del self.milHand[cardNum]
				return "ok - tactics played"
			
			cardNum = int(commandString[1]) # bug here if hand size huge
			if cardNum >= len(self.civilHand):
				return "no - not a valid card"
			card = self.civilHand[cardNum]
			if (self.civilActions <= 0):
				return "no - not enough civil actions"
			violentRevolution = False
			if "Tech cost" in card and len(card["Tech cost"]) > 0:
				if '(' in card["Tech cost"]:
					# Government with alt cost -- assume command string specifies ('p' = peacefully)
					if len(commandString) < 3:
						cost = int(card["Tech cost"][0])
						violentRevolution = True
						if self.civilActions < self.getCivilActionsMax():
							return "no - violent gov change must be first action in turn"
					else:
						splitString = card["Tech cost"].split("()")
						cost = splitString[1]
				else:
					cost = int(card["Tech cost"])
				if cost > self.science:
					return "no - not enough science"
				else:
					self.science -= cost
			if "Type" in card and card["Type"] == "Action":
				optArg = commandString[2:]
				result = self.tryActionCard(card, techRow, allMats, optArg)
				if result[0:2] == "no":
					return result # tryActionCard handles action
			else:
				self.triggerPlayEffects(card)
				if (violentRevolution):
					self.civilActions = 0
				else:
					self.civilActions -= 1
			del self.civilHand[cardNum]
			return "ok"
						
		if (commandString[0] == 't'):
			# Take (a card from the tech row)
			if (len(commandString) < 2):
				return "no - (t)ake needs card number"
			if (len(self.civilHand) >= self.handLimit(True)):
				return "no - hand limit reached"
			numString = commandString[1]
			if (len(commandString) == 3):
				numString += commandString[2]
			cardNum = int(numString)
			actionCost = techRowCost[cardNum]
			card = techRow[cardNum]
			if (card["Type"] == "Wonder"):
				if (len(self.wonderRemaining) > 0):
					return "no - wonder already under construction"
				actionCost += len(self.wonders)
				if self.leaderIs("Michelangelo"):
					actionCost -= 1
			if (self.civilActions < actionCost):
				return "no - not enough actions"
			if (isTech(card)):
				if card["Card Name"] in self.techsTaken:
					return "no - already took this tech"
				else:
					# Can't return False now!
					self.techsTaken.append(card["Card Name"])
					if self.leaderIs("Aristotle"):
						self.science += 1
			if (card["Type"] == "Leader"):
				if (self.leaderTaken[ageMap[card["Age"]]]):
					return "no - leader already taken this age"
				else:
					# Can't return False now!
					self.leaderTaken[ageMap[card["Age"]]] = True
			if (card["Type"] == "Action"):
				card.update({"isNew":True})
			if (card["Type"] == "Wonder"):
				self.wonders.append(card)
				self.wonderRemaining = map(int, card["Build cost"].split(' '))
			else:
				self.civilHand.append(techRow[cardNum])
			techRow[cardNum] = "-"
			self.civilActions -= actionCost
			return "ok"
		if (commandString[0] == 'g'):
			# Grow
			ocean = False
			barbarossaAction = False
			if (len(commandString) > 1):
				if commandString[1] == 'o': 
					for w in self.builtWonders():
						if w["Card Name"] == "Ocean Liner Service":
							if not self.oceanUsed:
								ocean = True
								break
							else:
								return "no - Ocean Liner already used this turn"
					if not ocean:
						return "no - Ocean Liner Service not found"
				elif commandString[1] == 'b':
					if not self.leaderIs["Frederick Barbarossa"]:
						return "no - only Barbarossa can use the 'gb' option"
					else:
						barbarossaAction = True
			if (self.civilActions <= 0 and not ocean):
				return "no - out of civil actions"
			cost = self.growCost()
			if (ocean):
				cost = max(cost-5,0)
			if (barbarossaAction):
				cost -= 1
				level = 0
				if len(commandString) >= 4 and commandString[3].isdigit():
					level = int(commandString[3])
				rockCost = milCost[level]-1
				if self.getRocks() < rockCost:
					return "no - not enough rock to build that"
			if self.getFood() < cost:
				return "no - not enough food"
			if self.populationBank <= 0:
				return "no - population bank is empty"
			self.loseResource(cost, False)
			self.workerPool += 1
			self.populationBank -= 1
			if (ocean):
				self.oceanUsed = True
			elif (barbarossaAction):
				return self.parseCommand(commandString[1:],techRow,allMats, 1)
			else:
				self.civilActions -= 1
			return "ok"
		elif (commandString[0] == 'd'):
			# Disband
			if (len(commandString) < 2):
				return "no - disband what?"
			level = 0
			if (len(commandString) >= 3):
				level = int(commandString[2])
			disbandArray = self.techDict[commandString[1]]
			if disbandArray[level] < 1:
				return "no - no unit to disband at level" + str(level)
			civil = True
			if commandString[1] in ['i','c','a','p']:
				civil = False
			if (civil):
				if self.civilActions <=0:
					return "no - not enough civil actions"
				else:
					self.civilActions -= 1
			else:
				if self.milActions <=0:
					return "no - not enough military actions"
				else:
					self.milActions -= 1
			disbandArray[level] -= 1
			self.workerPool += 1
			return "ok - level " + str(level) + " unit disbanded"
		elif (commandString[0] == 'b' or commandString[0] == 'u'):
			# Build
			if (len(commandString) < 2):
				return "no - build/upgrade what?"
			if (commandString[1] == 'w'):
				# wonder 
				if (len(self.wonderRemaining) <= 0):
					return "no - no wonder under construction"
				if (self.civilActions <= 0):
					return "no - not enough civil actions"
				stages = 1
				if (len(commandString) == 3):
					stages = int(commandString[2])
					if self.wonderRate < stages:
						return "no - Construction allows max " + str(self.wonderRate)
					if stages > len(self.wonderRemaining):
						return "no - not that much wonder left"
				cost = max(sum(self.wonderRemaining[0:stages]) - discount, 0)
					
				if (self.getRocks() < cost):
					return "no - not enough resources"
				for i in range(stages):
					if discount > 0:
						# Eng genius
						self.loseResource(cost, True)
					else:
						self.loseResource(self.wonderRemaining[0], True)
					self.resourceReserve -= 1
					self.guysOnWonder += 1
					self.wonderRemaining = self.wonderRemaining[1:len(self.wonderRemaining)]
				if (len(self.wonderRemaining) == 0):
					self.resourceReserve += self.guysOnWonder
					self.guysOnWonder = 0
					self.triggerPlayEffects(self.wonders[len(self.wonders)-1])
				self.civilActions -= 1
				return "ok"
			if (self.workerPool <= 0 and commandString[0] == 'b'):
				return "no - no workers in worker pool"
			# Going to try avoiding code duplication by
			# having prevLevel -1 = new build, otherwise upgrade
			if (commandString[0] == 'u'):
				if len(commandString) >= 3:
					prevLevel = int(commandString[2])
				else:
					prevLevel = 0
			else:
				prevLevel = -1
			if commandString[0] == 'b':
				if (len(commandString) < 3):
					level = 0
				else:
					level = int(commandString[2])
			elif commandString[0] == 'u':
				if len(commandString) > 3:
					level = int(commandString[3])
				else:
					level = prevLevel + 1
			
			if (commandString[1] == 's'): # "science"
				success = self.tryBuild(self.labs, labCost, level, True, True, discount, prevLevel)
			elif (commandString[1] == 'r'): # "religion"
				success = self.tryBuild(self.temples, templeCost, level, True, True, discount, prevLevel)
			elif (commandString[1] == 'f'):
				success = self.tryBuild(self.farms, farmCost, level, False, True, discount, prevLevel)
			elif (commandString[1] == 'm'):
				 success = self.tryBuild(self.mines, mineCost, level, False, True, discount, prevLevel)
			elif (commandString[1] == 'd'): # "drama"
				success = self.tryBuild(self.theaters, theaterCost, level, True, True, discount, prevLevel)
			elif (commandString[1] == 'g'): # "gladiators"
				success = self.tryBuild(self.arenas, arenaCost, level, True, True, discount, prevLevel)
			elif (commandString[1] == 'l'): # "library" not "lab"
				success = self.tryBuild(self.libraries, libraryCost, level, True, True, discount, prevLevel)
			elif (commandString[1] == 'i'):
				success = self.tryBuild(self.infantry, milCost, level, False, False, discount, prevLevel)
			elif (commandString[1] == 'c'):
				success = self.tryBuild(self.cavalry, milCost, level, False, False, discount, prevLevel)
			elif (commandString[1] == 'a'): 
				success = self.tryBuild(self.artillery, milCost, level, False, False, discount, prevLevel)
			elif (commandString[1] == 'p'):
				success = self.tryBuild(self.airForce, milCost, 3, False, False, discount, prevLevel)
			else:
				return 'no - unrecognized build/upgrade order'
			return success
		if (commandString[0] == 'f'):
			self.myTurn = False
			return "ok"

		return "no - unrecognized command"

	def handleEOT(self, milDecks, age):
		if not self.inRevolt():
			self.produce()
		self.drawMil(milDecks, min(3, self.milActions), max(age,1))
		self.civilActions = self.getCivilActionsMax()
		self.milActions = self.getMilActionsMax()
		if (self.leaderIs("Homer")):
			self.milResource = 1
		else:
			self.milResource = 0
		for c in self.civilHand:
			c.update({"isNew":False})
		self.oceanUsed = False

	def drawMil(self, milDecks, num, age):
		for i in range(num):
			self.milHand.append(milDecks.deck[age].popleft())

	def inRevolt(self):
		return self.getUnhappy() > self.workerPool

	def builtWonders(self):
		maxIndex = len(self.wonders)
		if len(self.wonderRemaining) > 0:
			maxIndex -= 1
		return self.wonders[0:maxIndex]

	def getCivilActionsMax(self):
		ca = int(self.government["CA"])
		for w in self.builtWonders():
			if (len(w["CA"]) > 0):
				ca += int(w["CA"])
		if ("CA" in self.leader and len(self.leader["CA"]) > 0):
			ca += int(self.leader["CA"])
		return ca

	def getMilActionsMax(self):
		ma = int(self.government["MA"])
		for w in self.builtWonders():
			if (len(w["MA"]) > 0):
				ma += int(w["MA"])
		if ("MA" in self.leader and len(self.leader["MA"]) > 0):
			ma += int(self.leader["MA"])
		for t in self.techsInPlay:
			if(t["Type"] == "Military"):
				ma += int(t["MA"]) 
		return ma

	# This is only called for the blue sciences
	def removeTech(self, type):
		level = 0
		for i in range(len(self.techsInPlay)):
			t = self.techsInPlay[i]
			if t["Type"] == type:
				level = ageMap[t["Age"]]
				del self.techsInPlay[i]
		return level
				
	def tryActionCard(self, card, techRow, allMats, extraArg=""):
		if (card["isNew"] == True):
			return "no - can't play card on turn it was picked up"
		name = card["Card Name"]
		age = ageMap[card["Age"]]
		if name == "Engineering Genius":
			discount = [2,3,4,5]
			return self.parseCommand("bw", techRow,allMats, discount[age])
		if name == "Frugality":
			bonusFood = [1,2,3]
			result = self.parseCommand("g", techRow, allMats)
			if result[0:2] == "ok":
				self.gainResource(bonusFood[age],False)
			else:
				return result
		if name == "Ideal Building Site":
			discount = [1,2,3,4]
			if len(extraArg) > 0 and extraArg[0] in ["s","r","l","g","d"]:
				return self.parseCommand("b" + extraArg, techRow, allMats, discount[age])
			else:
				return "no - need to know building type as 3rd arg"
		if name == "Patriotism":
			milResource = [1,2,3,4]
			self.milActions += 1
			self.milResource += milResource[age]
			self.civilActions -= 1
		if name == "Revolutionary Idea":
			idea = [1,2,4,6]
			self.science += idea[age]
			self.civilActions -= 1
		if name == "Rich Land":
			discount = age + 1
			if len(extraArg) > 0 and extraArg[0] in ["f","m"]:
				return self.parseCommand("b" + extraArg, techRow, allMats, discount)
			else:
				return "no - need to know building type as 3rd arg"
		if name == "Work of Art":
			self.culture += 6 - age
			self.civilActions -= 1
		if name == "Bountiful Harvest":
			self.gainResource(age+1, False)
			self.civilActions -= 1
		if name == "Breakthrough":
			bonusSci = [0, 2, 4]
			result = parseCommand("p" + extraArg, techRow, allMats)
			if result == "ok":
				self.science += bonusSci[age]
				return "ok"
			else:
				return result
		if name == "Efficient Upgrade":
			discount = age + 1
			if len(extraArg) > 0 and extraArg[0] in ["s","r","l","g","d","f","m"]:
				return self.parseCommand("u" + extraArg, techRow, allMats, discount)
			else:
				return "no - need to know upgrade params"
				
		if name == "Mineral Deposits":
			self.gainResource(age+1, True)
			self.civilActions -= 1
		if name == "Wave of Nationalism":
			place = self.getMilPlace(allMats) # 0-indexed
			valueArray = [0, 6, 3, 2]
			self.milResource += valueArray[len(allMats)-1] * place
			self.civilActions -= 1
		if name == "Military Build-Up":
			place = self.getMilPlace(allMats)
			valueArray = [0, 8, 5, 3]
			self.milResource += valueArray[len(allMats)-1] * place
			self.civilActions -=1
		if name == "Endowment for the Arts":
			place = self.getCulturePlace(allMats)
			valueArray = [0, 6, 3, 2]
			self.culture += valueArray[len(allMats)-1] * place
			self.civilActions -= 1
		return "ok"

	# This and the following do the appropriate thing for ties
	# (cards are keyed to number of players greater), and
	# also don't really need to check against their player number unless
	# military gets to be expensive to calculate, since number
	# can't be greater than itself
	def getMilPlace(self, mats):
		place = 0
		for mat in mats:
			if mat.getMilitary() > self.getMilitary():
				place += 1
		return place

	def getCulturePlace(self, mats):
		place = 0
		for mat in mats:
			if mat.culture > self.culture:
				place += 1
		return place
		
	def triggerPlayEffects(self, card):
		if (len(card["CA"]) > 0 and not card["Type"] == "Govt"):
			self.civilActions += int(card["CA"])
		if (len(card["MA"]) > 0 and not card["Type"] == "Govt"):
			self.milActions += int(card["MA"])
		if (card["Tech cost"].isdigit()):
			if self.leaderIs("Leonardo da Vinci"):
				self.gainResource(1, True)
			if card["Type"] == "Military":
				self.removeTech("Military")
			if card["Type"] == "Civil":
				lastTech = self.removeTech("Civil")
				if (lastTech < 2 and ageMap[card["Age"]] >= 2):
					resourceReserve += 3
			if card["Type"] == "Colonization":
				lastTech = self.removeTech("Colonization")
				if (lastTech == 0):
					colonizeBonus += ageMap[card["Age"]] + 1
				else:
					colonizeBonus += ageMap[card["Age"]] - lastTech
			if card["Type"] == "Construction":
				self.removeTech("Construction")
				if card["Age"] == "I":
					self.buildDiscount = [0, 1, 1, 1]
					self.wonderRate = 2
				elif card["Age"] == "II":
					self.buildDiscount = [0, 1, 2, 2]
					self.wonderRate = 3
				elif card["Age"] == "III":
					self.buildDiscount = [0, 1, 2, 3]
					self.wonderRate = 4
			age = ageMap[card["Age"]]
			if card["Type"] == "Farm":
				self.farms[age] = 0
			if card["Type"] == "Mine":
				self.mines[age] = 0
			if card["Type"] == "Temple":
				self.temples[age] = 0
			if card["Type"] == "Lab":
				self.labs[age] = 0
			if card["Type"] == "Arena":
				self.arenas[age] = 0
			if card["Type"] == "Library":
				self.libraries[age] = 0
			if card["Type"] == "Theater":
				self.theaters[age] = 0
			if card["Type"] == "Infantry":
				self.infantry[age] = 0
			if card["Type"] == "Cavalry":
				self.cavalry[age] = 0
			if card["Type"] == "Artillery":
				self.artillery[age] = 0
			if card["Type"] == "Air Force":
				self.airForce[age] = 0
			self.techsInPlay.append(card)
		if (card["Type"] == "Leader"):
			# TODO: leader death effects here
			self.leader = card
			# TODO: leader cip effects here
		if (card["Type"] == "Govt"):
			civilActionsUsed = self.getCivilActionsMax() - self.civilActions
			milActionsUsed = self.getMilActionsMax() - self.milActions
			self.government = card
			civilActions = self.getCivilActionsMax() - civilActionsUsed
			milActions = self.getMilActionsMax() - milActionsUsed
			if card["Age"] == "III":
				self.urbanMax = 4
			else:
				self.urbanMax = 3
		if (card["Card Name"] == "Colossus"):
			self.colonizeBonus += 1
		if (card["Card Name"] == "Hollywood"):
			for level in range(4):
				if self.theaters[i] > 0:
					self.culture += 2 * i * self.theaters[i]
				if self.libraries[i] > 0:
					self.culture += 2 * i * self.libraries[i]
		if (card["Card Name"] == "Internet"):	
			for level in range(4):
				if self.labs[i] > 0:
					self.culture += 2 * i * self.labs[i]
				if self.libraries[i] > 0:
					self.culture += 2 * i * self.libraries[i]
		if (card["Card Name"] == "First Space Flight"):
			for tech in self.techsInPlay:
				culture += ageMap[tech["Age"]]
		if (card["Card Name"] == "Fast Food Chains"):
			culture += totalBuildings(self.labs)
			culture += totalBuildings(self.temples)
			culture += totalBuildings(self.farms) * 2
			culture += totalBuildings(self.mines) * 2
			culture += totalBuildings(self.infantry)
			culture += totalBuildings(self.cavalry)
			culture += totalBuildings(self.artillery)
			culture += totalBuildings(self.airForce)
			culture += totalBuildings(self.theaters)
			culture += totalBuildings(self.arenas)
			culture += totalBuildings(self.libraries)
		if (card["Card Name"] == "Homer"):
			self.milResource = 1
				

	def toString(self):
		result = ""
		result += buildingsToString("Labs", self.labs)
		result += buildingsToString("Temples", self.temples)
		result += "Happy/Unhappy: " + str(self.happiness()) + "/" + str(self.getUnhappy()) + "\n"
		result += buildingsToString("Farms", self.farms)
		result += "Food: " + resourceToString(self.food) + " (" + str(self.growCost()) + " to grow)\n"
		result += "Worker Pool: " + str(self.workerPool) + "\n"
		if (self.workerPool > 0 and self.workerPool == self.getUnhappy()):
			result += "~On the brink of revolt~\n"
		if (self.inRevolt()):
			result += "~REVOLT~\n"
		result += buildingsToString("Mines", self.mines)
		result += "Ore: " + resourceToString(self.rocks) + "\n"
		result += "Resource Bank: " + str(self.resourceReserve) + " (" + str(self.resourceReserve - 8) + " before corruption)\n"
		result += "Population Bank: " + str(self.populationBank) + "\n"
		result += buildingsToString("Libraries", self.libraries)
		result += buildingsToString("Theaters", self.theaters)
		result += buildingsToString("Arenas", self.arenas)
		result += buildingsToString("Infantry", self.infantry)
		result += buildingsToString("Cavalry", self.cavalry)
		result += buildingsToString("Artillery", self.artillery)
		if ("Card Name" in self.leader):
			result += "Leader: " + self.leader["Card Name"] + "\n"
		if ("Card Name" in self.tactics):
			result += "Tactics: " + self.tactics["Card Name"] + "\n"
		if (len(self.wonders) > 0):
			result += "Wonders: " + handToString(self.wonders) + " " + str(self.wonderRemaining) + "\n"
		result += "Civil Hand: " + handToString(self.civilHand) + "\n"
		result += "Military Hand: " + handToString(self.milHand) + "\n"
		result += "Civil Actions Left: " + str(self.civilActions) + "/" + str(self.getCivilActionsMax()) + "\n"
		result += "Military Actions Left: " + str(self.milActions) + "/" + str(self.getMilActionsMax()) + "\n"
		#result += "Science: " + str(self.science) + " (+" + str(self.dScience()) + ")\n"
		#result += "Culture: " + str(self.culture) + " (+" + str(self.dCulture()) + ")\n"
		#result += "Military: " + str(self.getMilitary()) + "\n"
		if (len(self.techsInPlay) > 0):
			result += "Techs in play: " + handToString(self.techsInPlay) + "\n"
		if (self.milResource > 0):
			result += "Military-only resources: " + str(self.milResource) + "\n"
		return result


	def farmsProduce(self):
		for i in [3,2,1,0]: # biggest first in case we run out of blue
			if (self.farms[i] > 0):
				amountGained = min(self.farms[i], self.resourceReserve)
				self.food[i] += amountGained
				self.resourceReserve -= amountGained

	def minesProduce(self):
		transcontinental = False
		for w in self.builtWonders():
			if w["Card Name"] == "Transcontinental Railroad":
				transcontinental = True
				break
		for i in [3,2,1,0]:
			if (self.mines[i] > 0):
				amountGained = min(self.mines[i], self.resourceReserve)
				if transcontinental:
					amountGained += 1
					transcontinental = False
				self.rocks[i] += amountGained
				self.resourceReserve -= amountGained

	def produce(self):
		self.culture += self.dCulture()
		self.science += self.dScience()
		self.farmsProduce()
		self.eatFood()
		self.minesProduce()
		self.corruption()

	def eatFood(self):
		if self.populationBank == 0:
			self.loseResource(6, False)
		elif self.populationBank <= 4:
			self.loseResource(4, False)
		elif self.populationBank <= 8:
			self.loseResource(3, False)
		elif self.populationBank <= 12:
			self.loseResource(2, False)
		elif self.populationBank <= 16:
			self.loseResource(1, False)
		return

	def corruption(self):
		if self.resourceReserve == 0:
			self.loseResource(6, True)
		elif self.resourceReserve <= 4:
			self.loseResource(4, True)
		elif self.resourceReserve <= 8:
			self.loseResource(2, True)
		return

	def endTheAge(self, newAge):
		if newAge > 1:
			self.populationBank = max(self.populationBank - 2, 0)
		# TODO:  pacts
		self.civilHand = filter(lambda(x):relativelyModern(x,newAge),self.civilHand)
		self.milHand = filter(lambda(x):relativelyModern(x,newAge),self.milHand)
		if ("Age" in self.leader and not relativelyModern(self.leader, newAge)):
			self.leader = False
		if (len(self.wonders) > 0 and (not relativelyModern(self.wonders[len(self.wonders)-1], newAge)) and len(self.wonderRemaining) > 0):
			self.wonders.pop()
			self.wonderRemaining = []

	def handlePoliticalAction(self, command, allMats, currentEvents, futureEvents, milDecks, civilDecks):
		if (not command.isdigit() and not command == 'n'):
			return "no - enter a number or 'n'"
		if command.isdigit():
			cardNum = int(command)
			if cardNum >= len(self.milHand):
				return "no - no such card exists"
			card = self.milHand[cardNum]
			if card["Type"] == "Event" or card["Type"] == "Territory":
				if len(currentEvents) <= 0:
					currentEvents = futureEvents
					random.shuffle(currentEvents)
					futureEvents = deque([])
				futureEvents.append(card)
				del self.milHand[cardNum]
				self.culture += ageMap[card["Age"]]
				eventNow = currentEvents.popleft()
				self.makeHappen(eventNow, allMats, milDecks, civilDecks)
			elif card["Type"] == "Aggression":
				maCost = 1 # by default
				maCostString = card["MA cost"]
				if maCostString.isdigit(): # may be ?
					maCost = int(maCostString)
					
				num = self.promptForPlayerToAttack(allMats)
				target = allMats[num]
				if card["Card Name"] == "Assassinate":
					if "Age" in target.leader:
						maCost = ageMap[target.leader["Age"]]
					else:
						return "no - no leader"
				elif card["Card Name"] == "Sabotage":
					if len(target.wonderRemaining) > 0:
						maCost = ageMap[target.wonders[len(target.wonders)-1]["Age"]]
					else:
						return "no - no wonder under construction"
				if maCost > self.milActions:
					return "no - not enough military actions"
				self.milActions -= maCost
				attackSac = self.promptForUnitsToSac()
				defSac = target.promptForUnitsToSac()
				totalAttack = self.getMilitary() + attackSac
				totalDefense = target.getMilitary() + defSac
				self.promptForLoss("Strength", attackSac)
				target.promptForLoss("Defense", defSac)
				if totalAttack > totalDefense:
					self.triggerAggression(target, card)
				del self.milHand[cardNum]
			else:
				return "no - not playable as political action"
				
	def triggerAggression(self, target, card):
		name = card["Card Name"]
		if name == "Enslave":
			target.promptForLoss("Any", 1)
			self.gainGenericResource(3)
		elif name == "Plunder":
			while (True):
				choice = self.playerPrompt("How much plunder will be food?", ['0','1','2','3'])
				foodAmount = int(choice)
				if target.getFood() >= foodAmount:
					foodLost = target.loseResource(foodAmount, False)
					rockLost = target.loseResource(3 - foodAmount, True)
					self.gainResource(foodLost, False)
					self.gainResource(rockLost, True)
					break
				else:
					print("That player doesn't have that much.")
		elif name == "Raid":
			buildingsToDestroy = []
			costs = {}
			for i in range(4):
				if target.labs[i] > 0:
					bName = 's' + str(i)
					buildingsToDestroy.append(bName)
					costs.update({bName:labCost[i]})
				if target.temples[i] > 0:
					bName = 'r' + str(i)
					buildingsToDestroy.append(bName)
					costs.update({bName:templeCost[i]})
				if target.arenas[i] > 0:
					bName = 'g' + str(i)
					buildingsToDestroy.append(bName)
					costs.update({bName:arenaCost[i]})
				if target.libraries[i] > 0:
					bName = 'l' + str(i)
					buildingsToDestroy.append(bName)
					costs.update({bName:arenaCost[i]})
			choice = self.playerPrompt("Choose an urban building to destroy:", buildingsToDestroy)
			cost = costs[choice]
			self.gainResource(math.ceil(cost/2), True)
			destroyedArray = target.techDict[choice[0]]
			age = int(choice[1])
			destroyedArray[age] -= 1
			# Again, unclear whether destroyed building kills guy, but assume not since this is brutal
			target.workerPool += 1
			

	def gainGenericResource(self, num):
		for i in range(num):
			response = self.playerPrompt("Gain (r) esources or (f)ood?", ['r','f'])
			if response == 'r':
				self.gainResource(1, True)
			else:
				self.gainResource(1, False)
					

	def handleDiscards(self, numberString):
		if (not numberString.isdigit()):
			return "no - enter a number"
		num = int(numberString)
		if num >= len(self.milHand):
			return "no - number must be less than " + str(len(self.milHand))
		del self.milHand[num]
		return "ok"
			
	def territoryAuction(self, card, allMats):
		playersIn = i in range(len(allMats))
		bidder = self.playerNum
		winningBid = 0
		winningBidder = 0
		while len(playersIn) > 1:
			reply = allMats[playersIn[bidder]].promptBid(winningBid, card)
			if reply[0] == 'p':
				playersIn.remove(bidder)
			else:
				winningBid = int(reply)
				bidder = playersIn[(bidder + 1) % len(playersIn)]
		winner = allMats[playersIn[0]]
		amountToLose = max(winningBid - self.colonizeBonus, 1)
		winner.promptForLoss("Colonize", amountToLose)
		winner.gainTerritory(card)

	# This will need AI
	def promptBid(self, winningBid, card):
		while (True):
			print("Bid for this card (min " + str(winningBid + 1) + "):")
			showCard(card)
			reply = raw_input("Bid or p for pass:")
			if (not reply[0] == 'p' and not reply.isdigit()):
				print("Need a number or p")
			# TODO: Check here for adequate military + cards
			else:
				break
		return reply

	def promptForUnitsToSac(self):
		while (True):
			choice = raw_input("Choose an amount of strength to sacrifice: ")
			if choice.isdigit():
				return int(choice) 

	def promptForPlayerToAttack(self, allMats):
		while True:
			choice = raw_input("Choose a player to attack (1-4): ")
			if choice.isdigit() and int(choice)-1 < len(allMats) and not int(choice)-1 == self.playerNum:
				return int(choice)-1
			

	def promptForLoss(self, mode, amountToLose):
		if not mode == "Any" and not mode == "Building" and "Card Name" in self.tactics:
			tacticsInf = 0
			tacticsCav = 0
			tacticsArt = 0
			[infNeeded, cavNeeded, artNeeded] = figureTacticsReqs(self.tactics)
		while amountToLose > 0:
			prompt = "Choose something to lose (" + mode + ", amount left = " + str(amountToLose) + ")"
			if mode == "Colonize" or mode == "Defense":
				prompt += "or choose (b)onus card to play"
			if mode == "Any":
				prompt += "or lose from (w)orker pool"
			prompt += ": "
			choice = raw_input(prompt)
			if choice[0] == 'b':
				if len(choice) < 2 or not choice[1].isdigit():
					print "Need to specify card number"
					continue
				card = self.milHand[int(choice[1])]
				if not card["Type"] == "Bonus":
					print "Not a bonus card"
					continue
				if mode == "Colonize":
					bonuses = [0,1,2,3]
				elif mode == "Defense":
					bonuses = [0,2,4,6]
				else:
					print("Bonus cards not allowed!")
					continue
				amountToLose -= bonuses[ageMap[card["Age"]]]
				del self.milHand[int(choice[1])]
				continue
			if choice[0] == 'w':
				if not mode == "Any":
					print "Can't lose from worker pool"
					continue
				amountToLose -= 1
				self.workerPool -= 1
				continue
					
			if not choice in self.techDict:
				print("Must choose using build abbreviations (i/c/a etc)")
				continue
			if not choice in ['a','c','i','p']:
				if not not mode == "Building" and not mode == "Any":
					print("Must choose a military unit or (b)onus card.")
					continue
			elif mode == "Building":
				print "Can't sac a mil unit for a building"
				continue
			unitArray = self.techDict[choice[0]]
			if (len(choice) < 2):
				unitAge = 0
			else:
				unitAge = int(choice[1])
			unitArray[unitAge] -= 1
			if mode == "Building":
				# Controversial, but losing to worker pool seems less harsh when 'lose a building' vague
				self.workerPool += 1
			else:
				self.populationBank += 1
			if mode == "Building" or mode == "Any":
				amountToLose -= 1
			else: # Military
				amountToLose -= milStrength[unitAge]
				if "Card Name" in self.tactics:
					if choice[0] == 'i':
						tacticsInf += 1
					elif choice[0] == 'c':
						tacticsCav += 1
					elif choice[0] == 'a':
						tacticsArt += 1
					if tacticsInf >= infNeeded and tacticsCav >= cavNeeded and tacticsArt >= artNeeded:
						amountToLose -= int(self.tactics["Army bonus"])
						tacticsInf -= infNeeded
						tacticsCav -= cavNeeded
						tacticsArt -= artNeeded
					
				
			

	def gainTerritory(self, card, milDecks, civilDecks):
		name = card["Card Name"]	
		age = ageMap[card["Age"]]
		if name == "Developed Territory":
			stuffBonus = [0,1,2]
			sciBonus = [0,3,5]
			self.populationBank += stuffBonus[age]
			self.resourceReserve += stuffBonus[age]
			self.science += sciBonus[age]
		elif name == "Fertile Territory":
			peopleBonus = [0,3,4]
			foodBonus = [0,3,5]
			self.populationBank += peopleBonus[age]
			self.gainResource(foodBonus[age], False)
		elif name == "Historic Territory":
			# Calculate happiness in that function
			if age == 1:
				self.culture += 6
			else:
				self.happiness += 11
		elif name == "Inhabited Territory":
			self.populationBank += 1
			self.workerPool += age
		elif name == "Strategic Territory":
			# Calculate strength in that function
			self.drawMil(milDecks, 1 + age * 2, civilDecks.currentAge())
		elif name == "Wealthy Territory":
			self.resourceReserve += age + 1
			self.gainResource(2 + 3*age, True)
		self.territories.append(card)
		


	def makeHappen(self, card, allMats, milDecks, civilDecks):
		name = card["Card Name"]
		if card["Type"] == "Territory":
			self.territoryAuction(card, allMats, milDecks, civilDecks)
			return
		print name + " happens!"
		print card["Card text and comments"]
		# HEEERRREEE WEEEE GOOOOOOOOOOOOOOOOOOOOOOOOOOOOO!
		if name == "Development of Agriculture":
			for p in allMats:
				p.gainResource(2, False)
		elif name == "Development of Crafts":
			for p in allMats:
				p.gainResource(2, True)
		elif name == "Development of Markets":
			for p in allMats:
				response = p.playerPrompt("Gain (r) esources or (f)ood?", ['r','f'])
				if response == 'r':
					p.gainResource(2, True)
				else:
					p.gainResource(2, False)
		elif name == "Development of Politics":
			for p in allMats:
				p.drawMil(milDecks,3,civilDecks.currentAge())
			self.discardMilThisTurn = False
		elif name == "Development of Religion":
			for p in allMats:
				if p.workerPool >= 1:
					response = p.playerPrompt("Build a free temple with your unused worker? (y/n)", ['y','n'])
					if (response == 'y'):
						p.workerPool -= 1
						p.temples[0] += 1
		elif name == "Development of Science":
			for p in allMats:
				p.science += 2
		elif name == "Development of Settlement":
			for p in allMats:
				p.workerPool += 1
				p.populationBank -= 1
		elif name == "Development of Trade Routes":
			for p in allMats:
				p.science += 1
				p.gainResource(1, True)
				p.gainResource(1, False)
		elif name == "Development of Warfare":
			for p in allMats:
				if p.workerPool >= 1:
					response = p.playerPrompt("Build a free Warrior with your unused worker? (y/n)", ['y','n'])
					if (response == 'y'):
						p.workerPool -= 1
						p.infantry[0] += 1
		# No Event is free, yay
		elif name == "Barbarians":
			cultureLeader = findHighestCulture(allMats, self.playerNum)
			weakest = findWeakest(allMats, self.playerNum, 2)
			if cultureLeader in weakest:
				weakling = allMats[cultureLeader]
				weakling.promptForLoss("Any", 1)
		elif name == "Border Conflict":
			weakest = findWeakest(allMats, self.playerNum, 1)
			strongest = findStrongest(allMats, self.playerNum, 1)
			allMats[weakest[0]].promptForLoss("Building", 1)
			allMats[strongest[0]].gainResource(3, True)
		elif name == "Crusades":
			weakest = findWeakest(allMats, self.playerNum, 1)
			strongest = findStrongest(allMats, self.playerNum, 1)
			allMats[weakest[0]].culture -= 4
			allMats[strongest[0]].culture += 4
		elif name == "Cultural Influence":
			for p in allMats:
				p.culture += p.dCulture()
		elif name == "Foray":
			strongest = findStrongest(allMats, self.playerNum, 2)
			for s in strongest:
				s.gainGenericResource(3)
		elif name == "Good Harvest":
			for p in allMats:
				p.farmsProduce()
		elif name == "Immigration":
			mostHappy = []
			happyLevel = 0
			for p in allMats:
				h = p.happiness()
				if h > happyLevel:
					happyLevel = h
					mostHappy = [p]
				elif h == happyLevel:
					mostHappy.append(p)
			for p in mostHappy:
				p.workerPool += 1
				p.populationBank -= 1
		elif name == "New Deposits":
			for p in allMats:
				p.minesProduce()
		elif name == "Pestilence":
			for p in allMats:
				p.promptForLoss("Any", 1)
		elif name == "Raiders":
			weakest = findWeakest(allMats, self.playerNum, 2)
			for w in weakest:
				p = allMats[w]
				for i in range(2):
					if p.getRocks() == 0:
						p.loseResource(1, False)
					elif p.getFood() == 0:
						p.loseResource(1, True)
					else:
						response = p.playerPrompt("Lose (r) esources or (f)ood?", ['r','f'])
						if response == 'r':
							p.loseResource(1, True)
						else:
							p.loseResource(1, False)
		elif name == "Rats":
			for p in allMats:
				p.loseResource(p.getFood(), False)
		elif name == "Rebellion":
			for p in allMats:
				p.civilActions -= 2 * p.getUnhappy()
		elif name == "Reign of Terror":
			weakest = findWeakest(allMats, self.playerNum, 1)
			weakest[0].promptForLoss("Any", 1)
		elif name == "Scientific Breakthrough":
			for p in allMats:
				p.science += dScience()
		elif name == "Uncertain Borders":
			weakest = findWeakest(allMats, self.playerNum, 1)
			strongest = findStrongest(allMats, self.playerNum, 1)
			weakest[0].populationBank -= 1
			strongest[0].populationBank += 1
			
	def playerPrompt(self, msg, choices):
		while True:
			input = raw_input(msg)
			if not input in choices:
				print "Not a valid choice -- must be one of: " + str(choices)
			else:
				break
		return input
		
def findWeakest(players, currentPlayer, numberToGet):
	if len(players) == 2:
		numberToGet = 1 # 2p game, treat 2's as 1's
	ordering = orderByStrength(players, currentPlayer)
	return ordering[len(players)-numberToGet:]

def findStrongest(players, currentPlayer, numberToGet):
	if len(players) == 2:
		numberToGet = 1 # 2p game, treat 2's as 1's
	ordering = orderByStrength(players, currentPlayer)
	return ordering[0:numberToGet]

# strongest to weakest
def orderByStrength(players, currentPlayer, isCulture = False):
	if isCulture:
		strengths = [p.culture for p in players]
	else:
		strengths = [p.getMilitary() for p in players]
	numPlayers = len(players)
	order = [(currentPlayer + i % numPlayers) for i in range(numPlayers)]
	ordered = True
	for j in range(numPlayers-1):
		for i in range(numPlayers-1):
			if strengths[order[i]] < strengths[order[i+1]]:
				temp = order[i] 
				order[i] = order[i+1]
				order[i+1] = temp
				ordered = False
		if ordered == True:
			break
	return order

def findHighestCulture(players, currentPlayer, numberToGet):
	if len(players) == 2:
		numberToGet = 1 # 2p game, treat 2's as 1's
	ordering = orderByStrength(players, currentPlayer, True)
	return ordering[0:numberToGet]

					
					
			
		
		
			

def relativelyModern(card, currentAge):
	return (ageMap[card["Age"]] >= currentAge - 1)


class Decks:
	def __init__(self, filenames, players):
		self.deck = [[],[],[],[]]
		tempDeck = [[],[],[],[]]
		
		for filename in filenames:
			reader = csv.DictReader(open(filename, "U"))
			for row in reader:
				name = row["Card Name"]  # card name for civil and mil
				if (name in ["", "Philosophy", "Religion", "Agriculture", "Bronze", "Warriors", "Despotism"]):  # starting cards or blank line
					if (name == "Despotism"):
						self.government = row
					continue
				count = int(row[str(players) + "er"])
				age = ageMap[row["Age"]]
				# Row is a dict -- use this as card data
				for i in range(count):
					tempDeck[age].append(row)
		for i in range(4):
			random.shuffle(tempDeck[i])
			self.deck[i] = deque(tempDeck[i])

	def currentAge(self):
		for i in range(4):
			if (len(self.deck[i]) > 0):
				return i
		return 4
				
	def fillRow(self, techRow):
		ageEnd = False
		age = self.currentAge()
		while("-" in techRow):
			techRow.remove("-")
		while (len(techRow) < 13):
			if (age > 3):
				return ageEnd
			lastAge = age
			techRow.append(self.deck[age].popleft())
			age = self.currentAge()
			if(age > lastAge):
				ageEnd = True
		return ageEnd

def printTechRow(techRow):
	for i in range(len(techRow)):
		if (techRow[i] == "-"):  # mixing dicts and strings here
			print("-")
		else:
			print(str(i) + ":" + techRow[i]["Card Name"]+ "@" + str(techRowCost[i]))

def handToString(cardList):
	result = ""
	i = 0
	for card in cardList:
		result += str(i) + ": " + card["Card Name"] + "  "
		i += 1
	return result
		

def isTech(card):
	return not (card["Type"] in ["Wonder", "Leader", "Action"])

def playerSummaryString(playerMatArray):
	result = "\t\t"
	n = len(playerMatArray)
	for i in range (n):
		result += "P " + str(i+1) + "\t"
	result += "\nCulture:\t"
	for i in range (n):
		result += str(playerMatArray[i].culture) + " (+" + str(playerMatArray[i].dCulture()) + ")\t"
	result += "\nScience:\t"
	for i in range (n):
		result += str(playerMatArray[i].science) + " (+" + str(playerMatArray[i].dScience()) + ")\t"
	result += "\nMilitary:\t"
	for i in range (n):
		result += str(playerMatArray[i].getMilitary()) + "\t"
	result += "\n"
	return result
			
def figureTacticsReqs(card):
	infNeeded = 0
	cavNeeded = 0
	artNeeded = 0
	infString = card["Inf"]
	if infString.isdigit():
		infNeeded = int(infString)
	cavString = card["Cav"]
	if cavString.isdigit():
		cavNeeded = int(cavString)
	artString = card["Arty"]
	if artString.isdigit():
		artNeeded = int(artString)
	return [infNeeded, cavNeeded, artNeeded]

# Begin script that will become main function
players = 4
playerMats = [MatState(1), MatState(2), MatState(3), MatState(4)]
myMat = playerMats[0]
civilDecks = Decks(["CivilNonAction.csv","CivilAction.csv"], players)
milDecks = Decks(["Events.csv", "Tactics.csv", "Aggression.csv", "Bonus.csv"], players)
techRow = deque([])
civilDecks.fillRow(techRow)
playerTurn = 0
myPlayerNum = 0
currentEvents = deque([])
futureEvents = deque([])
for i in range(5):
	currentEvents.append(milDecks.deck[0].popleft())

while(True):
	print myMat.toString()
	print playerSummaryString(playerMats)
	printTechRow(techRow)
	reply = myMat.parseCommand(raw_input("Enter a command (h for help): "), techRow, playerMats)
	print reply
	if (not myMat.myTurn):
		myMat.handleEOT(milDecks, civilDecks.currentAge())
		playerTurn = (playerTurn + 1) % players
		# For now, just pop cards on opponent turns
		while (playerTurn != myPlayerNum):
			for i in range(4 - players + 1):
				techRow.popleft()
			ageEnd = civilDecks.fillRow(techRow)
			if (ageEnd):
				print "AGE ENDS"
				for p in playerMats:
					p.endTheAge(civilDecks.currentAge())
			# Actions would go here
			playerMats[playerTurn].handleEOT(milDecks, civilDecks.currentAge())
			playerTurn = (playerTurn + 1) % players
		myMat.myTurn = True
		playerTurn = 0
		print handToString(myMat.milHand)
		reply = myMat.handlePoliticalAction(raw_input("Political action (# or n for none)?"), playerMats, currentEvents, futureEvents, milDecks, civilDecks)
		while myMat.discardMilThisTurn and len(myMat.milHand) > myMat.getMilActionsMax():
			print handToString(myMat.milHand)
			reply = myMat.handleDiscards(raw_input("Choose a military card to discard: "))
		myMat.discardMilThisTurn = True
