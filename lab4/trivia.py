from voice_assistant_lib import *
init_voice_assistant({
    "api_key": "sk-abc...(YOUR API KEY)",
    "system_prompt": "Your name is TriviaGPT. You are the host of a trivia game. Continuously provide questions and verify the correctness of the answers."
})

response = chat("Let’s begin")
while True:
    print("Response: ", response)
    user_prompt = input("User Prompt:")
    response = chat(user_prompt)
