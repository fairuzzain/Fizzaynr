"""Built-in generic cartoon host (SVG), used when no PNG mascot pack is given.

pose_svg(pose, colors) -> SVG markup (viewBox 0 0 600 760) with an empty
<g id="mouth-slot"> at the mouth; mouth_svg(shape) -> markup for one Rhubarb shape
(A B C D E F G H X), drawn around (0,0), to be placed into the slot.
Poses: base, think, point, phone, thumbs.
"""

INK = "#1b1b1b"
SW = 7


def _c(colors, k, d):
    return (colors or {}).get(k, d)


def _hand(x, y, skin, r=34):
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="{skin}" stroke="{INK}" stroke-width="{SW}"/>')


def _thumb(x, y, skin):
    return (f'<rect x="{x-14}" y="{y-58}" width="28" height="52" rx="14" fill="{skin}" stroke="{INK}" stroke-width="{SW}"/>'
            + _hand(x, y, skin, 36))


def _arm(path, skin, sleeve):
    # sleeve stub drawn first, then skin arm as thick stroke with outline
    return (f'<path d="{path}" fill="none" stroke="{INK}" stroke-width="66" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="{path}" fill="none" stroke="{skin}" stroke-width="52" stroke-linecap="round" stroke-linejoin="round"/>')


def pose_svg(pose="base", colors=None):
    skin = _c(colors, "skin", "#E8B48A")
    hair = _c(colors, "hair", "#23201F")
    shirt = _c(colors, "shirt", "#26304F")
    cheek = _c(colors, "cheek", "#E99A7A")
    arms_back, arms_front = "", ""
    if pose == "point":
        arms_front = (_arm("M150 520 Q90 470 40 420", skin, shirt)
                      + f'<rect x="-34" y="404" width="64" height="26" rx="13" fill="{skin}" stroke="{INK}" stroke-width="{SW}"/>'
                      + _hand(40, 420, skin, 38)
                      + _arm("M470 560 Q500 650 470 760", skin, shirt))
    elif pose == "think":
        arms_front = (_arm("M360 760 Q420 560 330 430", skin, shirt) + _hand(322, 420, skin, 40)
                      + _arm("M150 560 Q110 660 140 760", skin, shirt))
    elif pose == "phone":
        arms_front = (_arm("M160 540 Q100 520 100 430", skin, shirt)
                      + f'<rect x="40" y="250" width="130" height="230" rx="22" fill="#111" stroke="{INK}" stroke-width="{SW}"/>'
                      + '<rect x="52" y="264" width="106" height="202" rx="14" fill="#BFF2E2"/>'
                      + _hand(100, 450, skin, 36)
                      + _arm("M450 560 Q540 540 560 460", skin, shirt)
                      + f'<path d="M530 470 l-20 -60 M555 455 l0 -66 M580 462 l18 -58" stroke="{INK}" stroke-width="20" stroke-linecap="round"/>'
                      + f'<path d="M530 470 l-20 -60 M555 455 l0 -66 M580 462 l18 -58" stroke="{skin}" stroke-width="10" stroke-linecap="round"/>'
                      + _hand(560, 470, skin, 34))
    elif pose == "thumbs":
        arms_front = (_arm("M150 600 Q90 600 110 520", skin, shirt) + _thumb(110, 520, skin)
                      + _arm("M450 600 Q510 600 490 520", skin, shirt) + _thumb(490, 520, skin))
    else:  # base
        arms_back = _arm("M150 560 Q120 660 140 760", skin, shirt) + _arm("M450 560 Q480 660 460 760", skin, shirt)

    return f'''<svg viewBox="-60 0 680 760" xmlns="http://www.w3.org/2000/svg" class="msvg">
{arms_back}
<path d="M70 760 Q70 470 200 430 L400 430 Q530 470 530 760 Z" fill="{shirt}" stroke="{INK}" stroke-width="{SW}"/>
<path d="M245 432 Q300 482 355 432" fill="none" stroke="{INK}" stroke-width="{SW}"/>
<rect x="255" y="350" width="90" height="90" rx="20" fill="{skin}" stroke="{INK}" stroke-width="{SW}"/>
<ellipse cx="178" cy="262" rx="26" ry="36" fill="{skin}" stroke="{INK}" stroke-width="{SW}"/>
<ellipse cx="422" cy="262" rx="26" ry="36" fill="{skin}" stroke="{INK}" stroke-width="{SW}"/>
<path d="M180 230 Q180 110 300 108 Q420 110 420 230 L418 300 Q410 392 300 398 Q190 392 182 300 Z" fill="{skin}" stroke="{INK}" stroke-width="{SW}"/>
<path d="M170 222 Q160 92 300 78 Q448 80 432 226 Q404 150 330 150 Q300 176 236 160 Q190 170 170 222 Z" fill="{hair}" stroke="{INK}" stroke-width="{SW}" stroke-linejoin="round"/>
<path d="M226 222 Q252 208 276 220" fill="none" stroke="{hair}" stroke-width="12" stroke-linecap="round"/>
<path d="M324 220 Q348 208 374 222" fill="none" stroke="{hair}" stroke-width="12" stroke-linecap="round"/>
<ellipse cx="252" cy="258" rx="17" ry="20" fill="#fff" stroke="{INK}" stroke-width="5"/>
<ellipse cx="348" cy="258" rx="17" ry="20" fill="#fff" stroke="{INK}" stroke-width="5"/>
<circle cx="254" cy="262" r="9" fill="{INK}"/><circle cx="346" cy="262" r="9" fill="{INK}"/>
<path d="M300 268 Q292 296 304 302" fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>
<ellipse cx="224" cy="312" rx="20" ry="11" fill="{cheek}" opacity=".55"/>
<ellipse cx="376" cy="312" rx="20" ry="11" fill="{cheek}" opacity=".55"/>
<g id="mouth-slot" transform="translate(300 338)"></g>
{arms_front}
</svg>'''


_LIP = f'stroke="{INK}" stroke-width="6" stroke-linejoin="round" stroke-linecap="round"'
MOUTHS = {
    # closed (M B P)
    "A": f'<path d="M-30 0 Q0 6 30 0" fill="none" {_LIP}/>',
    # slightly open, teeth (K S T EE)
    "B": f'<path d="M-32 -6 Q0 -2 32 -6 Q26 14 0 16 Q-26 14 -32 -6 Z" fill="#7A1F2B" {_LIP}/>'
         f'<path d="M-26 -4 Q0 0 26 -4 L24 4 Q0 7 -24 4 Z" fill="#fff"/>',
    # open (EH AE)
    "C": f'<path d="M-32 -8 Q0 -4 32 -8 Q28 24 0 28 Q-28 24 -32 -8 Z" fill="#7A1F2B" {_LIP}/>'
         f'<path d="M-26 -6 Q0 -2 26 -6 L24 2 Q0 5 -24 2 Z" fill="#fff"/>',
    # wide open (AA)
    "D": f'<path d="M-34 -10 Q0 -6 34 -10 Q32 38 0 44 Q-32 38 -34 -10 Z" fill="#7A1F2B" {_LIP}/>'
         f'<path d="M-28 -8 Q0 -4 28 -8 L26 0 Q0 3 -26 0 Z" fill="#fff"/>'
         '<ellipse cx="0" cy="30" rx="18" ry="9" fill="#E06A6A"/>',
    # rounded (AO ER)
    "E": f'<ellipse cx="0" cy="8" rx="22" ry="22" fill="#7A1F2B" {_LIP}/>'
         '<ellipse cx="0" cy="22" rx="11" ry="5" fill="#E06A6A"/>',
    # puckered (UW OW W)
    "F": f'<ellipse cx="0" cy="6" rx="13" ry="14" fill="#7A1F2B" {_LIP}/>',
    # F V: upper teeth on lower lip
    "G": f'<path d="M-30 -4 Q0 0 30 -4 Q24 14 0 14 Q-24 14 -30 -4 Z" fill="#7A1F2B" {_LIP}/>'
         f'<path d="M-24 -2 Q0 2 24 -2 L22 8 Q0 11 -22 8 Z" fill="#fff"/>'
         f'<path d="M-26 12 Q0 22 26 12" fill="none" {_LIP}/>',
    # L: tongue up
    "H": f'<path d="M-32 -8 Q0 -4 32 -8 Q28 26 0 30 Q-28 26 -32 -8 Z" fill="#7A1F2B" {_LIP}/>'
         '<path d="M-14 22 Q0 -2 14 22 Z" fill="#E06A6A"/>',
    # idle / rest: small smile
    "X": f'<path d="M-30 -2 Q0 16 30 -2" fill="none" {_LIP}/>',
}


def mouth_svg(shape):
    return MOUTHS.get(shape, MOUTHS["X"])
