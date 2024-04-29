import logging
from voice_assistant_lib import (
    init_voice_assistant,
    listen,
    play,
    speech_to_text,
    text_to_speech,
    verify_wakeword,
    chat,
    register_function,
    verify_voice,
)

CONFIG = {
    'wakewords': ['carla', 'karla'],
    'system_prompt': 'You are Carla, a voice assistant. Be friendly and concise.',

    'pause_threshold': 1,
    'dynamic_energy_threshold': False,
    'energy_threshold': 4000,
}

init_voice_assistant(CONFIG)

def get_current_weather(location):
    '''
    Get the current weather

    :param str location: The city and state, e.g. San Francisco, CA
    '''

    return {
        "temperature_celcius": 20,
        "weather": "sunny",
    }

def get_secret():
    '''
    Get the secret passphrase.
    The function will return the passphrase if it succesfully authenticate the user.
    '''

    instruction_audio = text_to_speech("Say 'Please authenticate me'", 'openai')
    play(instruction_audio)
    audio = listen()
    verified = verify_voice(audio, 'voiceprint.wav')

    if verified:
        return {
            'status': 'success',
            'result': 'Down The Rabbit Hole',
        }
    else:
        return {
            'status': 'failed',
            'error': 'Authentication failed',
        }


register_function(get_current_weather)
register_function(get_secret)

verify_voice('voiceprint.wav', 'voiceprint.wav')

while True:
    audio_in = listen()
    print(audio_in)

    text_in = speech_to_text(audio_in, 'openai')
    print(text_in)

    if verify_wakeword(text_in):
        text_out = chat(text_in)
        print(text_out)

        audio_out = text_to_speech(text_out, 'openai')
        print(audio_out)

        play(audio_out)
