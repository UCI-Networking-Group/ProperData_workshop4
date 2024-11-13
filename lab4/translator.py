from voice_assistant_lib import *
init_voice_assistant({
    "api_key": "sk-abc...(YOUR API KEY)",
    "system_prompt": "Your name is TranslatorGPT. You are a translator from English to Spanish. Your task is to translate user prompts into Spanish."
})

while True:
    user_prompt = input("User Prompt: ")
    response = chat(user_prompt)
    print("Response:", response)
