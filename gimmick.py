# __all__ = ['Gimmick', 'RotatePaddle']
from stupid_pong import *

def reset_players(leftPlayer, rightPlayer):
    print("resetting")
    leftPlayer.changeVertical()
    rightPlayer.changeVertical()
    leftPlayer.verticalOrientation(20, 0)
    rightPlayer.verticalOrientation(WIDTH-40, 0)

class Gimmick:

    name = "Gimmick"
    nameShow = None
    start_time = None

    # type is used to check gimmick compatibility
    def __init__(self, name, type="play"):
        self.type = type
        self.name = name
        print("activate gimmick")
        self.nameShow = warningText.render(name + " Activated", True, WHITE)
        self.start_time = pygame.time.get_ticks()
        
    def update(self):
        pass
    # def activate(self):
    #     print("activate gimmick")
    def deactivate(self):
        print("deactivate gimmick")


# Changes controls to use webcam for up & down
class CamControl(Gimmick):
    def __init__(self, type="control"):
        super().__init__(self, "Camera", type=type)
        
    def activate(self):
        pass
    


class NoGimmick(Gimmick):
    plr1 = None
    plr2 = None
    
    def __init__(self, p1, p2):
        super().__init__("Normal Pong")
        self.plr1 = p1
        self.plr2 = p2
        self.activate()
        
    def activate(self):
        reset_players(self.plr1, self.plr2)
    
# Moves paddles to be moving left to right and changing their positions to the top and bottom
class RotatePaddle(Gimmick):
    global orientation

    plr1 = None
    plr2 = None

    def __init__(self, p1, p2):
        super().__init__("Paddle Rotation")
        self.plr1 = p1
        self.plr2 = p2
        self.activate()

    def activate(self):
        self.plr1.changeHorizontal()
        self.plr2.changeHorizontal()
        self.plr1.horizontalOrientation((WIDTH - self.plr1.width)//2 , HEIGHT - self.plr1.height - 20)
        self.plr2.horizontalOrientation((WIDTH - self.plr1.width)//2 , self.plr1.height + 15)
        
    # def activate(self, p1, p2):
    #     pass
    def deactivate(self):
        reset_players(self.plr1, self.plr2)
        # self.plr1.changeVertical()
        # self.plr2.changeVertical()
        # self.plr1.verticalOrientation(20, 0)
        # self.plr2.verticalOrientation(WIDTH-40, 0)

class Charge(Gimmick):
    def __init__(self):
        super().__init__("Charge Paddles")
    
    def activate(self):
        global controlType
        controlType = 3
        #reset_players(self.plr1, self.plr2)
    
class Bounce(Gimmick):
    def __init__(self):
        super().__init__("Flappy Paddles")
    
    def activate(self):
        global controlType
        controlType = 2
        

class Keybind(Gimmick):
    def __init__(self):
        super().__init__("Random Keybinds")
    
    def activate(self):
        global controlType
        controlType = 4


class Baseball(Gimmick):
    def __init__(self):
        super().__init__("Baseball Parries", type)
    
    def activate():
        global controlType
        reset_players(leftPlayer, rightPlayer)
        controlType = 5
#class