import tkinter as tk
import random

# Constants
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800
LOG_WIDTH = 100
LOG_HEIGHT = 20
NUM_LOGS_PER_ROW = 3  # Three logs per row
NUM_ROWS = 6  # Set to 6 rows
INITIAL_LOG_SPEED = 6  # Increased initial log speed
SPEED_INCREMENT = 0.3
JUMP_DISTANCE = 100
KNIGHT_WIDTH = 30
KNIGHT_HEIGHT = 30
GRAVITY = 0.5  # Gravity constant
FAST_FALL_VELOCITY = -10  # Faster fall velocity for landing
MAX_FALL_VELOCITY = 10  # Maximum fall velocity to prevent very fast falling

class FrogJumpGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Frog Jump Game")

        # Canvas setup
        self.canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg="#faf0e6")
        self.canvas.pack()

        # Create logs in each row with different speeds and patterns
        self.logs = []
        self.log_speeds = []
        spacing_between_logs = (WINDOW_WIDTH - LOG_WIDTH * NUM_LOGS_PER_ROW) / (NUM_LOGS_PER_ROW + 1)  # Calculate spacing between logs

        for row in range(NUM_ROWS):
            row_y = WINDOW_HEIGHT - (row + 1) * JUMP_DISTANCE  # Adjusted Y position to fit in 6 rows
            row_logs = []
            row_speeds = []
            for i in range(NUM_LOGS_PER_ROW):
                log_x = spacing_between_logs * (i + 1) + LOG_WIDTH * i  # Distribute logs across the screen
                log = self.canvas.create_rectangle(log_x, row_y, log_x + LOG_WIDTH, row_y + LOG_HEIGHT, fill="brown")
                row_logs.append(log)
                speed = random.uniform(-INITIAL_LOG_SPEED, INITIAL_LOG_SPEED)  # Random speed for each log
                row_speeds.append(speed)
            self.logs.append(row_logs)
            self.log_speeds.append(row_speeds)

        # Knight setup
        self.knight = self.create_knight(LOG_WIDTH * NUM_LOGS_PER_ROW // 2, 
                                         WINDOW_HEIGHT - JUMP_DISTANCE - KNIGHT_HEIGHT)
        self.knight_coords = [LOG_WIDTH * NUM_LOGS_PER_ROW // 2, 
                              WINDOW_HEIGHT - JUMP_DISTANCE - KNIGHT_HEIGHT]
        self.velocity_y = 0  # Vertical velocity (starts at 0)
        self.on_log = False  # To track if the knight is on a log
        self.falling = False  # Flag to track whether knight is falling

        # Chest setup - placed initially
        self.chest = self.place_chest()

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
        self.root.bind("<Down>", lambda event: self.start_falling())  # Down arrow to start falling

        # Start game loop
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
        # Stop game loop if mission is completed
        if self.mission_completed:
            return

        # Move logs across the screen
        for i, row_logs in enumerate(self.logs):
            for j, log in enumerate(row_logs):
                # Update log position based on its speed
                self.canvas.move(log, self.log_speeds[i][j], 0)
                log_coords = self.canvas.coords(log)
                # Reverse direction if log goes off the screen
                if log_coords[2] >= WINDOW_WIDTH or log_coords[0] <= 0:
                    self.log_speeds[i][j] = -self.log_speeds[i][j]
        
        # Check for collisions between logs on the same row
        for i, row_logs in enumerate(self.logs):
            if self.check_log_collisions(row_logs):
                # Handle log collisions (optional behavior)
                self.handle_log_collisions(row_logs)

        # Check for knight's position on the logs
        self.check_knight_on_log()

        # Apply gravity to the knight if it's falling or not on a log
        if self.falling or not self.on_log:
            self.velocity_y += GRAVITY  # Accelerate falling
            # Cap the fall speed to avoid excessively fast falling
            if self.velocity_y > MAX_FALL_VELOCITY:
                self.velocity_y = MAX_FALL_VELOCITY

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
                    self.velocity_y = 0  # Stop falling when on log
                    break

    def check_log_collisions(self, row_logs):
        """Check if logs on the same row collide with each other."""
        for i, log1 in enumerate(row_logs):
            for j, log2 in enumerate(row_logs):
                if i != j and self.check_collision(log1, log2):
                    return True
        return False

    def handle_log_collisions(self, row_logs):
        """Handle collisions between logs on the same row."""
        # Example: reverse speeds of logs that collide (or any other behavior)
        for i, log1 in enumerate(row_logs):
            for j, log2 in enumerate(row_logs):
                if i != j and self.check_collision(log1, log2):
                    self.log_speeds[self.get_log_row(log1)][i] = -self.log_speeds[self.get_log_row(log1)][i]

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

    def start_falling(self):
        """Start the knight's falling when the down arrow is pressed."""
        self.falling = True  # Flag the knight as falling


# Run the game
root = tk.Tk()
game = FrogJumpGame(root)
root.mainloop()
