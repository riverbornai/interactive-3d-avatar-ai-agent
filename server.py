import os
import base64
import requests
import json
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from elevenlabs import ElevenLabs
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk

load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# Client setup
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=openai_api_key)

eleven_api_key = os.getenv("ELEVENLABS_API_KEY")
eleven_client = ElevenLabs(api_key=eleven_api_key) if eleven_api_key and len(eleven_api_key) > 10 else None

# History for conversation
conversation_history = [
    {"role": "system", "content": "You are a helpful AI voice assistant. Respond naturally and very concisely in English only. The user is talking to you via voice."}
]

def generate_azure_tts_with_visemes(text):
    """Generate audio and visemes (blendshapes) using Azure Speech Service"""
    try:
        speech_config = speechsdk.SpeechConfig(
            subscription=os.getenv("AZURE_SPEECH_KEY"), 
            region=os.getenv("AZURE_SPEECH_REGION")
        )
        # Force facial expression metadata
        speech_config.set_property(speechsdk.PropertyId.SpeechServiceResponse_RequestFacialExpression, "true")
        
        speech_config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
        )
        
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
        
        visemes = []
        
        def viseme_cb(evt):
            if evt.animation:
                anim_data = json.loads(evt.animation)
                visemes.append({
                    "time": evt.audio_offset / 10000,
                    "blendshapes": anim_data["BlendShapes"]
                })
                
        synthesizer.viseme_received.connect(viseme_cb)
        
        ssml = f"""
        <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xmlns:mstts='http://www.w3.org/2001/mstts' xml:lang='en-US'>
            <voice name='en-US-AvaMultilingualNeural'>
                <mstts:viseme type='FacialExpression'/>
                {text}
            </voice>
        </speak>
        """
        
        result = synthesizer.speak_ssml_async(ssml).get()
        
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            return base64.b64encode(result.audio_data).decode("utf-8"), visemes
        else:
            print(f"Azure TTS Error: {result.reason}")
            return "", []
    except Exception as e:
        print(f"Azure Exception: {e}")
        return "", []

@app.get("/", response_class=HTMLResponse)
async def get_index():
    try:
        with open("static/index.html", "r") as f:
            return f.read()
    except Exception as e:
        return f"Error loading index.html: {e}"

@app.post("/process-voice")
async def process_voice(audio: UploadFile = File(...)):
    try:
        audio_bytes = await audio.read()
        if not audio_bytes:
            return JSONResponse({"error": "Empty audio data"}, status_code=400)
        
        # Deepgram transcription
        deepgram_api_key = os.getenv("DEEPGRAM_API_KEY")
        url = "https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true&language=en-US"
        headers = {
            "Authorization": f"Token {deepgram_api_key}",
            "Content-Type": "audio/wav"
        }
        dg_response = requests.post(url, headers=headers, data=audio_bytes)
        
        if dg_response.status_code != 200:
            return JSONResponse({"error": "Speech transcription failed"}, status_code=500)
            
        dg_data = dg_response.json()
        alternatives = dg_data.get('results', {}).get('channels', [{}])[0].get('alternatives', [{}])
        user_text = alternatives[0].get('transcript', "") if alternatives else ""
        
        if not user_text.strip():
            return JSONResponse({"error": "No speech detected"})

        # OpenAI reasoning
        conversation_history.append({"role": "user", "content": user_text})
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=conversation_history,
            max_tokens=200
        )
        ai_text = response.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": ai_text})

        # Azure TTS with Visemes
        audio_base64 = ""
        visemes = []
        
        if os.getenv("AZURE_SPEECH_KEY"):
            audio_base64, visemes = generate_azure_tts_with_visemes(ai_text)

        # Fallbacks
        if not audio_base64:
            audio_base64 = generate_openai_tts(ai_text)

        if not audio_base64:
            return JSONResponse({"error": "Text-to-speech failed"}, status_code=500)

        return {
            "user_text": user_text,
            "ai_text": ai_text,
            "audio_base64": audio_base64,
            "visemes": visemes
        }

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

def generate_openai_tts(text):
    try:
        response = requests.post(
            "https://api.openai.com/v1/audio/speech",
            headers={
                "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={"model": "tts-1", "input": text, "voice": "alloy"}
        )
        if response.status_code == 200:
            return base64.b64encode(response.content).decode("utf-8")
    except: pass
    return ""

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

