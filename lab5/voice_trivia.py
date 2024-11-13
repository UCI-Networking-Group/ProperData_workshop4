from voice_assistant_lib import *
init_voice_assistant({
    "api_key": "sk-abc...(YOUR API KEY)",
    "wakewords": ["Trivia"],
    "system_prompt": "You are the host of a trivia game. Continuously provide questions and verify the correctness of the answers."
})

response = chat("Let's begin")
print(response)
audio_out = text_to_speech(response)
play(audio_out)

while True:
    audio_in = listen()
    user_prompt = speech_to_text(audio_in)
    print("Prompt: ", user_prompt)

    if verify_wakeword(user_prompt):
        response = chat(user_prompt)
        print("Response: ", response)
        audio_out = text_to_speech(response)
        play(audio_out)
