from eval_poker import simulate_win_percent
from fastapi import FastAPI


app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/implied_odds/")
async def calculate_pot_odds(chance_percent: int = 1, current_pot: float = 1.0, amount_to_call: float = 1.0):
    implied_odds_dollars = ((1 / (chance_percent/100.0)) * amount_to_call) - (current_pot + amount_to_call) 
    return {"implied_odds_dollars": implied_odds_dollars}


# @app.get("/g_bucks/")
# async def calculate_pot_odds(chance_percent: int = 1, current_pot: float = 1.0, amount_to_call: float = 1.0):
#     implied_odds_dollars = ((1 / (chance_percent/100.0)) * amount_to_call) - (current_pot + amount_to_call) 
#     return {"implied_odds_dollars": implied_odds_dollars}


from fastapi import FastAPI
import uvicorn
from mangum import Mangum
app = FastAPI()
handler = Mangum(app)
from eval_poker import simulate_win_percent



@app.get("/implied_odds/")
async def calculate_implied_odds(chance_percent: int = 1, current_pot: float = 1.0, amount_to_call: float = 1.0):
    implied_odds_dollars = ((1 / (chance_percent/100.0)) * amount_to_call) - (current_pot + amount_to_call) 
    return {"implied_odds_dollars": implied_odds_dollars}

@app.get("/pot_odds/")
async def calculate_pot_odds(current_pot: float = 1.0, bet: float = 1.0):
    pot_odds = (current_pot + bet ) /bet
    return {"pot_odds": pot_odds}




num_sims = 1000


# my_board_representation = ["3c", "3d", "7s"]
# my_hand = ["3h", "4s"] 





@app.get("/get_win_rate/")
async def calculate_pot_odds(my_board_representation: str = "",  my_hand:str = "", num_sims: int = 1000):

    my_board_representation = [str(x) for x in my_board_representation.split(",")]
    my_hand = [str(x) for x in my_hand.split(",")]
    print(my_hand)
    win_percent = simulate_win_percent(my_board_representation, my_hand, num_sims, n_other_players=3,print_sim=False, print_ravg=True, decimal_places=2)
    return {"win_percent": win_percent}



@app.get("/get_win_rate/")
async def get_win_rate(my_board_representation: str = "", my_hand: str = "", num_sims: int = 100, n_other_players: int = 5):
    if my_board_representation == "":
        # return {"x":my_board_representation}
        my_board_representation = None
    else:
        my_board_representation = my_board_representation.split(',')
    my_hand = my_hand.split(',')
        
    
    win_rate = simulate_win_percent(my_board_representation, my_hand, num_sims, n_other_players=5,print_sim=False, print_ravg=True, decimal_places=2)
    
    return {"win_rate": win_rate}


