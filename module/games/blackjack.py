#  ------------------------------------------------------------
#  Copyright (c) 2024 Rystal-Team
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.
#  ------------------------------------------------------------
#

import random
from enum import Enum


class BlackjackResult(Enum):
    """
    Enum representing the possible outcomes of a Blackjack game.
    """

    PLAYER_BUSTS = 1
    DEALER_BUSTS = 2
    TIE = 3
    PLAYER_WINS = 4
    DEALER_WINS = 5
    PLAYER_BLACKJACK = 6


class Blackjack:
    """
    A class to represent a game of Blackjack.
    """

    def __init__(self):
        """
        Initialize the Blackjack game with a shuffled deck and empty hands for player and dealer.
        """
        self.deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11] * 4
        random.shuffle(self.deck)
        self.player_hand = []
        self.dealer_hand = []

    def deal_card(self, hand):
        """
        Deal a card from the deck to the specified hand.

        Parameters:
        hand (list): The hand to which the card will be dealt.
        """
        hand.append(self.deck.pop())

    def calculate_hand(self, hand):
        """
        Calculate the total value of a hand, adjusting for Aces as necessary.

        Parameters:
        hand (list): The hand to be calculated.

        Returns:
        int: The total value of the hand.
        """
        total = sum(hand)
        while total > 21 and 11 in hand:
            total -= 10
            hand[hand.index(11)] = 1
        return total

    def start_game(self):
        """
        Start the game by dealing two cards to both the player and the dealer.

        Returns:
        tuple: The initial totals of the player's and dealer's hands.
        """
        for _ in range(2):
            self.deal_card(self.player_hand)
            self.deal_card(self.dealer_hand)
        return self.calculate_hand(self.player_hand), self.calculate_hand(
            self.dealer_hand
        )

    def hit(self, hand):
        """
        Deal a card to the specified hand and calculate the new total.

        Parameters:
        hand (list): The hand to which the card will be dealt.

        Returns:
        tuple: The new total of the hand and a boolean indicating if the total is 21 or more.
        """
        self.deal_card(hand)
        total = self.calculate_hand(hand)
        return total, total >= 21

    def stand(self):
        """
        Complete the dealer's hand by dealing cards until the total is at least 17.

        Returns:
        int: The final total of the dealer's hand.
        """
        while self.calculate_hand(self.dealer_hand) < 17:
            self.deal_card(self.dealer_hand)
        return self.calculate_hand(self.dealer_hand)

    def check_winner(self):
        """
        Determine the winner of the game based on the totals of the player's and dealer's hands.

        Returns:
        BlackjackResult: The result of the game.
        """
        player_total = self.calculate_hand(self.player_hand)
        dealer_total = self.calculate_hand(self.dealer_hand)
        if player_total > 21:
            return BlackjackResult.PLAYER_BUSTS
        if player_total == 21 and not dealer_total == 21:
            return BlackjackResult.PLAYER_BLACKJACK
        if dealer_total > 21:
            return BlackjackResult.DEALER_BUSTS
        if player_total == dealer_total:
            return BlackjackResult.TIE
        if player_total > dealer_total:
            return BlackjackResult.PLAYER_WINS
        return BlackjackResult.DEALER_WINS
