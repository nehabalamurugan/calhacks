# Install the assemblyai package by executing the command "pip install assemblyai"

import assemblyai as aai
import re
import os
from dotenv import load_dotenv
import json
from google import genai
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")


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
        1. The name of the other speaker (not Neha)
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

# list_conversation = [{'speaker': 'Neha', 'text': "Hi, I'm Neha."}, {'speaker': 'Speaker_B', 'text': 'How are you doing well. How are you, Neha?'}, {'speaker': 'Neha', 'text': 'Good.'}, {'speaker': 'Speaker_B', 'text': 'Do you remember how we first met?'}, {'speaker': 'Neha', 'text': 'Oh my God. We met at sgsi.'}, {'speaker': 'Speaker_B', 'text': 'Yeah. That was like more than a year ago.'}, {'speaker': 'Neha', 'text': "That's kind of crazy. SGSI was also low key, like a hackathon."}, {'speaker': 'Speaker_B', 'text': 'Yeah, that was a bit intense, but it was so fun.'}, {'speaker': 'Neha', 'text': 'Yeah. Do you think we were actually a high performance team?'}, {'speaker': 'Speaker_B', 'text': 'I think the high performance team was the friends we made along the way.'}, {'speaker': 'Neha', 'text': "I'm not sure you know who was in our team. Hannah."}, {'speaker': 'Speaker_C', 'text': 'Oh, Hannah.'}, {'speaker': 'Neha', 'text': 'Yeah.'}, {'speaker': 'Speaker_C', 'text': 'Nice.'}, {'speaker': 'Neha', 'text': 'Threshold. Hannah. Yeah, Threshold, Hannah. Threshold.'}, {'speaker': 'Speaker_C', 'text': 'Sydney.'}, {'speaker': 'Neha', 'text': 'She did threshold.'}, {'speaker': 'Speaker_C', 'text': "Because Sydney has two really good friends she made at SGSI and they're both named Hannah."}, {'speaker': 'Neha', 'text': 'Oh really? So I was like, this is not a.'}, {'speaker': 'Speaker_B', 'text': "Yeah, that's interesting."}, {'speaker': 'Neha', 'text': 'Yeah. Pish was in the group.'}, {'speaker': 'Speaker_B', 'text': 'Yeah.'}, {'speaker': 'Neha', 'text': "What do you think this smells like? Cuz it's like it smells like chemicals."}, {'speaker': 'Speaker_C', 'text': "The COVID is the vanilla one, but then it's blue inside, which makes me think it's the mint one. But it doesn't really smell like either vanilla or mint."}, {'speaker': 'Speaker_B', 'text': 'Wait, Ina, where do you get all these funny smelling things from?'}, {'speaker': 'Neha', 'text': "It's all horrible."}, {'speaker': 'Speaker_C', 'text': "This one from Visa. But this is. I used to love these as a kid. You couldn't get them in Europe cuz they like were a thing in the US and so when I had like a friend who went to the US for a trip and like everyone from our entire like middle school class asked her like to bring a bunch and she bought a bunch and then you could like order them from these like Facebook pages of like people who would get like dupes from China and try to sell them too and be like, oh, I went to the US and I brought them back."}, {'speaker': 'Speaker_B', 'text': 'I lowkey think Ina smelled whiteners in school.'}, {'speaker': 'Neha', 'text': "Yeah. Did you ever have like whiteners? You know what these are? These are like little like liquid things I didn't smell."}, {'speaker': 'Speaker_C', 'text': "I also didn't like the liquid one. I like the roller one."}, {'speaker': 'Neha', 'text': 'Did you ever eat chalk? People eat chalk.'}, {'speaker': 'Speaker_B', 'text': 'Like when they have calcium deficiency.'}, {'speaker': 'Neha', 'text': "Yeah, they're like actually like they like crave chalk and they just eat chalk. It's so strange to me that like that looks appetizing to them."}, {'speaker': 'Speaker_C', 'text': 'Yeah, strange to me. Then again, I see you eat a lot of stuff that is strange to me how it is appetizing.'}, {'speaker': 'Neha', 'text': 'And by that she means like carrots.'}, {'speaker': 'Speaker_B', 'text': 'What?'}, {'speaker': 'Speaker_C', 'text': "No, I love carrots. What do you mean? Like cabbage or like salad, like arugula, like spinach, like all of that. It's like what sheep eat."}, {'speaker': 'Neha', 'text': 'Sheep eat bro.'}, {'speaker': 'Speaker_C', 'text': 'I have beef with vegetarianism. Pun intended.'}, {'speaker': 'Speaker_B', 'text': 'Oh, my God.'}, {'speaker': 'Neha', 'text': "It took me so long to process what you were saying. I was like, you have beet beef with vegetarianism? Like, how? Okay, anyways. Okay, that's enough."}, {'speaker': 'Speaker_B', 'text': "If you have beef with vegetarianism, it's non vegetarian."}, {'speaker': 'Neha', 'text': "No, is bro. No, I'm just kidding."}, {'speaker': 'Speaker_C', 'text': 'Should go take a nap.'}, {'speaker': 'Speaker_B', 'text': "No, I'm just kidding."}, {'speaker': 'Neha', 'text': "Okay, that's enough of a conversation. It's going to break this API."}]

#here is an example of how to call it
audio = transcribe_audio('/Users/nehabalamurugan/Downloads/New Recording 43.m4a')
meta_data =extract_info(audio)