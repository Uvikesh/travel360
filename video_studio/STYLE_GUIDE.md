# Map Shorts — Style Guide (reference analysis + practice notes)

Reference: "Kings of every Indian states" — YouTube Short, channel *Sharp Scribe*, watermark "Study vision",
70 s, 720×1280, 30 fps, 4 lakh+ views (Nov 2026). Analysis was done from its metadata, Hindi auto-captions and
storyboard frames (the video file itself is not downloadable from this environment).

---

## 1. Format at a glance

| Item | Reference | Our setting |
|---|---|---|
| Aspect | 9:16 vertical | 1080×1920 (higher than the reference's 720p) |
| FPS | 30 | 30 |
| Length | 70 s | 60–80 s (a 16-state list fits in ~75 s) |
| Language | Hinglish (Hindi with English words: "स्टेट्स", "डायनेस्टी", "फाउंडर", "पीक") | same |
| Voice pace | ~165 words / 70 s ≈ 2.4 words/s | edge-tts `+25%` ≈ 2.5 words/s |
| On-screen text | Only name tags (yellow pill), no subtitles | same (SRT is exported separately for YouTube CC) |
| Watermark | top-left, white at ~60% opacity | "Travel360" |

## 2. Visual style (what the eye sees)

1. **Map look**
   - Sea: near-black `#101012`. Neighbouring land: mid-grey `#969698`.
   - India: vertical gradient **blue (north) → purple (centre) → magenta → red (south)**.
   - Bold white outline around India, faint white state borders (~25–30% opacity).
   - A **screen-space "plaster" emboss texture** over everything. Its blob size stays the same at every zoom
     level, which gives the hand-made, paper-like look.
2. **Camera**
   - It never sits still. Each new state means a **fly**: zoom out a little, pan, zoom back in (≈0.6 s, ease-in-out).
   - On hold it slowly pushes in (Ken Burns, about 1% per second).
   - There are 2 **cloud transitions**: after the hook (zoom out to the whole of India) and at the CTA ending.
     White puffy clouds come in from the edges, then the camera "flies through" them.
3. **State highlight**
   - The current state is filled with a flat bright colour (yellow / green / cyan / orange / lime / teal),
     gets a white edge and a drop shadow, and **pops up** (scale 1.0 → 1.05 → 1.0) as if lifted off the map.
   - Do not use magenta or pink in the south: the map there is already magenta-red, so there is no contrast.
4. **Character / object sticker**
   - A cut-out (AI portrait / food photo) with a **thick white sticker border and a soft shadow**, placed at the
     centre of the state. It pops in with an `ease-out-back` (overshoot) animation, ≈0.38 s.
   - Height is about 40–45% of the frame width.
5. **Name tag**: a yellow `#FFC41E` rounded pill with bold black Devanagari text. It sits just below the sticker
   and pops in 0.12 s after it.
6. **Ending**: the camera zooms out to all of India, every highlight shows together, and all the stickers appear
   small, one by one (a collage). This last frame is also the best source for the thumbnail.

## 3. Script formula (scripting)

```
[0–8 s]   HOOK      — 2 names everyone knows (zoomed in, instant)
                      "महाराष्ट्र के शिवाजी महाराज तो राजस्थान के महाराणा प्रताप को तो सभी जानते हैं।"
[8–11 s]  PROMISE   — "पर इस वीडियो में पता करते हैं भारत के हर स्टेट के ..."   (clouds → whole India)
[11–65 s] LIST      — one line per state, 3–4 s each, same pattern:
                      "<state> के हीरो हैं <name>" / "<state> से थे <name>, जिन्होंने <one fact>"
                      Keep connectors varied: तो / वहीं / और / जबकि
[65–70 s] CTA       — "अपने फेवरेट ___ का नाम कमेंट्स में ज़रूर लिखना।"   (collage)
```

Rules:
- Each line holds **one fact**, short and crisp, with no dates or long numbers.
- Say the name **at the end of the sentence**, so that the sticker pop lands on the word the viewer hears.
- Add a "relatable" hook such as "RRR पिक्चर में दिखाए गए कोमारम भीम": a pop-culture link keeps people watching.
- The CTA question should be **opinion-based** ("आपके स्टेट का ___ कौन सा है?") because it brings comments.
- Description: a one-line intro, then a 👑/🍛 bullet list (name + state), an exam/learning angle
  ("UPSC, SSC ke liye useful"), then the CTA. Disclose AI images: "portraits are AI-generated illustrations".
- Tags/hashtags: topic + the 2 biggest names + "India map animation", "history shorts", "GK".

## 4. Voice

- Engine: Microsoft Edge neural TTS (free) via `edge-tts`.
  - `hi-IN-MadhurNeural` (male, closest to the documentary tone) ✅ default
  - `hi-IN-SwaraNeural` (female)
- `rate: +20…+25%`. Above that, Hindi conjuncts start to sound unclear.
- Spell English words in Devanagari ("स्टेट", "डिश") so the Hindi voice pronounces them in an Indian accent.
- Punctuation controls the pauses: `।` gives a full stop, `,` a short breath.
- Each segment is synthesised separately and **word timings** come back with it. This is how the sticker / camera
  syncs to an exact word (`"at": "राजस्थान"`).
- Music: by default a soft synth bed (generated, no copyright issue) at −22 dB, automatically ducked under the voice.
  For a real upload, put a trending / licensed track in `assets/music/` and set `"music": "assets/music/x.mp3"`.
- SFX: a whoosh on every camera move and a pop on every sticker. These are generated, not copied.
- Final loudness is −14 LUFS, the YouTube standard.

## 5. Quality checklist before upload

- [ ] 1080×1920, 30 fps, H.264 CRF 17, AAC 192k, −14 LUFS
- [ ] Every fact checked (names, states, spellings); Hindi spellings checked on the name tags
- [ ] Map: **use the official map of India** (all of J&K + Ladakh, including PoK and Aksai Chin). The
      SVG used for this practice (`@svg-maps/india`) is an older map (J&K and Ladakh not split). Check it
      against the Survey of India outline before uploading, or replace the SVG.
- [ ] AI images: one consistent style, transparent PNG, face/object centred, label "AI-generated" in the description
- [ ] First 1 second: a sticker + a highlighted state (the hook must be visible)
- [ ] Last frame: collage + CTA, so it loops nicely
- [ ] Credits: map data from @svg-maps/india (CC BY 4.0) and Natural Earth / world-atlas, in the description

## 6. Topic ideas in the same format

- Famous food of every state (✅ practice episode)
- One must-visit place in every state (Travel360 brand fit)
- Kings / freedom fighters of every state
- Famous temple / fort / festival / dance / sweet of every state
- Famous cricketer / actor / scientist of every state
