import json
import random
import matplotlib.pyplot as plt

def load_betting_strategy():
    try:
        with open("betting_strategy.json", "r") as f:
            data = json.load(f)
        if "bet_multipliers" not in data:
            raise ValueError("Invalid betting strategy file format.")
        return data["bet_multipliers"]
    except (FileNotFoundError, ValueError) as e:
        print(f"Error loading betting strategy: {e}")
        exit()

bet_multipliers = load_betting_strategy()

def get_next_bet(previous_bet, won):
    if won:
        return finalInit  # Reset to initial bet after a win
    else:
        action = min(len(bet_multipliers) - 1, int(previous_bet / 20))  # Scale action selection better
        return max(finalInit, previous_bet * bet_multipliers[action])  # Prevent bets from going below minimum

def run_simulation(starting_balance):
    """Runs a simulated betting session for at least 50 rounds, stopping on a win or at 100 rounds."""
    total_balance = starting_balance
    rounds = 0
    current_bet = finalInit
    total_winnings = 0

    while rounds < 100:  # Maximum 100 rounds
        if current_bet > total_balance:  # Prevent betting more than available balance
            break

        won = random.choice([True, False])  # Simulating a 50% chance of winning
        rounds += 1

        if won:
            winnings = current_bet  # Won the bet, add bet amount to total balance
            total_balance += winnings
            total_winnings += winnings
            current_bet = get_next_bet(current_bet, True)  # Adjust bet for next round
            if rounds >= 50:
                if total_balance >= starting_balance:
                    return True  # Stop simulation on win
                return False  # Stop simulation on loss
        else:
            winnings = -current_bet  # Lost the bet, subtract from total balance
            total_balance = max(0, total_balance + winnings)  # Prevent negative balance
            total_winnings += winnings
            current_bet = get_next_bet(current_bet, False)  # Adjust bet for next round

        if total_balance <= 0:
            return False  # Stop if balance runs out

    return False  # Return True for win, False for loss

def simulate_with_graph():
    wins = 0
    losses = 0
    starting_balance = float(input("Enter your starting balance for simulation: "))
    
    for _ in range(1000):
        if run_simulation(starting_balance):
            wins += 1
        else:
            losses += 1
    
    # Plot results
    labels = ['Wins', 'Losses']
    values = [wins, losses]
    plt.bar(labels, values, color=['green', 'red'])
    plt.xlabel('Outcome')
    plt.ylabel('Count')
    plt.title('Simulation Results (1000 Runs)')
    plt.show()

print("Welcome to the Betting Advisor!")
try:
    initial_bet = float(input("Enter your initial bet amount: "))
    finalInit = initial_bet
    if initial_bet <= 0:
        raise ValueError("Bet amount must be greater than zero.")
except ValueError as e:
    print(f"Invalid input: {e}")
    exit()

while True:
    outcome = input("Did you win the last round? (yes/no/quit/simulate/graph): ").strip().lower()
    if outcome == "quit":
        print("Thanks for using the Betting Advisor!")
        break
    if outcome == "simulate":
        run_simulation(float(input("Enter your starting balance for simulation: ")))
        continue
    if outcome == "graph":
        simulate_with_graph()
        continue
    if outcome not in ["yes", "no"]:
        print("Invalid input. Please enter 'yes', 'no', 'simulate', or 'graph'.")
        continue
    
    next_bet = get_next_bet(initial_bet, outcome == "yes")
    print(f"Recommended next bet: ${next_bet:.2f}")
    
    initial_bet = next_bet  # Update bet for the next round
