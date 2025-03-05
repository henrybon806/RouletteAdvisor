import random
import numpy as np
import json
import tensorflow as tf
from tensorflow.keras import layers, optimizers
from multiprocessing import Pool, cpu_count
import matplotlib.pyplot as plt
from collections import deque

# Parameters
max_bet = 80
min_bet = 0.5
num_simulations = 100
initial_learning_rate = 0.001  # Adjusted for better convergence
discount_factor = 0.95
exploration_rate = 1.0
min_exploration_rate = 0.01
exploration_decay = 0.995  # Slower decay for better training
win_threshold = 0.90
target_bankroll = 150
batch_size = 64  # Increased batch size for stability
tau = 0.005  # Increased for a smoother soft update
replay_buffer = deque(maxlen=10_000)  # Larger buffer
bet_multipliers = np.linspace(1.5, 3, 5)

# Learning rate schedule
lr_schedule = optimizers.schedules.ExponentialDecay(
    initial_learning_rate, decay_steps=1000, decay_rate=0.96, staircase=True
)

# Build Neural Network Model
def build_model():
    model = tf.keras.Sequential([
        layers.Input(shape=(1,)),  
        layers.Dense(128, activation=None, kernel_initializer="he_normal"),  
        layers.BatchNormalization(),
        layers.LeakyReLU(),
        layers.Dense(64, activation=None, kernel_initializer="he_normal"),
        layers.BatchNormalization(),
        layers.LeakyReLU(),
        layers.Dense(5, activation="linear")  # 5 outputs for action values
    ])
    model.compile(optimizer=optimizers.Adam(learning_rate=lr_schedule), loss="mse")
    return model

# Initialize models
model = build_model()
target_model = build_model()
target_model.set_weights(model.get_weights())

# Train the model in batches
def train_model():
    if len(replay_buffer) < batch_size:
        return  

    batch = random.sample(replay_buffer, batch_size)
    states, actions, rewards, next_states, dones = zip(*batch)

    states = np.array(states).reshape(-1, 1)
    next_states = np.array(next_states).reshape(-1, 1)
    rewards = np.array(rewards)
    dones = np.array(dones)

    current_q_values = model.predict(states, verbose=0)
    next_q_values = target_model.predict(next_states, verbose=0)

    for i in range(batch_size):
        target = rewards[i] if dones[i] else rewards[i] + discount_factor * np.max(next_q_values[i])
        current_q_values[i][actions[i]] = target

    model.train_on_batch(states, current_q_values)

# Soft update target model
def soft_update_target_model():
    model_weights = model.get_weights()
    target_weights = target_model.get_weights()
    target_model.set_weights([tau * mw + (1 - tau) * tw for mw, tw in zip(model_weights, target_weights)])

# Simulate betting
def run_simulation(session_idx):
    bankroll = 100  
    bet = min_bet  
    rounds = 0

    while bankroll > 0 and bankroll < target_bankroll and rounds < 100:
        rounds += 1
        bankroll_state = np.array([[bankroll]])  

        if random.uniform(0, 1) < exploration_rate:
            action = random.randint(0, 4)
        else:
            action = np.argmax(model.predict(bankroll_state, verbose=0)[0])  

        bet_multiplier = bet_multipliers[action]
        bet_amount = min(max_bet, max(min_bet, bet * bet_multiplier))

        spin = random.randint(1, 38)
        won = 1 <= spin <= 18  

        if won:
            reward = bet_amount
            bankroll += bet_amount
            bet = min_bet
        else:
            reward = -bet_amount
            bankroll -= bet_amount
            bet = min(max_bet, bet * bet_multiplier)

        done = bankroll >= target_bankroll or bankroll <= 0
        replay_buffer.append((bankroll, action, reward, bankroll, done))

        if done:
            break  

    return bankroll >= target_bankroll  

# Train using multiprocessing
def parallel_training():
    global exploration_rate

    with Pool(cpu_count()) as pool:
        results = pool.map(run_simulation, range(num_simulations))

    success_rate = sum(results) / num_simulations
    train_model()
    soft_update_target_model()
    
    exploration_rate = max(min_exploration_rate, exploration_rate * exploration_decay)
    
    return success_rate

# Plot results
def plot_results():
    plt.figure(figsize=(12, 6))
    plt.plot(reward_history, label="Success Rate")
    plt.xlabel("Training Sessions")
    plt.ylabel("Success Rate")
    plt.title("Training Progress")
    plt.legend()
    plt.show()

# Main training loop
if __name__ == '__main__':
    reward_history = []
    best_success_rate = 0
    patience = 5  # Early stopping patience
    no_improve_count = 0  

    while True:
        success_rate = parallel_training()
        reward_history.append(success_rate)
        print(f"Success rate: {success_rate:.2%}")

        if success_rate > best_success_rate:
            best_success_rate = success_rate
            no_improve_count = 0  
        else:
            no_improve_count += 1  

        if success_rate >= win_threshold or no_improve_count >= patience:
            print("Training complete.")
            break

    with open("betting_strategy.json", "w") as f:
        json.dump({"bet_multipliers": bet_multipliers.tolist()}, f)

    plot_results()