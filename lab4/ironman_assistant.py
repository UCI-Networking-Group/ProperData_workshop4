from voice_assistant_lib import *
init_voice_assistant({
    "api_key": "sk-abc...(YOUR API KEY)",
    "system_prompt": "Your name is IronmanGPT. Respond like you
are Ironman from the Marvel Universe."
})

while True:
    user_prompt = input("User Prompt: ")
    response = chat(user_prompt)
    print("Response:", response)
