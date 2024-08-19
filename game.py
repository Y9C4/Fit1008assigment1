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
            Best Case Complexity:
            Worst Case Complexity:
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
            Best Case Complexity:
            Worst Case Complexity:
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
            player.add_card(cards_array[index])
            self.players.append(player)    
            dealt+=1        
        
        #Pass the remaining cards into the draw_pile
        self.draw_pile = ArrayStack(Constants.DECK_SIZE - dealt)
        for i in range(dealt, len(cards_array)):
            self.draw_pile.push(cards_array[i])

        #Draw the first card
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
            Best Case Complexity:
            Worst Case Complexity:
        """    
        self.current_color = CardColor(RandomGen.randint(0,3))
        self.current_label = card.label
        
        #draw four card mechanic
        if self.current_label == 'DRAW_FOUR':
            player = self.next_player() #appends the current player and pulls the drawing player
            for i in range(4):
                try:
                    self.draw_card(player, False)
                except Exception as e:
                    self.shuffle()
                    self.draw_card(player, False)
            
            self.players.append(player) #appends the drawing player
            self.current_player = None #ensures no duplicates
        
        # if card.label.name == 'DRAW_FOUR':
        #     for i in range(len(self.players.array)):
        #         print(self.players.array[i].name)
        #     print('current', self.current_player.name)
        #     self.players.append(self.current_player)
        #     player = self.players.serve()
        #     for i in range(4):
        #         try:
        #             self.draw_card(player, False)
        #         except Exception as e:
        #             print("shuffled at draw four")
        #             self.shuffle()
        #             self.draw_card(player, False)
            
        #     self.players.append(player)



    def play_reverse(self) -> None:
        """
        a method that changes the direction of play. If the direction of play is clockwise, it should be changed to anti-clockwise, and vice versa. The method should return None.

        Args:
            None

        Returns:
            None

        Complexity:
            Best Case Complexity:
            Worst Case Complexity:  
        """        
        stack = ArrayStack(self.players.length)
        stack_list =[]

        for i in range(self.players.length):
            stack.push(self.players.serve())
        
        # stack_copy = stack
        
        # for i in range(stack_copy.length):
        #     stack_list.append(stack_copy.pop().name)
        # stack_list.append(self.current_player.name)

        # print("reversed list: ", stack_list)
        
        self.players.clear()

        for i in range(stack.length):
            self.players.append(stack.pop())
        self.players.append(self.current_player)

        self.current_player = None

    def play_skip(self) -> None:
        """
        Method to play a skip card

        Args:
            None

        Returns:
            None

        Complexity:
            Best Case Complexity:
            Worst Case Complexity:
        """       
        self.players.append(self.current_player)
        self.current_player = self.players.serve()
        # self.players.append(self.current_player)
        # self.current_player = None

    def draw_card(self, player: Player, playing: bool) -> Card | None:
        """
        A method that takes a Player object as an argument and draws a Card object from the draw_pile. If the card can be played and the playing argument is True, the card should be returned. Otherwise, the card should be added to the player's hand and the method should return None. This method should be called multiple times if the special card is a Draw 2 or Draw 4.

        Args:
            player (Player): The player who is drawing the card
            playing (bool): A boolean indicating if the player is able to play the card

        Returns:
            Card - When drawing a playable card, other return None

        Complexity:
            Best Case Complexity:
            Worst Case Complexity:
        """
        draw = self.draw_pile.pop()
        
        if playing == True: #This condition is only true if the current player is drawing
            drawing = True
            while drawing == True:
                if draw.color == self.current_color or draw.label == self.current_label or draw.color.name == 'CRAZY':
                    return draw
                else:
                    self.current_player.add_card(draw)
                    draw = self.draw_pile.pop()
        else:
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
            Best Case Complexity:
            Worst Case Complexity:
        """
        served = self.players.serve()

        if self.current_player != None:
            self.players.append(self.current_player)        
        
        return served
    
    def shuffle(self) -> None:
        top_card = self.discard_pile.pop()
        temp = ArrayR(len(self.discard_pile))
        for i in range(len(self.discard_pile)):
            temp[i] = self.discard_pile.pop()
        RandomGen.random_shuffle(temp)
        for i in range(len(temp)):
            self.draw_pile.push(temp[i])
        self.discard_pile.push(top_card)

    def play_game(self) -> Player:
        """
        Method to play the game

        Args:
            None

        Returns:
            Player: The winner of the game

        Complexity:
            Best Case Complexity:
            Worst Case Complexity:
            
            play_game(self) - a method that starts the game. The game should continue until a player has no cards left in their hand. The method should return a reference to the player who won the game. You should utilise the methods defined above to achieve this method's purpose. Please remember the rules of the game! Here is a summary of the rules: 
        """
        while True:

            self.current_player = self.next_player() #player removed from queue
            cPlayer = self.current_player
            played=False
            
            i=0

            while i < self.current_player.hand.length:
                current_card = self.current_player.hand[i]
                if current_card.color == self.current_color or current_card.label == self.current_label or current_card.color.name == 'CRAZY':
                    self.current_player.hand.delete_at_index(i)
                    self.discard_pile.push(current_card)
                    break
                else:
                    i+=1
            #print("new hand size: ", len(self.current_player.hand))
            
            if played == False:
                try:
                    new_draw = self.draw_card(self.current_player, True)

                except Exception as e:

                    self.shuffle()
                    new_draw = self.draw_card(self.current_player, True)
                
                self.discard_pile.push(new_draw)           
                
            self.current_color, self.current_label = self.discard_pile.peek().color, self.discard_pile.peek().label
            
            #print(self.current_player.name, "has played a ", self.current_color.name, self.current_label.name)

        
            if self.current_label == 'DRAW_TWO':
                player = self.next_player() #appends current_player and serves the next player in the queue
                for i in range(2):
                    try:
                        self.draw_card(player, False) 
                    except Exception as e:
                        self.shuffle()
                        self.draw_card(player, False)
                self.players.append(player)

                self.current_player = None
            
            if self.current_color.name == 'CRAZY':            
                self.crazy_play(self.discard_pile.peek())
                       
            elif len(cPlayer.hand) < 1:
                return cPlayer
            
            elif self.current_label.name == 'REVERSE':
                self.play_reverse()

            elif self.current_label.name == 'SKIP':
                self.play_skip()

            

            
            
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

