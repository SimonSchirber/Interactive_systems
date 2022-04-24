from djitellopy import tello
import time
import cv2
import pygame
import pyaudio
import numpy as np

X = 500
Y = 400

def init():
    global win
    pygame.init()
    win = pygame.display.set_mode((X,Y))

def getKey(keyName):
    #return true if the keyname is what was pressed
    
    ans = False 
    for event in pygame.event.get(): 
        if event.type == pygame.QUIT:
         
            # deactivates the pygame library
            pygame.quit()
 
            # quit the program.
            quit()  
    keyInput = pygame.key.get_pressed()
    myKey = getattr(pygame, 'K_{}'.format(keyName))
    if keyInput[myKey]:
        ans = True
    pygame.display.update()
    
    return ans

CHUNK = 4096 # number of data points to read at a time
RATE = 44100 # time resolution of the recording device (Hz)

first_hit = False
wait_period = 0
quiet_count = 0
take_pic  = False
prev_vals = None

p=pyaudio.PyAudio() # start the PyAudio class
stream=p.open(format=pyaudio.paInt16,channels=1,rate=RATE,input=True,
              frames_per_buffer=CHUNK, input_device_index=2) #uses default input device

#Start Pygame
init()
drone = tello.Tello()
drone.connect()
print(f"Battery at {drone.get_battery()}%")
drone.streamon()


white = (255,255,255)
black= (0,0,0)
blue = (0,0,128)
green = (0,255,0)
text_color = (110,110,110)
font = pygame.font.Font('freesansbold.ttf', 70)

def display_text(what_to_say):
    if (what_to_say == 'quiet'):
        win.fill(white)
        pygame.display.update()
        time.sleep(.1)
    text = font.render(what_to_say, True, green, blue)
    textRect = text.get_rect()
    textRect.center = (X // 2, Y // 2)
    if (what_to_say != "double tap"):
        win.fill(black)
    win.blit(text, textRect)
    pygame.display.update()

def getInput():
    lr, fb, ud, yv = 0,0,0,0
    speed = 75
    global win
    global take_pic
    
    img = drone.get_frame_read()
    if getKey("LEFT"):   
        lr = -speed
    elif getKey("RIGHT"):
        lr = speed
    
    elif getKey("UP"):
        fb = speed
    elif getKey("DOWN"):
        fb = -speed
    
    elif getKey("w"):
        ud = speed
    elif getKey("s"):
        ud = -speed 
    
    elif getKey("d"):
        yv = speed
    elif getKey("a"):
        yv = -speed

    #land
    if getKey("q"):
        drone.land()
        quit()
        time.sleep(3)
    #takeoff
    if getKey("e"):
        drone.takeoff()
    #take a photo, save it uniquely
    if getKey('z') or take_pic:
        
        win.fill(white)  
        #img = drone.get_frame_read()
        timer = time.time()
        pygame.display.update()
        cv2.imwrite(f"Images/{timer}.png", img.frame)
        time.sleep(.1)
        png_photo = pygame.image.load(f'Images/{timer}.png')
        win.blit(png_photo, (0,0))
        pygame.display.update()
        display_text("double tap")
        time.sleep(.5)
        take_pic = False

    return [lr, fb, ud, yv]
#Listen for inputs   
init()
while True:
    vals = getInput()
    if vals != prev_vals:
        drone.send_rc_control(vals[0],vals[1],vals[2],vals[3])
    prev_vals = vals  
    
    #Check sound data
    data = np.fromstring(stream.read(CHUNK),dtype=np.int16)
    max_val = np.amax(data)
    if (max_val > 300 and first_hit == False):
        print("hit")
        display_text("hit")
        first_hit = True
        quiet_count = 0
    if first_hit:
        wait_period +=1
    if (wait_period > 2):
        if (max_val > 300):
            print("double tap")
            display_text("double tap")
            take_pic = True
            wait_period = 0
            first_hit = False
        if (wait_period > 5):
            print('single tap')
            display_text("single tap")
            wait_period = 0
            first_hit = False 
    if (first_hit == False):
        quiet_count += 1
        if (quiet_count == 20):
            print("quiet")
            display_text("quiet")
            quiet_count = 0
    