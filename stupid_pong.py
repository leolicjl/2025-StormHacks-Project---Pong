import pygame
import random
import sys
import requests
import math

from gimmick import *

pygame.init()

# Font that is used to render the text
font20 = pygame.font.Font('freesansbold.ttf', 20)
warningText = pygame.font.SysFont('freesansbold.ttf', 50, False, False)
ratingText = pygame.font.Font('freesansbold.ttf', 25)

# RGB values of standard colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0, 0)
PURPLE = (255, 0, 255, 255)
GOLD = (255, 183, 0)

# Evil RGB colors

EVIL_BLACK = (255, 255, 255)
EVIL_WHITE = (0, 0, 0)
EVIL_GREEN = (0, 0, 0)
EVIL_PURPLE = (255, 0, 255, 255)


# Text displays
warning = warningText.render("WARNING: Paddle Rotation Activated!", True, PURPLE)

# Constant game control variables
NEWGIMMICK = 0.6
orientation = True

# Basic parameters of the screen
WIDTH, HEIGHT = 1200, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SRCALPHA)
pygame.display.set_caption("Pong")

clock = pygame.time.Clock()
FPS = 60

# Gimmick Array
gimmicks = []
# texts
textShowing = []

sparksList = []

# Rhythm game ratings
ratings = ["You Suck","Good","Great!","Wow!", "Perfect!"]
ratingsOnScreen = []
parry_start = 0
parry_active = False

ballBuffer = 0

evil_mode = False
evil_active_time = 0

#keybind lists
key_list_player_1 = [
    pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d
 ]

key_list_player_2 = [
    pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT
]

# Striker class
class Player:

    parrying = False
    super_saiyan = False
    ss_active_time = 0
    
        # Take the initial position, dimensions, speed and color of the object
    def __init__(self, posx, posy, width, height, speed, color):

        self.mult = 1

        self.posx = posx
        self.posy = posy
        self.width = width
        self.height = height*self.mult

        self.default_width = width
        self.default_height = height*self.mult
        self.horiz_width = height*self.mult
        self.horiz_height = width

        self.speed = speed
        self.color = color
        self.parry_color = WHITE
        # Rect that is used to control the position and collision of the object
        self.geekRect = pygame.Rect(posx, posy, width, height)
        # Object that is blit on the screen
        if self.parrying:
            self.geek = pygame.draw.rect(screen, self.parry_color, self.geekRect)
        else:
            self.geek = pygame.draw.rect(screen, self.color, self.geekRect)

    # Used to display the object on the screen
    def refresh_colors(self):
        self.parry_color = WHITE
        self.color = GREEN
        if self.super_saiyan:
            self.color = GOLD
        
    def display(self):
        if self.parrying:
            self.geek = pygame.draw.rect(screen, self.parry_color, self.geekRect)
        else:
            self.geek = pygame.draw.rect(screen, self.color, self.geekRect)

    def update(self, fac):
        if self.super_saiyan:
            if pygame.time.get_ticks()-self.ss_active_time > 30000:
                self.mult = 1
                self.super_saiyan = False
                self.refresh_colors()

        if not controlType == 1:
            self.posy = self.posy + self.speed*fac

            # Restricting the striker to be below the top surface of the screen
            if self.posy <= 0:
                self.posy = 0
            # Restricting the striker to be above the bottom surface of the screen
            elif self.posy + self.height >= HEIGHT:
                self.posy = HEIGHT-self.height
        
        elif controlType == 1:
            self.posx = self.posx + self.speed*fac
            
            # Restricting the striker from the left edge of the screen
            if self.posx <= 0:
                self.posx = 0
            # Restricting the striker until the right edge of the screen
            elif self.posx + self.width >= WIDTH:
                self.posx = WIDTH-self.width

            # Updating the rect with the new values
        self.geekRect = pygame.Rect(self.posx, self.posy, self.width, self.height*self.mult)

    def displayScore(self, text, score, x, y, color):
        text = font20.render(text+str(score), True, color)
        textRect = text.get_rect()
        textRect.center = (x, y)

        screen.blit(text, textRect)

    def getRect(self):
        return self.geekRect
    
    def changeVertical(self):
        # temp = self.width
        self.width = self.default_width
        self.height = self.default_height
    
    def changeHorizontal(self):
        # temp = self.width
        self.width = self.horiz_width*self.mult
        self.height = self.horiz_height
        
    def verticalOrientation(self, startX, startY):
        self.posx = startX
        self.posy = startY
        
    def horizontalOrientation(self, startX, startY):
        self.posx = startX
        self.posy = startY
        
ball_trail = []

# Ball class
class Ball:

    can_hit = True
    last_hit = None

    def __init__(self, posx, posy, radius, speed, color):
        self.posx = posx
        self.posy = posy
        self.radius = radius
        self.speed = speed
        self.intangible = 0

        # CT 5 exclusive
        self.yspeed = -5

        self.color = color
        self.xFac = 1
        self.yFac = -1
        self.ball = pygame.draw.circle(
            screen, self.color, (self.posx, self.posy), self.radius)
        self.firstTime = 1


    def refresh_colors(self):
        self.color = WHITE

    def display(self):
        self.ball = pygame.draw.circle(
            screen, self.color, (self.posx, self.posy), self.radius)
        ball_trail.append((self.posx, self.posy))
        if len(ball_trail) > 5:
            ball_trail.pop(0)
        for i, (x, y) in enumerate(ball_trail):
            alpha = 120 * (i / len(ball_trail))
            trail_color = (*self.color[:3], int(alpha))
            pygame.draw.circle(screen, trail_color, (int(x), int(y)), self.radius)
        pygame.draw.circle(screen, self.color, (self.posx, self.posy), self.radius)

    def update(self):
        global controlType
        
        if self.intangible > 0:
            self.intangible -=1
        if not self.last_hit == None:
            if pygame.time.get_ticks() - self.last_hit > 500:
                self.can_hit = True

        # ball but gravity???
        if controlType == 5:
            self.posx += self.speed * self.xFac # move sideways

            # Apply vertical motion
            self.posy += self.yspeed
            self.yspeed += 0.1  # gravity

            # Clamp to floor
            if self.posy >= HEIGHT - self.radius:
                self.posy = HEIGHT - self.radius
                self.yspeed = 0 

        # Business as usual
        else:
            self.posx += self.speed*self.xFac
            self.posy += self.speed*self.yFac
           
            # If the ball hits the top or bottom surfaces, 
            # then the sign of yFac is changed and 
            # it results in a reflection
        if not controlType == 1:
            if self.posy < 0 or self.posy >= HEIGHT:
                self.yFac *= -1

            if self.posx <= 0 and self.firstTime:
                self.firstTime = 0
                return 1
            elif self.posx >= WIDTH and self.firstTime:
                self.firstTime = 0
                return -1
            else:
                return 0
        
        # If the ball hits the left or right edges,
        elif controlType == 1:
            if self.posx <= 0 or self.posx >= WIDTH:
                self.xFac *= -1

            if self.posy <= 0 and self.firstTime:
                self.firstTime = 0
                return 1
            elif self.posy >= HEIGHT and self.firstTime:
                self.firstTime = 0
                return -1
            else:
                return 0

    def reset(self):
        global parry_active
        self.posx = WIDTH//2
        self.posy = HEIGHT//2
        self.xFac *= -1
        self.firstTime = 1
        parry_active = False
        leftPlayer.parrying = False
        rightPlayer.parrying = False

        if controlType == 5:
            self.yspeed = -4

    # Used to reflect the ball along the X-axis
    def hit(self):
        global parry_active, rightMeter, leftMeter  # 🔥 Add this line
        
        if not self.intangible > 0:
            if not controlType == 1:
                self.xFac *= -1
                
            elif controlType == 1:
                self.yFac *= -1
            
            self.intangible = 20

        
        
        
            
        score = 0
        if parry_active:
            delay = pygame.time.get_ticks() - parry_start
            if delay >= 1000:
                score = 0
                self.speed *= 0.8
                pygame.mixer.music.load("rage.mp3")
                pygame.mixer.music.play()
            elif delay < 50:
                score = 4
                self.speed *= 1.3
                pygame.mixer.music.load("parry.wav")
                pygame.mixer.music.play()
                newSpark = Spark(self.posx, self.posy)
                newSpark.clash(sparksList, self.posx, self.posy)
                activate_evil_mode()

            elif delay < 150:
                score = 3
                self.speed *= 1.1
                pygame.mixer.music.load("parry.wav")
                pygame.mixer.music.play()
                newSpark = Spark(self.posx, self.posy)
                newSpark.clash(sparksList, self.posx, self.posy, 20)
                #activate_evil_mode()
            elif delay < 300:
                score = 2
                pygame.mixer.music.load("block.wav")
                pygame.mixer.music.play()
                newSpark = Spark(self.posx, self.posy)
                newSpark.clash(sparksList, self.posx, self.posy, 10)
            elif delay < 600:
                score = 1
                self.speed *= 0.95
                pygame.mixer.music.load("block.wav")
                pygame.mixer.music.play()

        if len(ratingsOnScreen) == 0:
            # randRating = random.randint(0,len(ratings)-1)
            onRight = False
            if self.xFac < 0:
                onRight = True

            if onRight:
                rightMeter.increase(1)
            else:
                leftMeter.increase(1)
            if score > 2:
                if onRight:
                    rightMeter.increase(1)
                else:
                    leftMeter.increase(1)
            ratingsOnScreen.append(Rating(score,not onRight, self.posy))
            ball.yspeed -= 8+ score//2
        parry_active = False
        leftPlayer.parrying = False
        rightPlayer.parrying = False

    def getRect(self):
        return pygame.Rect(
            self.posx - self.radius,
            self.posy - self.radius,
            self.radius * 2,
            self.radius * 2)
        #return self.ball
    
class Meter:
    def __init__(self,side,x,y):
        self.maxVal = 10
        self.val = 0
        self.width = 10
        # self.height = HEIGHT*(self.val/self.maxVal)
        self.side = side
        self.x = x
        self.y = y

        self.meterRect = pygame.Rect(self.x-self.width//2, self.y-(HEIGHT*(self.val/self.maxVal))//2, self.width, HEIGHT*(self.val/self.maxVal))
        self.meterBar = pygame.draw.rect(screen, GOLD, self.meterRect)

    def increase(self, inc):
        self.val+=inc
        print(self.side+"increased")
        if self.val >= self.maxVal:
            self.val = 0
            if self.side == 'left':
                leftPlayer.super_saiyan = True
                leftPlayer.ss_active_time = pygame.time.get_ticks()
                leftPlayer.mult = 2
                leftPlayer.refresh_colors()
                pygame.mixer.music.load("power.mp3")
                pygame.mixer.music.play()
            elif self.side == 'right':
                rightPlayer.super_saiyan = True
                rightPlayer.ss_active_time = pygame.time.get_ticks()
                rightPlayer.mult = 2
                rightPlayer.refresh_colors()
                pygame.mixer.music.load("power.mp3")
                pygame.mixer.music.play()
            else:
                print('that doesnt seem right')

    def update(self):
        self.meterBar = pygame.draw.rect(screen, GOLD, self.meterRect)
        self.meterRect = pygame.Rect(self.x-self.width//2, self.y-(HEIGHT*(self.val/self.maxVal))//2, self.width, HEIGHT*(self.val/self.maxVal))

class Rating:
    score = 0
    start_time = 0
    onRight = False
    y = 0
    toShow = None
    def __init__(self,score, onRight, y):
        self.score = score
        self.onRight = onRight
        self.y = y
        self.toShow = ratingText.render(ratings[score],True,WHITE)
        self.start_time = pygame.time.get_ticks()
    def update(self):
        self.y-=0.5

# Spark class
class Spark:
    def __init__(self, posx, posy):
        self.posx = posx
        self.posy = posy
        self.speed = 10 - random.randrange(0, 5)
        self.velx = self.speed * math.cos(random.random()*20) * random.randrange(1, 3)
        self.vely = self.speed * math.sin(random.random()*20) * random.randrange(1, 3)
        self.life = 30
        self.color = (random.randrange(150, 255), random.randrange(100, 180), 0)
        self.radius = 10
        self.spark = pygame.draw.circle(
            screen, self.color, (self.posx, self.posy), self.radius)
    
    def clash(self, sparksList, posx, posy, count=40):
        for i in range(0, count):
            newSpark = Spark(posx, posy)
            sparksList.append(newSpark)
    
    def update(self):
        self.posx = self.posx + self.velx
        self.posy = self.posy + self.vely
        self.life += -1
        self.velx = self.velx * 0.95
        self.vely = self.vely * 0.95
        self.radius = self.radius * 0.9
        if self.life < 1:
            del self
    
    def display(self):
        if evil_mode:
            self.spark = pygame.draw.circle(screen, (0, 0, 0), (self.posx, self.posy), self.radius)
        else:
            self.spark = pygame.draw.circle(screen, self.color, (self.posx, self.posy), self.radius)


#keybind randomizers for player1 & player2 (Leo)
def randomizer_player1():
    up_key, down_key = random.sample(key_list_player_1, 2)
    return up_key, down_key

def randomizer_player2():
    up_key, down_key = random.sample(key_list_player_2, 2)
    return up_key, down_key
    
# Adds Gimmick to the list
def safeGimmickInsert(obj):
    # Check if an object of the same class already exists
    if not any(isinstance(item, obj.__class__) for item in gimmicks):
        gimmicks.append(obj)
        return True
    else:
        print(f"An instance of {obj.__class__.__name__} already exists!")
        return False

# Randomly selects a gimmick to change the gameplay too
def addGimmick():
    global controlType
    # print("test")

    # random gimmick time
    
    added = False

    while not added:
        global controlType, player1_up, player1_down, player2_up, player2_down
        success = False
        randPick = random.randint(0, 5)
        removeAllGimmicks()
        #Initial player keybinds (Leo)
        player1_up = pygame.K_w
        player1_down = pygame.K_s
        player2_up = pygame.K_UP
        player2_down = pygame.K_DOWN
        
        if not controlType == randPick:
            
            #reset_players(leftPlayer, rightPlayer)
            match randPick:
                case 0:
                    # if not controlType == 0:
                    controlType = 0
                    default = NoGimmick(leftPlayer, rightPlayer)
                    success = safeGimmickInsert(default)
                case 1:
                    #print("gimmick 1")
                    # if not controlType == 1:
                    controlType = 1
                    rotation = RotatePaddle(leftPlayer, rightPlayer)
                    success = safeGimmickInsert(rotation)
                case 2:
                    controlType = 2
                    reset_players(leftPlayer, rightPlayer)
                    gim = Bounce()
                    success = safeGimmickInsert(gim)
                case 3:
                    controlType = 3
                    reset_players(leftPlayer, rightPlayer)
                    gim = Charge()
                    success = safeGimmickInsert(gim)
                case 4:
                    controlType = 4
                    reset_players(leftPlayer, rightPlayer)
                    gim = Keybind()
                    success = safeGimmickInsert(gim)
                case 5:
                    controlType = 5
                    reset_players(leftPlayer, rightPlayer)
                    gim = Baseball()
                    success = safeGimmickInsert(gim)
            if success:
                added = True

def removeGimmick(n):
    print("remove gimmick")
    gimmicks[n].deactivate()
    del gimmicks[n]

def removeAllGimmicks():
    print("removing all gimmicks")
    # for i in gimmicks:
    #     i.deactivate()
    gimmicks.clear()

# "Parry"
def parry(side):
    global parry_active, parry_start  # 🔥 Add this line
    if not parry_active:
        print("parry")
        parry_start = pygame.time.get_ticks()
        parry_active = True
        if side == "left":
            leftPlayer.parrying = True
        elif side == "right":
            rightPlayer.parrying = True
        else:
            print("bruh")

def activate_evil_mode():
    global evil_mode, BLACK, WHITE, GREEN, PURPLE
    if not evil_mode:
        print("Evil Mode Activated")
        global evil_active_time
        evil_active_time = pygame.time.get_ticks()
        evil_mode = True
        BLACK = EVIL_BLACK
        WHITE = EVIL_WHITE
        GREEN = EVIL_GREEN
        PURPLE = EVIL_PURPLE
    else:
        print("Evil Mode Deactivated")
        evil_mode = False
        BLACK = (0, 0, 0)
        WHITE = (255, 255, 255)
        GREEN = (0, 255, 0, 0)
        PURPLE = (255, 0, 255, 255)
    leftPlayer.refresh_colors()
    rightPlayer.refresh_colors()
    ball.refresh_colors()

    
# Game Manager
def main():
    global newGimmick, leftPlayer, rightPlayer, controlType, ballBuffer, bufferTimer, ball, leftMeter, rightMeter, player1_down, player1_up, player2_down, player2_up

    # Initialize the mixer
    pygame.mixer.init()
    running = True
    
    # URL for block sfx
    blockUrl = "https://drive.google.com/uc?export=download&id=1MOFpDRil_gZ-uHtXUUGgZrbDSd-1Iqg_"
    response = requests.get(blockUrl)
    
    # Installs block sfx
    if response.status_code == 200:
        with open("block.wav", "wb") as file:
            file.write(response.content)

    # URL for parry sfx
    parryUrl = "https://drive.google.com/uc?export=download&id=1tl3ay4KjrsnmgPdxjpx7auWDIa5vm-TG"
    response = requests.get(parryUrl)
    
    # Installs parry sfx
    if response.status_code == 200:
        with open("parry.wav", "wb") as file:
            file.write(response.content)

    # Installs rage sfx
    rageUrl = "https://drive.google.com/uc?export=download&id=1v8Q5F5RQ6XOPJLsmiwO6cGpV0h20tKfE"
    response = requests.get(rageUrl)
    if response.status_code == 200:
        with open("rage.mp3", "wb") as file:
            file.write(response.content)

    cheerUrl = "https://drive.google.com/uc?export=download&id=1RRxg6eLAsB_zNAat5qGeTdLy9uRSWXGW"
    response = requests.get(cheerUrl)
    if response.status_code == 200:
        with open("cheer.wav", "wb") as file:
            file.write(response.content)

    powerUrl = "https://drive.google.com/uc?export=download&id=1W8P-5CyuykmWgHD2ZoRw1Ovj_3NLW95U"
    response = requests.get(powerUrl)
    if response.status_code == 200:
        with open("power.mp3", "wb") as file:
            file.write(response.content)

    # 0 = Regular, 1 = Rotate, 2 = Flappy, 3 = Charging, 4 = Keybind
    controlType = 0

    # Defining the objects
    leftPlayer = Player(20, 0, 10, 100, 10, GREEN)
    rightPlayer = Player(WIDTH-30, 0, 10, 100, 10, GREEN)
    ball = Ball(WIDTH//2, HEIGHT//2, 7, 7, WHITE)
    newGimmick = 0

    leftMeter = Meter('left',0,HEIGHT//2)
    rightMeter = Meter('right',WIDTH,HEIGHT//2)
    
    listOfPlayers = [leftPlayer, rightPlayer]
    leftPlayer.verticalOrientation(20, HEIGHT//2-50)
    rightPlayer.verticalOrientation(WIDTH-30, HEIGHT//2-50)
    # rotationTest = RotatePaddle(leftPlayer, rightPlayer)

    # Initial parameters of the players
    leftPlayerScore, rightPlayerScore, totalScore = 0, 0, 0
    leftPlayerYFac, leftPlayerXFac, rightPlayerYFac, rightPlayerXFac = 0, 0, 0, 0
    # Power = strength of player's stored jump, Release = true/false for jumping state
    leftPlayerPower, rightPlayerPower, leftPlayerRelease, rightPlayerRelease = 0, 0, 0, 0
    leftPlayerHolding, rightPlayerHolding = 0, 0

    #Initial player keybinds (Leo)
    player1_up, player1_down = pygame.K_w, pygame.K_s
    player2_up, player2_down = pygame.K_UP, pygame.K_DOWN
    #leftPlayerRelease, rightPlayerRelease = 0, 0, 0, 0
    #leftPlayerHolding, rightPlayerHolding = 0, 0

    #Initialize keybind messgages (Leo)
    keybind_font = pygame.font.SysFont('freesansbold.ttf', 50, False, False)
    keybind_message = ""
    keybind_start_time = 0
    
    while running:
        screen.fill(BLACK)
        
        if evil_mode:
            if pygame.time.get_ticks() - evil_active_time > 1000:
                activate_evil_mode()
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LSHIFT:
                    parry("left")
                if event.key == pygame.K_RSHIFT:
                    parry("right")
            # Control type 0 is default pong controls
            if controlType == 0 or controlType == 5:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        rightPlayerYFac = -1
                            
                    if event.key == pygame.K_DOWN:
                        rightPlayerYFac = 1
                            
                    if event.key == pygame.K_w:
                        leftPlayerYFac = -1
                            
                    if event.key == pygame.K_s:
                        leftPlayerYFac = 1
                        
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                        rightPlayerYFac = 0

                    if event.key == pygame.K_w or event.key == pygame.K_s:
                        leftPlayerYFac = 0
                            
            # Control type 1 is changes positions to be top and bottom
            elif controlType == 1:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        rightPlayerXFac = -1
                            
                    if event.key == pygame.K_DOWN:
                        rightPlayerXFac = 1
                            
                    if event.key == pygame.K_w:
                        leftPlayerXFac = -1
                            
                    if event.key == pygame.K_s:
                        leftPlayerXFac = 1
                        
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                        rightPlayerXFac = 0

                    if event.key == pygame.K_w or event.key == pygame.K_s:
                        leftPlayerXFac = 0
                            
            # Type 2 turns paddles into flappy birds
            elif controlType == 2:
                # print("c2 active")
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        rightPlayerPower += 1.5
                    if event.key == pygame.K_w:
                        leftPlayerPower += 1.5
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                        rightPlayerRelease = 1
                    if event.key == pygame.K_w or event.key == pygame.K_s:
                        leftPlayerRelease = 1

            # Type 3 turns paddles into springy thingies
            elif controlType == 3:
                # print("c2 active")
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        rightPlayerHolding = 1
                        print("Holding")
                    if event.key == pygame.K_w:
                        leftPlayerHolding = 1
                        
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP:
                        rightPlayerRelease = 1
                        rightPlayerHolding = 0
                    if event.key == pygame.K_w:
                        leftPlayerRelease = 1
                        leftPlayerHolding = 0
            
            # Type 4 randomizes keybinds per paddle hit
            elif controlType == 4:
                if event.type == pygame.KEYDOWN:
                    if event.key == player2_up:
                        rightPlayerYFac = -1
                    if event.key == player2_down:
                        rightPlayerYFac = 1
                    if event.key == player1_up:
                        leftPlayerYFac = -1
                    if event.key == player1_down:
                        leftPlayerYFac = 1
                if event.type == pygame.KEYUP:
                    if event.key in (player2_up, player2_down):
                        rightPlayerYFac = 0
                    if event.key in (player1_up, player1_down):
                        leftPlayerYFac = 0
                        
        # Collision detection
        for players in listOfPlayers:
            if pygame.Rect.colliderect(ball.getRect(), players.getRect()):
                ball.hit()

        # Makes paddles 'jump' if the player releases the jump key
        if controlType == 2 or controlType == 3:
            if rightPlayerRelease:
                rightPlayerYFac = rightPlayerPower*(-1)
                rightPlayerRelease, rightPlayerPower = 0, 0
            if leftPlayerRelease:
                leftPlayerYFac = leftPlayerPower*(-1)
                leftPlayerRelease, leftPlayerPower = 0, 0

        
        # Gravity
        if controlType == 2:
            rightPlayerYFac += 0.1
            leftPlayerYFac += 0.1
        
        # Gravity
        if controlType == 3:
            rightPlayerYFac += 0.07
            leftPlayerYFac += 0.07
            
            # Charging the jump
            if rightPlayerHolding == 1:
                rightPlayerPower += 0.09
            if leftPlayerHolding == 1:
                leftPlayerPower += 0.09
            # Limiting the maximum power
            if leftPlayerPower > 3:
                leftPlayerPower = 3
            if rightPlayerPower > 3:
                rightPlayerPower = 3
        
            
        # Updating the objects
        if controlType in (0, 2, 3, 4, 5):
            leftPlayer.update(leftPlayerYFac)
            rightPlayer.update(rightPlayerYFac)
            
        elif controlType == 1:
            leftPlayer.update(leftPlayerXFac)
            rightPlayer.update(rightPlayerXFac)
            
        leftMeter.update()
        rightMeter.update()
        point = ball.update()
        ballBuffer -= 1
        
        if ballBuffer > 0:
            ball.speed = 7
            ball.reset()
    
        #print(leftPlayer.posy)

        # -1 -> Geek_1 has scored
        # +1 -> Geek_2 has scored
        #  0 -> None of them scored
        if point == -1:
            leftPlayerScore += 1
            totalScore += 1
            if controlType == 4:
                player2_up, player2_down = randomizer_player2()
                keybind_message = "Player 2 new keys: {} / {}" .format(pygame.key.name(player2_up), pygame.key.name(player2_down))
        elif point == 1:
            rightPlayerScore += 1
            totalScore += 1
            if controlType == 4:
                player1_up, player1_down = randomizer_player1()
                keybind_message = "Player 1 new keys: {} / {}" .format(pygame.key.name(player1_up), pygame.key.name(player1_down))

        # Someone has scored, so add a point to the winner and reset the ball position
        # Each time a point is scored, there is a 20% chance that a new gimmick will be added
        if point:
        
            if controlType == 4:
                
                keybind_start_time = pygame.time.get_ticks()
                print(keybind_message) #for debugging   

                ball.reset()
                
            ballBuffer = 130
            print(ballBuffer)
                
            newGimmick = random.random()
            print(newGimmick)
            if newGimmick < NEWGIMMICK:
                addGimmick()

        #temporarily display keybinds (Leo)
        if keybind_message:
            elapsed = pygame.time.get_ticks() - keybind_start_time
            if elapsed < 2000:
                keybind_surface = keybind_font.render(keybind_message, True, WHITE)
                screen.blit(keybind_surface, (WIDTH//2 - keybind_surface.get_width() //
                        2, HEIGHT*0.9 - keybind_surface.get_height()//2))
        else: 
            keybind_message = ""
               
            #print(totalScore)
            
        # Displaying the objects on the screen
        leftPlayer.display()
        rightPlayer.display()
        ball.display()

        for spark in sparksList:
            spark.update()
            spark.display()
        
    
        # screen.blit(warning, (WIDTH//2 - warning.get_width() //
        #                      2, HEIGHT*0.1 - warning.get_height()//2))

        for i in gimmicks:
            if pygame.time.get_ticks() - i.start_time < 3000:
                screen.blit(i.nameShow, (WIDTH//2 - i.nameShow.get_width() //
                                2, HEIGHT*0.1 - i.nameShow.get_height()//2))
        
        # Show the ratings that are on the screen
        for i in ratingsOnScreen:
            if pygame.time.get_ticks() - i.start_time < 1000:
                wid = WIDTH*0.9 - i.toShow.get_width()//2
                if i.onRight:
                    wid = WIDTH*0.1 - i.toShow.get_width()//2
                    

                screen.blit(i.toShow,(wid, i.y))
                i.update()
            else:
                ratingsOnScreen.clear()
                del i
                
        # Displaying the scores of the players
        leftPlayer.displayScore("Player 1 : ",
                           leftPlayerScore, 100, 20, WHITE)
        rightPlayer.displayScore("Player 2 : ", 
                           rightPlayerScore, WIDTH-100, 20, WHITE)
        for i in textShowing:
            textShowing[i].draw()

        pygame.display.update()
        if evil_mode:
            pygame.time.delay(100)
        clock.tick(FPS)   


if __name__ == "__main__":
    main()
    pygame.quit()
    sys.exit()
