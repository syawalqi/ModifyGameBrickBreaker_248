import tkinter as tk
import random


class GameObject(object):
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)


class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.radius = 10
        self.direction = [1, -1]  # Horizontal and vertical direction
        self.speed = 5
        self.color_cycle = ['white', 'red', 'blue', 'green', 'yellow']
        self.current_color = 0
        item = canvas.create_oval(x - self.radius, y - self.radius,
                                  x + self.radius, y + self.radius,
                                  fill=self.color_cycle[self.current_color])
        super(Ball, self).__init__(canvas, item)
        self.change_color()

    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        if coords[1] <= 0:
            self.direction[1] *= -1
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)

    def collide(self, game_objects):
        coords = self.get_position()
        x = (coords[0] + coords[2]) * 0.5
        if len(game_objects) > 1:
            self.direction[1] *= -1
        elif len(game_objects) == 1:
            game_object = game_objects[0]
            game_coords = game_object.get_position()

            if isinstance(game_object, Paddle):
                if coords[3] >= game_coords[1] and coords[1] <= game_coords[3]:
                    if self.direction[1] > 0 and coords[3] <= game_coords[1]:
                        self.randomize_trajectory(game_object)
                        game_object.change_color('blue')

            if x > game_coords[2]:
                self.direction[0] = 1
            elif x < game_coords[0]:
                self.direction[0] = -1
            else:
                self.direction[1] *= -1

        for game_object in game_objects:
            if isinstance(game_object, Brick):
                game_object.hit()

    def randomize_trajectory(self, paddle):
        """Randomize the ball's trajectory when it hits the paddle."""
        angle_variation = random.uniform(-0.5, 0.5)
        self.direction[1] *= -1
        self.direction[0] += angle_variation
        direction_magnitude = (self.direction[0]**2 + self.direction[1]**2)**0.5
        self.direction[0] /= direction_magnitude
        self.direction[1] /= direction_magnitude

    def change_color(self):
        """Change the ball's color to the next one in the cycle."""
        self.current_color = (self.current_color + 1) % len(self.color_cycle)
        self.canvas.itemconfig(self.item, fill=self.color_cycle[self.current_color])
        self.canvas.after(1500, self.change_color)


class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 80
        self.height = 10
        self.ball = None
        self.color_cycle = ['#FFB643', '#FF6347', '#FFD700', '#ADFF2F', '#32CD32', '#FF1493']  # List of colors
        self.current_color = 0  # Start with the first color in the cycle
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill=self.color_cycle[self.current_color])
        super(Paddle, self).__init__(canvas, item)

        # Start the color change loop
        self.change_color()

    def set_ball(self, ball):
        self.ball = ball

    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super(Paddle, self).move(offset, 0)
            if self.ball is not None:
                self.ball.move(offset, 0)

    def change_color(self):
        """Change the paddle's color to the next one in the cycle."""
        self.current_color = (self.current_color + 1) % len(self.color_cycle)
        self.canvas.itemconfig(self.item, fill=self.color_cycle[self.current_color])
        # Call this method again after 1000ms (1 second)
        self.canvas.after(1000, self.change_color)


class Brick(GameObject):
    COLOR_CYCLE = ['#4535AA', '#ED639E', '#8FE1A2', '#FF6347', '#FFD700', '#ADFF2F', '#FF1493', '#00FA9A']  # List of colors

    def __init__(self, canvas, x, y, hits, game):
        self.width = 75
        self.height = 20
        self.hits = hits
        self.current_color = random.choice(Brick.COLOR_CYCLE)
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill=self.current_color, tags='brick')
        super(Brick, self).__init__(canvas, item)
        self.game = game  # Store the reference to the Game object

    def hit(self):
        self.hits -= 1
        if self.hits <= 0:
            self.canvas.delete(self.item)
            self.game.update_score(10)  # Now we call update_score directly from self.game

    def change_color(self):
        """Change this brick's color to the next random color from the cycle."""
        self.current_color = random.choice(Brick.COLOR_CYCLE)  # Select a new random color
        self.canvas.itemconfig(self.item, fill=self.current_color)
        # Call this method again after 2 seconds to change the color
        self.canvas.after(2000, self.change_color)  # 2000ms = 2 seconds

class Menu:
    def __init__(self, master, game):
        self.master = master
        self.game = game
        
        # Create a menu frame that fills the entire window
        self.menu_frame = tk.Frame(self.master, width=610, height=400, bg='#D6D1F5')
        self.menu_frame.pack(fill="both", expand=True)  # Fill the entire window
        
        self.create_menu()

    def create_menu(self):
        # Create menu content like title and start text
        self.canvas = tk.Canvas(self.menu_frame, bg='#D6D1F5', width=610, height=400)
        self.canvas.pack(fill="both", expand=True)

        self.canvas.create_text(305, 50, text="Welcome to Breakout!", font=('Forte', 30))

        # Display Start Game text
        self.start_text = self.canvas.create_text(305, 200, text=" Start Game", font=('Forte', 20, 'bold'), fill='blue')
        self.exit_text = self.canvas.create_text(305, 250, text=" Exit Game", font=('Forte', 20, 'bold'), fill='red')

        # Bind mouse click on the text to start the game
        self.canvas.tag_bind(self.start_text, "<Button-1>", self.start_game)
        self.canvas.tag_bind(self.exit_text, "<Button-1>", self.exit_game)

    def start_game(self, event=None):
        # Hide the menu
        self.menu_frame.pack_forget()  # Hide the menu frame

        # Now start the game
        self.game.pack()  # Show the game screen
        self.game.start_game()  # Start the game loop
        self.game.canvas.focus_set()

    def exit_game(self, event=None):
        self.master.quit()  # Close the application


class Game(tk.Frame):
    def __init__(self, master):
        super(Game, self).__init__(master)
        self.lives = 9999
        self.width = 610
        self.height = 400
        self.canvas = tk.Canvas(self, bg='#D6D1F5',
                                width=self.width,
                                height=self.height, )
        self.canvas.pack()
        self.pack_forget()

        self.items = {}
        self.ball = None
        self.paddle = Paddle(self.canvas, self.width / 2, 326)
        self.items[self.paddle.item] = self.paddle
        for x in range(5, self.width - 5, 75):
            self.add_brick(x + 37.5, 50, 3)
            self.add_brick(x + 37.5, 70, 2)
            self.add_brick(x + 37.5, 90, 1)

        self.hud = None
        self.score_hud = None
        self.score = 0
        self.setup_game()
        self.canvas.focus_set()
        self.canvas.bind('<Left>', lambda _: self.paddle.move(-20))
        self.canvas.bind('<Right>', lambda _: self.paddle.move(20))

    def setup_game(self):
        self.add_ball()
        self.update_lives_text()
        self.update_score_text()  # Display the score
        self.text = self.draw_text(300, 200, 'Press Space to start')
        self.canvas.bind('<space>', lambda _: self.start_game())

    def add_ball(self):
        if self.ball is not None:
            self.ball.delete()
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        self.ball = Ball(self.canvas, x, 310)
        self.paddle.set_ball(self.ball)

    def add_brick(self, x, y, hits):
        # Pass self (the Game object) as the last argument to the Brick constructor
        brick = Brick(self.canvas, x, y, hits, self)
        self.items[brick.item] = brick
        brick.change_color()

    def draw_text(self, x, y, text, size='40'):
        font = ('Forte', size)
        return self.canvas.create_text(x, y, text=text, font=font)

    def update_lives_text(self):
        text = 'Lives: %s' % self.lives
        if self.hud is None:
            self.hud = self.draw_text(50, 20, text, 15)
        else:
            self.canvas.itemconfig(self.hud, text=text)

    def update_score_text(self):
        """Display the current score on the screen."""
        text = 'Score: %s' % self.score
        if self.score_hud is None:
            self.score_hud = self.draw_text(self.width - 100, 20, text, 15)
        else:
            self.canvas.itemconfig(self.score_hud, text=text)

    def start_game(self):
        self.canvas.unbind('<space>')
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.game_loop()

    def game_loop(self):
        self.check_collisions()
        num_bricks = len(self.canvas.find_withtag('brick'))
        if num_bricks == 0:
            self.ball.speed = None
            self.draw_text(300, 200, 'You win! You the Breaker of Bricks.')
        elif self.ball.get_position()[3] >= self.height:
            self.lives -= 1
            if self.lives == 0:
                self.draw_text(300, 200, 'You lost! Game over!')
            else:
                self.setup_game()
        else:
            self.ball.update()
            self.after(24, self.game_loop)

    def check_collisions(self):
        ball_coords = self.ball.get_position()
        items = self.canvas.find_overlapping(*ball_coords)
        objects = [self.items[x] for x in items if x in self.items]
        self.ball.collide(objects)

    def update_score(self, points):
        """Update the score when a brick is hit."""
        self.score += points
        self.update_score_text()


if __name__ == '__main__':
    root = tk.Tk()
    root.title("Breakout Game")
    
    # Create the game instance, but don't start it yet
    game = Game(root)
    
    # Create the menu page in the same root window
    menu = Menu(root, game)
    
    # Start the Tkinter main loop
    root.mainloop()
