# Fraser King, 2011

import pygame, socket, thread, time, os, math, sys, random
import string
from pygame.locals import *

shipnames = ["nyan2.png",
             "nyan3.png",
             "nyan4.png",
             "nyan5.png",
             "nyan6.png"
             ]

connum = 0

print("Welcome to Nyan Battles! If you need help, type 'help' here into the terminal!\n -Fraser King\n\n")

def load_image(name, colorkey=None, blur = False):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', name
        raise SystemExit, message
    if blur:
        image.set_alpha(blur, RLEACCEL)
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    image = image.convert_alpha()
    return image, image.get_rect()

class cl_box:
    "Client handler class"
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect()
        self.data = []
        self.players = []
        self.messages = []
        self.bullets = []
        self.sounds = []
        self.name = ""
        thread.start_new_thread(self.receive, ())
    def connect(self):
        self.socket.connect((self.host, self.port))
    def receive(self):
        "Receive and parse data"
        databuffer = ""
        while True:
#            time.sleep(0.005)
            databuffer += self.socket.recv(1024)
            if not "\r\n" in databuffer: continue
            while "\r\n" in databuffer:
                self.data.append(databuffer[:databuffer.index("\r\n")])
                databuffer = databuffer[databuffer.index("\r\n")+2:]

            info = []

            if self.data:

                for info in self.data:
                    if info.startswith("NAME:"):
                        self.name = info[5:].strip()
                        continue
                    info = info.replace(">", "")
                    info = info.split("<")

                    if info:
                        self.players = []
                        self.messages = []
                        self.bullets = []
                        self.sounds = []
                        for signal in info:
                            signal = signal.strip()
                            if not signal: continue
                            signal = signal.split()
                            sigtype = signal[0]
                            if sigtype == "P":
                                self.players.append(signal)
                            elif sigtype == "M":
                                self.messages.append(signal)
                            elif sigtype == "B":
                                self.bullets.append(signal)
                            elif sigtype == "S":
                                self.sounds.append(signal)
            self.data = []
        

class comms:
    "Server communications class"
    def __init__(self, port):
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        
        thread.start_new_thread(self.listen, ())
        thread.start_new_thread(self.receive, ())
#        self.listen()

    def listen(self):
        global Game, connum, shipnames
        "Listens for new connections."
        try:
            self.socket.bind(('', self.port))
            self.socket.listen(1)
        except:
            print "\nYou already have a server running through this address. Exit that and try again."

        while True:
            #time.sleep(0.005)
            conn, addr = self.socket.accept()
            self.clients.append(client(conn, addr))
            try:
                if len(Game.messages) > 28:
                    Game.messages = []
                    Game.messages.append("<Chat Reset>")
                Game.players.append(player(conn, shipnames[connum%len(shipnames)]))
                Game.messages.append(Game.players[-1].name + " joined")
                self.clients[-1].name = Game.players[-1].name
                conn.send("NAME:"+Game.players[-1].name+"\r\n")
                connum += 1
                #joinSound = pygame.mixer.Sound('join.wav')
                #joinSound.set_volume(5)
                #joinSound.play()
               # sendsounds.append(["L", int(localplayer.x), int(localplayer.y)])
            except Exception, e:
                print e

    def receive(self):
        "Initiates the client's receiving function."
        while True:
            time.sleep(0.05)
            for client in self.clients:
                if client.init_r == False:
                    client.init_recv()

class client:
    "Client class"
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        self.ready_for_game = False
        self.init_r = False
        self.data = []
        self.name = ""
    def init_recv(self):
        thread.start_new_thread(self.receive, ())
        self.init_r = True
    def receive(self):
        global Game
        databuffer = ""
        while True:
            time.sleep(0.005)
            try:
                databuffer += self.conn.recv(1024)
            except:
                if len(Game.messages) > 28:
                    Game.messages = []
                    Game.messages.append("<Chat Reset>")
                Game.messages.append(self.name + " left")
                for p in Game.players:
                    if p.name == self.name:
                        abc = pygame.Surface((1,1))
                        rawabc=pygame.image.load('data/abc.png')
                        p.image = rawabc
                        p.x = 20000
                        p.y = 20000
                       # leaveSound = pygame.mixer.Sound('leave.wav')
                        #leaveSound.set_volume(5)
                       # leaveSound.play()
                       # sendsounds.append(["L", int(localplayer.x), int(localplayer.y)])
                        #p.namerect = font.render(" ", 1, (0,0,0))
                        #p.hprect = Rect(0,0,0,0)
                break
            if not "\r\n" in databuffer: continue
            while "\r\n" in databuffer:
                self.data.append(databuffer[:databuffer.index("\r\n")])
                databuffer = databuffer[databuffer.index("\r\n")+2:]


class playfield:
    "Playing field, the level."
    def __init__(self):
        self.width = 2000
        self.height = 2000
    def blit_at(self, surf, x, y, bg):
        surf.blit(bg, (0,0))
        for c in range(21):
            pygame.draw.line(surf, (0,0,0), (400-x + 100*c, 300-y), (400-x+100*c, 2300-y), 1)
            pygame.draw.line(surf, (0,0,0), (400-x, 300-y+100*c), (2400-x, 300-y+100*c), 1)
            
class player:
    def __init__(self, conn, shname):
        global arial12
        global Game
        font = arial12
        self.conn = conn
        self.movmask = 0
        self.name = "".join([string.lowercase[random.randint(0,25)] for x in range(random.randint(4,10))]).capitalize()
        self.imname = shname
        self.image, self.rect = load_image(self.imname)
        self.crosshair, self.crosshairrect = load_image("Crosshair.png")
        self.score = 0
        self.x = 400
        self.y = 300
        self.inertia = [0, 0]
        self.xalt = 0
        self.yalt = 0
        self.rxalt = 0
        self.ryalt = 0
        self.angle = 0
        self.vangle = 0
        self.aim = (400, 300)
        self.ticker = 0
        self.namesurf = font.render(self.name, 1, (255,255,255))
        self.namerect = self.namesurf.get_rect()
        self.hp = 100
        self.hprect = Rect(0,0,100,8)
    def blit(self, surf, crot = False):
        self.rect.center = (self.x, self.y)
        rotsurf = pygame.transform.rotate(self.image, math.degrees(-self.vangle+math.pi/2*3))
        rotrect = rotsurf.get_rect()
        rotrect.center = (self.x-self.rxalt+400, self.y-self.ryalt+300)
        surf.blit(rotsurf, rotrect)
        if crot:
            crotsurf = pygame.transform.rotate(self.crosshair, self.ticker*8)
            crotrect = crotsurf.get_rect()
            crotrect.center = self.aim
            surf.blit(crotsurf, crotrect)
        self.namerect.center = rotrect.center
        self.namerect.move_ip(0, 40)
        surf.blit(self.namesurf, self.namerect)
        self.hprect.center = self.namerect.center
        self.hprect.move_ip(0, 12)
        surf.fill((255,0,0), self.hprect)
        surf.fill((0,255,0), self.hprect.inflate(self.hp-100,0))

    def tick(self):

        self.ticker += 1
        
        self.x += self.inertia[0]
        self.y += self.inertia[1]

        if self.inertia[0] > 6:
            self.inertia[0] = 6
        elif self.inertia[0] < -6:
            self.inertia[0] = -6

        if self.inertia[1] > 6:
            self.inertia[1] = 6
        elif self.inertia[1] < -6:
            self.inertia[1] = -6

        self.inertia[0] *= 0.98
        self.inertia[1] *= 0.98

        angle = self.angle

        if self.vangle - self.angle > math.pi:
            angle += 2 * math.pi

        self.vangle = (self.vangle * 4 + angle)/5.0

        self.vangle = self.vangle%(math.pi*2)

        self.xalt = (self.xalt * 8 + self.x) / 9.0
        self.yalt = (self.yalt * 8 + self.y) / 9.0

        if self.x < 0: self.x = 0; self.inertia[0] = -self.inertia[0]
        if self.x > 2000: self.x = 2000; self.inertia[0] = -self.inertia[0]
        if self.y < 0: self.y = 0; self.inertia[1] = -self.inertia[1]
        if self.y > 2000: self.y = 2000; self.inertia[1] = -self.inertia[1]
        
    def point(self, pos):
        self.aim = pos
        pos = list(pos)
        pos[0] += (self.xalt-400)
        pos[1] += (self.yalt-300)

        x, y = pos
        
        if x - self.x == 0:
            if y < self.y:
                self.angle = math.pi * 3 / 2
            elif y > self.y:
                self.angle = math.pi / 2
        else:
            self.angle = math.atan(float(y-self.y)/float(x-self.x))

        if x < self.x:
            self.angle += math.pi

class game:
    def __init__(self):
        self.players = []
        self.messages = ["Welcome To Nyan Battle!",
                         "To enter chat, press enter and type your message in the console."]
        self.bullets = []
        

class bullet:
    def __init__(self, name, x, y, angle):
        self.name = name
        self.x = x
        self.y = y
        self.angle = angle

pygame.init() 

arial12 = pygame.font.Font(os.path.join("fonts", "arial.ttf"), 12)
arial16 = pygame.font.Font(os.path.join("fonts", "arial.ttf"), 16)


def main():    
    global Game, connum, shipnames
    ticker = 0
    porting = False
    sendsounds = []
    Comm = comms(int(7777))
    icon = pygame.Surface((32,32))
    rawicon=pygame.image.load('data/logo.png')
    pygame.display.set_icon(rawicon)
    pygame.display.set_mode((800,600))#, FULLSCREEN)
    #pygame.display.set_caption('Nyan Battle (Server) Ver: 1.01')

    bg = load_image("bg.jpg")[0]
    lasersound = pygame.mixer.Sound("laser.ogg")

    explosionSound = pygame.mixer.Sound('2.wav')

    cooldownSound = pygame.mixer.Sound('ding.wav')
    teleportSound = pygame.mixer.Sound('teleporting.wav')

    clock = pygame.time.Clock()
    FPS = 80
    coolDown = 0.0
    
    pygame.mixer.music.load("nyan-looped.mp3")
    pygame.mixer.music.play(-1)

    screen = pygame.display.get_surface()
    pygame.mouse.set_visible(False)

    Play_Area = playfield()
    Game = game()
    localplayer = player(None, "nyan1.png")
    Game.players.append(localplayer)
    Game.messages.append("Host is: " + localplayer.name)
    
    mpos = (400, 300)

    while True:
        ot = pygame.time.get_ticks()
        Play_Area.blit_at(screen, localplayer.xalt, localplayer.yalt, bg)

        milliseconds = clock.tick(FPS)
        coolDown += milliseconds / 1000.0
        pygame.display.set_caption("Nyan Battle! (Server) Ver: 1.02 | FPS: %.0f" % (clock.get_fps()))

        if porting == True:
            if coolDown >= 30:
                porting = False
                coolDown = 0.0
                print "You can now port again!"
                cooldownSound.set_volume(5)
                cooldownSound.play()
        
        pygame.event.pump()
        keystate = pygame.key.get_pressed()

        if keystate[K_w]: localplayer.inertia[1] -= 0.4
        if keystate[K_s]: localplayer.inertia[1] += 0.4
        if keystate[K_a]: localplayer.inertia[0] -= 0.4
        if keystate[K_d]: localplayer.inertia[0] += 0.4
        if keystate[K_h]: localplayer.hp -= 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                pygame.mixer.music.stop()
                pygame.display.quit()
                sys.exit(0)
            t = event.type
            if t == MOUSEBUTTONDOWN:
                if event.button == 1:
                    Game.bullets.append(bullet(localplayer.name, localplayer.x, localplayer.y, -localplayer.vangle+math.pi/2*3))
                    lasersound.set_volume(1)
                    lasersound.play()
                    sendsounds.append(["L", int(localplayer.x), int(localplayer.y)])
            if t == KEYDOWN:
                key=pygame.key.get_pressed()
                if event.key == K_ESCAPE:
                    pygame.mixer.music.stop()
                    pygame.display.quit()
                    sys.exit(0)
                if event.key == K_RETURN:
                    if len(Game.messages) > 28:
                        Game.messages = []
                        Game.messages.append("<Chat Reset>")
                    myMessage = raw_input("Type your message: ")
                    if myMessage != "":
                        if myMessage == 'help':
                            print "This is the help panel.\n Fullscreen = Left Ctrl\n Normal size = Right Alt\n Chat = Enter and then Enter again to submit the message in\n the terminal (Alt tab between both applicaitons)\n Exit = Escape\n Fire laser = left mouse button click\n Teleport = Shift + directional key (30 sec coolDown)\n\n You can mute the music by typing 'mute' ('unmute' unmutes) and \nchange the music to jazz by typing 'jazz'\n Hope that helped!\n\n -Fraser King"
                        elif myMessage == 'Help':
                            print "This is the help panel.\n Fullscreen = Left Ctrl\n Normal size = Right Alt\n Chat = Enter and then Enter again to submit the message in\n the terminal (Alt tab between both applicaitons)\n Exit = Escape\n Fire laser = left mouse button click\n Teleport = Shift + directional key (30 sec coolDown)\n\n You can mute the music by typing 'mute' ('unmute' unmutes) and \nchange the music to jazz by typing 'jazz'\n Hope that helped!\n\n -Fraser King"
                        elif myMessage == 'Mute':
                            print "Music muted (unmute to unmute)."
                            pygame.mixer.music.stop()
                        elif myMessage == 'mute':
                            print "Music muted (unmute to unmute)."
                            pygame.mixer.music.stop()
                        elif myMessage == 'unmute':
                            print "Music unmuted."
                            pygame.mixer.music.play(-1)
                        elif myMessage == 'Unmute':
                            print "Music unmuted."
                            pygame.mixer.music.play(-1)
                        elif myMessage == 'jazz':
                            print "Let's get funky up in here..."
                            pygame.mixer.music.stop()
                            pygame.mixer.music.load("jazz.mp3")
                            pygame.mixer.music.play(-1)
                        elif myMessage == 'Jazz':
                            print "Let's get funky up in here..."
                            pygame.mixer.music.stop()
                            pygame.mixer.music.load("jazz.mp3")
                            pygame.mixer.music.play(-1)
                        elif myMessage == 'regular':
                            print "Normal Music? Okay..."
                            pygame.mixer.music.stop()
                            pygame.mixer.music.load("nyan-looped.mp3")
                            pygame.mixer.music.play(-1)
                        elif myMessage == 'Regular':
                            print "Normal Music? Okay..."
                            pygame.mixer.music.stop()
                            pygame.mixer.music.load("nyan-looped.mp3")
                            pygame.mixer.music.play(-1)
                        else:
                            myMessage = "["+localplayer.name+"] " + myMessage
                            Game.messages.append(myMessage + "")
                if event.key == K_LCTRL:
                    pygame.display.set_mode((800,600), FULLSCREEN)
                if event.key == K_RCTRL:
                    pygame.display.set_mode((800,600))
                if key[pygame.K_LSHIFT]:
                    if key[pygame.K_d]:
                        if porting == False:
                            localplayer.x += 300
                            porting = True
                            coolDown = 0.0
                            teleportSound.set_volume(5)
                            teleportSound.play()
                    if key[pygame.K_a]:
                        if porting == False:
                            localplayer.x -= 300
                            porting = True
                            coolDown = 0.0
                            teleportSound.set_volume(5)
                            teleportSound.play()
                    if key[pygame.K_w]:
                        if porting == False:
                            localplayer.y -= 300
                            porting = True
                            coolDown = 0.0
                            teleportSound.set_volume(5)
                            teleportSound.play()
                    if key[pygame.K_s]:
                        if porting == False:
                            localplayer.y += 300
                            porting = True
                            coolDown = 0.0
                            teleportSound.set_volume(5)
                            teleportSound.play()
                    
        mpos = pygame.mouse.get_pos()

        localplayer.point(mpos)
#        localplayer.tick()
        i = 0
        for message in Game.messages:
            msurf = arial16.render(message, 1, (255,255,255))
            mrect = msurf.get_rect()
            mrect.midleft = (5, 15 + 20 * i)
            screen.blit(msurf, mrect)
            i += 1

        for b in Game.bullets:
            b.x -= 22*math.sin(b.angle)
            b.y -= 22*math.cos(b.angle)
            x = b.x - localplayer.xalt + 400
            y = b.y - localplayer.yalt + 300

            if x < -20 or x > 820 or y < -20 or y > 620:
                continue

            pygame.draw.line(screen, (255, 0, 0), (x,y), (x+40*math.sin(b.angle),y+40*math.cos(b.angle)), 7)


        for x in range(len(Game.bullets)):
            b = Game.bullets[x]
            for p in Game.players:
                if b.name != p.name:
                    if p.rect.inflate(10,10).collidepoint((b.x,b.y)):
                        Game.bullets[x] = None
                        p.hp -= 4

                        if p.hp <= 0:
                            p.dead = True
                            if len(Game.messages) > 28:
                                Game.messages = []
                                Game.messages.append("<Chat Reset>")
                            p.hp = 100
                            Game.messages.append(b.name + " killed " + p.name)
                            p.score += 1
                            Game.messages.append(p.name + " has died " + str(p.score) + " times")                            
                            explosionSound.set_volume(3)
                            explosionSound.play()
                            sendsounds.append(["L", int(localplayer.x), int(localplayer.y)])
                            #porting = False

            if b.x < 0 or b.x > 2000 or b.y < 0 or b.y > 2000:
                Game.bullets[x] = None

        while None in Game.bullets:
            Game.bullets.remove(None)

        for client in Comm.clients:
            cpc = None
            for p in Game.players:
                if p.conn is client.conn:
                    cpc = p

            if cpc:
                if cpc.movmask & 1:
                    cpc.inertia[1] -= 0.4
                if cpc.movmask & 2:
                    cpc.inertia[1] += 0.4
                if cpc.movmask & 4:
                    cpc.inertia[0] -= 0.4
                if cpc.movmask & 8:
                    cpc.inertia[0] += 0.4


            if not client.data: continue
            for data in client.data:
                data = data.replace(">", "")
                data = data.split("<")
                for signal in data:
                    signal = signal.strip()
                    signal = signal.split()
                    if not signal:
                        continue
                    sigtype = signal[0]
                    if sigtype == "M":
                        movmask = int(signal[1])
                        cpc.movmask = movmask
                    elif sigtype == "X":
                        cpc.y = int(signal[1])
                    elif sigtype == "J":
                        cpc.x = int(signal[1])
                    elif sigtype == "A":
                        cpc.angle = float(signal[1])
                    elif sigtype == "F":
                        Game.bullets.append(bullet(cpc.name, cpc.x, cpc.y, -cpc.vangle+math.pi/2*3))
                        dist = math.sqrt(abs(localplayer.x-cpc.x)**2+abs(localplayer.y-cpc.y)**2)
                        lasersound.set_volume(1.0-dist/500.0)
                        lasersound.play()
                    elif sigtype == "R":
                        myName1 = str(signal[1])
                    elif sigtype == "Q":
                        if len(Game.messages) > 28:
                            Game.messages = []
                            Game.messages.append("<Chat Reset>")
                        myMessage2 = ""
                        for i in signal:
                            if i != 'Q':
                                if i != '\u': 
                                    myMessage2 = myMessage2 + " " + i
                        Game.messages.append(myName1 + " " + myMessage2)
                        
            client.data = []
        
        for p in Game.players:
            p.tick()

        if not ticker%2:
            for p in Game.players:
                p.rxalt = localplayer.xalt
                p.ryalt = localplayer.yalt
                p.blit(screen, p is localplayer)

        if not ticker%2:
            pygame.display.flip()

        timetaken = pygame.time.get_ticks() - ot
        if timetaken > 15: timetaken = 15
        time.sleep((15-timetaken)/1000.0)
        # networking code
        if not ticker%1:
            GAME_INFO = ""
            for x in range(len(Game.players)):
                cp = Game.players[x]
                GAME_INFO += "< P " + cp.name + " X "
                GAME_INFO += str(int(cp.x)) + " Y "
                GAME_INFO += str(int(cp.y)) + " XA "
                GAME_INFO += str(int(cp.xalt)) + " YA "
                GAME_INFO += str(int(cp.yalt)) + " H "
                GAME_INFO += str(cp.hp) + " I "
                GAME_INFO += cp.imname + " A "
                GAME_INFO += str(float(cp.vangle))
                GAME_INFO += " >"
            for x in range(len(Game.messages)):
                GAME_INFO += "< M " + Game.messages[x] + " >"
            for x in range(len(Game.bullets)):
                cb = Game.bullets[x]
                GAME_INFO += "< B " + cb.name + " X "
                GAME_INFO += str(int(cb.x)) + " Y "
                GAME_INFO += str(int(cb.y)) + " A "
                GAME_INFO += str(cb.angle) + " >"
            for s in sendsounds:
                GAME_INFO += "< S " + str(s[0]) + " X " + str(s[1])
                GAME_INFO += " Y " + str(s[2]) + " >"

            for pl in Comm.clients:
                try:
                    pl.conn.send(GAME_INFO+"\r\n")
                except:
                    pass

            sendsounds = []

        ticker += 1
    
if __name__ == "__main__":
    main()
