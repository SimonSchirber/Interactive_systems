
import pyaudio
import numpy as np

CHUNK = 4096 # number of data points to read at a time
RATE = 44100 # time resolution of the recording device (Hz)

first_hit = False
wait_period = 0
quiet_count = 0

p=pyaudio.PyAudio() # start the PyAudio class
stream=p.open(format=pyaudio.paInt16,channels=1,rate=RATE,input=True,
              frames_per_buffer=CHUNK, input_device_index=2) #uses default input device

# create a numpy array holding a single read of audio data
for i in range(10000): #to it a few times just to see
    data = np.fromstring(stream.read(CHUNK),dtype=np.int16)
    #print(max(data, key=abs))
    max_val = np.amax(data)
    if (max_val > 300 and first_hit == False):
        print("hit")
        first_hit = True
        quiet_count = 0
    if first_hit:
        wait_period +=1
    if (wait_period > 2):
        if (max_val > 300):
            print("double tap")
            wait_period = 0
            first_hit = False
        if (wait_period > 5):
            print('single tap')
            wait_period = 0
            first_hit = False 
    if (first_hit == False):
        quiet_count += 1
        if (quiet_count == 20):
            print("quiet")
            quiet_count = 0


# close the stream gracefully
stream.stop_stream()
stream.close()
p.terminate()