import random
import numpy as np
import json

# Parameters
max_bet = 80  # Maximum allowed bet
min_bet = 0.05  # Minimum bet
num_simulations = 100  # Total number of training sessions
learning_rate = 0.01  # Learning rate (alpha)
discount_factor = 0.95  # Future reward discount (gamma)
exploration_rate = 1.0  # Initial exploration rate (epsilon)
min_exploration_rate = 0.01  # Minimum exploration rate
exploration_decay = 0.995  # Decay rate for exploration
win_threshold = 0.9  # Success rate to stop training
target_bankroll = 105  # Stop playing once bankroll reaches this amount

# Initialize Q-table and bet multipliers dynamically
Q_table = np.zeros((500, 5))
bet_multipliers = np.random.uniform(1, 3, 5)  # Start with random multipliers

successful_runs = 0
while successful_runs / num_simulations < win_threshold:
    successful_runs = 0
    for _ in range(num_simulations):
        total = 100
        current = min_bet
        loss_in_session = 0
        
        while total > 0 and total < target_bankroll:
            bankroll_state = max(0, min(int(total), 499))
            
            if random.uniform(0, 1) < exploration_rate:
                action = random.randint(0, 4)
            else:
                action = np.argmax(Q_table[bankroll_state])
            
            current_multiplier = bet_multipliers[action]
            bet_amount = min(max_bet, max(min_bet, current * current_multiplier))
            
            spin = random.randint(1, 38)
            is_red = 1 <= spin <= 18
            
            if is_red:
                reward = bet_amount
                total += bet_amount
                current = min_bet
            else:
                reward = -bet_amount
                total -= bet_amount
                loss_in_session += 1
                current = min(max_bet, current * current_multiplier)
            
            if total >= target_bankroll:
                reward += 10
            
            next_state = max(0, min(int(total), 499))
            best_next_action = np.max(Q_table[next_state])
            Q_table[bankroll_state, action] += learning_rate * (reward + discount_factor * best_next_action - Q_table[bankroll_state, action])
            
            bet_multipliers[action] += learning_rate * reward / 100  # Adjust multipliers
            bet_multipliers = np.clip(bet_multipliers, 1, 3)  # Keep multipliers within bounds
        
        if total >= target_bankroll:
            successful_runs += 1
    
    exploration_rate = max(min_exploration_rate, exploration_rate * exploration_decay)

# Save optimized multipliers
optimized_data = {
    "bet_multipliers": bet_multipliers.tolist()
}

with open("betting_strategy.json", "w") as f:
    json.dump(optimized_data, f)

print("Optimized betting strategy saved!")