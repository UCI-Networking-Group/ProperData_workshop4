from voice_assistant_lib import init_voice_assistant, listen, text_to_speech, play
from shutil import copyfile

CONFIG = {
    'pause_threshold': 1,
    'dynamic_energy_threshold': False,
    'energy_threshold': 4000,
}

init_voice_assistant(CONFIG)

instruction_audio = text_to_speech("Say 'Please authenticate me'", 'openai')
play(instruction_audio)

audio = listen()
copyfile(audio, 'voiceprint.wav')
play('voiceprint.wav')

instruction_audio = text_to_speech("The voiceprint is saved to voiceprint.wav. You are all set!", 'openai')
play(instruction_audio)
