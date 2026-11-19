#!/usr/bin/env python3
"""
analyze_logo.py - Analyzes a logo image to extract visual attributes and pre-fill the Logo Reveal template.
"""

import os
import sys
import json
import argparse
import numpy as np
from PIL import Image

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def analyze_logo_image(image_path, target_ratio="9:16", bg_choice=None):
    """
    Analyzes an input logo image:
    - Dimensions, aspect ratio, transparency
    - Dominant background and foreground colors
    - Prepares a clean centered canvas for video generation (16:9, 9:16, or 1:1)
    - Returns structured metadata for the prompt template.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Logo image not found: {image_path}")

    img = Image.open(image_path)
    has_alpha = img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info)
    
    # Convert to RGBA for consistent analysis
    rgba_img = img.convert("RGBA")
    arr = np.array(rgba_img)
    w, h = img.size

    # Check alpha transparency
    alpha = arr[:, :, 3]
    transparent_pixels = np.sum(alpha < 128)
    is_transparent = transparent_pixels > (w * h * 0.05)

    # Determine background color
    if is_transparent:
        bg_type = "transparent"
        # Default suggested canvas backgrounds
        suggested_bg = bg_choice if bg_choice else "dark obsidian matte (#0D0D11)"
    else:
        bg_type = "opaque"
        # Sample the 4 corners to find background color
        corners = [
            arr[0, 0, :3],
            arr[0, -1, :3],
            arr[-1, 0, :3],
            arr[-1, -1, :3]
        ]
        avg_corner = np.mean(corners, axis=0).astype(int)
        r, g, b = int(avg_corner[0]), int(avg_corner[1]), int(avg_corner[2])
        hex_code = f"#{r:02x}{g:02x}{b:02x}"
        
        # Classify background shade
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        if brightness > 220:
            suggested_bg = f"clean studio white ({hex_code})"
        elif brightness < 45:
            suggested_bg = f"deep obsidian black ({hex_code})"
        elif r > g and r > b:
            suggested_bg = f"warm crimson/burgundy tone ({hex_code})"
        elif b > r and b > g:
            suggested_bg = f"deep midnight navy ({hex_code})"
        elif g > r and g > b:
            suggested_bg = f"luxurious forest emerald ({hex_code})"
        else:
            suggested_bg = f"refined neutral tone ({hex_code})"

    # Extract dominant non-background colors from foreground
    if is_transparent:
        fg_mask = alpha > 128
        fg_pixels = arr[fg_mask][:, :3]
    else:
        # Distance from background color
        diff = np.abs(arr[:, :, :3].astype(int) - avg_corner.astype(int))
        fg_mask = np.sum(diff, axis=2) > 40
        fg_pixels = arr[fg_mask][:, :3]

    dominant_colors = []
    if len(fg_pixels) > 0:
        # Quantize colors to find top 3-4 dominant hues
        # Bin colors by dividing by 32
        quantized = (fg_pixels // 32) * 32 + 16
        unique_bins, counts = np.unique(quantized, axis=0, return_counts=True)
        sorted_indices = np.argsort(counts)[::-1]
        
        for idx in sorted_indices[:4]:
            col = unique_bins[idx]
            hex_c = f"#{int(col[0]):02x}{int(col[1]):02x}{int(col[2]):02x}"
            # Name color roughly
            cr, cg, cb = int(col[0]), int(col[1]), int(col[2])
            luma = (cr * 299 + cg * 587 + cb * 114) / 1000
            name = "metallic/accent"
            if luma > 200 and np.std([cr, cg, cb]) < 20:
                name = "pure platinum/white"
            elif luma < 50:
                name = "deep shadow black"
            elif cr > 180 and cg > 140 and cb < 80:
                name = "burnished gold / amber"
            elif cr > 180 and cg < 100 and cb < 100:
                name = "vibrant ruby red"
            elif cb > 160 and cr < 120:
                name = "electric cobalt blue"
            elif cg > 150 and cr < 120 and cb < 150:
                name = "emerald / mint green"
            elif cr > 150 and cb > 150 and cg < 120:
                name = "royal purple"
            dominant_colors.append({"hex": hex_c, "name": name, "rgb": [cr, cg, cb]})

    # Prepare video canvas dimensions
    canvas_sizes = {
        "9:16": (1080, 1920),
        "16:9": (1920, 1080),
        "1:1": (1080, 1080)
    }
    cw, ch = canvas_sizes.get(target_ratio, (1080, 1920))

    # Calculate padding so logo fits naturally in 60-70% of canvas width or height
    max_target_w = int(cw * 0.70)
    max_target_h = int(ch * 0.55)
    
    scale = min(max_target_w / w, max_target_h / h, 1.0)
    new_w = int(w * scale)
    new_h = int(h * scale)
    
    resized_logo = rgba_img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    # Determine canvas background RGBA
    if suggested_bg.startswith("clean studio white"):
        canvas_bg_color = (255, 255, 255, 255)
    elif "black" in suggested_bg or "obsidian" in suggested_bg:
        canvas_bg_color = (13, 13, 17, 255)
    elif "navy" in suggested_bg:
        canvas_bg_color = (10, 18, 30, 255)
    elif "emerald" in suggested_bg:
        canvas_bg_color = (12, 28, 20, 255)
    else:
        canvas_bg_color = (13, 13, 17, 255)

    canvas = Image.new("RGBA", (cw, ch), canvas_bg_color)
    pos_x = (cw - new_w) // 2
    pos_y = (ch - new_h) // 2
    canvas.paste(resized_logo, (pos_x, pos_y), resized_logo)

    out_frame_dir = os.path.join(os.path.dirname(image_path), "prepared_canvas")
    os.makedirs(out_frame_dir, exist_ok=True)
    canvas_path = os.path.join(out_frame_dir, f"prepared_logo_{target_ratio.replace(':', 'x')}.png")
    canvas.save(canvas_path, "PNG")

    outer_col = dominant_colors[0]["name"] if len(dominant_colors) > 0 else "burnished gold"
    inner_col = dominant_colors[1]["name"] if len(dominant_colors) > 1 else dominant_colors[0]["name"] if dominant_colors else "radiant emerald"

    analysis_result = {
        "source_image": os.path.abspath(image_path),
        "prepared_canvas_path": os.path.abspath(canvas_path),
        "dimensions": {"width": w, "height": h},
        "target_canvas": {"width": cw, "height": ch, "ratio": target_ratio},
        "is_transparent": bool(is_transparent),
        "background_type": bg_type,
        "suggested_background": suggested_bg,
        "dominant_colors": dominant_colors,
        "draft_slots": {
            "overall_style_vibe": "luxury metallic" if "gold" in outer_col else "minimalist corporate",
            "background_color": suggested_bg,
            "shape_style": "geometric symmetrical",
            "outer_element_color": outer_col,
            "outer_main_visual_element": "shield emblem",
            "inner_element_color": inner_col,
            "inner_main_visual_element": "core insignia",
            "secondary_top_element": "a subtle five-point star icon",
            "middle_element_calligraphy": "an elegant centered monogram mark",
            "text_line_1": "BRAND NAME",
            "text_line_2": "TAGLINE / SUBTITLE",
            "text_line_3": "EST. 2026",
            "font_description": "clean, tracked-out modern sans-serif"
        }
    }
    return analysis_result

def main():
    parser = argparse.ArgumentParser(description="Analyze logo image and extract template slots")
    parser.add_argument("logo", help="Path to input logo image (PNG/JPG)")
    parser.add_argument("--ratio", default="9:16", choices=["9:16", "16:9", "1:1"], help="Target video aspect ratio")
    parser.add_argument("--bg", default=None, help="Explicit background override")
    parser.add_argument("--json", action="store_true", help="Print json output only")
    
    args = parser.parse_args()
    
    result = analyze_logo_image(args.logo, target_ratio=args.ratio, bg_choice=args.bg)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("\n================ LOGO IMAGE ANALYSIS ================")
        print(f"Source Image: {result['source_image']} ({result['dimensions']['width']}x{result['dimensions']['height']})")
        print(f"Transparency: {'Yes (Alpha Channel)' if result['is_transparent'] else 'Opaque'}")
        print(f"Detected Background: {result['suggested_background']}")
        print(f"Prepared Video Canvas: {result['prepared_canvas_path']} ({result['target_canvas']['width']}x{result['target_canvas']['height']})")
        print("Dominant Palette:")
        for c in result['dominant_colors']:
            print(f"  - {c['name']} ({c['hex']})")
        
        print("\n--- Auto-Filled Template Prompt Draft ---")
        s = result['draft_slots']
        prompt = (
            f"A {s['overall_style_vibe']} logo design on a {s['background_color']} background. "
            f"It features a {s['shape_style']} {s['outer_element_color']} outer {s['outer_main_visual_element']} "
            f"and a {s['inner_element_color']} inner {s['inner_main_visual_element']}. "
            f"At the top is {s['secondary_top_element']}. "
            f"Below the main elements is {s['middle_element_calligraphy']}. "
            f"At the bottom, the text '{s['text_line_1']}', '{s['text_line_2']}', and '{s['text_line_3']}' "
            f"is stacked in a {s['font_description']} font."
        )
        print(f'"{prompt}"\n')

if __name__ == "__main__":
    main()
