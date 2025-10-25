# Install the assemblyai package by executing the command "pip install assemblyai"

import assemblyai as aai
import re
import os
from dotenv import load_dotenv

load_dotenv()

def transcribe_audio(audio_file: str = "/Users/nehabalamurugan/Downloads/New Recording 41.m4a", start_phrase: str = "hi i'm neha"):
  aai.settings.api_key = os.getenv('ASSEMBLYAI_API_KEY')

  config = aai.TranscriptionConfig(speech_model=aai.SpeechModel.universal,speaker_labels=True,summarization=True,summary_model="informative",summary_type="bullets")

  transcript = aai.Transcriber(config=config).transcribe(audio_file)

  if transcript.status == "error":
        raise RuntimeError(f"Transcription failed: {transcript.error}")


  # Detect which speaker said "hi i'm neha"
  start_phrase_pattern = re.compile(start_phrase, re.IGNORECASE)
  neha_speaker = None
  for utt in transcript.utterances:
      if start_phrase_pattern.search(utt.text):
          neha_speaker = utt.speaker
          break

  # If not found, default to first speaker
  if not neha_speaker:
      neha_speaker = transcript.utterances[0].speaker

  # Build structured turns
  turns = []
  for utt in transcript.utterances:
      speaker_name = "Neha" if utt.speaker == neha_speaker else f"Speaker_{utt.speaker}"
      turns.append({
          "speaker": speaker_name,
          "text": utt.text.strip()
      })

  # Construct final JSON-style object
  conversation_chunk = {
      "conversation_id": audio_file.split("/")[-1].split(".")[0],
      "turns": turns,
      "summary": transcript.summary if hasattr(transcript, "summary") else None
  }

  return conversation_chunk

print(transcribe_audio())


