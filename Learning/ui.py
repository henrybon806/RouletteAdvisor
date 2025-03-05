import json
import random
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox

def load_betting_strategy():
    try:
        with open("betting_strategy.json", "r") as f:
            data = json.load(f)
        if "bet_multipliers" not in data:
            raise ValueError("Invalid betting strategy file format.")
        return data["bet_multipliers"]
    except (FileNotFoundError, ValueError) as e:
        show_error("Error", f"Error loading betting strategy: {e}")
        exit()

bet_multipliers = load_betting_strategy()

def get_next_bet(previous_bet, won):
    try:
        initial_bet_value = float(initial_bet.text())
    except ValueError:
        show_error("Error", "Invalid initial bet value.")
        return previous_bet  # Return the previous bet if the initial bet is invalid
    
    if won:
        return initial_bet_value  # Reset to initial bet after a win
    else:
        action = min(len(bet_multipliers) - 1, int(previous_bet / 20))
        return max(initial_bet_value, previous_bet * bet_multipliers[action])

def update_next_bet(won):
    try:
        if bet_amount.text() == "":
            current_bet = float(initial_bet.text())
        else:
            current_bet = float(bet_amount.text())
        next_bet = get_next_bet(current_bet, won)
        bet_amount.setText(f"{next_bet:.2f}")
    except ValueError:
        show_error("Error", "Invalid bet amount.")

def run_simulation():
    try:
        balance = float(total_balance.text())
        initial_bet_value = float(initial_bet.text())
        
        if balance <= 0 or initial_bet_value <= 0:
            show_error("Error", "Balance and initial bet must be positive numbers.")
            return
        
        current_bet = initial_bet_value
        rounds = 0
        total_winnings = 0

        while rounds < 100:
            if current_bet > balance:
                show_info("Simulation End", f"Not enough balance to place bet ($ {current_bet:.2f}).")
                break

            won = random.choice([True, False])
            rounds += 1
            if won:
                winnings = current_bet
                balance += winnings
                total_winnings += winnings
                current_bet = get_next_bet(current_bet, True)
                if rounds >= 50:
                    break
            else:
                winnings = -current_bet
                balance = max(0, balance + winnings)
                total_winnings += winnings
                current_bet = get_next_bet(current_bet, False)

            if rounds >= 50 and won:
                break
            if balance <= 0:
                show_info("Simulation End", "Balance depleted.")
                break

        avg_winnings = total_winnings / rounds if rounds > 0 else 0
        show_info("Simulation Complete", f"Total Winnings: ${total_winnings:.2f}\nFinal Balance: ${balance:.2f}\nAvg Winnings per Round: ${avg_winnings:.2f}")
    except ValueError:
        show_error("Error", "Invalid input values.")

def show_error(title, message):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.exec_()

def show_info(title, message):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.exec_()

# PyQt5 UI Setup
app = QApplication([])

window = QWidget()
window.setWindowTitle("Betting Advisor")

layout = QVBoxLayout()

total_balance_label = QLabel("Total Balance:")
layout.addWidget(total_balance_label)
total_balance = QLineEdit()
layout.addWidget(total_balance)

initial_bet_label = QLabel("Initial Bet:")
layout.addWidget(initial_bet_label)
initial_bet = QLineEdit()
layout.addWidget(initial_bet)

bet_amount_label = QLabel("Current Bet:")
layout.addWidget(bet_amount_label)
bet_amount = QLineEdit()
bet_amount.setReadOnly(True)
layout.addWidget(bet_amount)

won_button = QPushButton("Won")
won_button.clicked.connect(lambda: update_next_bet(True))
layout.addWidget(won_button)

lost_button = QPushButton("Lost")
lost_button.clicked.connect(lambda: update_next_bet(False))
layout.addWidget(lost_button)

simulate_button = QPushButton("Simulate")
simulate_button.clicked.connect(run_simulation)
layout.addWidget(simulate_button)

exit_button = QPushButton("Exit")
exit_button.clicked.connect(window.close)
layout.addWidget(exit_button)

window.setLayout(layout)
window.show()

app.exec_()