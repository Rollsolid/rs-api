from fastapi import FastAPI
import uvicorn
app = FastAPI()

from eval_poker import simulate_win_percent



@app.get("/implied_odds/")
async def calculate_implied_odds(chance_percent: int = 1, current_pot: float = 1.0, amount_to_call: float = 1.0):
    implied_odds_dollars = ((1 / (chance_percent/100.0)) * amount_to_call) - (current_pot + amount_to_call) 
    return {"implied_odds_dollars": implied_odds_dollars}

@app.get("/pot_odds/")
async def calculate_pot_odds(current_pot: float = 1.0, bet: float = 1.0):
    pot_odds = (current_pot + bet ) /bet
    return {"pot_odds": pot_odds}



@app.get("/get_win_rate/")
async def get_win_rate(my_board_representation: str = "", my_hand: str = "", num_sims: int = 100, n_other_players: int = 5):
    win_rate = simulate_win_percent(my_board_representation.split(','), my_hand.split(','), num_sims, n_other_players=5,print_sim=False, print_ravg=True, decimal_places=2)
    return {"win_rate": win_rate}



if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000)