import os
import uuid
from dotenv import load_dotenv
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
import google.generativeai as genai
from gtts import gTTS

# configure
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI()

# routes
@app.get("/", response_class=HTMLResponse)
async def text_send():
    return '''
<html>
    <body>
        <form action="/result" method="post">
            <textarea name="text" rows="5" cols="40"></textarea>
            <br>
            <input type="submit" value="translate to audio">
        </form>
    </body>
</html>
'''

@app.post("/result", response_class=HTMLResponse)
def translate(text: str = Form(...)):
    model = genai.GenerativeModel("gemini-flash-latest")
    response = model.generate_content(text)

    if not response.text:
        raise HTTPException(status_code=500, detail="No text generated")

    filename = f"{uuid.uuid4().hex}.mp3"

    tts = gTTS(response.text, lang="en")
    tts.save(filename)

    return f'''
<html>
    <body>
        <h3>Result</h3>
        <p>{response.text}</p>

        <h3>Audio Output</h3>
        <audio controls>
            <source src="/audio/{filename}" type="audio/mpeg">
        </audio>

        <br><br>
        <a href="/">Go Back</a>
    </body>
</html>
'''

@app.get("/audio/{filename}")
async def fileOutput(filename: str):
    if not os.path.exists(filename):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(filename, media_type="audio/mpeg")
