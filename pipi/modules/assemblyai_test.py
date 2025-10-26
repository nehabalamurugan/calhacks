# Install the assemblyai package by executing the command "pip install assemblyai"

import assemblyai as aai
import re
import os
from dotenv import load_dotenv
import json
from google import genai
from datetime import datetime
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")


def transcribe_audio(audio_file: str = "temp_storage/audio.wav", start_phrase: str = "hi i'm ina"):
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
    
    # Wait for completion using built-in method
    transcript = transcriber.wait_for_completion(transcript.id)
    
  except Exception as e:
    print(f"Transcription error: {e}")
    raise

  if transcript.status == "error":
        raise RuntimeError(f"Transcription failed: {transcript.error}")

  # Save transcript JSON for debugging
  os.makedirs('temp_storage', exist_ok=True)
  # Create timestamped filename
  timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
  transcript_path = f'temp_storage/transcript_{timestamp}.json'
  with open(transcript_path, 'w') as f:
      json.dump(transcript.dict(), f, indent=2)

  # Detect which speaker said "hi i'm ina"
  start_phrase_pattern = re.compile(start_phrase, re.IGNORECASE)
  ina_speaker = None
  for utt in transcript.utterances:
      if start_phrase_pattern.search(utt.text):
          ina_speaker = utt.speaker
          break

  # If not found, default to first speaker
  if not ina_speaker:
      ina_speaker = transcript.utterances[0].speaker

  # Build structured turns
  turns = []
  for utt in transcript.utterances:
      speaker_name = "Ina" if utt.speaker == ina_speaker else f"Speaker_{utt.speaker}"
      turns.append({
          "speaker": speaker_name,
          "text": utt.text.strip()
      })

  # Construct final JSON-style object
  return turns

# output_json = transcribe_audio()
# print(output_json)

def extract_info(conversation_turns: list):
    """
    Extracts structured information about the other speaker
    using Gemini from a conversation transcript.
    """
    try:
        
        # Convert list to simple string format
        conversation_text = ""
        for turn in conversation_turns:
            conversation_text += f"{turn['speaker']}: {turn['text']}\n"
        
        prompt = f"""
        Analyze this conversation and extract:
        1. The name of the other speaker (not Ina)
        2. Their company/organization  
        3. Their date of birth (if mentioned)
        4. A summary of what was discussed
        
        Return ONLY valid JSON in this format:
        {{
          "other_speaker_name": "name or null",
          "company": "company or null", 
          "date_of_birth": "date or null",
          "conversation_summary": "summary text"
        }}
        
        Conversation:
        {conversation_text}
        """
        client = genai.Client(api_key=GOOGLE_API_KEY)
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )

        
        # Clean the response and extract JSON
        text = response.text.strip()
        print(f"Gemini response: {text}")
        
        # Try to find JSON in the response
        if "{" in text and "}" in text:
            start = text.find("{")
            end = text.rfind("}") + 1
            json_str = text[start:end]
            data = json.loads(json_str)
        else:
            raise ValueError("No JSON found in response")
            
    except Exception as e:
        print(f"Error extracting info: {e}")
        data = {
            "other_speaker_name": None,
            "company": None,
            "date_of_birth": None,
            "conversation_summary": "Error processing conversation"
        }

    return data

# list_conversation = [{'speaker': 'Ina', 'text': "Hi, I'm Ina."}, {'speaker': 'Speaker_B', 'text': 'How are you doing well. How are you, Ina?'}, {'speaker': 'Ina', 'text': 'Good.'}, {'speaker': 'Speaker_B', 'text': 'Do you remember how we first met?'}, {'speaker': 'Ina', 'text': 'Oh my God. We met at sgsi.'}, {'speaker': 'Speaker_B', 'text': 'Yeah. That was like more than a year ago.'}, {'speaker': 'Ina', 'text': "That's kind of crazy. SGSI was also low key, like a hackathon."}, {'speaker': 'Speaker_B', 'text': 'Yeah, that was a bit intense, but it was so fun.'}, {'speaker': 'Ina', 'text': 'Yeah. Do you think we were actually a high performance team?'}, {'speaker': 'Speaker_B', 'text': 'I think the high performance team was the friends we made along the way.'}, {'speaker': 'Ina', 'text': "I'm not sure you know who was in our team. Hannah."}, {'speaker': 'Speaker_C', 'text': 'Oh, Hannah.'}, {'speaker': 'Ina', 'text': 'Yeah.'}, {'speaker': 'Speaker_C', 'text': 'Nice.'}, {'speaker': 'Ina', 'text': 'Threshold. Hannah. Yeah, Threshold, Hannah. Threshold.'}, {'speaker': 'Speaker_C', 'text': 'Sydney.'}, {'speaker': 'Ina', 'text': 'She did threshold.'}, {'speaker': 'Speaker_C', 'text': "Because Sydney has two really good friends she made at SGSI and they're both named Hannah."}, {'speaker': 'Ina', 'text': 'Oh really? So I was like, this is not a.'}, {'speaker': 'Speaker_B', 'text': "Yeah, that's interesting."}, {'speaker': 'Ina', 'text': 'Yeah. Pish was in the group.'}, {'speaker': 'Speaker_B', 'text': 'Yeah.'}, {'speaker': 'Ina', 'text': "What do you think this smells like? Cuz it's like it smells like chemicals."}, {'speaker': 'Speaker_C', 'text': "The COVID is the vanilla one, but then it's blue inside, which makes me think it's the mint one. But it doesn't really smell like either vanilla or mint."}, {'speaker': 'Speaker_B', 'text': 'Wait, Ina, where do you get all these funny smelling things from?'}, {'speaker': 'Ina', 'text': "It's all horrible."}, {'speaker': 'Speaker_C', 'text': "This one from Visa. But this is. I used to love these as a kid. You couldn't get them in Europe cuz they like were a thing in the US and so when I had like a friend who went to the US for a trip and like everyone from our entire like middle school class asked her like to bring a bunch and she bought a bunch and then you could like order them from these like Facebook pages of like people who would get like dupes from China and try to sell them too and be like, oh, I went to the US and I brought them back."}, {'speaker': 'Speaker_B', 'text': 'I lowkey think Ina smelled whiteners in school.'}, {'speaker': 'Ina', 'text': "Yeah. Did you ever have like whiteners? You know what these are? These are like little like liquid things I didn't smell."}, {'speaker': 'Speaker_C', 'text': "I also didn't like the liquid one. I like the roller one."}, {'speaker': 'Ina', 'text': 'Did you ever eat chalk? People eat chalk.'}, {'speaker': 'Speaker_B', 'text': 'Like when they have calcium deficiency.'}, {'speaker': 'Ina', 'text': "Yeah, they're like actually like they like crave chalk and they just eat chalk. It's so strange to me that like that looks appetizing to them."}, {'speaker': 'Speaker_C', 'text': 'Yeah, strange to me. Then again, I see you eat a lot of stuff that is strange to me how it is appetizing.'}, {'speaker': 'Ina', 'text': 'And by that she means like carrots.'}, {'speaker': 'Speaker_B', 'text': 'What?'}, {'speaker': 'Speaker_C', 'text': "No, I love carrots. What do you mean? Like cabbage or like salad, like arugula, like spinach, like all of that. It's like what sheep eat."}, {'speaker': 'Ina', 'text': 'Sheep eat bro.'}, {'speaker': 'Speaker_C', 'text': 'I have beef with vegetarianism. Pun intended.'}, {'speaker': 'Speaker_B', 'text': 'Oh, my God.'}, {'speaker': 'Ina', 'text': "It took me so long to process what you were saying. I was like, you have beet beef with vegetarianism? Like, how? Okay, anyways. Okay, that's enough."}, {'speaker': 'Speaker_B', 'text': "If you have beef with vegetarianism, it's non vegetarian."}, {'speaker': 'Ina', 'text': "No, is bro. No, I'm just kidding."}, {'speaker': 'Speaker_C', 'text': 'Should go take a nap.'}, {'speaker': 'Speaker_B', 'text': "No, I'm just kidding."}, {'speaker': 'Ina', 'text': "Okay, that's enough of a conversation. It's going to break this API."}]

#here is an example of how to call it
audio = transcribe_audio('temp_storage/audio.wav')
meta_data =extract_info(audio)