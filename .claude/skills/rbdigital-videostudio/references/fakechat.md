# 7. Fake chat (WhatsApp) (recipe — not yet tested)

Look: phone chat screen drawn entirely in code — header (avatar circle + name + "online"/"typing..."), chat wallpaper, green (outgoing) and white (incoming) bubbles with time + ticks, typing indicator (3 bouncing dots) before each incoming message, auto-scroll as messages stack, occasional zoom-in on a key message, emoji via text, voice-note bubble optional.
Best for: drama, funny conversations, client–agent situations, testimonials, scams awareness, sales (customer asks → you answer).
Note: don't copy WhatsApp's logo/branding; generic chat look (own colours close to it is fine).

## Flow (optional)
Only avatars: ONE sheet 2x2: `4 separate circular profile avatar illustrations in a 2x2 grid, <style>, plain solid background, no text`. Or skip and use initials circles.

## Build (common.py, all vector-drawn with PIL)
- Script format: list of (t, sender 'me'|'them'|'system', text) timed to VO or ~1.2–2.5 s apart (reading speed ~ 12 chars/s). Emoji: PIL can't render colour emoji reliably → avoid or use simple text like ":)" / draw icons.
- Bubble: rounded_rectangle with tail, max width 760, Poppins-Regular 40, time 24 grey bottom-right, blue double ticks for 'me'.
- Stack from bottom above input bar (y≈1700); when total height exceeds the screen, scroll up with ease_out over 0.25 s.
- Incoming: show typing indicator 0.6–1.2 s first ("typing..." in header too), then bubble pops (scale 0.9→1, ease_back). Outgoing: appears with slide-up.
- Drama beats: zoom 1.0→1.25 onto a message + shake; "blocked"/"deleted message" system bubbles.
- Audio: `notif` on incoming, soft `pop` on outgoing, `typing` clicks while typing indicator shows, music per mood (comedy/tense).
- Cheap render: precompute each bubble sprite, compose per frame.
