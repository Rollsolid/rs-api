import random
from tqdm import tqdm
# from treys import Card

from typing import Sequence

class Card:
    """
    Static class that handles cards. We represent cards as 32-bit integers, so 
    there is no object instantiation - they are just ints. Most of the bits are 
    used, and have a specific meaning. See below: 

                                    Card:

                          bitrank     suit rank   prime
                    +--------+--------+--------+--------+
                    |xxxbbbbb|bbbbbbbb|cdhsrrrr|xxpppppp|
                    +--------+--------+--------+--------+

        1) p = prime number of rank (deuce=2,trey=3,four=5,...,ace=41)
        2) r = rank of card (deuce=0,trey=1,four=2,five=3,...,ace=12)
        3) cdhs = suit of card (bit turned on based on suit of card)
        4) b = bit turned on depending on rank of card
        5) x = unused

    This representation will allow us to do very important things like:
    - Make a unique prime prodcut for each hand
    - Detect flushes
    - Detect straights

    and is also quite performant.
    """

    # the basics
    STR_RANKS: str = '23456789TJQKA'
    STR_SUITS: str = 'shdc'
    INT_RANKS: range = range(13)
    
    from typing import List
# tricks: List[str] =`` []
    PRIMES: List[int] = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41]

    # conversion from string => int
    CHAR_RANK_TO_INT_RANK: dict[str, int] = dict(zip(list(STR_RANKS), INT_RANKS))
    CHAR_SUIT_TO_INT_SUIT: dict[str, int] = {
        's': 1,  # spades
        'h': 2,  # hearts
        'd': 4,  # diamonds
        'c': 8,  # clubs
        '\u2660': 1, # spades (unicode)
        '\u2764': 2, # hearts (unicode)
        '\u2666': 4, # diamonds (unicode)
        '\u2663': 8, # clubs (unicode)
    }
    INT_SUIT_TO_CHAR_SUIT: str = 'xshxdxxxc'

    # for pretty printing
    PRETTY_SUITS: dict[int, str] = {
        1: chr(9824),   # spades
        2: chr(9829),   # hearts
        4: chr(9830),   # diamonds
        8: chr(9827)    # clubs
    }

    SUIT_COLORS: dict[int, str] = {
        2: "red",
        4: "blue",
        8: "green"
    }

    @staticmethod
    def new(string: str) -> int:
        """
        Converts Card string to binary integer representation of card, inspired by:
        
        http://www.suffecool.net/poker/evaluator.html
        """

        rank_char = string[0]
        suit_char = string[1]
        rank_int = Card.CHAR_RANK_TO_INT_RANK[rank_char]
        suit_int = Card.CHAR_SUIT_TO_INT_SUIT[suit_char]
        rank_prime = Card.PRIMES[rank_int]

        bitrank = 1 << rank_int << 16
        suit = suit_int << 12
        rank = rank_int << 8

        return bitrank | suit | rank | rank_prime

    @staticmethod
    def int_to_str(card_int: int) -> str:
        rank_int = Card.get_rank_int(card_int)
        suit_int = Card.get_suit_int(card_int)
        return Card.STR_RANKS[rank_int] + Card.INT_SUIT_TO_CHAR_SUIT[suit_int]

    @staticmethod
    def get_rank_int(card_int: int) -> int:
        return (card_int >> 8) & 0xF

    @staticmethod
    def get_suit_int(card_int: int) -> int:
        return (card_int >> 12) & 0xF

    @staticmethod
    def get_bitrank_int(card_int: int) -> int:
        return (card_int >> 16) & 0x1FFF

    @staticmethod
    def get_prime(card_int: int) -> int:
        return card_int & 0x3F

    @staticmethod
    def hand_to_binary(card_strs: Sequence[str]) -> list[int]:
        """
        Expects a list of cards as strings and returns a list
        of integers of same length corresponding to those strings. 
        """
        bhand = []
        for c in card_strs:
            bhand.append(Card.new(c))
        return bhand

    @staticmethod
    def prime_product_from_hand(card_ints: Sequence[int]) -> int:
        """
        Expects a list of cards in integer form. 
        """

        product = 1
        for c in card_ints:
            product *= (c & 0xFF)

        return product

    @staticmethod
    def prime_product_from_rankbits(rankbits: int) -> int:
        """
        Returns the prime product using the bitrank (b)
        bits of the hand. Each 1 in the sequence is converted
        to the correct prime and multiplied in.

        Params:
            rankbits = a single 32-bit (only 13-bits set) integer representing 
                    the ranks of 5 _different_ ranked cards 
                    (5 of 13 bits are set)

        Primarily used for evaulating flushes and straights, 
        two occasions where we know the ranks are *ALL* different.

        Assumes that the input is in form (set bits):

                              rankbits     
                        +--------+--------+
                        |xxxbbbbb|bbbbbbbb|
                        +--------+--------+

        """
        product = 1
        for i in Card.INT_RANKS:
            # if the ith bit is set
            if rankbits & (1 << i):
                product *= Card.PRIMES[i]

        return product

    @staticmethod
    def int_to_binary(card_int: int) -> str:
        """
        For debugging purposes. Displays the binary number as a 
        human readable string in groups of four digits. 
        """
        bstr = bin(card_int)[2:][::-1]  # chop off the 0b and THEN reverse string
        output = list("".join(["0000" + "\t"] * 7) + "0000")

        for i in range(len(bstr)):
            output[i + int(i/4)] = bstr[i]

        # output the string to console
        output.reverse()
        return "".join(output)

    @staticmethod
    def int_to_pretty_str(card_int: int) -> str:
        """
        Prints a single card 
        """
        
        color = False
        try:
            from termcolor import colored
            # for mac, linux: http://pypi.python.org/pypi/termcolor
            # can use for windows: http://pypi.python.org/pypi/colorama
            color = True
        except ImportError: 
            pass

        # suit and rank
        suit_int = Card.get_suit_int(card_int)
        rank_int = Card.get_rank_int(card_int)

        # color
        s = Card.PRETTY_SUITS[suit_int]
        if color and suit_int in Card.SUIT_COLORS:
            s = colored(s, Card.SUIT_COLORS[suit_int])

        r = Card.STR_RANKS[rank_int]

        return "[{}{}]".format(r,s)

    @staticmethod
    def print_pretty_card(card_int: int) -> None:
        """
        Expects a single integer as input
        """
        print(Card.int_to_pretty_str(card_int))

    @staticmethod
    def ints_to_pretty_str(card_ints: Sequence[int]) -> str:
        """
        Expects a list of cards in integer form.
        """
        output = " "
        for i in range(len(card_ints)):
            c = card_ints[i]
            if i != len(card_ints) - 1:
                output += str(Card.int_to_pretty_str(c)) + ","
            else:
                output += str(Card.int_to_pretty_str(c)) + " "
    
        return output

    @staticmethod
    def print_pretty_cards(card_ints: Sequence[int]) -> None:
        """
        Expects a list of cards in integer form.
        """
        print(Card.ints_to_pretty_str(card_ints))
        
        
        


def _to_treys_representation(card_list):
    trey_cards = []
    for x in card_list:
        st = str(x[0]).upper() + x[1]
        trey_cards.append(Card.new(st))
    return trey_cards
    

    # board = [
    # Card.new('Ah'),
    # Card.new('Kd'),
    # Card.new('Jc')


def get_deck(exclude_me=None):
    full_deck = []
    for suit in ["s", "c", "h", "d"]:
        for num in ["2", "3", "4", "5", "6", "7", "8", "9", "t", "j", "q", "k", "a"]:
            if exclude_me:
                if num + suit not in exclude_me:
                    full_deck.append(num + suit)
            else:
                full_deck.append(num + suit)
    random.shuffle(full_deck)
    return full_deck



def get_random_hands(n_other_players, remaining_cards, needed_flop_cards=0):
    random.shuffle(remaining_cards)
    all_cards_copy = remaining_cards.copy()
    other_hands = []
    for _ in range(n_other_players):
        cards = [
        all_cards_copy.pop(random.randint(0, len(all_cards_copy) - 1)) for _ in range(2)
        ]
        other_hands.append(cards)
        
    if needed_flop_cards > 0:
        board_ext = [
        all_cards_copy.pop(random.randint(0, len(all_cards_copy) - 1)) for _ in range(needed_flop_cards)
        ]
        return other_hands, board_ext
    return other_hands

def generate_game_start_state(my_board_representation, my_hand):
    
    exclude_me = my_hand.copy()
    
    if my_board_representation is not None:
        exclude_me.extend(my_board_representation)
    
    remaining_cards = get_deck(exclude_me)
    remaining_cards=sorted(remaining_cards)
    
    hand = _to_treys_representation(my_hand)
    if my_board_representation:
        board = _to_treys_representation(my_board_representation)
    else:
        board=None
    remaining_cards = _to_treys_representation(remaining_cards)
    
    
    result = 0
    return remaining_cards, hand, board





def get_winner(hand, other_hands, board, evaluator, fast=True):
    player_score = evaluator.evaluate(board, hand)
    player_rank = evaluator.get_rank_class(player_score)
    # other_hands = [_to_treys_representation(x) for x in other_hands]
    op_hand_scores = []
    op_hand_ranks = []
    if fast:
        for x in other_hands:
            score = evaluator.evaluate(board, x)
            rank_class = evaluator.get_rank_class(score)
            op_hand_ranks.append(rank_class)
        if min(op_hand_ranks) < player_rank:
            return -1
        elif min(op_hand_ranks) == player_rank:
            return 0
        else: 
            return 1
    
    for x in other_hands:
        score = evaluator.evaluate(board, x)
        rank_class = evaluator.get_rank_class(score)
        op_hand_scores.append(score)
        op_hand_ranks.append(rank_class)
        
    
    for i in range(len(op_hand_scores)):
        Card.print_pretty_cards(other_hands[i])
        print(evaluator.class_to_string(op_hand_ranks[i]), op_hand_ranks[i])
    
    Card.print_pretty_cards(hand)
    print(evaluator.class_to_string(player_rank))
    print(player_rank)
    print(player_score)
    
    
    
    

def simulate_win_percent(my_board_representation, my_hand, num_sims, n_other_players=5, print_sim=False, print_ravg=False, decimal_places=None):
    remaining_cards, hand, board = generate_game_start_state(my_board_representation, my_hand)


    wins = 0
    draws = 0
    losses = 0
    # if not board or len(board) < 5:
    #     print(f"Need to generate  {5-len(board)} board cards each sim")
    
    win_rates = []

    og_board = board 
    pbar = tqdm(range(num_sims))
    for i in pbar:
        if og_board:
            temp_board = og_board.copy()
        else:
            temp_board = None
                
        # For each sim
        if temp_board:
            if len(temp_board) == 5:
                other_hands = get_random_hands(5, remaining_cards)
            else:
                other_hands, board_ext = get_random_hands(n_other_players, remaining_cards, needed_flop_cards=5-len(temp_board))
                # print(board_ext)
                # board_ext = _to_treys_representation(board_ext)
                temp_board.extend(board_ext)
        else:
            other_hands, board_ext = get_random_hands(n_other_players, remaining_cards, needed_flop_cards=5)
            temp_board = board_ext
                
            # board_ext = _to_treys_representation(board_ext)
            # if board:
                
            # else:
            #     board = board_ext
            assert len(temp_board) == 5
        from treys import Evaluator
        evaluator = Evaluator()
        if print_sim:
            print("\n")
            for x in other_hands:
                Card.print_pretty_cards(x)
            Card.print_pretty_cards(temp_board)
        result = get_winner(hand, other_hands, temp_board, evaluator)

        
        if result == 1:
            wins +=1 
            if print_sim:
                print("Win\n")
        elif result == 0:
            draws +=1
            if print_sim:
                print("Draw\n")
            
        elif result == -1:
            losses +=1
            if print_sim:
                print("Loss\n")
        
        total_games = wins + draws + losses
        avg = wins/total_games
        win_rates.append(avg)
        if print_ravg and i%10 == 0:
            pbar.set_description(f"Running Average: {avg*100:{5}.{5}}%")
        board=None
    total_games = wins + draws + losses
    avg = wins/total_games

    if decimal_places > 0:
        avg *= 100
        avg = round(avg, decimal_places)
    return avg

    
    # import matplotlib.pyplot as plt
    # import numpy as np

    # win_rates = [x * 100 for x in win_rates]
    # x = np.arange(len(win_rates))

    # plt.title("Win Rate Over Time")
    # plt.plot(x, win_rates)
    # plt.ylim([np.mean(win_rates) - 10, np.mean(win_rates) + 10])
    # plt.xlabel("Number of Simulations")
    # plt.ylabel("Win Rate %")
    # plt.show()







    
