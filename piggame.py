# IS211_Assignment8.py Pig game with Factory + Timed Proxy
# Run examples to use:
#   python IS211_Assignment8.py --player1 human --player2 computer
#   python IS211_Assignment8.py --player1 computer --player2 computer
#   python IS211_Assignment8.py --player1 computer --player2 computer --timed

import argparse
import random
import time

TARGET_SCORE = 100
CPU_HOLD_DEFAULT = 25


class Dice:
    def roll(self) -> int:
        return random.randint(1, 6)


class Player:
    def __init__(self, name: str):
        self.name = name
        self.score = 0

    def take_turn(self, dice: Dice) -> int:
        return 0


class HumanPlayer(Player):
    def take_turn(self, dice: Dice) -> int:
        turn_total = 0
        print(f"\n{self.name}'s turn. Current score = {self.score}")
        while True:
            choice = input("Roll or Hold? (r/h): ").strip().lower()
            if choice not in ("r", "h"):
                print("Please type 'r' or 'h'.")
                continue
            if choice == "h":
                print(f"{self.name} holds with {turn_total} this turn.")
                return turn_total
            roll = dice.roll()
            print(f"Rolled: {roll}")
            if roll == 1:
                print("Pig! Turn ends with 0.")
                return 0
            turn_total += roll
            print(f"Turn total: {turn_total}")


class ComputerPlayer(Player):
    def take_turn(self, dice: Dice) -> int:
        threshold = min(CPU_HOLD_DEFAULT, TARGET_SCORE - self.score)
        turn_total = 0
        print(f"\n{self.name}'s turn (CPU). Score={self.score}, threshold={threshold}")
        while turn_total < threshold:
            roll = dice.roll()
            print(f"{self.name} rolled {roll}")
            if roll == 1:
                print("Pig! CPU turn ends with 0.")
                return 0
            turn_total += roll
        print(f"{self.name} holds with {turn_total}")
        return turn_total


#  Factory Pattern
class PlayerFactory:
    @staticmethod
    def create(kind: str, name: str) -> Player:
        k = kind.lower()
        if k == "human":
            return HumanPlayer(name)
        if k == "computer":
            return ComputerPlayer(name)
        raise ValueError("Player type must be 'human' or 'computer'.")


# Game
class Game:
    def __init__(self, p1: Player, p2: Player, dice: Dice | None = None):
        self.players = [p1, p2]
        self.dice = dice or Dice()

    def play(self) -> Player:
        turn = 0
        while True:
            current = self.players[turn % 2]
            earned = current.take_turn(self.dice)
            current.score += earned
            print(f"{current.name} total score: {current.score}")
            if current.score >= TARGET_SCORE:
                print(f"\n{current.name} wins!")
                return current
            turn += 1


#Proxy Pattern (Timed)
class TimedGameProxy:
    """Wraps a Game and enforces a time limit; leader at timeout wins (tie -> player 1)."""
    def __init__(self, game: Game, seconds: int = 60):
        self._game = game
        self._limit = seconds

    def play(self) -> Player:
        start = time.time()
        turn = 0
        while True:
            if time.time() - start >= self._limit:
                p1, p2 = self._game.players
                print("\n⏱ Time is up!")
                if p1.score == p2.score:
                    print(f"Tie on points ({p1.score}). {p1.name} wins by tiebreak.")
                    return p1
                winner = p1 if p1.score > p2.score else p2
                print(f"Leader at time up: {winner.name}")
                return winner

            current = self._game.players[turn % 2]
            earned = current.take_turn(self._game.dice)
            current.score += earned
            print(f"{current.name} total score: {current.score}")
            if current.score >= TARGET_SCORE:
                print(f"\n{current.name} wins!")
                return current
            turn += 1


def parse_args():
    ap = argparse.ArgumentParser(description="Pig with Factory and Timed Proxy")
    ap.add_argument("--player1", choices=["human", "computer"], required=True)
    ap.add_argument("--player2", choices=["human", "computer"], required=True)
    ap.add_argument("--timed", action="store_true", help="Enable 60-second timed mode")
    return ap.parse_args()


def main():
    args = parse_args()
    p1 = PlayerFactory.create(args.player1, "Player 1")
    p2 = PlayerFactory.create(args.player2, "Player 2")
    base_game = Game(p1, p2)
    game = TimedGameProxy(base_game) if args.timed else base_game
    winner = game.play()
    print(f"\nWinner: {winner.name} (Score: {winner.score})")


if __name__ == "__main__":
    main()
