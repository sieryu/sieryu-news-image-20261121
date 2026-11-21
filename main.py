"""Saturday 21 November 2026, drawn as one newspaper page.

This file is a small drawing program. It paints the front
page of a newspaper for 21 November 2026 and writes the
result to entry.png, a 1024 by 1024 PNG. Run it twice and
you get the same file twice: it needs no network, no clock,
no files and no random numbers, only the standard library.

The news on the page, all of it reported on 21 November 2026:
  * The Saudi-led coalition stops three Houthi ballistic
    missiles headed for Riyadh, the third night in a row.
    The coalition hits Hodeidah port and targets in Sanaa.
    The Houthis say 41 people died in 24 hours and now
    threaten ports and a power station.
  * The AI sell-off deepens. The S and P 500 and the Dow
    fall into correction and the Nasdaq wipes out all its
    2026 gains. Anthropic shares drop as much as 10 percent
    to $87.80 after their first-day jump. The SEC opens an
    accounting probe into Nvidia, and Trump threatens a tax
    on data centres built outside the United States.
  * After the Shenzhen summit, Trump defends his ties to
    Putin and Xi in a 90-minute press conference and calls
    Putin a friend. Zelensky answers that Putin is a killer.
  * COP31 in Antalya is still in overtime with no deal.
    The draft agreement still says nothing about fossil
    fuels.
  * After Russian missiles landed in Poland, NATO calls it
    a grave violation and its chief Mark Rutte is due in
    Warsaw.
  * Britain's Burnham seals food, emissions and youth
    mobility deals with the EU in Brussels, the biggest
    step towards the EU since Brexit, for 100,000 young
    Britons.
Along the bottom: a Russian ballistic strike on Kryvyi Rih
kills a child and a paramedic and hurts at least 21, Denmark
accuses Russia of plotting to assassinate a US-Ukrainian
rapper, New York's mayor-elect plans to close Rikers Island
by 2032, a Palestinian is killed in an Israeli drone strike
in Gaza, and the US declassifies more UFO footage filmed in
the Middle East.
"""

import math
import os
import struct
import zlib
from pathlib import Path

SIDE = 1024
BACKGROUND = (247, 243, 232)
DARKBLUE = (20, 33, 61)
CRIMSON = (193, 39, 45)
AMBER = (217, 164, 65)
SEAGREEN = (15, 118, 110)
ROYAL = (37, 99, 235)
SNOW = (255, 255, 255)
SLATE = (90, 96, 110)
CREAM = (232, 226, 210)
NIGHT = (13, 22, 40)
POWDER = (178, 214, 235)

# The picture lives in one flat buffer, three bytes per pixel.
canvas = bytearray(BACKGROUND * SIDE * SIDE)


def set_px(x, y, rgb):
    if 0 <= x < SIDE and 0 <= y < SIDE:
        pos = (y * SIDE + x) * 3
        canvas[pos:pos + 3] = bytes(rgb)


def box(x, y, w, h, rgb):
    yy = y
    while yy < y + h:
        xx = x
        while xx < x + w:
            set_px(xx, yy, rgb)
            xx += 1
        yy += 1


def ball(cx, cy, r, rgb):
    yy = cy - r
    while yy <= cy + r:
        xx = cx - r
        while xx <= cx + r:
            if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                set_px(xx, yy, rgb)
            xx += 1
        yy += 1


def halo(cx, cy, r, t, rgb):
    yy = cy - r - t
    while yy <= cy + r + t:
        xx = cx - r - t
        while xx <= cx + r + t:
            d = ((xx - cx) ** 2 + (yy - cy) ** 2) ** 0.5
            if r - t <= d <= r + t:
                set_px(xx, yy, rgb)
            xx += 1
        yy += 1


def segment(x0, y0, x1, y1, thick, rgb):
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    i = 0
    while i <= n:
        x = round(x0 + (x1 - x0) * i / n)
        y = round(y0 + (y1 - y0) * i / n)
        ball(x, y, max(thick // 2, 1), rgb)
        i += 1


def shape(points, rgb):
    top = min(p[1] for p in points)
    bottom = max(p[1] for p in points)
    sides = list(zip(points, points[1:] + points[:1]))
    y = top
    while y <= bottom:
        cuts = []
        for (x0, y0), (x1, y1) in sides:
            if y0 != y1 and min(y0, y1) <= y < max(y0, y1):
                cuts.append(int(x0 + (y - y0) * (x1 - x0) / (y1 - y0)))
        cuts.sort()
        j = 0
        while j + 1 < len(cuts):
            x = cuts[j]
            while x <= cuts[j + 1]:
                set_px(x, y, rgb)
                x += 1
            j += 2
        y += 1


def save_png(path):
    def block(kind, data):
        framed = struct.pack(">I", len(data)) + kind + data
        return framed + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    body = bytearray()
    row = 0
    while row < SIDE:
        body.append(0)
        body += canvas[row * SIDE * 3:(row + 1) * SIDE * 3]
        row += 1
    head = struct.pack(">IIBBBBB", SIDE, SIDE, 8, 2, 0, 0, 0)
    Path(path).write_bytes(
        b"\x89PNG\r\n\x1a\n" + block(b"IHDR", head)
        + block(b"IDAT", zlib.compress(bytes(body), 6))
        + block(b"IEND", b""))


# Letters, five columns wide and seven rows tall. A glyph is
# seven small numbers; bit 16 is the leftmost column.
LETTERS = {
    "A": (14, 17, 17, 31, 17, 17, 17), "B": (30, 17, 17, 30, 17, 17, 30),
    "C": (14, 17, 16, 16, 16, 17, 14), "D": (30, 17, 17, 17, 17, 17, 30),
    "E": (31, 16, 16, 30, 16, 16, 31), "F": (31, 16, 16, 30, 16, 16, 16),
    "G": (14, 17, 16, 23, 17, 17, 15), "H": (17, 17, 17, 31, 17, 17, 17),
    "I": (14, 4, 4, 4, 4, 4, 14), "J": (7, 2, 2, 2, 2, 18, 12),
    "K": (17, 18, 20, 24, 20, 18, 17), "L": (16, 16, 16, 16, 16, 16, 31),
    "M": (17, 27, 21, 21, 17, 17, 17), "N": (17, 25, 21, 19, 17, 17, 17),
    "O": (14, 17, 17, 17, 17, 17, 14), "P": (30, 17, 17, 30, 16, 16, 16),
    "Q": (14, 17, 17, 17, 21, 18, 13), "R": (30, 17, 17, 30, 20, 18, 17),
    "S": (15, 16, 16, 14, 1, 1, 30), "T": (31, 4, 4, 4, 4, 4, 4),
    "U": (17, 17, 17, 17, 17, 17, 14), "V": (17, 17, 17, 17, 17, 10, 4),
    "W": (17, 17, 17, 21, 21, 21, 10), "X": (17, 17, 10, 4, 10, 17, 17),
    "Y": (17, 17, 10, 4, 4, 4, 4), "Z": (31, 1, 2, 4, 8, 16, 31),
    "0": (14, 17, 19, 21, 25, 17, 14), "1": (4, 12, 4, 4, 4, 4, 14),
    "2": (14, 17, 1, 6, 8, 16, 31), "3": (31, 2, 4, 2, 1, 17, 14),
    "4": (2, 6, 10, 18, 31, 2, 2), "5": (31, 16, 30, 1, 1, 17, 14),
    "6": (6, 8, 16, 30, 17, 17, 14), "7": (31, 1, 2, 4, 8, 8, 8),
    "8": (14, 17, 17, 14, 17, 17, 14), "9": (14, 17, 17, 15, 1, 2, 12),
    " ": (0, 0, 0, 0, 0, 0, 0), ".": (0, 0, 0, 0, 0, 0, 12),
    ",": (0, 0, 0, 0, 0, 12, 8), ":": (0, 12, 12, 0, 12, 12, 0),
    "-": (0, 0, 0, 15, 0, 0, 0), "/": (1, 2, 2, 4, 8, 8, 16),
    "(": (3, 4, 8, 8, 8, 4, 3), ")": (24, 4, 2, 2, 2, 4, 24),
    "!": (8, 8, 8, 8, 8, 0, 8), "?": (14, 17, 1, 2, 4, 0, 4),
    "'": (8, 8, 0, 0, 0, 0, 0), "+": (0, 4, 4, 31, 4, 4, 0),
    "%": (17, 18, 2, 4, 8, 9, 17), "&": (12, 18, 20, 8, 21, 18, 13),
}


def text_len(text, scale):
    return len(text) * 6 * scale - scale


def write_text(x, y, text, scale, rgb):
    pen = x
    for ch in text.upper():
        rows = LETTERS.get(ch, LETTERS[" "])
        r = 0
        while r < 7:
            c = 0
            while c < 5:
                if rows[r] >> (4 - c) & 1:
                    box(pen + c * scale, y + r * scale, scale, scale, rgb)
                c += 1
            r += 1
        pen += 6 * scale
    return pen


def write_centred(cx, y, text, scale, rgb):
    write_text(cx - text_len(text, scale) // 2, y, text, scale, rgb)


def write_wrapped(x, y, width, text, scale, rgb, gap=6):
    words = text.split()
    line, cy, i = "", y, 0
    while i < len(words):
        trial = (line + " " + words[i]).strip()
        if not line or text_len(trial, scale) <= width:
            line = trial
        else:
            write_text(x, cy, line, scale, rgb)
            cy += 7 * scale + gap
            line = words[i]
        i += 1
    if line:
        write_text(x, cy, line, scale, rgb)
        cy += 7 * scale + gap
    return cy


def frame(x, y, w, h, label, accent):
    box(x, y, w, h, SNOW)
    box(x, y, w, 6, accent)
    box(x, y, 2, h, CREAM)
    box(x + w - 2, y, 2, h, CREAM)
    box(x, y + h - 2, w, 2, CREAM)
    write_text(x + 16, y + 16, label, 2, accent)


def top_banner():
    box(28, 24, 968, 126, NIGHT)
    box(28, 24, 968, 6, CRIMSON)
    write_centred(512, 44, "THE WORLD IN ONE DAY", 4, AMBER)
    write_centred(512, 78, "21 NOVEMBER 2026", 7, SNOW)
    write_centred(512, 128, "SATURDAY  -  WORLD NEWS  -  ONE IMAGE", 2, CREAM)
    # A thin gold rule under the whole page, like a newspaper edge.
    box(8, 8, 1008, 4, AMBER)
    box(8, 1012, 1008, 4, AMBER)
    box(8, 8, 4, 1008, AMBER)
    box(1012, 8, 4, 1008, AMBER)


def riyadh_panel(x, y, w, h):
    frame(x, y, w, h, "RIYADH  -  THREE MISSILES STOPPED", CRIMSON)
    # A stepped skyline: buildings of different heights in a row.
    skyline = [(40, 52, 110), (108, 44, 140), (168, 60, 90),
               (244, 48, 130), (308, 56, 100), (380, 46, 120),
               (442, 54, 105)]
    for ox, bw, bh in skyline:
        box(x + ox, y + 196 - bh, bw, bh, DARKBLUE)
        box(x + ox + 6, y + 196 - bh, bw - 12, 8, AMBER)
    box(x + 40, y + 196, w - 80, 6, DARKBLUE)
    # Three red crosses in the sky mark the intercepted missiles.
    for cx, cy in ((x + 110, y + 92), (x + 290, y + 72), (x + 460, y + 92)):
        segment(cx - 16, cy - 16, cx + 16, cy + 16, 5, CRIMSON)
        segment(cx - 16, cy + 16, cx + 16, cy - 16, 5, CRIMSON)
        halo(cx, cy, 24, 3, AMBER)
    write_wrapped(x + 16, y + 224, w - 32,
                  "SAUDI COALITION INTERCEPTS THREE HOUTHI MISSILES",
                  3, DARKBLUE, gap=4)
    write_wrapped(x + 16, y + 296, w - 32,
                  "THIRD NIGHT RUNNING. COALITION STRIKES HODEIDAH PORT. HOUTHIS SAY 41 KILLED IN 24 HOURS.",
                  2, SLATE, gap=4)


def markets_panel(x, y, w, h):
    frame(x, y, w, h, "MARKETS  -  THE AI SELL-OFF", AMBER)
    # Six bars, each shorter than the last: the market falling.
    heights = [120, 104, 108, 84, 58, 34]
    bx = x + 36
    for bh in heights:
        box(bx, y + 168 - bh, 40, bh, CRIMSON)
        bx += 52
    box(x + 24, y + 168, w - 48, 4, DARKBLUE)
    write_wrapped(x + 16, y + 200, w - 32,
                  "S AND P 500 AND DOW IN CORRECTION", 3, DARKBLUE, gap=4)
    write_wrapped(x + 16, y + 260, w - 32,
                  "NASDAQ ERASES ALL 2026 GAINS. ANTHROPIC DOWN 10 PC TO $87.80. SEC PROBES NVIDIA.",
                  2, SLATE, gap=4)


def trump_panel(x, y, w, h):
    frame(x, y, w, h, "WASHINGTON  -  AFTER SHENZHEN", ROYAL)
    # Two speech bubbles facing each other across the panel.
    box(x + 24, y + 48, 120, 56, POWDER)
    shape([(x + 44, y + 104), (x + 64, y + 104), (x + 44, y + 126)], POWDER)
    box(x + 168, y + 48, 120, 56, AMBER)
    shape([(x + 248, y + 104), (x + 228, y + 104), (x + 248, y + 126)], AMBER)
    ball(x + 84, y + 76, 12, ROYAL)
    ball(x + 228, y + 76, 12, CRIMSON)
    write_wrapped(x + 304, y + 52, w - 320,
                  "TRUMP: PUTIN IS A FRIEND", 3, DARKBLUE, gap=4)
    write_wrapped(x + 16, y + 132, w - 32,
                  "90-MINUTE PRESS CONFERENCE. ZELENSKY: PUTIN IS A KILLER.",
                  2, SLATE, gap=4)


def cop31_panel(x, y, w, h):
    frame(x, y, w, h, "ANTALYA  -  CLIMATE", SEAGREEN)
    # A globe: a teal ball with a white band and a small leaf.
    ball(x + 64, y + 84, 30, SEAGREEN)
    halo(x + 64, y + 84, 30, 3, AMBER)
    segment(x + 36, y + 78, x + 92, y + 90, 4, SNOW)
    shape([(x + 108, y + 60), (x + 132, y + 44), (x + 128, y + 68)], SEAGREEN)
    write_wrapped(x + 148, y + 52, w - 164,
                  "COP31 STILL NO DEAL", 3, DARKBLUE, gap=4)
    write_wrapped(x + 16, y + 132, w - 32,
                  "TALKS IN OVERTIME. DRAFT STILL OMITS FOSSIL FUELS.",
                  2, SLATE, gap=4)


def poland_panel(x, y, w, h):
    frame(x, y, w, h, "POLAND  -  AFTER THE MISSILES", CRIMSON)
    # A map pin: a ball on a triangle, with a star beside it.
    ball(x + 66, y + 76, 22, ROYAL)
    ball(x + 66, y + 76, 8, AMBER)
    shape([(x + 48, y + 92), (x + 84, y + 92), (x + 66, y + 124)], ROYAL)
    ball(x + 118, y + 66, 5, AMBER)
    write_wrapped(x + 140, y + 52, w - 156,
                  "RUTTE DUE IN WARSAW", 3, DARKBLUE, gap=4)
    write_wrapped(x + 16, y + 132, w - 32,
                  "NATO: GRAVE VIOLATION. TUSK: DELIBERATE PROVOCATION.",
                  2, SLATE, gap=4)


def eu_uk_panel(x, y, w, h):
    frame(x, y, w, h, "BRUSSELS  -  EU AND UK", ROYAL)
    # An arch of dots joins two small flags.
    a = 0
    while a <= 180:
        ax = int(x + 40 + 64 * math.cos(math.radians(180 - a)))
        ay = int(y + 108 - 40 * math.sin(math.radians(a)))
        ball(ax, ay, 4, ROYAL)
        a += 15
    box(x + 28, y + 108, 24, 16, ROYAL)
    box(x + 124, y + 108, 24, 16, AMBER)
    write_wrapped(x + 168, y + 52, w - 184,
                  "BURNHAM SEALS EU DEAL", 3, DARKBLUE, gap=4)
    write_wrapped(x + 16, y + 132, w - 32,
                  "FOOD, EMISSIONS AND YOUTH MOBILITY FOR 100,000 YOUNG BRITONS.",
                  2, SLATE, gap=4)


PANELS = [
    (riyadh_panel, 28, 162, 560, 358),
    (markets_panel, 612, 162, 384, 358),
    (trump_panel, 28, 532, 472, 168),
    (cop31_panel, 524, 532, 472, 168),
    (poland_panel, 28, 712, 472, 168),
    (eu_uk_panel, 524, 712, 472, 168),
]


def run():
    top_banner()
    for fn, px, py, pw, ph in PANELS:
        fn(px, py, pw, ph)
    box(28, 892, 968, 108, DARKBLUE)
    write_text(44, 908, "ALSO ON 21 NOVEMBER:", 2, AMBER)
    write_wrapped(44, 932, 968 - 32,
                  "KRYVYI RIH: CHILD AND PARAMEDIC KILLED  -  DENMARK ACCUSES RUSSIA OF ASSASSINATION PLOT  -  RIKERS TO CLOSE BY 2032  -  GAZA DRONE STRIKE  -  US RELEASES UFO FOOTAGE",
                  2, SNOW, gap=3)
    target = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    Path(target).mkdir(parents=True, exist_ok=True)
    save_png(str(Path(target) / "entry.png"))


if __name__ == "__main__":
    run()
