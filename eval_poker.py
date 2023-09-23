import random
from tqdm import tqdm
from card import Card
import itertools
from typing import Sequence, List
from lookup import LookupTable


class Evaluator:
    """
    Evaluates hand strengths using a variant of Cactus Kev's algorithm:
    http://suffe.cool/poker/evaluator.html

    I make considerable optimizations in terms of speed and memory usage, 
    in fact the lookup table generation can be done in under a second and 
    consequent evaluations are very fast. Won't beat C, but very fast as 
    all calculations are done with bit arithmetic and table lookups. 
    """

    HAND_LENGTH = 2
    BOARD_LENGTH = 5

    def __init__(self) -> None:

        self.table = LookupTable()
        
        self.hand_size_map = {
            5: self._five,
            6: self._six,
            7: self._seven
        }

    def evaluate(self, hand: List[int], board: List[int]) -> int:
        """
        This is the function that the user calls to get a hand rank. 

        No input validation because that's cycles!
        """
        all_cards = hand + board
        return self.hand_size_map[len(all_cards)](all_cards)

    def _five(self, cards: Sequence[int]) -> int:
        """
        Performs an evalution given cards in integer form, mapping them to
        a rank in the range [1, 7462], with lower ranks being more powerful.

        Variant of Cactus Kev's 5 card evaluator, though I saved a lot of memory
        space using a hash table and condensing some of the calculations. 
        """
        # if flush
        if cards[0] & cards[1] & cards[2] & cards[3] & cards[4] & 0xF000:
            handOR = (cards[0] | cards[1] | cards[2] | cards[3] | cards[4]) >> 16
            prime = Card.prime_product_from_rankbits(handOR)
            return self.table.flush_lookup[prime]

        # otherwise
        else:
            prime = Card.prime_product_from_hand(cards)
            return self.table.unsuited_lookup[prime]

    def _six(self, cards: Sequence[int]) -> int:
        """
        Performs five_card_eval() on all (6 choose 5) = 6 subsets
        of 5 cards in the set of 6 to determine the best ranking, 
        and returns this ranking.
        """
        minimum = LookupTable.MAX_HIGH_CARD

        for combo in itertools.combinations(cards, 5):

            score = self._five(combo)
            if score < minimum:
                minimum = score

        return minimum

    def _seven(self, cards: Sequence[int]) -> int:
        """
        Performs five_card_eval() on all (7 choose 5) = 21 subsets
        of 5 cards in the set of 7 to determine the best ranking, 
        and returns this ranking.
        """
        minimum = LookupTable.MAX_HIGH_CARD

        for combo in itertools.combinations(cards, 5):
            
            score = self._five(combo)
            if score < minimum:
                minimum = score

        return minimum

    def get_rank_class(self, hr: int) -> int:
        """
        Returns the class of hand given the hand hand_rank
        returned from evaluate. 
        """
        if hr >= 0 and hr <= LookupTable.MAX_ROYAL_FLUSH:
            return LookupTable.MAX_TO_RANK_CLASS[LookupTable.MAX_ROYAL_FLUSH]
        elif hr <= LookupTable.MAX_STRAIGHT_FLUSH:
            return LookupTable.MAX_TO_RANK_CLASS[LookupTable.MAX_STRAIGHT_FLUSH]
        elif hr <= LookupTable.MAX_FOUR_OF_A_KIND:
            return LookupTable.MAX_TO_RANK_CLASS[LookupTable.MAX_FOUR_OF_A_KIND]
        elif hr <= LookupTable.MAX_FULL_HOUSE:
            return LookupTable.MAX_TO_RANK_CLASS[LookupTable.MAX_FULL_HOUSE]
        elif hr <= LookupTable.MAX_FLUSH:
            return LookupTable.MAX_TO_RANK_CLASS[LookupTable.MAX_FLUSH]
        elif hr <= LookupTable.MAX_STRAIGHT:
            return LookupTable.MAX_TO_RANK_CLASS[LookupTable.MAX_STRAIGHT]
        elif hr <= LookupTable.MAX_THREE_OF_A_KIND:
            return LookupTable.MAX_TO_RANK_CLASS[LookupTable.MAX_THREE_OF_A_KIND]
        elif hr <= LookupTable.MAX_TWO_PAIR:
            return LookupTable.MAX_TO_RANK_CLASS[LookupTable.MAX_TWO_PAIR]
        elif hr <= LookupTable.MAX_PAIR:
            return LookupTable.MAX_TO_RANK_CLASS[LookupTable.MAX_PAIR]
        elif hr <= LookupTable.MAX_HIGH_CARD:
            return LookupTable.MAX_TO_RANK_CLASS[LookupTable.MAX_HIGH_CARD]
        else:
            raise Exception("Inavlid hand rank, cannot return rank class")

    def class_to_string(self, class_int: int) -> str:
        """
        Converts the integer class hand score into a human-readable string.
        """
        return LookupTable.RANK_CLASS_TO_STRING[class_int]

    def get_five_card_rank_percentage(self, hand_rank: int) -> float:
        """
        Scales the hand rank score to the [0.0, 1.0] range.
        """
        return float(hand_rank) / float(LookupTable.MAX_HIGH_CARD)

    def hand_summary(self, board: List[int], hands: List[List[int]]) -> None:
        """
        Gives a sumamry of the hand with ranks as time proceeds. 

        Requires that the board is in chronological order for the 
        analysis to make sense.
        """

        assert len(board) == self.BOARD_LENGTH, "Invalid board length"
        for hand in hands:
            assert len(hand) == self.HAND_LENGTH, "Invalid hand length"

        line_length = 10
        stages = ["FLOP", "TURN", "RIVER"]

        for i in range(len(stages)):
            line = "=" * line_length
            print("{} {} {}".format(line,stages[i],line))
            
            best_rank = 7463  # rank one worse than worst hand
            winners = []
            for player, hand in enumerate(hands):

                # evaluate current board position
                rank = self.evaluate(hand, board[:(i + 3)])
                rank_class = self.get_rank_class(rank)
                class_string = self.class_to_string(rank_class)
                percentage = 1.0 - self.get_five_card_rank_percentage(rank)  # higher better here
                print("Player {} hand = {}, percentage rank among all hands = {}".format(player + 1, class_string, percentage))

                # detect winner
                if rank == best_rank:
                    winners.append(player)
                    best_rank = rank
                elif rank < best_rank:
                    winners = [player]
                    best_rank = rank

            # if we're not on the river
            if i != stages.index("RIVER"):
                if len(winners) == 1:
                    print("Player {} hand is currently winning.\n".format(winners[0] + 1))
                else:
                    print("Players {} are tied for the lead.\n".format([x + 1 for x in winners]))

            # otherwise on all other streets
            else:
                hand_result = self.class_to_string(self.get_rank_class(self.evaluate(hands[winners[0]], board)))
                print()
                print("{} HAND OVER {}".format(line, line))
                if len(winners) == 1:
                    print("Player {} is the winner with a {}\n".format(winners[0] + 1, hand_result))
                else:
                    print("Players {} tied for the win with a {}\n".format([x + 1 for x in winners],hand_result))


class PLOEvaluator(Evaluator):

    HAND_LENGTH = 4

    def evaluate(self, hand: List[int], board: List[int]) -> int:
        minimum = LookupTable.MAX_HIGH_CARD

        for hand_combo in itertools.combinations(hand, 2):
            for board_combo in itertools.combinations(board, 3):
                score = Evaluator._five(self, list(board_combo) + list(hand_combo))
                if score < minimum:
                    minimum = score

        return minimum


def _to_treys_representation(card_list):
    trey_cards = []
    print(f"Card List: {card_list}")
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
        # from evaluator import Evaluator
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







    
