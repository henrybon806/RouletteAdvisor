import random

class Game():
    def __init__(self, bankroll=100, bet=.1, numSims=1000):
        self.bankroll = bankroll
        self.bet = bet
        self.numSims = numSims
    
    def playGame(self, x, y):
        for _ in range(self.numSims):
            for _ in range(0, 1000):
                win = 1 <= random.randint(1, 38) <= 18
                if win:
                    self.bankroll += self.bet
                    self.bet = x(self.bet)
                else:
                    self.bankroll -= self.bet
                    self.bet = y(self.bet)
        return self.bankroll
    
    def playLive(self):
        self.bankroll = float(input("Enter your starting bankroll: "))
        while self.bankroll > 0:
            self.bet = float(input("Enter your bet amount: "))
            win = 1 <= random.randint(1, 38) <= 18
            if win:
                self.bankroll += self.bet
                print(f"You won! Your new bankroll is {self.bankroll}")
            else:
                self.bankroll -= self.bet
                print(f"You lost! Your new bankroll is {self.bankroll}")
            
            if self.bankroll <= 0:
                print("Game over! You've lost all your money.")
                break
            
            play_again = input("Do you want to play again? (yes/no): ").lower()
            if play_again == 'no':
                print(f"You ended the game with a bankroll of {self.bankroll}")
                break
Game().playLive()