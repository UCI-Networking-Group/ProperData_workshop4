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
)

CONFIG = {
    'wakewords': ['carla', 'karla'],
    'system_prompt': 'You are Carla, a voice assistant. Be friendly and concise.',

    'pause_threshold': 1,
    'dynamic_energy_threshold': False,
    'energy_threshold': 4000,
}

logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logging.INFO)
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


register_function(get_current_weather)


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
