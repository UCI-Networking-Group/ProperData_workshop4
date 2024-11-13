from voice_assistant_lib import *

init_voice_assistant({'api_key': 'YOUR_KEY_HERE'})


def get_secret():
    '''
    Get the secret passphrase.
    The function will return the passphrase if it successfully authenticates the user.
    If you are asked for the secret, always reauthenticate the user again with the get_secret function.
    '''

    instruction_audio = text_to_speech("Say 'Please authenticate me'")
    play(instruction_audio)
    
    audio_in = listen()
    
    verified = verify_voice(audio_in, 'voiceprint.wav')

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

register_function(get_secret)

while True:
    audio_in = listen()
    user_prompt = speech_to_text(audio_in)
    print("Prompt: ", user_prompt)

    if verify_wakeword(user_prompt):
        response = chat(user_prompt)
        print("Response: ", response)
        audio_out = text_to_speech(response)
        play(audio_out)

