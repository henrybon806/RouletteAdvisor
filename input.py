import random
import numpy as np
import json

# Parameters
max_bet = 500  # Maximum allowed bet
learning_rate = 0.1  # Learning rate (alpha)
discount_factor = 0.95  # Future reward discount (gamma)
exploration_rate = 1.0  # Initial exploration rate
min_exploration_rate = 0.01  # Minimum exploration rate
exploration_decay = 0.99  # Decay rate for exploration
target_bankroll = 105  # Stop playing once bankroll reaches this amount

# Bet multipliers
bet_multipliers = [1, 1.5, 2, 2.25, 3]

# Q-learning table for strategy
Q_table = np.zeros((500, len(bet_multipliers)))

def save_data(bankroll, history):
    """Save game history to JSON"""
    data = {"bankroll": bankroll, "history": history}
    with open("betting_data.json", "w") as f:
        json.dump(data, f)

def load_data():
    """Load game history from JSON"""
    try:
        with open("betting_data.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"bankroll": 100, "history": []}

def simulate_best_bet(bankroll, trials=1000):
    """Run simulations to determine best betting strategy based on current bankroll"""
    outcomes = np.zeros(len(bet_multipliers))
    for _ in range(trials):
        for i, multiplier in enumerate(bet_multipliers):
            bet_amount = min(max_bet, bankroll * multiplier)
            spin = random.randint(1, 38)
            is_red = 1 <= spin <= 18
            if is_red:
                outcomes[i] += bet_amount
            else:
                outcomes[i] -= bet_amount
    best_bet = np.argmax(outcomes)
    return best_bet, bet_multipliers[best_bet]

def play_game():
    """Play a game with user input and provide optimal betting strategy."""
    data = load_data()
    bankroll = data["bankroll"]
    history = data["history"]
    
    print(f"Starting bankroll: ${bankroll}")
    
    while bankroll > 0 and bankroll < target_bankroll:
        best_bet, best_multiplier = simulate_best_bet(bankroll)
        bet_amount = min(max_bet, bankroll * best_multiplier)
        
        print(f"Suggested Bet: ${bet_amount:.2f} (Multiplier: {best_multiplier}x)")
        result = input("Did you win or lose? (w/l): ").strip().lower()
        
        if result == "w":
            bankroll += bet_amount
        else:
            bankroll -= bet_amount
        
        history.append({"bet": bet_amount, "result": result, "new_bankroll": bankroll})
        save_data(bankroll, history)
        
        if bankroll >= target_bankroll:
            print("Target bankroll reached! Stopping.")
            break
        elif bankroll <= 0:
            print("Bankrupt! Game over.")
            break
    
if __name__ == "__main__":
    play_game()
