from collections import Counter

# Card ranks and suits
ranks = "23456789TJQKA"
suits = "shdc"


def get_rank(card):
    return card[0]


def get_suit(card):
    return card[1]

def get_hand_rank(hand):
    rank_values = {rank.lower(): i for i, rank in enumerate(ranks)}
    ranks_count = [get_rank(card).lower() for card in hand]
    suits_count = [get_suit(card) for card in hand]
    rank_counts = Counter(ranks_count)
    suit_counts = Counter(suits_count)

    straight = False
    flush = False

    # Check for straight
    sorted_ranks = sorted(ranks_count, key=lambda x: rank_values[x], reverse=True)
    highest_rank = rank_values[sorted_ranks[0]]
    lowest_rank = rank_values[sorted_ranks[-1]]
    if len(rank_counts) == 5 and (highest_rank - lowest_rank == 4):
        straight = True

    # Check for flush
    if len(suit_counts) == 1:
        flush = True

    # Check for straight flush
    if straight and flush:
        return 9, highest_rank

    # Check for four of a kind
    if len(rank_counts) == 2 and 4 in rank_counts.values():
        for rank, count in rank_counts.items():
            if count == 4:
                return 8, rank_values[rank]

    # Check for full house
    if len(rank_counts) == 2 and 3 in rank_counts.values():
        for rank, count in rank_counts.items():
            if count == 3:
                return 7, rank_values[rank]

    # Check for flush
    if flush:
        return 6, highest_rank

    # Check for straight
    if straight:
        return 5, highest_rank

    # Check for three of a kind
    if 3 in rank_counts.values():
        for rank, count in rank_counts.items():
            if count == 3:
                return 4, rank_values[rank]

    # Check for two pair
    if len(rank_counts) == 3 and 2 in rank_counts.values():
        pairs = []
        for rank, count in rank_counts.items():
            if count == 2:
                pairs.append(rank_values[rank])
        return 3, max(pairs)

    # Check for one pair
    if len(rank_counts) == 4 and 2 in rank_counts.values():
        for rank, count in rank_counts.items():
            if count == 2:
                return 2, rank_values[rank]

    # High card
    return 1, highest_rank


def compare_hands(player_hand, other_hands, flopped_cards):
    best_rank = get_hand_rank(player_hand + flopped_cards)
    winners = [player_hand]

    for hand in other_hands:
        rank = get_hand_rank(hand + flopped_cards)
        if rank > best_rank:
            best_rank = rank
            winners = [hand]
        elif rank == best_rank:
            winners.append(hand)

    return winners, best_rank


def eval_hands_QUICK(player_hand, other_hands, flopped_cards):
    best_rank = get_hand_rank(player_hand + flopped_cards)
    winners = [player_hand]
    draw_possible = False
    for hand in other_hands:
        rank = get_hand_rank(hand + flopped_cards)
        if rank > best_rank:
            return -1
            best_rank = rank
            winners = [hand]
        elif rank == best_rank:
            draw_possible = True

    if draw_possible == True:
        return 0
    return 1


def pick_best_hand(winners):
    best_hand = winners[0]
    best_rank = get_hand_rank(best_hand)

    for hand in winners[1:]:
        rank = get_hand_rank(hand)
        if rank > best_rank:
            best_hand = hand
            best_rank = rank

    return best_hand


# Example usage:
player_hand = ["Kc", "Jc"]
other_hands = [["Ah", "Qh"], ["As", "Kd"], ["8s", "8h"]]


player_hand = ["kc", "Jc"]
other_hands = [["Ah", "Qh"], ["Kc", "Js"], ["8s", "8h"]]


flopped_cards = ["Ts", "Js", "Qs", "Ks", "9s"]

# winners, best_rank = compare_hands(player_hand, other_hands, flopped_cards)
# print("Winning hand(s):")
# for hand in winners:
#     print(hand)

# best_hand = pick_best_hand(winners)
# print("Best hand:", best_hand)


# eval_hands_QUICK(player_hand, other_hands, flopped_cards)

import random

# USER INPUTS


def subtract(all_cards, known_flops):
    filtered = []
    for card in enumerate(all_cards):
        isFlop = False
        for x in known_flops:
            if card == x:
                isFlop = True
                break
        if not isFlop:
            filtered.append(card)

    return filtered


def sample_flop_and_player_hands(all_cards=None, n_players=5, n_flops=0, flops=None):
    hands = []
    # if flops:
    #     flop = flops
    #     all_cards = subtract(all_cards, flop)
    #     print(all_cards)
    for _ in range(n_players):
        hand = [all_cards.pop(random.randint(0, len(all_cards) - 1)) for _ in range(2)]
        hands.append(hand)
    if flops:
        flop = flops
    else:
        flop = [
            all_cards.pop(random.randint(0, len(all_cards) - 1)) for _ in range(n_flops)
        ]
    return hands, flop




def  get_cards(n_cards, all_cards):
    cards = [
        all_cards.pop(random.randint(0, len(all_cards) - 1)) for _ in range(n_cards)
    ]
    return cards


# def subtract(all_cards, known_flops):
#     filtered = []
#     for card in enumerate(all_cards):
#         isFlop = False
#         for x in known_flops:
#             if card == x:
#                 isFlop = True
#                 break
#         if not isFlop:
#             filtered.append(card)

#     return filtered


def get_deck(my_hand=None):
    full_deck = []
    for suit in ["s", "c", "h", "d"]:
        for num in ["2", "3", "4", "5", "6", "7", "8", "9", "t", "j", "q", "k", "a"]:
            if my_hand:
                if num + suit not in my_hand:
                    full_deck.append(num + suit)
            else:
                full_deck.append(num + suit)
    random.shuffle(full_deck)
    return full_deck


from tqdm import tqdm


def generate_game(n_other_players, player_hand, flops):
    
    all_cards = get_deck(my_hand)
    if flops:
        remaining_flops = 5 - len(flops)
        if remaining_flops > 0:
            extra_flops = get_cards(remaining_flops, all_cards)
            flops.extend(extra_flops)
    else:
        flops = get_cards(5, all_cards)
        
    hands = [get_cards(2, all_cards) for _ in range(n_other_players)]
    
    # hands, flops = sample_flop_and_player_hands(
    #     all_cards, n_other_players, n_flops)
    # print(player_hand, hands, flops)
    res = eval_hands_QUICK(player_hand, hands, flops)
    return my_hand, res
    return {
        "player_hand": player_hand,
        "other_hands": hands,
        "flops": flops,
        "results": res,
    }


def get_odds(hand, deck_hash_perf):
    player_hand = tuple(hand)
    total_sims = deck_hash_perf["total_games"]
    try:
        wins = deck_hash_perf[player_hand]["wins"]
        draws = deck_hash_perf[player_hand]["draws"]
        losses = deck_hash_perf[player_hand]["losses"]
    except KeyError:
        new_hand = tuple([player_hand[1], player_hand[0]])
        wins = deck_hash_perf[new_hand]["wins"]
        draws = deck_hash_perf[new_hand]["draws"]
        losses = deck_hash_perf[new_hand]["losses"]

    print(f"total_sims : {total_sims}")
    total_games = wins + losses + draws
    print(f"total_games : {total_games}")

    win_rate = wins / total_games
    draw_rate = draws / total_games
    print(f"win_rate: {win_rate}")
    print(f"draw_rate: {draw_rate}")
    return wins, draws, total_games


import pickle

LOAD = False
if not LOAD:
    all_cards = get_deck()

    deck_hash_perf = {"total_games": 0}
    i = 0
    set_so_far = []
    for card1 in all_cards:
        copy = all_cards.copy()
        for card2 in copy:
            if card1 != card2:
                hand = set([card1, card2])
                if hand not in set_so_far:
                    set_so_far.append(hand)

                    hand = tuple(hand)
                    if hand not in deck_hash_perf.keys():
                        deck_hash_perf[hand] = {"wins": 0, "draws": 0, "losses": 0}
    del set_so_far
if LOAD:
    with open("deck_hash_perf.pickle", "rb") as handle:
        deck_hash_perf = pickle.load(handle)





from pokereval.card import Card
from pokereval.hand_evaluator import HandEvaluator

hole = [Card(2, 1), Card(2, 2)]
board = []
score = HandEvaluator.evaluate_hand(hole, board)

Rank is 2-14 representing 2-A, while suit is 1-4 representing spades, hearts, diamonds, clubs.

The Card constructor accepts two arguments, rank, and suit.

aceOfSpades = Card(14, 1)
twoOfDiamonds = Card(2, 3)


def eval_hands():
    





def get_win_rate(my_hand, flops=None, n_other_players=5):
    win_rates = []
    iterations = 30000
    for x in range(iterations):
        deck_hash_perf["total_games"] += 1
        # if my_hand arg is supplied it will focus on generating those hands
        player_hand, res = generate_game(
            n_other_players=n_other_players, player_hand=my_hand, flops=flops
        )
        player_hand = tuple(player_hand)
        try:
            if res == 1:
                deck_hash_perf[player_hand]["wins"] += 1
            elif res == 0:
                deck_hash_perf[player_hand]["draws"] += 1
            elif res == -1:
                deck_hash_perf[player_hand]["losses"] += 1
            # print(deck_hash_perf[player_hand]["wins"],deck_hash_perf[player_hand]["draws"],deck_hash_perf[player_hand]["losses"],end="\r")
            total_games = (
                deck_hash_perf[player_hand]["wins"]
                + deck_hash_perf[player_hand]["losses"]
                # + deck_hash_perf[player_hand]["draws"]
            )
            win_rate = deck_hash_perf[player_hand]["wins"] / total_games
            win_rates.append(win_rate)

            print(f"win_rate: {win_rate}", end="\r")
        except KeyError:
            player_hand = tuple([player_hand[1], player_hand[0]])
            if res == 1:
                deck_hash_perf[player_hand]["wins"] += 1
            elif res == 0:
                deck_hash_perf[player_hand]["draws"] += 1
            elif res == -1:
                deck_hash_perf[player_hand]["losses"] += 1
            # print(deck_hash_perf[player_hand]["wins"],deck_hash_perf[player_hand]["draws"],deck_hash_perf[player_hand]["losses"],end="\r")
            total_games = (
                deck_hash_perf[player_hand]["wins"]
                + deck_hash_perf[player_hand]["losses"]
                # + deck_hash_perf[player_hand]["draws"]
            )
            win_rate = deck_hash_perf[player_hand]["wins"] / total_games
            win_rates.append(win_rate)
            print(f"win_rate: {win_rate}", end="\r")
    return win_rates


# with open("deck_hash_perf.pickle", "wb") as handle:
#     pickle.dump(deck_hash_perf, handle, protocol=pickle.HIGHEST_PROTOCOL)
#  if x % 24000 == 0:
#         with open("deck_hash_perf.pickle", "wb") as handle:
#             pickle.dump(deck_hash_perf, handle, protocol=pickle.HIGHEST_PROTOCOL)


my_hand = ["kh", "kc"]
flops = []

win_rates = get_win_rate(my_hand, flops)
# get_odds(my_hand, deck_hash_perf)


import matplotlib.pyplot as plt
import numpy as np

win_rates = [x * 100 for x in win_rates]
x = np.arange(len(win_rates))
plt.plot(x, win_rates)
plt.ylim([np.mean(win_rates) - 10, np.mean(win_rates) + 10])
plt.xlabel("Number of Simulations")
plt.ylabel("Win Rate %")
plt.show()
