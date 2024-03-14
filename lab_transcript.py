from voice_assistant_lib import init_voice_assistant, listen, speech_to_text

CONFIG = {
    'pause_threshold': 1,
    'dynamic_energy_threshold': False,
    'energy_threshold': 4000,
}

init_voice_assistant(CONFIG)

while True:
    audio = listen()
    text = speech_to_text(audio)
    print(text)
