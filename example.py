from eval_poker import simulate_win_percent
num_sims = 1000



my_board_representation = []
my_hand = ["3h", "4s"] 

simulate_win_percent(my_board_representation, my_hand, num_sims, n_other_players=3,print_sim=False, print_ravg=True, decimal_places=2)

# print(f"{avg}%")