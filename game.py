
class Game():
    def __init__(self):
        self.score = 0
        self.missed_notes = 0
        self.max_missed_notes = 5  # Game over after missing 5 notes

    def note_hit(self):
        self.score += 1
        print(f"Score: {self.score}")

    def note_missed(self):
        self.missed_notes += 1
        print(f"Missed Notes: {self.missed_notes}")
        if self.missed_notes >= self.max_missed_notes:
            print("GG game over")
