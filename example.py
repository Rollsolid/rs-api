from eval_poker import simulate_win_percent
num_sims = 100



my_board_representation = ["3c", "4d", "7s"]
my_hand = ["3h", "5s"]  #99.7 %

avg = simulate_win_percent(my_board_representation, my_hand, num_sims, n_other_players=3,print_sim=False, print_ravg=False, decimal_places=2)
print("\n",avg)
