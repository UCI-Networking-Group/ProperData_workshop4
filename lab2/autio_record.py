from voice_assistant_lib import *

init_voice_assistant()

audio = text_to_speech("Say something. I will play it back.")
play(audio)

my_voice = listen()
play(my_voice)
