import pygame, random, os, time
from pygame.locals import *
import pygame.mixer as mixer

pygame.init()
mixer.init()
clock = pygame.time.Clock()
PATH = os.path.dirname(__file__)
FPS = 60 #change frame rate
SIZE = 20 #change the size fof each block
RATIO = 5/3 #change the screen ratio
FACTOR = 30 #change how big the screen is (must be a multiple of denominator of RATIO)
DIVISOR = 3 #change the size of side panel (must be equal to denominator of RATIO)

SCREEN_W = int(SIZE*RATIO*FACTOR)
SCREEN_H = SIZE*FACTOR
BG_COLOR = (30,30,30)
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("SNAKE")

background = pygame.image.load(PATH+"/background.jpg")
panel_bg = pygame.image.load(PATH+"/panel.jpg")
panel_bg = pygame.transform.rotate(panel_bg,90)
apple_bg = pygame.image.load(PATH+"/apple.png")
apple_bg = pygame.transform.scale(apple_bg,(SIZE,SIZE))
playing=True
paused=True

class Snake():
    def __init__(self, size, length, play_area):
        self.play_area = play_area
        self.size = size
        self.length = length
        self.snake = [[i*SIZE, SIZE] for i in range(length-1,-1,-1)]
        self.direction = 'r'

    def move(self):
        global playing
        for i in range(self.length-1,0,-1):
            if self.snake[0]==self.snake[i]:
                mixer.music.load(PATH+random.choice(("/over1.mp3","/over2.mp3")))
                mixer.music.play()
                playing=False
            self.snake[i][0]=self.snake[i-1][0]
            self.snake[i][1]=self.snake[i-1][1]

        if self.direction=='l':
            self.snake[0][0]-=self.size
        elif self.direction=='r':
            self.snake[0][0]+=self.size
        elif self.direction=='u':
            self.snake[0][1]-=self.size
        elif self.direction=='d':
            self.snake[0][1]+=self.size
    
    def check_collision(self):
        if self.snake[0][0]==self.play_area[0]:
            self.snake[0][0]=0
        elif self.snake[0][1]==self.play_area[1]:
            self.snake[0][1]=0
        elif self.snake[0][0]==-self.size:
            self.snake[0][0]=self.play_area[0]-self.size
        elif self.snake[0][1]==-self.size:
            self.snake[0][1]=self.play_area[1]-self.size

    def draw(self):
        for i in range(self.length):
            rect = pygame.Rect(self.snake[i][0],self.snake[i][1],self.size,self.size)
            if i:
                pygame.draw.rect(screen,(50,150,50),rect)
            else:
                pygame.draw.rect(screen,(50,100,100),rect)
            pygame.draw.rect(screen,(0,50,50),rect,2)

class Apple():
    def __init__(self, size, snake, play_area):
        self.play_area = play_area
        self.snake = snake
        self.size = size
        self.apple = None
        self.move()
    
    def move(self):
        self.apple = [random.choice([self.size*i for i in range(1,self.play_area[0]//self.size-2)]),random.choice([self.size*i for i in range(1,self.play_area[1]//self.size-2)])]
        if self.apple in self.snake:
            self.move()
    
    def draw(self):
        screen.blit(apple_bg,self.apple)

class Game():
    def __init__(self, panel):
        self.play_area = (SCREEN_W-panel[0],panel[1])
        self.snake = Snake(SIZE,3, self.play_area) #change initial length of snake
        self.apple = Apple(SIZE, self.snake.snake, self.play_area)
        self.grass = pygame.transform.scale(background,self.play_area)
        self.full_grass = pygame.transform.scale(background,(SCREEN_W,SCREEN_H))
        self.panel = pygame.transform.scale(panel_bg,panel)
        self.highscore = False
        self.score = 0
        self.font1 = pygame.font.SysFont("comicsans",25,1)
        self.font2 = pygame.font.SysFont("monospace",30,1)
        self.font3 = pygame.font.SysFont("catholic",50)
        self.font4 = pygame.font.SysFont("verdana",30)
        self.font5 = pygame.font.SysFont("verdana",20)
        self.music = mixer.Sound(PATH+"/music.mp3")
        self.music.set_volume(.3)
        mixer.Sound.play(self.music,-1)
    
    def draw(self):
        screen.blit(self.grass,(0,0))
        self.apple.draw()
        self.snake.draw()
        screen.blit(self.panel,(self.play_area[0],0))
        if paused:
            text=self.font5.render("(Press Spacebar to Resume)",1,(100,100,100))
            screen.blit(text,((self.play_area[0]-text.get_width())/2, self.play_area[1]-5*text.get_height()))

    def check_eaten(self):
        if self.snake.snake[0]==self.apple.apple:
            self.collided=True
            self.apple.move()
            self.snake.snake.append([-100,-100])
            self.snake.length+=1
            self.score+=1
            mixer.music.load(PATH+"/eat.mp3")
            mixer.music.play()
    
    def show_score(self):
        text1 = self.font1.render("Score",1,(100,200,100))
        text2 = self.font2.render(str(self.score),1,(255,255,255))
        text3 = self.font1.render("Highscore",1,(100,200,100))
        with open(PATH+"/highscore.txt") as f:
            text4 = self.font2.render(f.read(),1,(255,255,255))
        screen.blit(text1,((SCREEN_W+self.play_area[0]-text1.get_width())/2,0))
        screen.blit(text2,((SCREEN_W+self.play_area[0]-text2.get_width())/2,text2.get_height()*2))
        screen.blit(text3,((SCREEN_W+self.play_area[0]-text3.get_width())/2,text2.get_height()*5))
        screen.blit(text4,((SCREEN_W+self.play_area[0]-text4.get_width())/2,text2.get_height()*7))
        with open(PATH+"/highscore.txt", "r+") as f:
            if int(f.read())<self.score:
                f.seek(0)
                f.write(str(self.score))
                self.highscore = True
    
    def game_over(self):
        screen.blit(self.full_grass,(0,0))
        over = self.font3.render("GAME OVER",1,(150,20,0))
        text = self.font5.render("(Press Spacebar to play again)",1,(100,100,100))
        if self.highscore:
            score = self.font4.render(f"Hooray! New Highscore {self.score}",1,(255,255,255))
        else:
            score = self.font4.render(f"Your score is {self.score}",1,(255,255,255))
        screen.blit(over,((SCREEN_W-over.get_width())/2, 100))
        screen.blit(score,((SCREEN_W-score.get_width())/2, (SCREEN_H-score.get_height())/2))
        screen.blit(text,((SCREEN_W-text.get_width())/2, (SCREEN_H+text.get_height()*4)/2))

    def run(self):
        global playing,paused
        while True:
            screen.fill(BG_COLOR)
            for ev in pygame.event.get():
                if ev.type==QUIT:
                    pygame.quit()
                    exit()
            
                if ev.type==KEYDOWN:
                    if not paused:
                        if (ev.key==K_UP or ev.key==K_w) and self.snake.direction!="d":
                            self.snake.direction='u'
                        elif (ev.key==K_DOWN or ev.key==K_s) and self.snake.direction!="u":
                            self.snake.direction='d'
                        elif (ev.key==K_LEFT or ev.key==K_a) and self.snake.direction!="r":
                            self.snake.direction='l'
                        elif (ev.key==K_RIGHT or ev.key==K_d) and self.snake.direction!="l":
                            self.snake.direction='r'
                    if ev.key==K_SPACE:
                        if playing:
                            paused=not paused
                        else:
                            mixer.music.pause()
                            playing=True
                            self.__init__([SCREEN_W-self.play_area[0], self.play_area[1]])
            
            if playing:
                self.snake.check_collision()
                self.draw()
                if paused:
                    self.music.set_volume(0)
                else:
                    self.music.set_volume(.3)
                    self.snake.move()
                    self.check_eaten()
                self.show_score()
            else:
                self.music.stop()
                self.game_over()

            time.sleep(1/(SIZE*FACTOR)**(1/2.5)) #change the snake speed
            pygame.display.update()
            clock.tick(FPS)

game= Game((SIZE*FACTOR//DIVISOR,SCREEN_H))
game.run()