import streamlit as st
import requests
import os
import tempfile

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

st.title("🎯 Sales Pitch Analyzer")
st.write("Upload a voice recording of your sales pitch. We'll transcribe it and GPT-4 will give you detailed feedback.")

uploaded_file = st.file_uploader("Upload your sales pitch (WAV, MP3, M4A)", type=["wav", "mp3", "m4a"])

if uploaded_file is not None:
    st.audio(uploaded_file, format="audio/wav")
    st.success("Recording uploaded. Transcribing...")
    
    # Save audio to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(uploaded_file.read())
        audio_path = tmp_file.name
    
    # Transcribe with Deepgram
    with open(audio_path, 'rb') as audio_file:
        dg_response = requests.post(
            "https://api.deepgram.com/v1/listen",
            headers={
                "Authorization": f"Token {DEEPGRAM_API_KEY}",
                "Content-Type": "audio/wav"
            },
            data=audio_file
        )
    
    if dg_response.status_code != 200:
        st.error("Deepgram transcription failed.")
    else:
        transcript = dg_response.json()["results"]["channels"][0]["alternatives"][0]["transcript"]
        st.markdown("### 📄 Transcript")
        st.write(transcript)
        
        st.markdown("### 🤖 Analyzing your pitch with GPT-4...")
        
        prompt = f"""
You are a sales pitch coach. A salesperson has submitted the transcript of their pitch below.
Evaluate it across the following 6 categories (1–10 scale):
1. Clarity and confidence
2. Structure and flow
3. Communication of value
4. Personalization
5. Objection handling (if applicable)
6. Call to action

Provide a score for each, a final letter grade (A+ to F), and 2–3 sentences of feedback per category.
End with 3 specific, constructive recommendations for improvement.

Transcript:
{transcript}
"""
        
        openai_response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7
            }
        )
        
        if openai_response.status_code != 200:
            st.error("OpenAI analysis failed.")
        else:
            analysis = openai_response.json()["choices"][0]["message"]["content"]
            st.markdown("### 📝 Feedback")
            st.markdown(analysis)
