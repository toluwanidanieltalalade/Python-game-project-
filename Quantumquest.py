import tkinter as tk
import random

#Global var
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
        left_log_x = 150
        right_log_x = WINDOW_WIDTH - LOG_WIDTH - 150
        self.logs = []
        for row in range(NUM_ROWS):
            row_y = WINDOW_HEIGHT - (row + 1) * JUMP_DISTANCE  # Adjusted Y position to fit in 6 rows
            row_logs = []
            for i in range(NUM_LOGS_PER_ROW):
                log_x = left_log_x + (i * (WINDOW_WIDTH // NUM_LOGS_PER_ROW))
                log = self.canvas.create_rectangle(log_x, row_y, log_x + LOG_WIDTH, row_y + LOG_HEIGHT, fill="brown")
                row_logs.append(log)
            self.logs.append(row_logs)

        # Knight setup
        self.knight = self.create_knight(left_log_x + LOG_WIDTH // 2 - KNIGHT_WIDTH // 2, 
                                         WINDOW_HEIGHT - JUMP_DISTANCE - KNIGHT_HEIGHT)
        self.knight_coords = [left_log_x + LOG_WIDTH // 2 - KNIGHT_WIDTH // 2, 
                              WINDOW_HEIGHT - JUMP_DISTANCE - KNIGHT_HEIGHT]
        self.velocity_y = 0  # Vertical velocity (starts at 0)
        self.on_log = False  # To track if the knight is on a log

        # Chest setup - placed initially
        self.chest = self.place_chest()

        # Ball setup
        self.balls = []  # List to store falling balls

        # Log speeds
        self.log_speeds = [[INITIAL_LOG_SPEED if random.choice([True, False]) else -INITIAL_LOG_SPEED
                            for _ in range(NUM_LOGS_PER_ROW)] for _ in range(NUM_ROWS)]

        # Score setup
        self.score = 0
        self.score_text = self.canvas.create_text(WINDOW_WIDTH - 50, 20, text="Score: 0", font=("Arial", 14), fill="black")

        # Mission completion flag
        self.mission_completed = False

        # Key bindings
        self.root.bind("<Up>", lambda event: self.jump_knight(0, -JUMP_DISTANCE))  # Jump with Up arrow or space
        self.root.bind("<Left>", lambda event: self.move_knight(-30, 0))           # Move left with Left arrow
        self.root.bind("<Right>", lambda event: self.move_knight(30, 0))           # Move right with Right arrow
        self.root.bind("<space>", lambda event: self.jump_knight(0, -JUMP_DISTANCE))  # Spacebar jump (same as Up)
        self.root.bind("<Down>", lambda event: self.fall_to_next_log())  # Down arrow to fall to the next log

        # Start game loop
        self.update_game()

    def create_knight(self, x, y):
        return self.canvas.create_rectangle(x, y, x + KNIGHT_WIDTH, y + KNIGHT_HEIGHT, fill="gray", outline="black")

    def place_chest(self):
        """Place chest randomly on a log."""
        row = random.randint(0, NUM_ROWS - 1)
        log = random.choice(self.logs[row])  # Choose a random log from a row
        log_coords = self.canvas.coords(log)
        chest_x = log_coords[0] + (LOG_WIDTH - KNIGHT_WIDTH) // 2  # Center chest on the log
        chest_y = log_coords[1] - KNIGHT_HEIGHT - 10  # Slight offset above the log
        return self.canvas.create_rectangle(chest_x, chest_y, chest_x + KNIGHT_WIDTH, chest_y + KNIGHT_HEIGHT, fill="yellow")

    def update_game(self):
        """Game loop to update movement and check conditions."""
        # Stop game loop if mission is completed
        if self.mission_completed:
            return

        # Move logs across the screen
        for i, row_logs in enumerate(self.logs):
            for j, log in enumerate(row_logs):
                self.canvas.move(log, self.log_speeds[i][j], 0)
                log_coords = self.canvas.coords(log)
                if log_coords[2] >= WINDOW_WIDTH or log_coords[0] <= 0:
                    self.log_speeds[i][j] = -self.log_speeds[i][j]

        # Check for knight's position on the logs
        self.check_knight_on_log()

        # Apply gravity to the knight if it's not on a log
        if not self.on_log:
            self.velocity_y += GRAVITY  # Accelerate falling

        # Move knight with current vertical velocity
        self.canvas.move(self.knight, 0, self.velocity_y)

        # Check for ball movement and collisions
        self.update_balls()

        # Check if knight has fallen below the ground
        knight_coords = self.canvas.coords(self.knight)
        if knight_coords[1] >= WINDOW_HEIGHT:
            self.velocity_y = 0
            self.mission_completed = True
            self.canvas.create_text(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, text="Game Over!", font=("Arial", 24), fill="red")
            return

        # Periodic ball spawning
        self.spawn_balls_periodically()

        # Continue game loop
        self.root.after(50, self.update_game)

    def jump_knight(self, dx, dy):
        self.move_knight(dx, dy)

    def move_knight(self, dx, dy):
        """Move the knight and check for falling, collision, or victory."""
        self.canvas.move(self.knight, dx, dy)
        self.knight_coords[0] += dx
        self.knight_coords[1] += dy

        knight_coords = self.canvas.coords(self.knight)

        # Victory condition
        if knight_coords[1] <= 0:
            self.mission_completed = True
            self.canvas.create_text(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, text="You Win!", font=("Arial", 24), fill="green")
            return

        # Apply gravity when not on a log
        if not self.on_log:
            self.velocity_y += GRAVITY

        # Check for chest collision
        if self.check_collision(self.knight, self.chest):
            self.score += 10
            self.update_score()
            self.canvas.delete(self.chest)  # Remove the old chest
            self.chest = self.place_chest()  # Place a new chest

    def check_knight_on_log(self):
        """Check if the knight is on any log and move accordingly."""
        self.on_log = False
        for row_logs in self.logs:
            for log in row_logs:
                if self.check_collision(self.knight, log):
                    self.on_log = True
                    log_speed = self.log_speeds[self.get_log_row(log)][row_logs.index(log)]
                    self.velocity_y = 0  # Reset vertical velocity if knight is on a log
                    return

    def get_log_row(self, log):
        """Get the row number of a given log."""
        for i, row_logs in enumerate(self.logs):
            if log in row_logs:
                return i
        return -1

    def check_collision(self, item1, item2):
        """Check if two items are colliding."""
        coords1 = self.canvas.coords(item1)
        coords2 = self.canvas.coords(item2)
        print(coords1,coords2)
        return (coords1[2] > coords2[0] and coords1[1] < coords2[2] and 
                coords1[3] > coords2[1] )
        

    def update_score(self):
        """Update score display."""
        self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")

    def spawn_falling_ball(self):
        """Spawn a small black ball falling from the top logs."""
        row = random.randint(0, NUM_ROWS - 1)
        log = random.choice(self.logs[row])  # Random log
        log_coords = self.canvas.coords(log)
        ball_x = log_coords[0] + (LOG_WIDTH - BALL_RADIUS) // 2  # Center the ball on the log
        ball_y = log_coords[1] - BALL_RADIUS  # Slightly above the log
        ball = self.canvas.create_oval(ball_x, ball_y, ball_x + BALL_RADIUS, ball_y + BALL_RADIUS, fill="black")
        self.balls.append(ball)

    def update_balls(self):
        """Move balls and check for collisions with knight."""
        for ball in self.balls:
            self.canvas.move(ball, 0, 5)  # Move ball downwards
            ball_coords = self.canvas.coords(ball)

            if ball_coords[3] >= WINDOW_HEIGHT:  # Ball falls off the screen
                self.canvas.delete(ball)
                self.balls.remove(ball)

            if self.check_collision(self.knight, ball):  # Collision with knight
                self.canvas.delete(ball)
                self.balls.remove(ball)
                self.score -= 2  # Decrease score by 2
                self.update_score()

    def spawn_balls_periodically(self):
        """Spawn balls at regular intervals."""
        if random.random() < 0.02 and len(self.balls) < MAX_BALLS:  # Control ball spawn frequency
            self.spawn_falling_ball()

    def fall_to_next_log(self):
        """Make the knight fall to the next log below if possible."""
        knight_coords = self.canvas.coords(self.knight)
        current_row = self.get_knight_row(knight_coords[1])

        if current_row < NUM_ROWS - 1:
            next_row = current_row + 1
            for log in self.logs[next_row]:
                if self.check_collision(self.knight, log):
                    self.canvas.move(self.knight, 0, JUMP_DISTANCE)
                    return

    def get_knight_row(self, knight_y):
        """Get the row number based on the knight's Y position."""
        for i in range(NUM_ROWS):
            row_y = WINDOW_HEIGHT - (i + 1) * JUMP_DISTANCE
            if knight_y >= row_y:
                return i
        return NUM_ROWS - 1  # Default to last row if it's at the bottom

# Run the game
root = tk.Tk()
game = FrogJumpGame(root)
root.mainloop()
