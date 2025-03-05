import random
import numpy as np

# Parameters
max_bet = 1000  # Maximum allowed bet
num_simulations = 1000  # Total number of sessions
learning_rate = 0.01  # Learning rate (alpha)
discount_factor = 0.95  # Future reward discount (gamma)
exploration_rate = 1.0  # Initial exploration rate (epsilon)
min_exploration_rate = 0.01  # Minimum exploration rate
exploration_decay = 0.995  # Decay rate for exploration
target_bankroll = 105  # Stop playing once bankroll reaches this amount

# Initialize Q-table and bet multipliers dynamically
Q_table = np.zeros((500, 5))
bet_multipliers = np.random.uniform(1, 3, 5)  # Start with random multipliers

total_winnings = 0
total_losses = 0

for i in range(num_simulations):
    total = 100
    current = 0.05
    loss_in_session = 0
    
    while total > 0 and total < target_bankroll:
        bankroll_state = max(0, min(int(total), 499))

        if random.uniform(0, 1) < exploration_rate:
            action = random.randint(0, 4)
        else:
            action = np.argmax(Q_table[bankroll_state])

        current_multiplier = bet_multipliers[action]
        bet_amount = min(max_bet, current * current_multiplier)

        spin = random.randint(1, 38)
        is_red = 1 <= spin <= 18

        if is_red:
            reward = bet_amount
            total += bet_amount
            current = 0.1
        else:
            reward = -bet_amount
            total -= bet_amount
            loss_in_session += 1
            if bet_amount < max_bet:
                current = min(max_bet, current * current_multiplier)

        if total >= target_bankroll:
            reward += 10

        next_state = max(0, min(int(total), 499))
        best_next_action = np.max(Q_table[next_state])
        Q_table[bankroll_state, action] += learning_rate * (reward + discount_factor * best_next_action - Q_table[bankroll_state, action])

        # Update multipliers based on performance
        bet_multipliers[action] += learning_rate * reward / 100  # Adjust based on rewards
        bet_multipliers = np.clip(bet_multipliers, 1, 3)  # Keep multipliers within bounds
    
    total_winnings += total
    total_losses += loss_in_session
    exploration_rate = max(min_exploration_rate, exploration_rate * exploration_decay)

print(f"Average Winnings: ${total_winnings / num_simulations}")
print(f"Total Losses: {total_losses}")

print("\nOptimal bet multipliers for different bankroll states:")
for bankroll in range(0, 500, 50):
    best_action = np.argmax(Q_table[bankroll])
    print(f"Bankroll ${bankroll}: Best multiplier = {bet_multipliers[best_action]:.2f}")

def play_example_game():
    total = 100
    current = 0.1
    print("\nExample Game Using Optimal Strategy:")

    spin_num = 0
    while total > 0 and total < target_bankroll:
        bankroll_state = max(0, min(int(total), 499))
        action = np.argmax(Q_table[bankroll_state])
        current_multiplier = bet_multipliers[action]
        bet_amount = min(max_bet, current * current_multiplier)

        spin = random.randint(1, 38)
        is_red = 1 <= spin <= 18

        if is_red:
            total += bet_amount
            current = 0.1
            result = "Win"
        else:
            total -= bet_amount
            current = min(max_bet, current * current_multiplier)
            result = "Loss"

        spin_num += 1
        print(f"Spin {spin_num}: Bet ${bet_amount:.2f} (Multiplier: {current_multiplier:.2f}x) -> {result}, New Bankroll: ${total:.2f}")

        if total <= 0:
            print("Bankrupt! Game Over.")
            break
        elif total >= target_bankroll:
            print(f"Reached ${target_bankroll}! Stopping.")
            break

play_example_game()
