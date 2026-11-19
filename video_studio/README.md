# Travel360 Video Studio — map-explainer Shorts

A pipeline that renders a Hindi map-animation Short (9:16) from one JSON "episode" file, with neural
voice-over, word-synced camera moves, state highlights, sticker pops, cloud transitions, a collage ending,
a thumbnail and an SRT.
Style notes, script formula and checklist: [STYLE_GUIDE.md](STYLE_GUIDE.md).

## Setup (one time)

```bash
pip install edge-tts svgelements numpy scipy pillow fonttools brotli
# ffmpeg must be installed. The first run builds the map rasters (~40 s, cached in output/map_cache).
```

`edge-tts` needs `speech.platform.bing.com` to be reachable (in this cloud environment it goes through the HTTPS proxy automatically).

## Make a video

```bash
cd video_studio
python3 -m engine.render episodes/famous_food_every_state.json --stills 1,10,40   # check a few frames
python3 -m engine.render episodes/famous_food_every_state.json --preview          # 540p quick video (~30 s)
python3 -m engine.render episodes/famous_food_every_state.json                    # final 1080x1920
```

Output: `output/<episode>/<episode>.mp4`, `_thumbnail.jpg`, `captions.srt`, `mix.wav`.

## Episode format

```jsonc
{
  "voice": "hi-IN-MadhurNeural", "rate": "+25%", "watermark": "Travel360",
  "music": "synth",                // or "assets/music/track.mp3", or null
  "thumbnail": {"lines": ["हर राज्य का", "फेमस खाना"], "colors": ["white", "yellow"], "pill": "..."},
  "segments": [
    { "text": "narration for this part (one or two sentences)",
      "beats": [
        // a beat with no "at" happens when the segment starts; "at": "<word>" fires when that word is spoken
        {"camera": {"fit": ["mh"]}, "transition": "cut | fly | clouds",
         "show": {"state": "mh", "label": "वड़ा पाव", "sticker": "mh.png", "emoji": "🍔", "color": "yellow"}},
        {"at": "राजस्थान", "camera": {"fit": ["rj"]}, "show": {...}},
        {"camera": {"fit": "india"}, "transition": "clouds", "collage": true}
      ]}
  ]
}
```

- `camera.fit`: a list of state ids, or `"india"`. Optional: `pad` (bigger = more zoomed out), `max_zoom`, `dx`/`dy`.
- `show.sticker`: a PNG with a transparent background in `assets/stickers/` (AI portrait / food photo). If the file
  is missing, the `emoji` placeholder badge is used instead.
- `show.color`: yellow, green, cyan, orange, lime, teal, magenta, pink (cycles automatically if left out).
- A new camera beat fades out the previous stickers automatically (`"clear": false` keeps them).
- State ids: an ap ar as br ch ct dd dl dn ga gj hp hr jh jk ka kl ld mh ml mn mp mz nl or pb py rj sk tg tn tr up ut wb

## Credits / licences

- India states map: [@svg-maps/india](https://github.com/VictorCazanave/svg-maps) — CC BY 4.0
- Neighbouring land: Natural Earth via [world-atlas](https://github.com/topojson/world-atlas) (public domain / ISC)
- Fonts: Noto Sans Devanagari, Poppins — SIL Open Font License
