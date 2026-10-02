import os
import speech_recognition as sr
from openai import OpenAI
from elevenlabs import ElevenLabs, play
from dotenv import load_dotenv

load_dotenv()

# Client setup
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
eleven_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

# Conversation history
conversation_history = [
    {"role": "system", "content": "You are a helpful AI assistant. Please respond in English."}
]

def listen():
    """Listens for input from the microphone"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\n🎤 Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source, timeout=10)
    
    try:
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Could not understand, please try again.")
        return None
    except sr.RequestError:
        print("Network issue!")
        return None

def think(user_input):
    """Generates a response using GPT-4o"""
    conversation_history.append({"role": "user", "content": user_input})
    
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=conversation_history,
        max_tokens=300
    )
    
    reply = response.choices[0].message.content
    conversation_history.append({"role": "assistant", "content": reply})
    print(f"AI: {reply}")
    return reply

def speak(text):
    """Generates voice with ElevenLabs and plays it"""
    audio = eleven_client.text_to_speech.convert(
        text=text,
        voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel voice (default)
        model_id="eleven_multilingual_v2"
    )
    play(audio)

def run():
    print("=" * 40)
    print("🤖 Voice Agent is Active!")
    print("Say 'stop' or 'exit' to shut down")
    print("=" * 40)
    
    while True:
        user_input = listen()
        
        if user_input is None:
            continue
            
        if "stop" in user_input.lower() or "exit" in user_input.lower():
            print("Shutting down...")
            speak("Thank you! Talk to you later.")
            break
        
        reply = think(user_input)
        speak(reply)

if __name__ == "__main__":
    run()
