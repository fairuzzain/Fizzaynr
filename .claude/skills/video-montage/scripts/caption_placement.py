"""Place caption ink inside reviewed safe areas, clear of reviewed subject regions.

Boxes are normalized [left, top, right, bottom], authored from inspected video
frames over time intervals. This validates geometry, not automatic face detection.
"""
import json
import math
from pathlib import Path
from PIL import Image


def read_regions(path, duration, video=None, cues=None):
    data = json.loads(Path(path).read_text())
    reviewed = float(data['reviewed_duration'])
    if not math.isfinite(reviewed) or abs(reviewed - duration) > .3:
        raise ValueError('protected regions must be reviewed for this full video duration')
    regions = data['regions']
    if video is not None:
        from caption_evidence import sha256
        if data.get('video_sha256') != sha256(video):
            raise ValueError('protected regions belong to a different source video')
    if cues is not None:
        windows = data.get('reviewed_intervals', [])
        for start, end, _ in cues:
            cursor = start
            for window in sorted(windows, key=lambda w: w['start']):
                left, right = window['start'], window['end']
                if not (math.isfinite(left + right) and 0 <= left < right <= duration + .05):
                    raise ValueError('invalid reviewed interval')
                if left <= cursor + 1e-6 and right > cursor:
                    cursor = right
            if cursor < end - 1e-6:
                raise ValueError('every caption interval needs reviewed subject geometry')
    if not isinstance(regions, list):
        raise ValueError('regions must be a list; empty means explicitly no protected subjects')
    for region in regions:
        start, end = float(region['start']), float(region['end'])
        box = region['box']
        if (not all(math.isfinite(v) for v in [start, end, *box]) or
            not 0 <= start < end <= duration + .05 or len(box) != 4 or
            not 0 <= box[0] < box[2] <= 1 or not 0 <= box[1] < box[3] <= 1):
            raise ValueError('invalid protected region interval or normalized box')
    return regions


def intersects(a, b, pad=0):
    return a[0] < b[2]+pad and a[2] > b[0]-pad and a[1] < b[3]+pad and a[3] > b[1]-pad


def bottom_center(overlay):
    """Faceless: one fixed lower baseline, orientation margins, no subject search."""
    width, height = overlay.size
    bounds = overlay.getchannel('A').getbbox()
    if not bounds:
        raise ValueError('caption rendered no visible ink')
    crop = overlay.crop(bounds)
    cw, ch = crop.size
    side = round(width * (.11 if height > width else .075))
    floor = int(height * (.83 if height > width else .90))
    left, top = (width-cw)//2, floor-ch
    if left < side or left+cw > width-side or top < height*.60:
        raise ValueError('caption cannot fit the lower band; re-chunk the SRT')
    result = Image.new('RGBA', overlay.size)
    result.alpha_composite(crop, (left, top))
    return result, [round(v/d, 6) for v,d in zip(
        [left, top, left+cw, floor], [width,height,width,height])]


def place(overlay, start, end, regions):
    width, height = overlay.size
    bounds = overlay.getchannel('A').getbbox()
    if not bounds:
        raise ValueError('caption rendered no visible ink')
    crop = overlay.crop(bounds)
    cw, ch = crop.size
    # Keep bottom 17% and side 11% clear in portrait; 10%/7.5% landscape.
    side = round(width * (.11 if height > width else .075))
    floor = int(height * (.83 if height > width else .90))
    ceiling = round(height * .60)
    active = [[r['box'][0]*width, r['box'][1]*height,
               r['box'][2]*width, r['box'][3]*height]
              for r in regions if start < r['end'] and end > r['start']]
    # Prefer the lowest centered position. Fixed candidates avoid arbitrary nudges.
    lower = list(range(floor, ceiling+ch-1, -max(1, round(height*.025))))
    # A close-up can occupy the entire lower band. Try the upper safe area,
    # never the platform's top 10%, before refusing the render.
    upper = list(range(round(height*.12)+ch, round(height*.40)+1, max(1,round(height*.025))))
    for bottom in lower + upper:
        top = bottom-ch
        for left in ((width-cw)//2, side, width-side-cw):
            box = [left, top, left+cw, bottom]
            if left < side or left+cw > width-side or top < height*.10:
                continue
            if any(intersects(box, protected, pad=height*.015) for protected in active):
                continue
            result = Image.new('RGBA', overlay.size)
            result.alpha_composite(crop, (left, top))
            return result, [round(v/d, 6) for v,d in zip(box,[width,height,width,height])]
    raise ValueError(f'caption at {start:.2f}–{end:.2f}s has no subject-clear position in the safe areas')
