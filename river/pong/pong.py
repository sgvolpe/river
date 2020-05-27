# pong!
import functools
import pygame
import random
import time
import datetime
import winsound

BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255,255,255)
# Coordinates p1, p2 and ball
x1 = 490
y1 = 250
x2 = 0
y2 = 250
xb = 300
yb = 300

dbo = 'left'
dbv = 'down'

start_time = time.perf_counter()
scorep1 = 0
scorep2 = 0
speed = 0

bar_size = 50
ball_size = 10

clock = pygame.time.Clock()
screen = pygame.display.set_mode((500, 500))
pygame.display.set_caption("My game" + "Score player 1: " + str(scorep1) + " - Score player 2: " + str(scorep2) + " Speed: " + str(speed))

pygame.init()


def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()  # 1
        value = func(*args, **kwargs)
        end_time = time.perf_counter()  # 2
        run_time = end_time - start_time  # 3
        to_write = f"{datetime.datetime.now()},{start_time},{end_time},{run_time:.4f} secs,{func.__name__!r}\n"
        log = open('log.log', 'a')
        log.write(to_write)
        log.close()
        print(f'{func.__name__}______________________No Error: {run_time}')
        return value
    try:
        return wrapper
    except Exception as e:
        raise Exception(f'Error on: {func.__name__} | {str(e)}')


def ball():
    "Draw the ball"
    global xb, yb
    pygame.draw.ellipse(screen, WHITE, (xb, yb, 10, 10))


def sprite1(x, y):
    "Draw Player 1"
    global bar_size
    pygame.draw.rect(screen, RED, (x, y, 10, bar_size))


def sprite2(x, y):
    "Draw Player 2"
    global bar_size
    pygame.draw.rect(screen, GREEN, (x, y, 10, bar_size))


def move_ball(x, y, speed=5):
    "The ball moves"
    global xb, yb, dbo, dbv, ball_size
    if dbv == 'down':
        yb += speed
        if yb >= 500 - ball_size:
            yb = 490
            dbv = 'up'
    if dbv == 'up':
        yb -= speed
        if yb <= 0:
            yb = 0
            dbv = 'down'

    if dbo == "left":
        xb -= speed
    if dbo == "right":
        xb += speed


def collision():
    global x1, y1  # the player 1 x and y (on the right)
    global x2, y2  # the player 2 x and y (on the left)
    global xb, yb  # the ball x and y
    global dbo
    global scorep1, scorep2, start_time, speed
    if dbo == "left":
        if xb <= 10:
            xb = 10
            if yb > y2 + bar_size or yb + 10 < y2:
                scorep2 += 10
                restart()
            else:
                dbo = "right"
                winsound.Beep(500, 100)


    else:
        if xb >= 480:
            if yb > y1 + bar_size or yb + 10 < y1:
                scorep1 += 10
                restart()
            else:
                dbo = "left"
                winsound.Beep(400, 100)


def restart():
    global xb, yb, start_time
    winsound.Beep(100, 50)
    winsound.Beep(300, 50)
    pygame.draw.ellipse(screen, BLACK, (xb, yb, 10, 10))
    pygame.display.update()
    xb, yb = 300, 300
    start_time = time.perf_counter()
    pygame.display.set_caption(
        "My game" + "Score player 1: " + str(scorep1) + " - Score player 2: " + str(scorep2) + " Speed: " + str(speed))


def computer_ai(func):
    """"""
    global y1, y2, xb, yb, dbo, dbv

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        global y1, y2, xb, yb, dbo, dbv, speed

        formula = yb - (bar_size / 2) + (ball_size / 2)
        if func.__name__ == 'move1':
            y1 = formula

        elif func.__name__ == 'move2':
            y2 = formula

        value = func(*args, **kwargs)
        return value
    return wrapper

#@timer
@computer_ai
def move1():
    pass

#@timer
@computer_ai
def move2():
    global y2
    if y2 <= 450:
        if keys[pygame.K_m]:
            y2 += 20
    if y2 > 0:
        if keys[pygame.K_k]:
            y2 -= 20


loop = 1
coords_log = open('coords_log.csv', 'a')
while loop:

    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            loop = 0

    current_time = time.perf_counter()

    speed = 10 + 10 * (current_time - start_time) / 10

    move_ball(xb, yb, speed=speed)
    ball()
    move1()
    move2()
    sprite2(x2, y2)
    sprite1(x1, y1)
    #time.sleep(0.3)
    collision()
    #coords_log.write(f'{x1, x2, xb, y1, y2, yb, speed, bar_size}\n')
    pygame.display.update()
    screen.fill((0, 0, 0))
    clock.tick(30)

    pygame.display.set_caption(
         str(scorep1) + " vs " + str(scorep2) + " Speed: " + str(int(speed)) + " Time: " + str(int(current_time - start_time)))


pygame.quit()
coords_log.close()