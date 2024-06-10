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
    'system_prompt': "You are Carla, the voice assistant of the summer program on privacy, IoT, and AI. Here it is the summer program information: The ProperData Center at UCI will host a week long, commuter, summer program for high school students interested in pursuing a bachelor's degree in computer science, computer engineering, data science, or related field. Participants will work with top faculty and researchers and will be introduced to the fields of privacy, Internet of Things, and Artificial Intelligence. Opportunities for career development and post-secondary education preparation will also be provided. High school students: rising 10th, 11th, or 12th grade Minimum 3.0 unweighted cumulative GPA. PROGRAM DATES: JUNE 23 - JUNE 28, 2024 M-F 9:00am - 4:00pm. The program offers Hands-on experience with: Raspberry Pi microcomputers, Python programming, Building a voice assistant powered by OpenAI ChatGPT, applications and threats of generative AI. Instructors: Athina Markopoulou, Luca Baldesi, Cui Hao, Tu Le, Ernest Garrison. Students: John Doe, Jane Smith, Mike Tyson. For your answers, use an informal but elegant style; be funny. Be very concise in your answers, reply with two sentences.",

    'pause_threshold': 1,
    'dynamic_energy_threshold': False,
    'energy_threshold': 4000,
}

init_voice_assistant(CONFIG)


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
