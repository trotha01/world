""" For playing sections of an audio file """
import pygame
import sys

def play_init():
    """ Initializes for playing audio """
    pygame.init()

def play_audio(audio_file, start, length):
    """ Plays file starting at 'start' secs, and plays for 'length' secs """
    length_mili_secs = float(length) * 1000
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play(0, float(start))

    print "Start playing :)"
    while pygame.mixer.music.get_pos() < length_mili_secs:
        pygame.time.Clock().tick(10)
        continue
    pygame.mixer.music.stop()
    print "Done playing :)"

def usage_error():
    """ Prints error if this is used incorrectly """
    print "Usage: "
    print sys.argv[0] + " [file] [start] [length]"
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        usage_error()

    play_init()

    AUDIO_FILE = sys.argv[1]
    START      = sys.argv[2]
    LENGTH     = sys.argv[3]
    play_audio(AUDIO_FILE, START, LENGTH)
