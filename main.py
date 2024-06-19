# -------
# IMPORTS
# -------

from pyscript import document
from js import window
from js import localStorage
import pyodide_http
import requests
import time
import random as rand

# ----------------
# DEFINING GLOBALS
# ----------------

blacklist = [] # defining blacklist
cardList = [[],[],[],[]] # defining blacklist

# -----------
# SUBPROGRAMS
# -----------

# loads the blacklist from localstorage into a string
def load_blacklist():
    global blacklist
    
    blacklistStr = localStorage.getItem("blacklistStr")
    if blacklistStr != None:
        blacklist = blacklistStr.split("|")
        blacklist.pop(len(blacklist)-1)
        print_list()

# ----------------------------------------

# takes the item from the textbox, and adds it to the blacklist
def add_item(event):
    item = document.getElementById("list-box")
    item = item.value

    if item in sum(cardList, []) and item not in blacklist:
        blacklist.append(item)
    
    print_list()
    save_list()

# ----------------------------------------

# displays the list on the UI
def print_list():
    blacklistElement = document.getElementById("blacklist")
    blacklistElement.innerHTML = ""
    for i in blacklist:
        blacklistElement.innerHTML += (f"<li><input type=\"checkbox\" py-click=\"remove_item\" checked></input><label>{i}</label></li>")

# ----------------------------------------

# saves the list to localstorage
def save_list():
    blacklistStr = ""

    for i in blacklist:
        blacklistStr = (blacklistStr + i + "|")
    localStorage.setItem("blacklistStr", blacklistStr)

# ----------------------------------------    

# removes an item from the list
def remove_item(event):
    blacklist.remove(event.target.nextSibling.innerText)
    print_list()
    save_list()

# ----------------------------------------    

# displays the 4 boxes to input how many of each rarity you want, and hides the others
def show_rarity(event):
    rarityBoxes = document.getElementById("rarityBoxes")
    rarityBoxes.style.display = "block"
    overallBox = document.getElementById("overallBox")
    overallBox.style.display = "none"
    
# ----------------------------------------

# displays the box to input how many overall cards you want, and hides the others
def show_total(event):
    rarityBoxes = document.getElementById("rarityBoxes")
    rarityBoxes.style.display = "none"
    overallBox = document.getElementById("overallBox")
    overallBox.style.display = "block"

# ----------------------------------------

# interracts with the wikimedia api, and gets all the pages in a specified category
# side note, i hate the wikimedia api
def getPagesInCategory(api, category):
    obtainableCards = []
    apiUrl = api
    apiParams = {
        "action": "query",
        "format": "json",
        "list": "categorymembers",
        "cmtitle": category,
        "cmprop": "title",
        "cmlimit": "500",
        "origin": "*"
    }

    response = requests.get(apiUrl, params = apiParams)
    

    while "continue" in response.json():
        apiParams.update({"cmcontinue": response.json()["continue"]["cmcontinue"]})
        pages = response.json()["query"]["categorymembers"]

        for i in pages:
            obtainableCards.append(i["title"])
        response = requests.get(apiUrl, params = apiParams)
    
    pages = response.json()["query"]["categorymembers"]
    for i in pages:
        obtainableCards.append(i["title"])


    return(obtainableCards)

# ----------------------------------------

# gets a list of all the obtainable cards from the wiki
def getObtainableCards():
    global cardList
  
    wiki = "https://hexaria-full-version.fandom.com/api.php"
    
    print("getting cards from wiki\nthere's also probably a ton of errors, don't know what they mean but it works despite them")
    
    # getting lists for all cards and unobtainable cards
    wikiCards = getPagesInCategory(wiki, "Category:Card")
    unobCardList = getPagesInCategory(wiki, "Category:Unobtainable")

    print("i think things broken")
    # removing unobtainable cards from the obtainable list
    for i in wikiCards[:]:
        if i in unobCardList:
            wikiCards.remove(i)
            print(i)
  
    wikiCards.remove("Cards List")    # manually removing some exceptions
    print("1")
    wikiCards.remove("Envenomed Tokens")
    print("2")
    wikiCards.remove("Inflamed Tokens")
    print("3")
    wikiCards.remove("Tomes")
    print("4")
    
    for card in wikiCards:
        rarity = getRarity(card)
        cardList[rarity].append(card)


# ----------------------------------------

# checks if the card list needs to be pulled from the wiki again
# i gotta give this a better name than lastWikiGet
def lastWikiGet():
    global cardList
    
    currentTime = int(time.time())
    lastTime = localStorage.getItem("lastWikiGet")
    
    # checks if the timestamp is there, if not make it an interger for the next check
    if  lastTime == None:
        
        localStorage.setItem("lastWikiGet", "0")
        lastTime = int(localStorage.getItem("lastWikiGet"))
    else:
        lastTime = int(lastTime)
        
    # checks if it's been 20 hours since the list was last pulled, if so pull it again
    if (currentTime-72000) > lastTime:
        localStorage.setItem("lastWikiGet", currentTime)
        getObtainableCards()
        saveObtainableCards()
    else:
        loadObtainableCards()
        
# ----------------------------------------

# saves the card list to localstorage
def saveObtainableCards():
    global cardList
    
    
    commons = ""
    rares = ""
    ultras = ""
    legendaries = ""
       
    for i in range(len(cardList)):
        for card in cardList[i]:
            if i == 0:
                commons = (commons + card + "|")
            if i == 1:
                rares = (rares + card + "|")
            if i == 2:
                ultras = (ultras + card + "|")
            if i == 3:
                legendaries = (legendaries + card + "|")

        localStorage.setItem("commons", commons)
        localStorage.setItem("rares", rares)
        localStorage.setItem("ultras", ultras)
        localStorage.setItem("legendaries", legendaries)

# ----------------------------------------

# loads the card list from localstorage
def loadObtainableCards():
    global cardList
    
    commons = localStorage.getItem("commons")
    rares = localStorage.getItem("rares")
    ultras = localStorage.getItem("ultras")
    legendaries = localStorage.getItem("legendaries")




    cardList[0] = commons.split("|")
    cardList[0].pop(len(cardList[0])-1)

    cardList[1] = rares.split("|")
    cardList[1].pop(len(cardList[1])-1)

    cardList[2] = ultras.split("|")
    cardList[2].pop(len(cardList[2])-1)

    cardList[3] = legendaries.split("|")
    cardList[3].pop(len(cardList[3])-1)

# ----------------------------------------

def dropdownInit():
    global cardList
	
    
    options = ""

    for card in sum(cardList, []):
        
        options += f'<option value="{card}"/>'
    document.getElementById("cards").innerHTML = options

# ----------------------------------------

def getRarity(card):
    wiki = "https://hexaria-full-version.fandom.com/api.php"

    if not hasattr(getRarity, "common"):
        getRarity.common = set(getPagesInCategory(wiki,"Category:Common_cards"))
    
    if not hasattr(getRarity, "rare"):
        getRarity.rare = set(getPagesInCategory(wiki,"Category:Rare_cards"))
    
    if not hasattr(getRarity, "ultra"):
        getRarity.ultra = set(getPagesInCategory(wiki,"Category:Ultra_Rare_cards"))
    
    if not hasattr(getRarity, "legendary"):
        getRarity.legendary = set(getPagesInCategory(wiki,"Category:Legendary_cards"))
    
    if card in getRarity.legendary:
        return(3)
    elif card in getRarity.ultra:
        return(2)  
    elif card in getRarity.rare:
        return(1)
    elif card in getRarity.common:
        return(0)

# ----------------------------------------

def generateDeck(event):
    global blacklist
    global cardList

    validLimits = False
    validDeck = False
    deck = [[],[],[],[]]
    limits = [0, 0, 0, 0]    # (commonLimit, rareLimit, ultraLimit, legendaryLimit)
    cleanCardList = cardList # cardList, but without the cards in the blacklist

    vals = [document.getElementById("box1").value,
    document.getElementById("box2").value,
    document.getElementById("box3").value,
    document.getElementById("box4").value,
    document.getElementById("box5").value]

        
    for card in blacklist:
        for i in range(len(cleanCardList)):
            if card in cleanCardList[i]:
                cleanCardList[i].remove(card)
  
    rarityChecked = document.getElementById("rarityRad").checked
    totalChecked = document.getElementById("totalRad").checked


    for i in range(len(vals)):
        if vals[i] == '':
            vals[i] = 0

    
    if rarityChecked == True:
        limits = [
        int(vals[0]),
        int(vals[1]),
        int(vals[2]),
        int(vals[3])
        ]    # assigning the variables in the string
        deckSize = sum(limits)
    elif totalChecked == True:
        deckSize = int(vals[4])
        
        commonLen = len(cleanCardList[0])
        rareLen = len(cleanCardList[1])
        ultraLen = len(cleanCardList[2])
        legendaryLen = len(cleanCardList[3])
        
        for i in range(0,deckSize):
            pickedCard = rand.randint(0,len(sum(cleanCardList,[])))

            if pickedCard < commonLen:
                limits[0] += 1
            elif pickedCard < commonLen + rareLen:
                limits[1] += 1
            elif pickedCard < commonLen + rareLen + ultraLen:
                limits[2] += 1
            else:
                limits[3] += 1
            
          

    else:
        window.alert("Neither generation option was selected")
        return
    if deckSize < 1:
        window.alert("Deck size would be zero or less, please make deck size be 1-50")
        return

    conditions = [
deckSize <= 50,
limits[0] <= len(cleanCardList[0])*4,
limits[1] <= len(cleanCardList[1])*3,
limits[2] <= len(cleanCardList[2])*2,
limits[3] <= len(cleanCardList[3])*1
    ]
      
    if all(conditions):
        validLimits = True
    else:
        window.alert("Total deck size exceeds 50 cards or exceeds the number of available cards in a category")
        return
    
    # enumerate iterates through the items and keeps track of the iteration
    for i, limit in enumerate(limits):
        validDeck = False    # resetting this after each rarity is done
    
        while validDeck == False and limit != 0:    # doesn't make a deck of 0 cards
            card = cleanCardList[i][rand.randint(0,len(cleanCardList[i])-1)]    # getting a random card
            count = deck[i].count(card)    # checks how many of the card are in the deck
      
            if count < (4-i):    # makes there aren't too many copies of the card
                deck[i].append(card)
                count = 0
            else:    # goes back and gets a new card if there's too many of the chosen one
                count = 0
                
            if len(deck[i]) == limit:    # checking if we've generated enough cards
                validDeck = True
    printDeck(deck)

# ----------------------------------------

def printDeck(deck):
    headers = document.getElementsByClassName("rarityHeader");
    for i in headers:
        i.style.display = "inline"
    
    commonCards = document.getElementById("commonCards")
    commonCards.textContent = ""
    for i in deck[0]:
        commonCards.textContent += f"{i}, "
    
    rareCards = document.getElementById("rareCards")
    rareCards.textContent = ""
    for i in deck[1]:
        rareCards.textContent += f"{i}, "

    ultraCards = document.getElementById("ultraCards")
    ultraCards.textContent = ""
    for i in deck[2]:
        ultraCards.textContent += f"{i}, "

    legendaryCards = document.getElementById("legendaryCards")
    legendaryCards.textContent = ""
    for i in deck[3]:
        legendaryCards.textContent += f"{i}, "
# ----------
# MAIN STUFF
# ----------

pyodide_http.patch_all() # patching stuff to make it work in pyscript

lastWikiGet()

load_blacklist() # loading the blacklist

dropdownInit()


