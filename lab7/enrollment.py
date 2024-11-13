from voice_assistant_lib import *
from shutil import copyfile


init_voice_assistant({'api_key': 'YOUR_KEY_HERE'})

instruction_audio = text_to_speech("Say 'Please authenticate me'")
play(instruction_audio)

audio_in = listen()

copyfile(audio_in, 'voiceprint.wav')

instruction_audio = text_to_speech("The voiceprint is saved to voiceprint.wav. You are all set!")
play(instruction_audio)
