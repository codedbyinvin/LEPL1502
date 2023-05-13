import vlc
import time
p = vlc.MediaPlayer("./goofy-ahh-sounds.mp3")

def sound_event():
    p.play()
    time.sleep(5)
    p.stop()

if __name__ == "__main__":
    sound_event()
