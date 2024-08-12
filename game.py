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
        
        #wild card mechanic
        if card.label == 14:
            player = self.players.serve()  
            for i in range(4):
                player.add_card(self.draw_card(player, False))
            self.players.append(player)



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
        stack = ArrayStack(Constants.MAX_PLAYERS)
        
        while not self.players.is_empty():
            try:
                stack.push(self.players.serve())
            except Exception as e:
                break
            
        self.players.clear()
        for i in range(0, len(stack)):
            self.players.append(stack.pop())

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
        self.players.append(self.players.serve())

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
        if playing == True:
            if draw.color == self.current_color and draw.label == self.current_label:
                return draw
            else:
                player_updated = self.players.serve().add_card(draw)
                self.players.append(player_updated)
                while self.players.peek() != player_updated:
                    i = self.players.serve()
                    self.players.append(i)
        else:
            return draw
            
        # if playing == True:
        #     drawing = True
        #     while drawing == True:
        #         draw = self.draw_pile.pop()
        #         if draw.color != self.current_color and draw.label != self.current_label:
        #             player.add_card(draw)
        #         else:
        #             player.add_card(draw)
        #             drawing = False
        # else:
        #     player.add_card(draw)
        
        # return player
                
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
        player = self.players.serve()
        self.players.append(player)
        return player

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
        """
        raise NotImplementedError


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

