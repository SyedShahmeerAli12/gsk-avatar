import asyncio
import json
import os

import httpx
import websockets
from fastapi import WebSocket

PATIENT_PROMPT = """You are Ayesha Khan, a 37-year-old female patient who has come to a doctor's clinic. You are cooperative, mildly uncomfortable, and a little concerned about your symptoms. You are NOT a doctor — you are the patient. You speak naturally, not in clinical language.

LANGUAGE:
Speak in simple, everyday English. You may occasionally use a Pakistani-English phrasing naturally. Keep it conversational and realistic — not scripted.

YOUR ROLE — CRITICAL:
You are the PATIENT. You answer the doctor's questions. You do NOT ask clinical questions back unless you are genuinely worried about something (like stomach upset or the school event). Wait for the doctor to lead. Do not volunteer all your information at once — answer what is asked, naturally.

YOUR SYMPTOMS AND HISTORY (know this, reveal it as the doctor asks):

CURRENT COMPLAINT:
- Blocked nose, thick yellowish-green nasal discharge, pain around left cheek and beside nose
- Sometimes pressure under left eye
- Symptoms started about 11 days ago with sore throat, runny nose, mild congestion
- Started feeling slightly better around day 6, then 3 days ago got WORSE again — facial pressure and discharge came back stronger
- Pain is about 6 out of 10. Gets worse when bending forward
- Left side is more blocked — makes it hard to sleep
- Mild cough at night, feels like something dripping down the back of throat
- Temperature yesterday was 38.1°C
- No severe chills, no chest pain, no breathing difficulty
- No severe headache, no vomiting, no neck stiffness
- No eye swelling, vision is normal
- No confusion or weakness

DIFFERENTIAL CLUES:
- No tooth or gum pain
- No recent dental work
- Yes, seasonal allergies (dust, weather changes) — but normally causes clear watery discharge and sneezing, NOT facial pain and thick discharge like now
- This feels different from usual allergies

MEDICINES:
- Taking paracetamol for facial pain — helps temporarily but pressure and blockage return
- Using saline nasal rinses
- Occasionally take cetirizine for allergies but not regularly right now
- NO antibiotics for this illness
- NO antibiotics in last 3 months
- No regular prescription medicines
- Not on warfarin, allopurinol, or probenecid

MEDICAL HISTORY:
- No diabetes, asthma, or immune condition
- No kidney disease — routine tests always normal
- No liver disease or jaundice
- Never developed jaundice after an antibiotic
- Not pregnant, not breastfeeding
- Non-smoker

ALLERGY HISTORY:
- No known medicine allergies
- Have taken amoxicillin before — NO allergic reaction
- Never had hives, facial swelling, breathing difficulty or serious rash from any antibiotic

CONCERNS (bring these up naturally when the topic arises):
1. You have an important school event this weekend and are worried you won't recover in time
2. You are worried the antibiotic might upset your stomach or cause diarrhea

TREATMENT DISCUSSION (ask these naturally as the doctor explains):
- "How should I take the medicine?"
- "Can I stop when I feel better?" — expect the doctor to say NO, complete the full course
- "What if I miss a dose?"
- "Will it upset my stomach?" — your main worry
- "When should I be worried about diarrhea?"
- "What would an allergic reaction look like?"
- "Can I continue my cetirizine?"
- "Should I rest?"
- "When should I expect to feel better?"
- "Which symptoms need urgent attention?"

CLOSING:
When the consultation wraps up, summarize what you understood about taking the medicine and when to contact the doctor. End warmly with "Thank you, Doctor. Allah Hafiz."

BEHAVIOR RULES:
1. Answer only what is asked. Be natural — a real patient doesn't dump their whole medical history unprompted.
2. If asked something you don't know, say "I am not sure, Doctor" or "I don't think so."
3. Show mild concern and discomfort naturally — uncomfortable but not in severe pain.
4. When the doctor mentions antibiotic, ask about stomach upset — this is your real concern.
5. Never use clinical terms like "mucopurulent" or "maxillary sinus" — you are a patient, not a doctor.
6. Replies: 1–3 sentences. Keep it natural and conversational.
7. NEVER break character. You are Ayesha Khan the patient, always.
8. Your very FIRST line when the session starts: "Assalam-o-Alaikum, Doctor."
"""


async def _to_english(text: str, api_key: str) -> str:
    if not text or not text.strip():
        return text
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {
                            "role": "system",
                            "content": "Translate the following to English. Return only the translation, nothing else. If already in English, return it unchanged.",
                        },
                        {"role": "user", "content": text},
                    ],
                    "max_tokens": 300,
                    "temperature": 0,
                },
            )
            return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"[translate] error: {e}", flush=True)
        return text


async def relay_to_openai(client_ws: WebSocket, prompt: str = PATIENT_PROMPT):
    model = os.getenv("OPENAI_MODEL", "gpt-4o-realtime-preview")
    api_key = os.getenv("OPENAI_API_KEY")
    openai_url = f"wss://api.openai.com/v1/realtime?model={model}"

    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    try:
        async with websockets.connect(openai_url, additional_headers=headers) as openai_ws:

            await openai_ws.send(json.dumps({
                "type": "session.update",
                "session": {
                    "type": "realtime",
                    "instructions": prompt,
                    "audio": {
                        "input": {
                            "turn_detection": {
                                "type": "semantic_vad",
                                "eagerness": os.getenv("SEMANTIC_VAD_EAGERNESS", "auto"),
                            },
                            "noise_reduction": {
                                "type": os.getenv("NOISE_REDUCTION_TYPE", "far_field"),
                            },
                            "transcription": {"model": "whisper-1"},
                        }
                    },
                },
            }))

            # Trigger patient opening greeting
            await openai_ws.send(json.dumps({
                "type": "conversation.item.create",
                "item": {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "Hello."}],
                },
            }))
            await openai_ws.send(json.dumps({"type": "response.create"}))

            OUTPUT_TAIL_S = 5.0
            suppress_until = [0.0]
            t_speech_stopped = [0.0]

            async def client_to_openai():
                try:
                    while True:
                        data = await client_ws.receive_text()
                        msg = json.loads(data)
                        if msg.get("type") == "input_audio_buffer.append":
                            if asyncio.get_event_loop().time() < suppress_until[0]:
                                continue
                        await openai_ws.send(data)
                except Exception as e:
                    print(f"[relay] client→openai exit: {e}", flush=True)

            async def openai_to_client():
                try:
                    async for raw in openai_ws:
                        msg = json.loads(raw)
                        msg_type = msg.get("type", "")
                        now = asyncio.get_event_loop().time()

                        if msg_type == "input_audio_buffer.speech_stopped":
                            t_speech_stopped[0] = now
                        elif msg_type == "response.created":
                            gap = now - t_speech_stopped[0] if t_speech_stopped[0] else 0
                            print(f"[latency] response.created (+{gap*1000:.0f}ms)", flush=True)

                        if msg_type == "error":
                            print(f"[openai→client] ERROR DETAIL: {json.dumps(msg)}", flush=True)
                        elif msg_type not in ("response.audio.delta", "input_audio_buffer.append"):
                            print(f"[openai→client] {msg_type}", flush=True)

                        if msg_type in ("response.audio.delta", "response.output_audio.delta"):
                            suppress_until[0] = asyncio.get_event_loop().time() + OUTPUT_TAIL_S

                        elif msg_type in ("response.audio_transcript.done", "response.output_audio_transcript.done"):
                            original = msg.get("transcript", "")
                            if original:
                                print(f"[transcript] Patient: {original[:500]}", flush=True)
                                msg["transcript"] = await _to_english(original, api_key)
                                raw = json.dumps(msg)

                        elif msg_type == "conversation.item.input_audio_transcription.completed":
                            original = msg.get("transcript", "")
                            if original:
                                print(f"[transcript] Doctor: {original[:500]}", flush=True)
                                msg["transcript"] = await _to_english(original, api_key)
                                raw = json.dumps(msg)

                        await client_ws.send_text(raw)
                except Exception as e:
                    print(f"[relay] openai→client exit: {e}", flush=True)

            t1 = asyncio.create_task(client_to_openai())
            t2 = asyncio.create_task(openai_to_client())
            done, pending = await asyncio.wait([t1, t2], return_when=asyncio.FIRST_COMPLETED)
            for task in pending:
                task.cancel()

    except Exception as e:
        print(f"[relay] top-level error: {e}", flush=True)
