import random
import numpy as np
import json
from multiprocessing import Pool

max_bet = 80 
min_bet = 0.5 
num_simulations = 100  
learning_rate = .000001  
discount_factor = .009  
exploration_rate = .2  
min_exploration_rate = 0.1  
exploration_decay = 0.25
win_threshold =  0.7 
target_bankroll = 150

Q_table = np.zeros((500, 5))
initial_bet_multipliers = np.random.uniform(1, 3, 5)

session_history = []

def run_simulation(session_idx, bet_multipliers):
    total = 100 
    current = min_bet  
    loss_in_session = 0
    successful_run = 0
    round_counter = 0 
    session_data = {
        'rounds': [],
        'bankroll': [],
        'bet_amounts': [],
        'rewards': [],
        'bet_multipliers': [],
    }

    while total > 0 and total < target_bankroll and round_counter < 100:
        round_counter += 1
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
        old_value = Q_table[bankroll_state, action]
        Q_table[bankroll_state, action] += learning_rate * (reward + discount_factor * best_next_action - old_value)

        bet_multipliers[action] += learning_rate * reward / 100
        bet_multipliers = np.clip(bet_multipliers, 1, 3) 

        session_data['rounds'].append(round_counter)
        session_data['bankroll'].append(total)
        session_data['bet_amounts'].append(bet_amount)
        session_data['rewards'].append(reward)
        session_data['bet_multipliers'].append(current_multiplier)

        if round_counter % 10 == 0:
            print(f"Round {round_counter}: Bankroll = {total:.2f}, Bet Multiplier = {current_multiplier:.2f}, Bet Amount = {bet_amount:.2f}, Reward = {reward:.2f}")
            print(f"Q-table at state {bankroll_state}: {Q_table[bankroll_state]}")

    if total >= target_bankroll:
        successful_run = 1

    session_history.append(session_data) 
    return successful_run

def parallel_training():
    global successful_runs
    successful_runs = 0
    with Pool() as pool:
        results = pool.starmap(run_simulation, [(i, initial_bet_multipliers.copy()) for i in range(num_simulations)])
        successful_runs = sum(results)

    return successful_runs

if __name__ == '__main__':
    successful_runs = 0
    while successful_runs / num_simulations < win_threshold:
        successful_runs = parallel_training()
        exploration_rate = max(min_exploration_rate, exploration_rate * exploration_decay)  

        current_percent = (successful_runs / num_simulations) * 100
        print(f"Current progress: {current_percent:.2f}%")

        if successful_runs % 20 == 0:
            print(f"Q-table snapshot: {Q_table[:5]}")

    print(f"90% success rate reached! Running final simulation...")

    final_result = run_simulation("Final_Simulation", initial_bet_multipliers)
    if final_result:
        print(f"Final simulation successful!")
    else:
        print(f"Final simulation failed.")

    optimized_data = {
        "bet_multipliers": initial_bet_multipliers.tolist(),
        "session_history": session_history
    }

    with open("betting_strategy.json", "w") as f:
        json.dump(optimized_data, f)

    print("Optimized betting strategy and session history saved!")