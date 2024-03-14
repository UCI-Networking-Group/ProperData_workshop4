from voice_assistant_lib import init_voice_assistant, listen, speech_to_text, play, text_to_speech

CONFIG = {
    'pause_threshold': 1,
    'dynamic_energy_threshold': False,
    'energy_threshold': 4000,
}

init_voice_assistant(CONFIG)

while True:
    audio_in = listen()
    text = speech_to_text(audio_in)
    audio_out = text_to_speech(text)
    play(audio_out)
