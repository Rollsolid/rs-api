from eval_poker import simulate_win_percent, _to_treys_representation

from fastapi import FastAPI


print(_to_treys_representation(hand))


my_board_representation =  ""
my_hand = "8h,ks"
num_sims: int = 100
n_other_players: int = 5
if my_board_representation == "":
    # return {"x":my_board_representation}
    my_board_representation = None
else:
    my_board_representation = my_board_representation.split(',')
my_hand = my_hand.split(',')
print(my_hand)

win_rate = simulate_win_percent(my_board_representation, my_hand, num_sims, n_other_players=5,print_sim=False, print_ravg=True, decimal_places=2)

print(win_rate)