from data_structures.referential_array import ArrayR
from data_structures.queue_adt import CircularQueue
from data_structures.stack_adt import ArrayStack
from player import Player
from card import CardColor, CardLabel, Card
from random_gen import RandomGen
from constants import Constants


class Game:
    """
    Game class to play the game
    """
    def __init__(self) -> None:
        """
        Constructor for the Game class

        Args:
            None

        Returns:
            None

        Complexity:
            Best Case Complexity: O(1)
            Worst Case Complexity: O(1)
        """
        self.players = None
        self.draw_pile = None
        self.discard_pile = None
        self.current_player = None
        self.current_color = None
        self.current_label = None

    def generate_cards(self) -> ArrayR[Card]:
        """
        Method to generate the cards for the game

        Args:
            None

        Returns:
            ArrayR[Card]: The array of Card objects generated

        Complexity:
            Best Case Complexity: O(N) - Where N is the number of cards in the deck
            Worst Case Complexity: O(N) - Where N is the number of cards in the deck
        """
        list_of_cards: ArrayR[Card] = ArrayR(Constants.DECK_SIZE)
        idx: int = 0

        for color in CardColor:
            if color != CardColor.CRAZY:
                # Generate 4 sets of cards from 0 to 9 for each color
                for i in range(10):
                    list_of_cards[idx] = Card(color, CardLabel(i))
                    idx += 1
                    list_of_cards[idx] = Card(color, CardLabel(i))
                    idx += 1

                # Generate 2 of each special card for each color
                for i in range(2):
                    list_of_cards[idx] = Card(color, CardLabel.SKIP)
                    idx += 1
                    list_of_cards[idx] = Card(color, CardLabel.REVERSE)
                    idx += 1
                    list_of_cards[idx] = Card(color, CardLabel.DRAW_TWO)
                    idx += 1
            else:
                # Generate the crazy and crazy draw 4 cards
                for i in range(4):
                    list_of_cards[idx] = Card(CardColor.CRAZY, CardLabel.CRAZY)
                    idx += 1
                    list_of_cards[idx] = Card(CardColor.CRAZY, CardLabel.DRAW_FOUR)
                    idx += 1

                # Randomly shuffle the cards
                RandomGen.random_shuffle(list_of_cards)

                return list_of_cards

    def initialise_game(self, players: ArrayR[Player]) -> None:
        """
        Method to initialise the game

        Args:
            players (ArrayR[Player]): The array of players

        Returns:
            None

        Complexity:
            Best Case Complexity: O(log(N)) where N is the number of cards handed out. len(players)*num_cards_at_init
            Worst Case Complexity: O(log(N)) where N is the number of cards handed out. len(players)*num_cards_at_init
        """
        #Use the array of Player objects being passed to this method to populate the players attribute of the Game object.        
        self.players = CircularQueue(len(players))
        
        for player in players:
            self.players.append(player)

        # Call the method generate_cards to get an ArrayR of all cards
        cards_array = self.generate_cards()

        #Deal the cards one by one to each player.
        dealt=0
        for index in range(0, len(self.players)*Constants.NUM_CARDS_AT_INIT): 
            player = self.players.serve()
            player.add_card(cards_array[index]) #complexity of O(log(N))
            self.players.append(player)    
            dealt+=1        
        
        #Pass the remaining cards into the draw_pile
        self.draw_pile = ArrayStack(Constants.DECK_SIZE - dealt)
        for i in range(dealt, len(cards_array)): #O(N) where N is the number of cards in the draw_pile
            self.draw_pile.push(cards_array[i])

        #Draw the first card, best case scenario: O(1), worst case: O(32) as there are 32 non number cards in a suit
        self.discard_pile = ArrayStack(Constants.DECK_SIZE)
        legal_draw = False
        while legal_draw == False:
            first_draw = self.draw_pile.pop()
            if first_draw.label < 9 or first_draw.color < 3:
                legal_draw = True
            self.discard_pile.push(first_draw)
        
        #update current card attributes
        current_card = self.discard_pile.peek()
        self.current_color = current_card.color
        self.current_label = current_card.label

    def crazy_play(self, card: Card) -> None:
        """
        a method that takes a Card object and changes the game's current_color instance variable to a randomly chosen color. To choose the color, we use the following code: CardColor(RandomGen.randint(0,3)) where RandomGen is an instance of the RandomGen class and CardColor is an enum class representing the colors of the cards. If its a CRAZY Draw 4 card, this method makes the next player draw 4 cards from the draw_pile. The method should return None.

        Redundant calls to RandomGen.randint(0,3) will result in a loss of marks similar to as is explained with RandomGen.random_shuffle(temp_array) in Task 4.

        You can assume that the card being passed is a CRAZY card.

        Try to reuse predefined methods where possible to achieve this. Not reusing methods will result in a loss of marks.

        Args:
            card (Card): The card to be played

        Returns:
            None

        Complexity:
            Best Case Complexity: O(1)
            Worst Case Complexity: O(N) occurs when the card deck is empty and self.shuffle is called which has a linear time complexity.
        """    
        self.current_color = CardColor(RandomGen.randint(0,3))
        self.current_label = card.label
        
        if self.current_label.name == 'DRAW_FOUR':
            if self.current_player == None:
                drawing_player = self.players.serve()
            else:            
                self.players.serve() #removes the duplicate current_player item
                drawing_player = self.players.serve() #peeks the drawing player
                self.players.append(self.current_player)

            for i in range(4):
                self.draw_card(drawing_player, False) #O(1) or O(3N)
            
            self.players.append(drawing_player)
            self.current_player = None


    def play_reverse(self) -> None:
        """
        a method that changes the direction of play. If the direction of play is clockwise, it should be changed to anti-clockwise, and vice versa. The method should return None.

        Args:
            None

        Returns:
            None

        Complexity:
            Best Case Complexity: O(N) where N is the number of players in the game.
            Worst Case Complexity: O(N) where N is the number of players in the game.
        """        
        print('reverse played')
        stack = ArrayStack(self.players.length)
        self.players.serve() #get rid of current player who hasn't yet played the reverse card

        stack.push(self.current_player) #current player will go first.

        for i in range(self.players.length):
            stack.push(self.players.serve())
    
        self.players.clear()

        for i in range(stack.length):
            self.players.append(stack.pop())

        self.current_player = None

    def play_skip(self) -> None:
        """
        Method to play a skip card

        Args:
            None

        Returns:
            None

        Complexity:
            Best Case Complexity: O(1) everything is constant time complexity.
            Worst Case Complexity: O(1) everything is constant time complexity.
        """
        if self.current_player == None: #passes the test 3.7 as in a normal setting self.current_player wouldn't be empty
            skipped_player = self.players.serve()
            self.players.append(skipped_player)
        else:
            self.players.serve() #removes the current_player duplicate
            self.players.append(self.current_player) #adds back the current_player
            skipped_player = self.players.serve()
            self.players.append(skipped_player)
            self.current_player = None #ensures that the next player isn't skipped as well

    def draw_card(self, player: Player, playing: bool) -> Card | None:
        """
        A method that takes a Player object as an argument and draws a Card object from the draw_pile. If the card can be played and the playing argument is True, the card should be returned. Otherwise, the card should be added to the player's hand and the method should return None. This method should be called multiple times if the special card is a Draw 2 or Draw 4.

        Args:
            player (Player): The player who is drawing the card
            playing (bool): A boolean indicating if the player is able to play the card

        Returns:
            Card - When drawing a playable card, other return None

        Complexity:
            Best Case Complexity: O(1) Best case ocurrs when playing is true and .pop() has a complexity of O(1)
            Worst Case Complexity: O(N) happens when cards have to shuffle before being .pop()'d. 
        """
        if self.draw_pile.length < 1: #deal with empty draw pile 
            self.shuffle()        
        if playing == True:
            draw = self.draw_pile.pop()
            return draw
        else:            
            draw = self.draw_pile.pop()
            player_index = self.players.array.index(player)
            self.players.array[player_index].add_card(draw)
                
    def next_player(self) -> Player:
        """
        A method that gets the Player object of the next player (note: if current_player is None, this should simply return the Player to play the next turn). This will be helpful when you are making the next player draw cards. The method should return the Player object of the next player. This method should NOT update the current_player of the game object. This method should merely probe the next player in the order of the players.

        Args:
            None

        Returns:
            Player: The next player

        Complexity:
            Best Case Complexity: O(1) .peek() has a constant complexity
            Worst Case Complexity: O(1) .peek() has a constant complexity
        """
        return self.players.peek()

    def shuffle(self) -> None:
        """
        A method that shuffles the cards in the discard pile to fill up the draw pile.
        Args:
            None

        Returns:
            None

        Complexity:
            Best Case Complexity: O(N) where N is the number of cards being shuffled from the discard pile, the runtime is linear.
            Worst Case Complexity: O(N) where N is the number of cards being shuffled from the discard pile, the runtime is linear.
        """
        top_card = self.discard_pile.pop()
        temp = ArrayR(len(self.discard_pile))
        for i in range(len(self.discard_pile)): 
            temp[i] = self.discard_pile.pop() 
        RandomGen.random_shuffle(temp) 
        for i in range(len(temp)): 
            self.draw_pile.push(temp[i])
        self.discard_pile.push(top_card)
    
    def draw_two(self) -> None:
        """
        Method to draw 2 and skip the drawing player
        Best Case Complexity: O(1)
        Worst Case Complexity: O(1)
        """
        self.players.serve()
        drawing_player = self.players.peek()
        self.players.append(self.current_player)

        for _ in range(2):
            self.draw_card(drawing_player, False)

        self.players.serve()
        self.players.append(drawing_player)
        self.current_player = None

    def play_game(self) -> Player:
        """
        Method to play the game

        Args:
            None

        Returns:
            Player: The winner of the game

        Complexity:
            Best Case Complexity: O(P*C) (Where P is the number of players, and C is the number of cards in the deck)
            Worst Case Complexity: O(P*C) (Where P is the number of players, and C is the number of cards in the deck)
            
            play_game(self) - a method that starts the game. The game should continue until a player has no cards left in their hand. The method should return a reference to the player who won the game. You should utilise the methods defined above to achieve this method's purpose. Please remember the rules of the game! Here is a summary of the rules: 
        """
        while True:
            if self.current_player != None:
                self.players.serve() #gets rid of the first item which has been iterated in self.current_player
                self.players.append(self.current_player) #appends the updated element
            
            self.current_player = self.next_player() #peeks the next player object

            played=False #ensures the current player has finished 
            i=0
            while i < len(self.current_player.hand):
                current_card = self.current_player.hand[i]
                if current_card.color == self.current_color or current_card.label == self.current_label or current_card.color.name == 'CRAZY':
                    self.current_player.hand.delete_at_index(i)
                    self.discard_pile.push(current_card)
                    played = True
                    break
                else: 
                    i+=1            
            if played == False:
                new_draw = self.draw_card(self.current_player, True)
                if new_draw.color == self.current_color or new_draw.label == self.current_label or new_draw.color.name == 'CRAZY':
                    self.discard_pile.push(new_draw)
                    played = True           
                else:
                    self.current_player.add_card(new_draw)
            self.current_color, self.current_label = self.discard_pile.peek().color, self.discard_pile.peek().label

            cPlayer = self.current_player
            if self.current_label.name == 'DRAW_TWO' and played == True:
                self.draw_two()
            if self.current_color.name == 'CRAZY' and played == True:
                card = self.discard_pile.peek()                
                self.crazy_play(card)
            
            elif len(cPlayer.hand) < 1:
                return cPlayer
            
            elif self.current_label.name == 'REVERSE' and played == True:
                self.play_reverse()
            elif self.current_label.name == 'SKIP' and played == True:
                self.play_skip()
        return "DRAW"

def test_case():
    players: ArrayR[Player] = ArrayR(4)
    players[0] = Player("Alice", 0)
    players[1] = Player("Bob", 1)
    players[2] = Player("Charlie", 2)
    players[3] = Player("David", 3)

    g: Game = Game()
    g.initialise_game(players)
    winner: Player = g.play_game()
    print(f"Winner is {winner.name}")


if __name__ == '__main__':
    test_case()

