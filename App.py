import tkinter as tk
import random

class SpaceInvadersGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Space Invaders")

        self.canvas = tk.Canvas(self.root, width=600, height=600, bg='black')
        self.canvas.pack()

        # Create game objects
        self.player = self.canvas.create_rectangle(275, 550, 325, 580, fill='white')
        self.invaders = []
        self.bullets = []
        self.invader_bullets = []
        self.power_ups = []
        self.score = 0
        self.level = 1
        self.lives = 3
        self.game_over = False
        self.player_direction = 0
        self.invader_direction = 1
        self.invader_speed = 0.1

        self.create_invaders()
        self.root.bind("<KeyPress>", self.key_press)
        self.root.bind("<KeyRelease>", self.key_release)
        self.root.after(20, self.update_game)

    def create_invaders(self):
        self.invaders.clear()
        for i in range(6):
            for j in range(5):
                x = 50 + i * 80
                y = 50 + j * 60
                invader = self.canvas.create_rectangle(x, y, x + 50, y + 30, fill='green')
                self.invaders.append(invader)
        self.spawn_power_up()

    def spawn_power_up(self):
        if random.random() < 0.1:  # 10% chance to spawn a power-up
            x = random.randint(50, 540)
            y = random.randint(50, 200)
            power_up = self.canvas.create_rectangle(x, y, x + 20, y + 20, fill='purple')
            self.power_ups.append(power_up)

    def move_player(self):
        if self.player_direction != 0:
            self.canvas.move(self.player, self.player_direction, 0)
            x1, _, x2, _ = self.canvas.bbox(self.player)
            if x1 < 0:
                self.canvas.move(self.player, -x1, 0)
            elif x2 > 600:
                self.canvas.move(self.player, 600 - x2, 0)

    def move_invaders(self):
        if self.game_over:
            return

        if self.invaders:
            for invader in self.invaders:
                self.canvas.move(invader, self.invader_direction, 0)

            invader_coords = [self.canvas.bbox(invader) for invader in self.invaders]
            leftmost = min(x1 for x1, _, _, _ in invader_coords)
            rightmost = max(x2 for _, _, x2, _ in invader_coords)
            bottommost = max(y2 for _, _, _, y2 in invader_coords)

            if leftmost < 0 or rightmost > 600:
                self.invader_direction *= -1
                for invader in self.invaders:
                    self.canvas.move(invader, 0, 20)
            if bottommost > 550:
                self.game_over = True
                self.canvas.create_text(300, 300, text="Game Over", fill='red', font=('Arial', 24))
            elif not self.invaders:
                self.game_over = True
                self.canvas.create_text(300, 300, text="You Win!", fill='green', font=('Arial', 24))

    def move_bullets(self):
        if self.game_over:
            return

        for bullet in self.bullets[:]:
            self.canvas.move(bullet, 0, -10)
            coords = self.canvas.bbox(bullet)
            if coords[1] < 0:
                self.canvas.delete(bullet)
                self.bullets.remove(bullet)

        for bullet in self.invader_bullets[:]:
            self.canvas.move(bullet, 0, 5)
            coords = self.canvas.bbox(bullet)
            if coords[3] > 600:
                self.canvas.delete(bullet)
                self.invader_bullets.remove(bullet)

    def check_collisions(self):
        if self.game_over:
            return

        player_coords = self.canvas.bbox(self.player)
        for bullet in self.bullets[:]:
            bullet_coords = self.canvas.bbox(bullet)
            for invader in self.invaders[:]:
                invader_coords = self.canvas.bbox(invader)
                if (bullet_coords[0] < invader_coords[2] and bullet_coords[2] > invader_coords[0] and
                    bullet_coords[1] < invader_coords[3] and bullet_coords[3] > invader_coords[1]):
                    self.canvas.delete(bullet)
                    self.bullets.remove(bullet)
                    self.canvas.delete(invader)
                    self.invaders.remove(invader)
                    self.score += 10
                    self.update_score()
                    break

        for bullet in self.invader_bullets[:]:
            bullet_coords = self.canvas.bbox(bullet)
            if (bullet_coords[0] < player_coords[2] and bullet_coords[2] > player_coords[0] and
                bullet_coords[1] < player_coords[3] and bullet_coords[3] > player_coords[1]):
                self.lives -= 1
                if self.lives <= 0:
                    self.game_over = True
                    self.canvas.create_text(300, 300, text="Game Over", fill='red', font=('Arial', 24))
                self.canvas.delete(bullet)
                self.invader_bullets.remove(bullet)
                self.update_lives()

        for power_up in self.power_ups[:]:
            power_up_coords = self.canvas.bbox(power_up)
            if (player_coords[0] < power_up_coords[2] and player_coords[2] > power_up_coords[0] and
                player_coords[1] < power_up_coords[3] and player_coords[3] > power_up_coords[1]):
                self.canvas.delete(power_up)
                self.power_ups.remove(power_up)
                self.invader_speed = max(0.05, self.invader_speed - 0.01)
                self.canvas.create_text(300, 300, text="Speed Boost!", fill='yellow', font=('Arial', 24))
                self.root.after(1000, lambda: self.canvas.delete('text'))  # Clear text after 1 second

    def fire_bullet(self):
        if self.game_over:
            return
        x1, y1, x2, y2 = self.canvas.bbox(self.player)
        bullet = self.canvas.create_rectangle((x1 + x2) / 2 - 5, y1 - 20, (x1 + x2) / 2 + 5, y1 - 10, fill='white')
        self.bullets.append(bullet)

    def fire_invader_bullets(self):
        if self.game_over:
            return
        for invader in random.sample(self.invaders, min(len(self.invaders), 2)):
            x1, y1, x2, y2 = self.canvas.bbox(invader)
            bullet = self.canvas.create_rectangle((x1 + x2) / 2 - 5, y2, (x1 + x2) / 2 + 5, y2 + 10, fill='red')
            self.invader_bullets.append(bullet)

    def key_press(self, event):
        if event.keysym == 'Left':
            self.player_direction = -10
        elif event.keysym == 'Right':
            self.player_direction = 10
        elif event.keysym == 'space':
            self.fire_bullet()

    def key_release(self, event):
        if event.keysym in ['Left', 'Right']:
            self.player_direction = 0

    def update_game(self):
        self.move_player()
        self.move_invaders()
        self.move_bullets()
        self.check_collisions()
        self.fire_invader_bullets()
        if not self.game_over:
            self.root.after(100, self.update_game)

    def update_score(self):
        self.canvas.delete('score')
        self.canvas.create_text(10, 10, anchor='nw', text=f"Score: {self.score}", fill='white', font=('Arial', 12), tags='score')

    def update_lives(self):
        self.canvas.delete('lives')
        self.canvas.create_text(550, 10, anchor='ne', text=f"Lives: {self.lives}", fill='white', font=('Arial', 12), tags='lives')

# Create the main window
root = tk.Tk()
app = SpaceInvadersGame(root)
root.mainloop()
