import sys

import fixed_tempo_creative_karaoke
import free_tempo_creative_karaoke

# Mode 
FIXED = "0"
FREE = "1"

def main_program(mode, tempo, genre, filepath):
  if mode is FIXED:
    fixed_tempo_creative_karaoke.creative_karaoke(filepath, int(tempo), int(genre))
  else:
    free_tempo_creative_karaoke.creative_karaoke(filepath, int(genre))


# argv 0: mode, argv 1: tempo, argv2: genre, argv3: filepath
if __name__== "__main__":
  main_program(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])

