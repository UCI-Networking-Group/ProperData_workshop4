from voice_assistant_lib import *
from extra_functions import *
from time import ctime

def get_time():
    '''
    Get current date and time.
    '''
    current_time = ctime()
    return current_time

init_voice_assistant({
    "api_key": "sk-...(YOUR API KEY HERE)",
    'wakewords': ['carla', 'karla'],
    'system_prompt': "You are Carla, a voice assistant. Be friendly and concise.",
})
register_function(get_time)
register_function(set_light_color)
register_function(search_locations)
register_function(get_weather_forecast)

while True:
    audio_in = listen()
    user_prompt = speech_to_text(audio_in)
    print("Prompt: ", user_prompt)

    if verify_wakeword(user_prompt):
        response = chat(user_prompt)
        print("Response: ", response)
        audio_out = text_to_speech(response)
        play(audio_out)
