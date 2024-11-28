import tkinter as tk
import random

# Constants
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800
LOG_WIDTH = 100
LOG_HEIGHT = 20
NUM_LOGS_PER_ROW = 3  # Three logs per row
NUM_ROWS = 6  # Set to 6 rows
INITIAL_LOG_SPEED = 5
SPEED_INCREMENT = 0.3
JUMP_DISTANCE = 100
KNIGHT_WIDTH = 30
KNIGHT_HEIGHT = 30
GRAVITY = 0.5  # Gravity constant
FAST_FALL_VELOCITY = -10  # Faster fall velocity for landing
BALL_RADIUS = 10
MAX_BALLS = 3  # Limit number of balls on screen at once

class FrogJumpGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Frog Jump Game")

        # Canvas setup
        self.canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg="#faf0e6")
        self.canvas.pack()

        # Create logs in each row
        self.logs = []
        left_log_x = 150
        for row in range(NUM_ROWS):
            row_y = WINDOW_HEIGHT - (row + 1) * JUMP_DISTANCE  # Adjusted Y position to fit in 6 rows
            row_logs = []
            for i in range(NUM_LOGS_PER_ROW):
                log_x = left_log_x + (i * (WINDOW_WIDTH // NUM_LOGS_PER_ROW))
                log = self.canvas.create_rectangle(log_x, row_y, log_x + LOG_WIDTH, row_y + LOG_HEIGHT, fill="brown")
                row_logs.append(log)
            self.logs.append(row_logs)

        # Knight setup - place on first row of logs
        self.knight = self.create_knight(left_log_x + LOG_WIDTH // 2 - KNIGHT_WIDTH // 2, 
                                         WINDOW_HEIGHT - JUMP_DISTANCE - KNIGHT_HEIGHT)
        self.knight_coords = [left_log_x + LOG_WIDTH // 2 - KNIGHT_WIDTH // 2, 
                              WINDOW_HEIGHT - JUMP_DISTANCE - KNIGHT_HEIGHT]
        self.velocity_y = 0  # Vertical velocity (starts at 0)
        self.on_log = True  # Knight starts on a log
        self.knight_on_log_index = [0, 0]  # Initially on the first log of the first row

        # Chest setup - placed initially
        self.chest = self.place_chest()

        # Ball setup
        self.balls = []  # List to store falling balls

        # Log speeds
        self.log_speeds = [[random.choice([INITIAL_LOG_SPEED, -INITIAL_LOG_SPEED])
                            for _ in range(NUM_LOGS_PER_ROW)] for _ in range(NUM_ROWS)]

        # Score setup
        self.score = 0
        self.score_text = self.canvas.create_text(WINDOW_WIDTH - 50, 20, text="Score: 0", font=("Arial", 14), fill="black")

        # Key bindings
        self.root.bind("<Up>", lambda event: self.jump_knight(0, -JUMP_DISTANCE))  # Jump with Up arrow or space
        self.root.bind("<Left>", lambda event: self.move_knight(-30, 0))           # Move left with Left arrow
        self.root.bind("<Right>", lambda event: self.move_knight(30, 0))           # Move right with Right arrow
        self.root.bind("<space>", lambda event: self.jump_knight(0, -JUMP_DISTANCE))  # Spacebar jump (same as Up)
        self.root.bind("<Down>", lambda event: self.fall_to_next_log())  # Down arrow to fall to the next log

        # Ball spawn interval
        self.spawn_ball_interval = 3000  # Milliseconds
        self.spawn_balls()  # Start spawning balls regularly

        # Game loop
        self.mission_completed = False
        self.update_game()

    def create_knight(self, x, y):
        return self.canvas.create_rectangle(x, y, x + KNIGHT_WIDTH, y + KNIGHT_HEIGHT, fill="gray", outline="black")

    def place_chest(self):
        """Places the chest at a random position on one of the logs in a random row."""
        row = random.randint(0, NUM_ROWS - 1)
        log = self.logs[row][random.choice([0, 1, 2])]  # Choose a log randomly (now there are three logs per row)
        log_coords = self.canvas.coords(log)
        chest_x = log_coords[0] + (LOG_WIDTH - KNIGHT_WIDTH) // 2  # Center chest on log
        chest_y = log_coords[1] - KNIGHT_HEIGHT - 10  # Slight offset above the log
        # Ensure chest doesn't go off-screen
        if chest_y < 0:
            chest_y = 0  # Place chest at the top if it's too high
        return self.canvas.create_rectangle(chest_x, chest_y, chest_x + KNIGHT_WIDTH, chest_y + KNIGHT_HEIGHT, fill="yellow")

    def update_game(self):
        """Game loop to update movement and check conditions."""
        if self.mission_completed:
            return

        # Move logs across the screen
        for i, row_logs in enumerate(self.logs):
            for j, log in enumerate(row_logs):
                self.canvas.move(log, self.log_speeds[i][j], 0)
                log_coords = self.canvas.coords(log)
                if log_coords[2] >= WINDOW_WIDTH or log_coords[0] <= 0:
                    self.log_speeds[i][j] = -self.log_speeds[i][j]

        # Move balls across the screen and check for collisions
        self.move_balls()

        # Knight falling with gravity
        self.apply_gravity()

        # Check knight collision with chest
        self.check_chest_collision()

        # Update score
        self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")

        # Game loop - repeat after a small delay
        self.root.after(20, self.update_game)

    def apply_gravity(self):
        """Apply gravity to the knight if not on a log."""
        if not self.on_log:
            self.velocity_y += GRAVITY  # Increase fall speed due to gravity
            self.canvas.move(self.knight, 0, self.velocity_y)  # Move knight down

            # Check if knight reaches the bottom
            knight_coords = self.canvas.coords(self.knight)
            if knight_coords[1] >= WINDOW_HEIGHT - KNIGHT_HEIGHT:
                self.end_game()  # Game over when knight falls out of bounds
        else:
            # If on a log, move the knight with the log
            log = self.logs[self.knight_on_log_index[0]][self.knight_on_log_index[1]]
            log_coords = self.canvas.coords(log)
            knight_coords = self.canvas.coords(self.knight)
            # Align knight's movement with log (horizontal movement only)
            self.canvas.move(self.knight, log_coords[0] - knight_coords[0], 0)
            self.knight_coords = self.canvas.coords(self.knight)

    def move_balls(self):
        """Move balls and handle collisions."""
        for ball in self.balls[:]:
            self.canvas.move(ball, 0, BALL_RADIUS)
            ball_coords = self.canvas.coords(ball)
            knight_coords = self.canvas.coords(self.knight)

            if self.check_collision(ball, self.knight):
                self.score -= 2
                self.canvas.delete(ball)  # Remove ball when it hits the knight
                self.balls.remove(ball)

            if ball_coords[1] >= WINDOW_HEIGHT:
                self.canvas.delete(ball)
                self.balls.remove(ball)

    def spawn_balls(self):
        """Spawn new balls at regular intervals."""
        if len(self.balls) < MAX_BALLS:
            x_position = random.randint(0, WINDOW_WIDTH - BALL_RADIUS)
            ball = self.canvas.create_oval(x_position, 0, x_position + BALL_RADIUS * 2, BALL_RADIUS * 2, fill="red")
            self.balls.append(ball)

        self.root.after(self.spawn_ball_interval, self.spawn_balls)

    def move_knight(self, dx, dy):
        """Move the knight left or right."""
        self.canvas.move(self.knight, dx, dy)

    def jump_knight(self, dx, dy):
        """Make the knight jump."""
        if self.on_log:
            self.velocity_y = FAST_FALL_VELOCITY  # Reset fall velocity on jump
            self.canvas.move(self.knight, dx, dy)
            self.on_log = False  # Knight is no longer on a log when jumping

    def fall_to_next_log(self):
        """If the knight is not on a log, fall to the next available log."""
        if not self.on_log:
            self.on_log = True
            self.velocity_y = 0  # Reset vertical velocity
            self.canvas.move(self.knight, 0, JUMP_DISTANCE)  # Move knight down to the next row

    def check_chest_collision(self):
        """Check if knight collides with a chest."""
        knight_coords = self.canvas.coords(self.knight)
        chest_coords = self.canvas.coords(self.chest)

        if (knight_coords[0] < chest_coords[2] and knight_coords[2] > chest_coords[0] and
            knight_coords[1] < chest_coords[3] and knight_coords[3] > chest_coords[1]):
            self.score += 10
            self.canvas.delete(self.chest)  # Remove the chest after collection
            self.chest = self.place_chest()  # Place a new chest

    def check_collision(self, ball, knight):
        """Check if the ball collides with the knight."""
        ball_coords = self.canvas.coords(ball)
        knight_coords = self.canvas.coords(knight)
        return (ball_coords[0] < knight_coords[2] and ball_coords[2] > knight_coords[0] and
                ball_coords[1] < knight_coords[3] and ball_coords[3] > knight_coords[1])

    def end_game(self):
        """End the game when knight falls out of bounds."""
        self.canvas.create_text(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2,
                                text="Game Over! Final Score: " + str(self.score), font=("Arial", 20), fill="red")
        self.mission_completed = True

# Run the game
root = tk.Tk()
game = FrogJumpGame(root)
root.mainloop()
