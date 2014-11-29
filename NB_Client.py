# Fraser King, 2011

import pygame, socket, thread, time, os, math, sys, random
import string
from pygame.locals import *
from NB_Server import *

server = '5.195.13.69'
#server = raw_input("Server: ")
port = 7777
#port = int(raw_input("Port: "))

icon = pygame.Surface((326,32))
rawicon=pygame.image.load('data/logo.png')
pygame.display.set_icon(rawicon)
pygame.display.set_mode((800,600))
screen = pygame.display.get_surface()
pygame.display.set_caption("Nyan Battle (Client) Ver: 1.02")

pygame.mouse.set_visible(False)

localplayer = player(None, "nyan1.png")
Play_Area = playfield()

try:
    Comm = cl_box(server,port)
except:
    print "\nThe Server you are trying to connect to is not available at this point in time.\nPress enter to exit."
    raw_input()

porting = False

shipgraphics = {
    "nyan1.png": load_image("nyan1.png"),
    "nyan2.png": load_image("nyan2.png"),
    "nyan3.png": load_image("nyan3.png"),
    "nyan4.png": load_image("nyan4.png"),
    "nyan5.png": load_image("nyan5.png"),
    "nyan6.png": load_image("nyan6.png")
    }
ticker = 0
bg = load_image("bg.jpg")[0]
crosshair = load_image("Crosshair.png")[0]
ls = pygame.mixer.Sound("laser.ogg")
Es = pygame.mixer.Sound("2.wav")
cooldownSound = pygame.mixer.Sound('ding.wav')
teleportSound = pygame.mixer.Sound('teleporting.wav')
#Os = pygame.mixer.Sound('leave.wav')
#Js = pygame.mixer.Sound('join.wav')
pygame.mixer.music.load("nyan-looped.mp3")
pygame.mixer.music.play(-1)

clock = pygame.time.Clock()
FPS = 80
coolDown = 0.0

print "Connected to server: " + str(server) + " on port " + str(port) + ", enjoy your stay!"

while True:
    ot = pygame.time.get_ticks()
    screen.blit(bg, (0,0))
    i = 0
    x = localplayer.xalt
    y = localplayer.yalt
    for c in range(21):
        pygame.draw.line(screen, (0,0,0), (400-x + 100*c, 300-y), (400-x+100*c, 2300-y), 1)
        pygame.draw.line(screen, (0,0,0), (400-x, 300-y+100*c), (2400-x, 300-y+100*c), 1)

    milliseconds = clock.tick(FPS)
    coolDown += milliseconds / 1000.0
    pygame.display.set_caption("Nyan Battle! (Client) Ver: 1.02 | FPS: %.0f" % (clock.get_fps()))

    if porting == True:
        if coolDown >= 30:
            porting = False
            coolDown = 0.0
            print "You can now port again!"
            cooldownSound.set_volume(5)
            cooldownSound.play()
            
    for sound in Comm.sounds:
        S, sound, X, x, Y, y = sound
        x = int(x)
        y = int(y)
        dist = math.sqrt(abs(localplayer.x-x)**2 + abs(localplayer.y-y)**2)
        stp = {
            "L": ls
            }[sound]

        stp.set_volume(1.0-dist/500.0)
        stp.play()

        stp2 = {
            "L": Es
            }[sound]

        stp2.set_volume(1.0-dist/500.0)
        stp2.play()

       # stp3 = {
           # "L": Os
           # }[sound]

       # stp3.set_volume(5)
       # stp3.play()

       # stp4 = {
           # "L": Js
           # }[sound]

      #  stp4.set_volume(5)
       # stp4.play()

    for bullet in Comm.bullets:
        B, name, X, x, Y, y, A, a = bullet
        x = int(x)
        y = int(y)
        a = float(a)

        x -= localplayer.xalt - 400
        y -= localplayer.yalt - 300
        if x < -20 or x > 820 or y < -20 or y > 620:
            continue

        pygame.draw.line(screen, (255, 0, 0), (x,y), (x+40*math.sin(a),y+40*math.cos(a)), 7)

    for message in Comm.messages:
        message = " ".join(message[1:])
        msurf = arial16.render(message, 1, (255,255,255))
        mrect = msurf.get_rect()
        mrect.midleft = (5, 15 + 20 * i)
        screen.blit(msurf, mrect)
        i += 1


    for player in Comm.players:
        P, name, X, x, Y, y, XA, xa, YA, ya, H, h, I, i, A, a = player

        x = int(x)
        y = int(y)
        a = float(a)
        h = int(h)
        xa = int(xa)
        ya = int(ya)

        if name == Comm.name:
            localplayer.x = x
            localplayer.y = y
            localplayer.hp = h
            localplayer.xalt = xa
            localplayer.yalt = ya
        

        blitx, blity = (x-localplayer.xalt+400, y-localplayer.yalt+300)
        if blitx < -80 or blitx > 880 or blity < -80 or blity > 680:
            continue
        
        rotsurf = pygame.transform.rotate(shipgraphics[i][0], math.degrees(-a+math.pi/2*3))
        rotrect = rotsurf.get_rect()
        rotrect.center = (blitx, blity)
        screen.blit(rotsurf, rotrect)
        namesurf = arial12.render(name, 1, (255,255,255))
        namerect = namesurf.get_rect()
                                       
        namerect.center = rotrect.center
        namerect.move_ip(0, 40)
        screen.blit(namesurf, namerect)
        hprect = Rect(0,0,100,8)
        hprect.center = namerect.center
        hprect.move_ip(0, 12)
        screen.fill((255,0,0), hprect)
        screen.fill((0,255,0), hprect.inflate(h-100,0))

    if not ticker%1:
        pygame.event.pump()
        keystate = pygame.key.get_pressed()

        movmask = 0
        if keystate[K_w]: movmask += 1
        if keystate[K_s]: movmask += 2
        if keystate[K_a]: movmask += 4
        if keystate[K_d]: movmask += 8

        Comm.socket.send("<M "+str(movmask)+" >\r\n")

    mpos = pygame.mouse.get_pos()

    crotsurf = pygame.transform.rotate(crosshair, ticker*8)
    crotrect = crotsurf.get_rect()
    crotrect.center = mpos
    screen.blit(crotsurf, crotrect)

    localplayer.point(mpos)
    Comm.socket.send("<A " + str(localplayer.angle) + " >\r\n")

    for e in pygame.event.get():
        if e.type == pygame.QUIT: 
            pygame.mixer.music.stop()
            pygame.display.quit()
            sys.exit(0)
        if e.type == MOUSEBUTTONDOWN:
            if e.button == 1:
                Comm.socket.send("< F >")
                ls.set_volume(1)
                ls.play()
        if e.type == KEYDOWN:
            key=pygame.key.get_pressed()
            if e.key == K_ESCAPE:
                pygame.mixer.music.stop()
                pygame.display.quit()
                sys.exit(0)
            if e.key == K_RETURN:
                myMessage1 = raw_input("Type your message: ")
                myName1 = ("["+Comm.name+"]")
                myMessage2 = myMessage1
                if myMessage2 != "":
                    if myMessage2 == 'help':
                        print "This is the help panel.\n Fullscreen = Left Ctrl\n Normal size = Right Alt\n Chat = Enter and then Enter again to submit the message in\n the terminal (Alt tab between both applicaitons)\n Exit = Escape\n Fire laser = left mouse button click\n Teleport = Shift + directional key (30 sec coolDown)\n\n You can mute the music by typing 'mute' ('unmute' unmutes) and \nchange the music to jazz by typing 'jazz'\n Hope that helped!\n\n -Fraser King"
                    elif myMessage2 == 'Help':
                        print "This is the help panel.\n Fullscreen = Left Ctrl\n Normal size = Right Alt\n Chat = Enter and then Enter again to submit the message in\n the terminal (Alt tab between both applicaitons)\n Exit = Escape\n Fire laser = left mouse button click\n Teleport = Shift + directional key (30 sec coolDown)\n\n You can mute the music by typing 'mute' ('unmute' unmutes) and \nchange the music to jazz by typing 'jazz'\n Hope that helped!\n\n -Fraser King"
                    elif myMessage2 == 'Mute':
                        print "Music muted (unmute to unmute)."
                        pygame.mixer.music.stop()
                    elif myMessage2 == 'mute':
                        print "Music muted (unmute to unmute)."
                        pygame.mixer.music.stop()
                    elif myMessage2 == 'unmute':
                        print "Music unmuted."
                        pygame.mixer.music.play(-1)
                    elif myMessage2 == 'Unmute':
                        print "Music unmuted."
                        pygame.mixer.music.play(-1)
                    elif myMessage2 == 'jazz':
                        print "Let's get funky up in here..."
                        pygame.mixer.music.stop()
                        pygame.mixer.music.load("jazz.mp3")
                        pygame.mixer.music.play(-1)
                    elif myMessage2 == 'Jazz':
                        print "Let's get funky up in here..."
                        pygame.mixer.music.stop()
                        pygame.mixer.music.load("jazz.mp3")
                        pygame.mixer.music.play(-1)
                    elif myMessage2 == 'regular':
                        print "Normal Music? Okay..."
                        pygame.mixer.music.stop()
                        pygame.mixer.music.load("nyan-looped.mp3")
                        pygame.mixer.music.play(-1)
                    elif myMessage2 == 'Regular':
                        print "Normal Music? Okay..."
                        pygame.mixer.music.stop()
                        pygame.mixer.music.load("nyan-looped.mp3")
                        pygame.mixer.music.play(-1)
                    else:   
                        Comm.socket.send("<R " + myName1 + " >\r\n")
                        Comm.socket.send("<Q " + str(myMessage2) + " >\u\r\n")
            if e.key == K_LCTRL:
                    pygame.display.set_mode((800,600), FULLSCREEN)
            if e.key == K_RCTRL:
                    pygame.display.set_mode((800,600))
            if key[pygame.K_LSHIFT]:
                    if key[pygame.K_d]:
                        if porting == False:
                            x += 300
                            porting = True
                            coolDown = 0.0
                            teleportSound.set_volume(5)
                            teleportSound.play()
                    if key[pygame.K_a]:
                        if porting == False:
                            x -= 300
                            porting = True
                            coolDown = 0.0
                            teleportSound.set_volume(5)
                            teleportSound.play()
                    if key[pygame.K_w]:
                        if porting == False:
                            y -= 300
                            porting = True
                            coolDown = 0.0
                            teleportSound.set_volume(5)
                            teleportSound.play()
                    if key[pygame.K_s]:
                        if porting == False:
                            y += 300
                            porting = True
                            coolDown = 0.0
                            teleportSound.set_volume(5)
                            teleportSound.play()
                    Comm.socket.send("<J "+ str(x) +" >\r\n")
                    Comm.socket.send("<X "+ str(y) +" >\r\n")
                 
    pygame.display.flip()
    timetaken = pygame.time.get_ticks() - ot
    if timetaken > 15: timetaken = 15
    time.sleep((15-timetaken)/1000.0)
    ticker += 1


