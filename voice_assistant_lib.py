'''Voice assistant library'''

import json
import logging
import os
import re
import time
from pathlib import Path
from typing import Any, Callable, Optional

import docstring_parser
import gtts
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
from openai import OpenAI
from platformdirs import user_cache_dir

# https://raw.githubusercontent.com/spdustin/ChatGPT-AutoExpert/main/_system-prompts/voice-conversation.md
SYSTEM_PROMPT = """
You are a version of ChatGPT that has been customized as a voice assistant.

The user is talking to you over voice, and your response will be read out loud with realistic text-to-speech (TTS) technology.

Follow every direction here when crafting your response:
- Use natural, conversational language that are clear and easy to follow (short sentences, simple words).
- Clarify: when there is ambiguity, ask clarifying questions, rather than make assumptions.
- Don't ask them if there's anything else they need help with (e.g. don't say things like "How can I assist you further?").
- Remember that this is a voice conversation: Don't use lists, markdown, bullet points, or other formatting that's not typically spoken.
- If something doesn't make sense, it's likely because you misheard them. There wasn't a typo, and the user didn't mispronounce anything.

Here are additional instructions from the user outlining your goals and how you should respond:

{0}
"""


class __G:
    __slots__ = (
        'cache_dir',
        'speech_recognizer',
        'openai_client',
        'chat_messages',
        'chat_tools',
        'functions',
        'wakewords',
    )

    def __init__(self, config: dict[str, Any]):
        self.cache_dir = user_cache_dir(config['app_name'], ensure_exists=True)

        self.speech_recognizer = sr.Recognizer()
        self.speech_recognizer.pause_threshold = config['pause_threshold']
        self.speech_recognizer.dynamic_energy_threshold = config['dynamic_energy_threshold']
        self.speech_recognizer.energy_threshold = config['energy_threshold']

        self.wakewords: list[str] = config['wakewords']

        self.openai_client = OpenAI(api_key=config.get('api_key'))
        logging.getLogger('httpx').setLevel(logging.WARNING)

        self.chat_messages = [{
            "role": "system",
            "content": SYSTEM_PROMPT.format(config['system_prompt']).strip(),
        }]

        self.chat_tools: list[dict[str, Any]] = []
        self.functions: dict[str, Callable] = {}


g: Optional[__G] = None


def init_voice_assistant(config):
    global g
    g = __G(config)
    logging.info('Voice assistant initialized')


def listen():
    '''Listen to the microphone and save the speech to a wave file'''

    logging.info('Listening...')

    with sr.Microphone() as source:
        audio = g.speech_recognizer.listen(source)

    out_path = os.path.join(g.cache_dir, f'audio-{time.time_ns()}.wav')

    with open(out_path, "wb") as f:
        f.write(audio.get_wav_data(convert_rate=16000))

    logging.info('Audio saved to %s', out_path)

    return out_path


def play(audio_path, block=True):
    '''Play a wave file'''

    logging.info('Playing %s ...', audio_path)

    data, fs = sf.read(audio_path)
    sd.play(data, fs)

    if block:
        sd.wait()


def verify_wakeword(text_in):
    return re.search(
        r'\b(' + '|'.join(map(re.escape, g.wakewords)) + r')\b',
        text_in, re.I
    ) is not None


def chat(text_in):
    '''Interact with the GPT'''

    g.chat_messages.append({
        "role": "user",
        "content": text_in,
    })

    while True:
        response = g.openai_client.chat.completions.create(
            #model="gpt-3.5-turbo",
            model="gpt-4-0125-preview",
            messages=g.chat_messages,
            tools=g.chat_tools,
        )
        assistant_message = response.choices[0].message

        if not assistant_message.tool_calls:
            g.chat_messages.append(assistant_message)
            break

        for tool_call in assistant_message.tool_calls:
            func = g.functions[tool_call.function.name]
            params = json.loads(tool_call.function.arguments)
            result = func(**params)

            g.chat_messages.append({
                "role": "function",
                "tool_call_id": tool_call.id,
                "name": assistant_message.tool_calls[0].function.name,
                "content": result if isinstance(result, str) else json.dumps(result),
            })

    return assistant_message.content


def register_function(func):
    '''Add a function to the GPT'''

    # Populate the function description from docstring
    docstring = docstring_parser.parse(func.__doc__)

    type_mapping = {
        "int": "number",
        "float": "number",
        "str": "string",
        "bool": "boolean",
    }

    param_properties = {
        p.arg_name: {
            "type": type_mapping[p.type_name],
            "description": p.description,
        } for p in docstring.params
    }

    description = docstring.short_description

    if docstring.long_description:
        description += "\n\n" + docstring.long_description

    g.chat_tools.append({
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": param_properties,
                "required": list(param_properties.keys())
            }
        }
    })
    g.functions[func.__name__] = func


def speech_to_text(audio_path):
    '''Speech to text module'''

    try:
        response = g.openai_client.audio.transcriptions.create(
            model="whisper-1",
            file=Path(audio_path),
            language='en',
        )
        transcript = response.text
    except sr.UnknownValueError:
        logging.error('Whisper Recognition could not understand audio')

    return transcript


def text_to_speech(text, backend='openai'):
    '''Text to speech (TTS) module'''

    out_path = os.path.join(g.cache_dir, f'tts-{time.time_ns()}.wav')

    if backend == 'openai':
        with g.openai_client.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice="alloy",
            response_format="wav",
            input=text,
        ) as response:
            response.stream_to_file(out_path)
    elif backend == 'gtts':
        obj = gtts.gTTS(text=text, lang='en', slow=False)
        obj.save(out_path)

    return out_path
