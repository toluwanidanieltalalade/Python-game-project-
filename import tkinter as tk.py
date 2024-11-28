import tkinter as tk
import random

# Constants
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800
LOG_WIDTH = 100
LOG_HEIGHT = 20
NUM_LOGS_PER_ROW = 2  # Two logs per row
NUM_ROWS = 6  # Set to 6 rows
INITIAL_LOG_SPEED = 4
SPEED_INCREMENT = 0.3
JUMP_DISTANCE = 100
KNIGHT_WIDTH = 30
KNIGHT_HEIGHT = 30
GRAVITY = 0.5  # Gravity constant
BOUNCE_VELOCITY = -8  # Initial velocity when bouncing off a log or ground

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
            left_log = self.canvas.create_rectangle(left_log_x, row_y, left_log_x + LOG_WIDTH, row_y + LOG_HEIGHT, fill="brown")
            right_log = self.canvas.create_rectangle(right_log_x, row_y, right_log_x + LOG_WIDTH, row_y + LOG_HEIGHT, fill="brown")
            row_logs.append(left_log)
            row_logs.append(right_log)
            self.logs.append(row_logs)

        # Knight setup
        self.knight = self.create_knight(left_log_x + LOG_WIDTH // 2 - KNIGHT_WIDTH // 2, 
                                         WINDOW_HEIGHT - JUMP_DISTANCE - KNIGHT_HEIGHT)
        self.knight_coords = [left_log_x + LOG_WIDTH // 2 - KNIGHT_WIDTH // 2, 
                              WINDOW_HEIGHT - JUMP_DISTANCE - KNIGHT_HEIGHT]
        self.velocity_y = 0  # Vertical velocity (starts at 0)
        self.bounced = False  # To track if the knight has already bounced

        # Chest setup - placed initially
        self.chest = self.place_chest()

        # Log speeds
        self.log_speeds = [[INITIAL_LOG_SPEED if random.choice([True, False]) else -INITIAL_LOG_SPEED
                            for _ in range(NUM_LOGS_PER_ROW)] for _ in range(NUM_ROWS)]

        # Score setup
        self.score = 0
        self.score_text = self.canvas.create_text(WINDOW_WIDTH - 50, 20, text="Score: 0", font=("Arial", 14), fill="black")

        # Victory flag
        self.mission_completed = False

        # Key bindings
        self.root.bind("<Up>", lambda event: self.jump_knight(0, -JUMP_DISTANCE))  # Jump with Up arrow or space
        self.root.bind("<Left>", lambda event: self.move_knight(-30, 0))           # Move left with Left arrow
        self.root.bind("<Right>", lambda event: self.move_knight(30, 0))           # Move right with Right arrow
        self.root.bind("<space>", lambda event: self.jump_knight(0, -JUMP_DISTANCE))  # Spacebar jump (same as Up)

        # Start game loop
        self.update_game()

    def create_knight(self, x, y):
        return self.canvas.create_rectangle(x, y, x + KNIGHT_WIDTH, y + KNIGHT_HEIGHT, fill="gray", outline="black")

    def place_chest(self):
        """Places the chest at a random position on one of the logs in a random row."""
        row = random.randint(0, NUM_ROWS - 1)
        log = self.logs[row][random.choice([0, 1])]  # Choose a log randomly (now there are two logs per row)
        log_coords = self.canvas.coords(log)
        chest_x = log_coords[0] + (LOG_WIDTH - KNIGHT_WIDTH) // 2  # Center chest on log
        chest_y = log_coords[1] - KNIGHT_HEIGHT - 10  # Slight offset above the log
        # Ensure chest doesn't go off-screen
        if chest_y < 0:
            chest_y = 0  # Place chest at the top if it's too high
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

        # Check if knight has fallen below the ground
        knight_coords = self.canvas.coords(self.knight)
        if knight_coords[1] >= WINDOW_HEIGHT:
            self.velocity_y = 0
            self.mission_completed = True
            self.canvas.create_text(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, text="Game Over!", font=("Arial", 24), fill="red")
            return

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
                    log_speed = self.log_speeds[self.get_log_row(log)][self.get_log_index(log)]
                    # Move knight with the log's movement
                    knight_speed = log_speed * 0.5  # Adjust speed if necessary
                    self.canvas.move(self.knight, knight_speed, 0)

                    if not self.bounced:
                        self.velocity_y = BOUNCE_VELOCITY  # Bounce when landing on a log
                        self.bounced = True  # Set bounced flag to prevent multiple bounces
                    break
            # If knight is not on any log, it should fall (reset bounced flag)
        if not self.on_log:
            self.bounced = False

    def check_collision(self, rect1, rect2):
        """Check if two rectangles collide."""
        coords1 = self.canvas.coords(rect1)
        coords2 = self.canvas.coords(rect2)
        return not (coords1[2] < coords2[0] or coords1[0] > coords2[2] or 
                    coords1[3] < coords2[1] or coords1[1] > coords2[3])

    def get_log_row(self, log):
        """Get the row index of the log."""
        for i, row_logs in enumerate(self.logs):
            if log in row_logs:
                return i

    def get_log_index(self, log):
        """Get the index of the log in its row."""
        for row_logs in self.logs:
            if log in row_logs:
                return row_logs.index(log)

    def update_score(self):
        """Update the score displayed on the screen."""
        self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")


# Run the game
root = tk.Tk()
game = FrogJumpGame(root)
root.mainloop()
