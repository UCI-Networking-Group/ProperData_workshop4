'''Voice assistant library'''

import io
import json
import logging
import os
import re
import subprocess
import time
from pathlib import Path
from typing import Any, Callable, Optional

import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
from openai import OpenAI
from platformdirs import user_cache_dir

DEFAULT_CONFIG = {
    'app_name': 'properdata-voice-assistant',

    'api_key': None,

    'wakewords': ['carla', 'karla'],
    'system_prompt': 'You are Carla, a voice assistant. Be friendly and concise.',

    'pause_threshold': 1,
    'dynamic_energy_threshold': False,
    'energy_threshold': 4000,

    'log_level': 'INFO',
}


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
        'audio_dir',
        'cache_dir',
        'speech_recognizer',
        'openai_api_key',
        'chat_messages',
        'chat_tools',
        'functions',
        'wakewords',
        'verification_model',
    )

    def __init__(self, config: dict[str, Any]):
        self.cache_dir = user_cache_dir(config['app_name'], ensure_exists=True)
        self.audio_dir = os.path.join(os.getcwd(), "audio")

        self.speech_recognizer = sr.Recognizer()
        self.speech_recognizer.pause_threshold = config['pause_threshold']
        self.speech_recognizer.dynamic_energy_threshold = config['dynamic_energy_threshold']
        self.speech_recognizer.energy_threshold = config['energy_threshold']

        self.wakewords: list[str] = config['wakewords']

        self.openai_api_key: Optional[str] = config['api_key'] or os.environ.get("OPENAI_API_KEY")

        self.chat_messages = [{
            "role": "system",
            "content": SYSTEM_PROMPT.format(config['system_prompt']).strip(),
        }]

        self.chat_tools: list[dict[str, Any]] = []
        self.functions: dict[str, Callable] = {}

        self.verification_model = None

g: Optional[__G] = None


def init_voice_assistant(config={}):
    global g

    logging.getLogger('speechbrain.utils.train_logger').setLevel(logging.WARNING)
    logging.getLogger('speechbrain.utils.fetching').setLevel(logging.WARNING)
    logging.getLogger('speechbrain.utils.parameter_transfer').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)

    config = dict(DEFAULT_CONFIG, **config)

    logging.basicConfig(
        format='%(asctime)s [%(levelname)s] %(message)s',
        level=logging.getLevelName(config['log_level'])
    )

    g = __G(config)
    logging.info('Voice assistant initialized')


def listen():
    '''Listen to the microphone and save the speech to a wave file'''

    logging.info('Listening...')

    with sr.Microphone() as source:
        try:
            audio = g.speech_recognizer.listen(source)
        except KeyboardInterrupt:
            logging.info('Exiting the program...')
            exit(0)

    os.makedirs(g.audio_dir, exist_ok=True)
    out_path = os.path.join(g.audio_dir, f'audio-{time.time_ns()}.wav')

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
        try:
            sd.wait()
        except KeyboardInterrupt:
            sd.stop()


def stop_playback():
    '''Stop audio playback'''
    sd.stop()


def verify_wakeword(text_in):
    return re.search(
        r'\b(' + '|'.join(map(re.escape, g.wakewords)) + r')\b',
        text_in, re.I
    ) is not None


def chat(text_in):
    '''Interact with the GPT'''
    openai = OpenAI(api_key=g.openai_api_key)

    g.chat_messages.append({
        "role": "user",
        "content": text_in,
    })

    while True:
        response = openai.chat.completions.create(
            #model="gpt-3.5-turbo",
            model="gpt-4o",
            messages=g.chat_messages,
            tools=g.chat_tools or None,
        )
        assistant_message = response.choices[0].message

        if not assistant_message.tool_calls:
            g.chat_messages.append(assistant_message)
            break

        for tool_call in assistant_message.tool_calls:
            f_name = tool_call.function.name
            f_args = tool_call.function.arguments
            func = g.functions[f_name]
            params = json.loads(f_args)
            result = func(**params)

            logging.info(
                'ChatGPT calls function %r with params %r',
                f_name, f_args,
            )

            g.chat_messages.append({
                "role": "function",
                "tool_call_id": tool_call.id,
                "name": assistant_message.tool_calls[0].function.name,
                "content": result if isinstance(result, str) else json.dumps(result),
            })

    return assistant_message.content


def register_function(func):
    '''Add a function to the GPT'''
    import docstring_parser

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


def speech_to_text(audio_path, backend=None):
    '''Speech to text module'''

    # Prefer openai backend if API_KEY is set
    if backend is None:
        if g.openai_api_key:
            backend = 'openai'
        else:
            backend = 'google'

    transcript = ''

    if backend == 'openai':
        # speech_recognizer's Whisper API is broken...
        openai = OpenAI(api_key=g.openai_api_key)

        response = openai.audio.transcriptions.create(
            model="whisper-1",
            file=Path(audio_path),
            language='en',
        )

        transcript = response.text
    else:
        with sr.AudioFile(audio_path) as source:
            audio = g.speech_recognizer.record(source)

        try:
            match backend:
                case 'sphinx':
                    transcript = g.speech_recognizer.recognize_sphinx(audio)
                case 'google':
                    transcript = g.speech_recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            logging.error('Could not understand audio')
        except sr.RequestError:
            logging.exception("Could not request results")

    return transcript


def text_to_speech(text, backend=None, voice="alloy"):
    '''Text to speech (TTS) module'''

    # Prefer openai backend if API_KEY is set
    if backend is None:
        if g.openai_api_key:
            backend = 'openai'
        else:
            backend = 'gtts'

    os.makedirs(g.audio_dir, exist_ok=True)
    out_path = os.path.join(g.audio_dir, f'tts-{time.time_ns()}.wav')

    if backend == 'openai':
        openai = OpenAI(api_key=g.openai_api_key)

        with openai.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice=voice,
            response_format="wav",
            input=text,
        ) as response:
            response.stream_to_file(out_path)
    elif backend == 'gtts':
        import gtts

        obj = gtts.gTTS(text=text, lang='en', slow=False)

        # gTTS returns MP3 data. Convert to WAV for compatibility.
        with io.BytesIO() as f:
            obj.write_to_fp(f)
            f.seek(0)
            data, fs = sf.read(f)
            sf.write(out_path, data, fs)
    elif backend == 'pico':
        subprocess.check_call(['pico2wave', f'-w={out_path}', '--', text])
    else:
        raise RuntimeError(f'Unknown backend: {backend}')

    return out_path


def verify_voice(audio_path, voiceprint_path):
    '''Verify if the speech matches the voiceprint, for authentication'''

    from speechbrain.inference.speaker import SpeakerRecognition

    if g.verification_model is None:
        g.verification_model = SpeakerRecognition.from_hparams(
            source="speechbrain/spkrec-ecapa-voxceleb",
            savedir=os.path.join(g.cache_dir, "speaker-recognition"),
        )
        logging.info('Speech verification model has been initialized')

    score_ts, prediction_ts = g.verification_model.verify_files(audio_path, voiceprint_path)

    score = score_ts.item()
    prediction = prediction_ts.item()

    logging.info("Speech verification: score=%.4f, result=%r", score, prediction)

    return prediction
