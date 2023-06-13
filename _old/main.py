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


@app.get("/pot_odds/")
async def calculate_pot_odds(current_pot: float = 1.0, bet: float = 1.0):
    pot_odds = (current_pot + bet ) /bet
    return {"pot_odds": pot_odds}



