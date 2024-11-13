from voice_assistant_lib import *
init_voice_assistant({
    "api_key": "sk-abc...(YOUR API KEY)",
    'wakewords': ['Translate'],
    'system_prompt': 'You are a translator from English to Chinese Mandarin. Your task is to translate user prompts into Chinese.'
})

while True:
    audio_in = listen()
    user_prompt = speech_to_text(audio_in)
    print("Prompt: ", user_prompt)

    if verify_wakeword(user_prompt):
        response = chat(user_prompt)
        print("Response: ", response)
        audio_out = text_to_speech(response)
        play(audio_out)
