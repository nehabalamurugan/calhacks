# Install the assemblyai package by executing the command "pip install assemblyai"

import assemblyai as aai
import re
import os
from dotenv import load_dotenv

load_dotenv()

def transcribe_audio(audio_file: str = "/Users/nehabalamurugan/Downloads/New Recording 43.m4a", start_phrase: str = "hi i'm neha"):
  aai.settings.api_key = os.getenv('ASSEMBLYAI_API_KEY')
  
  if not aai.settings.api_key:
    raise ValueError("ASSEMBLYAI_API_KEY not found in environment variables")

  print(f"Starting transcription of: {os.path.basename(audio_file)}")
  print("This may take several minutes for long audio files...")

  config = aai.TranscriptionConfig(
    speech_model=aai.SpeechModel.universal,
    speaker_labels=True,
    summarization=True,
    summary_model="informative",
    summary_type="bullets"
  )

  # Use transcribe_async for longer files
  transcriber = aai.Transcriber(config=config)
  
  try:
    # For files longer than 5 minutes, use async transcription
    transcript = transcriber.transcribe(audio_file)
    
    # Wait for completion if it's still processing
    while transcript.status not in ['completed', 'error']:
      print(f"Status: {transcript.status}... waiting")
      transcript = transcriber.get_transcript(transcript.id)
      import time
      time.sleep(5)  # Wait 5 seconds before checking again
    
  except Exception as e:
    print(f"Transcription error: {e}")
    raise

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
      "turns": turns
  }

  return conversation_chunk

print(transcribe_audio())


