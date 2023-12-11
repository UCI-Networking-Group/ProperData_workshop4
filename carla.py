#!/usr/bin/env python3

import annotate
import gtts
from pathlib import Path
import numpy as np
import soundfile as sf
import speech_recognition as sr
import io
import os
import code
import subprocess
import time
from openai import OpenAI
ORG_ID = "org-edOxuQr5K7XudM03sd9x597s"

BOT_ID = "asst_6b1hYktWQEZUsdZW9nkypX6t"


# os.environ["OPENAI_API_KEY"] = API_KEY


class MediaPlayer(object):
    def __init__(self):
        self.running = None

    def play(self, filename):
        print(f"PLAYING {filename}")
        if self.running:
            self.stop()
        self.running = subprocess.Popen(["ffplay", "-autoexit", filename])

    def stop(self):
        if self.running:
            self.running.terminate()
            self.running.wait()
        self.running = None

    def is_playing(self):
        if self.running and self.running.poll() is None:
            return True
        return False


class Bot(object):
    def __init__(self, media_player):
        self.instructions = 'You are Carla, a digital privacy assistant. Base your replies off the json dataset sent in the first message. Your job is to report statistics about privacy regarding internet of things devices and trackers. Be very brief in your answers. when talking about the time, always express it in terms of hour and minutes only. Do not say the mac addresses. Do not say the domain names unless specifically requested for that. Do not use the character ". Speak like if you were a close friend. Be very precise and concise. Do not mention the data entries.'
        self.media_player = media_player
        self. client = OpenAI(
            organization=ORG_ID,
            api_key=API_KEY
        )
        self. assistant = self.client.beta.assistants.retrieve(BOT_ID)
        self. thread = self.client.beta.threads.create()
        self.interact(annotate.process_data_json(), False)

    def pysay(self, utterance):
        temp_file = "utter.mp3"
        obj = gtts.gTTS(text=utterance, lang='en', slow=False)
        obj.save(temp_file)
        self.media_player.play(temp_file)

    def interact(self, content, output=True):
        message = self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=content,
        )
        run = self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id,
            instructions=self.instructions
        )

        print("checking assistant status. ")
        while True:
            run = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread.id, run_id=run.id)

            if run.status == "completed":
                print("done!")
                messages = self.client.beta.threads.messages.list(
                    thread_id=self.thread.id)

                print("messages: ")
                for message in messages:
                    assert message.content[0].type == "text"
                    print({"role": message.role,
                           "message": message.content[0].text.value})
                    if message.role == 'assistant' and output:
                        self.pysay(message.content[0].text.value)
                        break  # we receive also old assistant messages
                break
            else:
                print("in progress...")
                time.sleep(5)

    def process_audio(self, audio):
        self.media_player.play("wait.opus")
        try:
            wav_bytes = audio.get_wav_data(convert_rate=16000)
            wav_stream = io.BytesIO(wav_bytes)
            audio_array, sampling_rate = sf.read(wav_stream)
            sf.write('test.wav', audio_array, sampling_rate)
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=Path('./test.wav'),
                language='en'
            )
            print("Whisper Recognition thinks you said " + str(transcript))
            if transcript.text.lower().startswith(
                    "carla") or transcript.text.lower().startswith("karla"):
                if "stop" in transcript.text.lower()[5:13]:
                    self.media_player.stop()
                else:
                    self.interact(transcript.text[5:])
            else:
                self.media_player.stop()
        except sr.UnknownValueError:
            print("Whisper Recognition could not understand audio")
        except sr.RequestError as e:
            print(
                "Could not request results from Whisper Recognition service; {0}".format(e))


if __name__ == "__main__":
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    recognizer.pause_threshold = 1  # 0.8
    recognizer.dynamic_energy_threshold = False  # True
    recognizer.energy_threshold = 4000  # 300

    media_player = MediaPlayer()
    bot = Bot(media_player)

    with microphone as source:
        while True:
            time.sleep(0.1)
            audio = recognizer.listen(source)
            bot.process_audio(audio)
            while media_player.is_playing():
                time.sleep(0.1)
