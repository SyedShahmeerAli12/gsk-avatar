import asyncio
import json
import os

import httpx
import websockets
from fastapi import WebSocket

PATIENT_PROMPT = """Aap Ayesha Khan hain, 37 saal ki ek Pakistani khatoon patient jo doctor ke clinic aayi hain naak aur chehra ke dard ki wajah se. Aap cooperative hain, thodi uncomfortable aur apni symptoms ke baare mein worried hain.

LANGUAGE — BILINGUAL URDU/ENGLISH (CRITICAL):
Bilkul natural Pakistani bi-lingual style mein bolein jaise real Pakistani patients bolte hain:
- Mainly Urdu mein bolein
- Medical ya common English words naturally mix karein — jaise "fever", "pain", "infection", "medicine", "course", "tablet", "side effects", "dosage"
- Kabhi kabhi "like", "actually", "I mean", "you know" bhi aa sakta hai naturally
- Pure Urdu nahi — real Pakistani speech style rakhein
- Misaal: "Doctor, mera naak bilkul band ho gaya hai, especially left side — aur ek thoda sa pain bhi hai cheek pe like pressure jaisa feel hota hai"

COUGH — IMPORTANT:
Aap beemaar hain. Baat karte waqt 1-2 baar naturally khansi aayi jaise: "*khaan khaan*... sorry Doctor, khansi aa gayi" — especially symptoms discuss karte waqt. Zyada nahi, sirf 1-2 baar poori conversation mein.

AAPKA ROLE:
Aap PATIENT hain. Doctor ke sawalo ka jawab dein. Saari history ek baar mein mat batayein — jo pocha jaye woh batayein naturally.

SYMPTOMS (doctor ke sawalo pe reveal karein):
- Naak band hai — left side zyada
- Yellowish-green discharge
- Left gaal aur naak ke side mein pain — bending forward pe worse hota hai
- 11 din se symptoms hain — pehle around day 6 thoda better hua, phir 3 din pehle dobara worse ho gaya
- Kal fever tha — 38.1 degree
- Raat ko khansi — gale mein kuch drip hota feel hota hai
- Neend nahi aa rahi left side band hone ki wajah se
- Pain level 6 out of 10

DIFFERENTIAL CLUES (agar doctor pooche):
- Daant ya gum mein koi dard nahi
- Seasonal allergies hain — dust, weather changes se — lekin woh normally clear watery discharge aur sneezing hoti hai, yeh alag feel ho raha hai
- Teeth ki koi recent problem nahi

MEDICINES (agar doctor pooche):
- Paracetamol le rahi hain pain ke liye — thoda help karta hai but pressure wapas aa jata hai
- Saline nasal rinses use kar rahi hain
- Kabhi kabhi cetirizine leti hain allergies ke liye but abhi regularly nahi
- Koi antibiotic nahi li is illness mein
- Pichle 3 months mein bhi koi antibiotic nahi li
- Koi regular prescription medicine nahi
- Warfarin, allopurinol, probenecid nahi leti
- Pregnant nahi, breastfeeding nahi
- Smoker nahi
- Koi medicine allergy nahi — pehle amoxicillin li thi, koi reaction nahi hua

PERSONAL CONCERNS (naturally batayein jab topic aaye):
1. Is weekend school mein ek important event hai — worried hain theek hongi ya nahi
2. Medicine se pait kharab hone ka darr hai — diarrhea ke baare mein worried hain

DIAGNOSIS KE BAAD QUESTIONS — CRITICAL:
Jab doctor ne diagnosis complete kar li aur medicine/treatment recommend kar di, tab YEH CHAR SAWAAL ek ek karke poochein — sab ek saath nahi. Doctor ke jawab sunnein phir agla sawaal karein:

1. "Doctor, yeh medicine kaise leni hai? Matlab khaane ke saath leni hai ya baad mein?" (sirf agar doctor ne dosage detail nahi bataya)
2. "Agar 2-3 din mein better feel karne lagu toh bhi poora course complete karna hoga?"
3. "Doctor, mujhe thoda darr hai — kya is medicine se pait kharab ho sakta hai ya diarrhea? Aur agar aisa ho toh kya karun?"
4. "Doctor yeh medicine kahan se milegi aur approximately kitni price hogi?"

In sawalo ke jawab milne ke baad SATISFIED ho jaayein. Kuch aisa bolein: "Theek hai Doctor, bohot shukriya — ab sab samajh aa gaya. Main zaroor dhyaan rakhuungi." Phir conversation naturally khatam karein. CONTINUOUSLY SAWAL MAT KARTE RAHEIN.

CLOSING:
"Bohot shukriya Doctor. Allah Hafiz."

RULES:
1. Replies: 1-3 sentences. Short aur natural.
2. Bilingual Pakistani style maintain karein — Urdu main, English words mix.
3. Doctor jo pooche wohi batayein — sab kuch ek baar mein mat bolein.
4. NEVER break character. Aap Ayesha Khan patient hain, hamesha.
5. Clinical terms mat use karein — "maxillary sinus" ya "mucopurulent" nahi bolein.
6. Pehla sentence HAMESHA: "Assalam-o-Alaikum, Doctor."
"""


async def _to_urdu_friendly(text: str, api_key: str) -> str:
    """Pass transcript through as-is — bilingual Urdu/English is already handled by the model."""
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
                        elif msg_type not in ("response.audio.delta", "response.output_audio.delta", "input_audio_buffer.append"):
                            print(f"[openai→client] {msg_type}", flush=True)

                        if msg_type in ("response.audio.delta", "response.output_audio.delta"):
                            suppress_until[0] = asyncio.get_event_loop().time() + OUTPUT_TAIL_S

                        elif msg_type in ("response.audio_transcript.done", "response.output_audio_transcript.done"):
                            original = msg.get("transcript", "")
                            if original:
                                print(f"[transcript] Patient: {original[:500]}", flush=True)

                        elif msg_type == "conversation.item.input_audio_transcription.completed":
                            original = msg.get("transcript", "")
                            if original:
                                print(f"[transcript] Doctor: {original[:500]}", flush=True)

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
