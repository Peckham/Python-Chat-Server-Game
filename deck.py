"""
@author: Tavish Peckham
"""

from random import shuffle
"""
    Deck objects are 52 card standard playing card decks.
"""

allCards = [
    "Ace of Diamonds", "Ace of Spades", "Ace of Hearts", "Ace of Clubs",
    "2 of Diamonds", "2 of Spades", "2 of Hearts", "2 of Clubs",
    "3 of Diamonds", "3 of Spades", "3 of Hearts", "3 of Clubs",
    "4 of Diamonds", "4 of Spades", "4 of Hearts", "4 of Clubs",
    "5 of Diamonds", "5 of Spades", "5 of Hearts", "5 of Clubs",
    "6 of Diamonds", "6 of Spades", "6 of Hearts", "6 of Clubs",
    "7 of Diamonds", "7 of Spades", "7 of Hearts", "7 of Clubs",
    "8 of Diamonds", "8 of Spades", "8 of Hearts", "8 of Clubs",
    "9 of Diamonds", "9 of Spades", "9 of Hearts", "9 of Clubs",
    "10 of Diamonds", "10 of Spades", "10 of Hearts", "10 of Clubs",
    "Jack of Diamonds", "Jack of Spades", "Jack of Hearts", "Jack of Clubs",
    "Queen of Diamonds", "Queen of Spades", "Queen of Hearts",
    "Queen of Clubs", "King of Diamonds", "King of Spades", "King of Hearts",
    "King of Clubs"
]
shorthand = [
    "1", "2", "3", "4", "5", "6", "7", "8", "9", "j", "q", "k", "a", "J", "Q",
    "K", "A"
]
S_IDLE = 0
S_FISHLOBBY = 1
S_FISH = 3
S_CHOOSING = 5


class Deck:
    def __init__(self):  # Creates a new deck object.
        self.cards = allCards[:]
        shuffle(self.cards)

    def getDeck(self):  # Returns number of cards left in the deck.
        return len(self.cards)

    def reset(self, cardList):  # Shuffles and returns the deck.
        cardlist = self.shuffle(cardList)
        return cardList

    def draw(self, numToDraw):  # Removes + returns cards from the deck.
        output = []
        if numToDraw < len(self.cards):
            for i in range(numToDraw):
                output.append(self.cards.pop())
        else:
            for i in range(len(self.cards)):
                output.append(self.cards.pop())
        return output

    def reveal(self):  # Returns the top card of the deck.
        topCard = self.cards[0]
        return topCard

    def burn(self, numToBurn):  # Removes the top x cards of the deck.
        if numToBurn < len(self.cards) and numToBurn > 0:
            self.cards = self.cards[numToBurn:]
            return ("%d cards burned." % (numToBurn))
        else:
            return ("Unable to burn %d cards." % (numToBurn))


class DealerBot:
    def __init__(self):
        self.state = S_IDLE
        self.players = {} # The hands of bother players.
        self.deck = Deck() # The 52-card deck.
        self.points = {} # How many points each player has. 

    def consolidate(self): 
        for player in self.players:
            cards = {
                "A": 0,
                "K": 0,
                "Q": 0,
                "J": 0,
                "1": 0,
                "9": 0,
                "8": 0,
                "7": 0,
                "6": 0,
                "5": 0,
                "4": 0,
                "3": 0,
                "2": 0
            }
            for cardType in cards:
                for card in self.players[player]: 
                    if card[0] == cardType:
                        cards[cardType] += 1

                if cards[cardType] / 4 >= 1: # If a player has 4 of one number or face card, those cards are removed from the player's hand and the player recieves a point. 
                    for i in range(4):
                        for card in self.players[player]:
                            if card[0] == cardType:
                                self.players[player].remove(card)

                    self.points[player] += 1

    def handsAreEmpty(self): # Return whether the player's hands are empty or not. 
        for i in self.players:
            if len(self.players[i]) > 0:
                return False
        return True

    def interMsg(self, msg, fromPlayer):
        recipients, response = "all", ""

        if msg == "stop" and self.state != S_IDLE: # Stop the game and set the state to idle.
            response = "Thanks for playing!"
            self.players = {} 
            self.state = S_IDLE
        if msg == "players":
            response = "\n"+" ".join(self.players.keys())

        if self.state == S_IDLE: # If the state is idle and a player types "play", start the DealerBot.
            if msg == "play":
                self.state = S_CHOOSING
                response = """Hello, my name is Dealerbot. Which game would you like to play?>
1. Go Fish
Type 'stop' at any time to end the Dealerbot"""

        if self.state is S_CHOOSING:
            if msg == "1":
                response = "Press 1 to enter the Go Fish lobby (Max 2 players)"
                self.state = S_FISHLOBBY

        elif self.state is S_FISHLOBBY:
            if msg == "1" and len(self.players.keys()) < 4:
                self.players[fromPlayer] = None
                response = "Player %s added. Type go to start." % (fromPlayer)
            elif msg == "1" and len(self.players.keys()) == 4:
                response = "Sorry, game is full!"
            elif msg == "go" and len(self.players.keys()) < 2:
                response = "Not enough players to start a game of Go Fish!"
            elif msg == "go" and len(self.players.keys()) > 1:
                self.state = S_FISH
                drawHand = [i for i in self.players]

                for i in drawHand:
                    self.players[i] = self.deck.draw(5)
                    self.points[i] = 0
                    print("player: ", i, "hand: ", self.players[i])
                recipients = 'all'
                response = "Game on! Type 'hand' to look at cards in your hand, and 'take' followed by a number or the first letter of a face card to attempt to take it from your opponent. "

        elif self.state is S_FISH:
            if msg == "hand": # Return a private message with the contents of the player's hand.
                recipients = 'private'
                response = self.players

            if msg == "points": # Return a private message with how many points the player has.
                recipients = 'private'
                response = {fromPlayer: [str(self.points)]}

            cardsToReturn = []
            if len(msg) == 6 or len(msg) == 7:
                if msg[0:4] == "take": # If the message begins with "take"...
                    if msg[5] in shorthand: # And the following number or letter is shorthand for a card in the deck...
                        cardInQuestion = msg[5]
                        for i in self.players:
                            if i != fromPlayer:
                                for k, j in enumerate(self.players[i]):
                                    if j[0] == cardInQuestion:
                                        cardsToReturn.append(
                                            self.players[i].pop(k))
                                if len(cardsToReturn) > 0:
                                    recipients = 'all'
                                    response = "%s got %s's" % (
                                        fromPlayer, i
                                    ) + str(cardsToReturn) + "!" # A player successfully guessed a card in their opponent's hand.
                                    self.players[fromPlayer].extend(
                                        cardsToReturn)
                        if cardsToReturn == []: # If we look through a player's hand and *don't* find the card that was asked for...
                            recipients = 'all'
                            response = 'go fish, %s!' % (fromPlayer) # Return a "Go Fish" message.
                            self.players[fromPlayer].extend(self.deck.draw(1))
            self.consolidate()

            if (self.deck.getDeck() == 0 and self.handsAreEmpty):
                maxPoint = 0
                maxPlayer = ""
                for i in self.points:
                    if self.points[i] > maxPoint:
                        maxPoint = self.points[i]
                        maxPlayer = i
                recipients = 'all'
                response = maxPlayer + " wins!"

        if response != "":
            if type(response) == str:
                response = " \n[Dealerbot] " + "\n" + response

        return recipients, response
