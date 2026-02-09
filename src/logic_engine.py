import os
import time
import json
from google import genai
from google.genai import types

# --- CONFIGURATION ---
# PASTE YOUR API KEY BELOW
API_KEY = "AIzaSyDTiTcTmrh_1BG-o5dtGSuu-ynR5ACksOM"

client = genai.Client(api_key=API_KEY)

# UPDATED: Using the Gemini 3 Pro Preview Model
MODEL_NAME = "gemini-flash-latest"

def analyze_logic(video_path, har_content):
    """
    Core function: Uploads video evidence + Network logs to Gemini 3
    and returns a JSON vulnerability assessment.
    """
    print(f"--- [LogicBreaker] Processing Video: {video_path} ---")

    # 1. Upload the Video
    try:
        # Uploading file to Google AI Studio
        video_file = client.files.upload(file=video_path)
        print(f"Uploading video to Gemini 3...")
    except Exception as e:
        return {"error": f"Failed to upload video: {str(e)}"}

    # 2. Wait for processing
    while video_file.state.name == "PROCESSING":
        print(".", end="", flush=True)
        time.sleep(2)
        video_file = client.files.get(name=video_file.name)

    if video_file.state.name == "FAILED":
        return {"error": "Video processing failed on Google's side."}

    print(f"\n[Video Ready] URI: {video_file.uri}")

    # 3. The "Red Team" Prompt
    prompt = f"""
    You are LogicBreaker, an expert automated security auditor.

    EVIDENCE PROVIDED:
    1. VIDEO: A screen recording of a user transaction.
    2. NETWORK LOGS (HAR Summary):
    ```json
    {har_content[:30000]}
    ```

    YOUR TASK:
    1. Map the Workflow (Video).
    2. Cross-Reference with Network Logs.
    3. Find Logic Bugs (Workflow Bypass, IDOR, Parameter Tampering).

    OUTPUT FORMAT (JSON ONLY):
    {{
        "analysis_summary": "Brief explanation of the workflow.",
        "vulnerability_found": true,
        "vulnerability_type": "Name of Bug or 'None'",
        "severity": "High/Medium/Low",
        "evidence": "Why is this a bug?",
        "exploit_script": "Python requests script (if bug found)."
    }}
    """

    print("--- Sending to Gemini 3 Brain... ---")

    # 4. Generate Content
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_uri(
                            file_uri=video_file.uri,
                            mime_type=video_file.mime_type),
                        types.Part.from_text(text=prompt)
                    ]
                )
            ],
            config=types.GenerateContentConfig(
                temperature=0.0
            )
        )

        # Clean JSON
        raw_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(raw_text)

    except Exception as e:
        return {"error": f"AI Analysis Failed: {str(e)}"}

# --- SELF-TEST BLOCK ---
if __name__ == "__main__":
    print(f"Testing Connection to {MODEL_NAME}...")
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents="Say 'LogicBreaker Gemini 3 Online' if you can hear me."
        )
        print(f"Server Response: {response.text}")
    except Exception as e:
        print(f"Connection Failed: {e}")
