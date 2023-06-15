from treys import Card
import random

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
    
    
    
    
from tqdm import tqdm

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
    # return avg

    # return avg*100
    
    import matplotlib.pyplot as plt
    import numpy as np

    win_rates = [x * 100 for x in win_rates]
    x = np.arange(len(win_rates))

    plt.title("Win Rate Over Time")
    plt.plot(x, win_rates)
    plt.ylim([np.mean(win_rates) - 10, np.mean(win_rates) + 10])
    plt.xlabel("Number of Simulations")
    plt.ylabel("Win Rate %")
    plt.show()







    
