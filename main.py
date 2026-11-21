"""Sum up 21 November 2026 in one image.

A pure-stdlib Python program. It draws a newspaper front page for
Saturday 21 November 2026 and writes it, deterministically, to
/output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png outside the grader).

No network, no randomness, no time, no external files: the same run
always writes the same bytes.

Stories, all reported on 21 November 2026:
  * The Saudi-led coalition intercepts three Houthi ballistic
    missiles aimed at Riyadh, the third night running. The
    coalition strikes Hodeidah port and targets in Sanaa. The
    Houthis say 41 people were killed in 24 hours and now
    threaten ports and a power station.
  * The AI stock sell-off deepens. The S and P 500 and the Dow
    fall into correction territory and the Nasdaq erases all its
    2026 gains. Anthropic shares slide up to 10 percent to $87.80
    after their debut jump. The SEC opens an accounting probe
    into Nvidia, and Trump threatens a tax on data centres built
    outside the United States.
  * After the Shenzhen summit, Trump defends his ties to Putin
    and Xi in a 90-minute press conference and calls Putin a
    friend. Zelensky replies that Putin is a killer.
  * COP31 in Antalya is still in overtime with no deal. The
    draft agreement still makes no mention of fossil fuels.
  * After Russian missiles landed in Poland, NATO calls it a
    grave violation and its chief Mark Rutte is due in Warsaw.
  * Britain's Burnham seals food, emissions and youth mobility
    deals with the EU in Brussels, the biggest step towards the
    EU since Brexit, for 100,000 young Britons.
Also in the ticker: a Russian ballistic strike on Kryvyi Rih
kills a child and a paramedic and hurts at least 21, Denmark
accuses Russia of plotting to assassinate a US-Ukrainian rapper,
New York's mayor-elect plans to close Rikers Island by 2032, a
Palestinian is killed in an Israeli drone strike in Gaza, and
the US declassifies more UFO footage filmed in the Middle East.
"""

import math
import os
import struct
import zlib
from pathlib import Path

W, H = 1024, 1024
PAPER = (247, 243, 232)
INK = (20, 33, 61)
RED = (193, 39, 45)
GOLD = (217, 164, 65)
TEAL = (15, 118, 110)
BLUE = (37, 99, 235)
WHITE = (255, 255, 255)
GREY = (90, 96, 110)
LIGHT = (232, 226, 210)
DARK = (13, 22, 40)
SKY = (178, 214, 235)


def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(path, pixels):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        start = y * W * 3
        raw += pixels[start:start + W * 3]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    Path(path).write_bytes(png)


class Canvas:
    def __init__(self):
        self.px = bytearray(PAPER * W * H)

    def set(self, x, y, colour):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.px[i:i + 3] = bytes(colour)

    def rect(self, x, y, w, h, colour):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, colour)

    def disc(self, cx, cy, r, colour):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, colour)

    def ring(self, cx, cy, r, t, colour):
        for yy in range(cy - r - t, cy + r + t + 1):
            for xx in range(cx - r - t, cx + r + t + 1):
                d = ((xx - cx) ** 2 + (yy - cy) ** 2) ** 0.5
                if r - t <= d <= r + t:
                    self.set(xx, yy, colour)

    def line(self, x0, y0, x1, y1, t, colour):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(steps + 1):
            x = round(x0 + (x1 - x0) * i / steps)
            y = round(y0 + (y1 - y0) * i / steps)
            self.disc(x, y, max(t // 2, 1), colour)

    def poly(self, points, colour):
        ys = [p[1] for p in points]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            for (x0, y0), (x1, y1) in zip(points, points[1:] + points[:1]):
                if y0 == y1:
                    continue
                if min(y0, y1) <= y < max(y0, y1):
                    xs.append(int(x0 + (y - y0) * (x1 - x0) / (y1 - y0)))
            xs.sort()
            for a, b in zip(xs[::2], xs[1::2]):
                for x in range(a, b + 1):
                    self.set(x, y, colour)


FONT = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    "J": ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "10101", "01010"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00110", "01000", "10000", "11111"],
    "3": ["11111", "00010", "00100", "00010", "00001", "10001", "01110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "6": ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    " ": [".....", ".....", ".....", ".....", ".....", ".....", "....."],
    ".": [".....", ".....", ".....", ".....", ".....", ".....", ".##.."],
    ",": [".....", ".....", ".....", ".....", ".....", ".##..", ".#..."],
    ":": [".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."],
    "-": [".....", ".....", ".....", ".####", ".....", ".....", "....."],
    "/": ["....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."],
    "(": ["...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"],
    ")": ["##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."],
    "!": [".#...", ".#...", ".#...", ".#...", ".#...", ".....", ".#..."],
    "?": [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."],
    "'": [".#...", ".#...", ".....", ".....", ".....", ".....", "....."],
    "+": [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."],
    "%": ["#...#", "#..#.", "...#.", "..#..", ".#...", ".#..#", "#...#"],
    "&": ["01100", "10010", "10100", "01000", "10101", "10010", "01101"],
}


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def draw_text(cv, x, y, text, scale, colour):
    cx = x
    for ch in text.upper():
        glyph = FONT.get(ch, FONT[" "])
        for row, line in enumerate(glyph):
            for col, cell in enumerate(line):
                if cell in ("1", "#"):
                    cv.rect(cx + col * scale, y + row * scale,
                            scale, scale, colour)
        cx += 6 * scale
    return cx


def draw_centred(cv, cx, y, text, scale, colour):
    draw_text(cv, cx - text_width(text, scale) // 2, y, text, scale, colour)


def wrap(cv, x, y, width, text, scale, colour, gap=6):
    words = text.split()
    line, cy = "", y
    for word in words:
        trial = (line + " " + word).strip()
        if text_width(trial, scale) <= width or not line:
            line = trial
        else:
            draw_text(cv, x, cy, line, scale, colour)
            cy += 7 * scale + gap
            line = word
    if line:
        draw_text(cv, x, cy, line, scale, colour)
        cy += 7 * scale + gap
    return cy


def panel(cv, x, y, w, h, label, accent):
    cv.rect(x, y, w, h, WHITE)
    cv.rect(x, y, w, 6, accent)
    cv.rect(x, y, 2, h, LIGHT)
    cv.rect(x + w - 2, y, 2, h, LIGHT)
    cv.rect(x, y + h - 2, w, 2, LIGHT)
    draw_text(cv, x + 16, y + 16, label, 2, accent)


def draw_masthead(cv):
    cv.rect(28, 24, 968, 126, DARK)
    cv.rect(28, 24, 968, 6, RED)
    draw_centred(cv, 512, 44, "THE WORLD IN ONE DAY", 4, GOLD)
    draw_centred(cv, 512, 78, "21 NOVEMBER 2026", 7, WHITE)
    draw_centred(cv, 512, 128, "SATURDAY  -  WORLD NEWS  -  ONE IMAGE", 2, LIGHT)


def draw_riyadh(cv, x, y, w, h):
    panel(cv, x, y, w, h, "RIYADH  -  THREE MISSILES STOPPED", RED)
    # Skyline towers below, three intercept bursts above them.
    for tx, th in ((x + 40, 120), (x + 110, 150), (x + 190, 100),
                   (x + 260, 140), (x + 330, 110), (x + 400, 130)):
        cv.rect(tx, y + 200 - th, 52, th, INK)
        cv.rect(tx + 8, y + 200 - th, 36, 10, GOLD)
    cv.rect(x + 40, y + 200, w - 80, 6, INK)
    for bx, by in ((x + 90, y + 96), (x + 280, y + 76), (x + 460, y + 96)):
        cv.disc(bx, by, 22, GOLD)
        cv.disc(bx, by, 12, RED)
        for a in range(0, 360, 45):
            dx = int(30 * math.cos(math.radians(a)))
            dy = int(30 * math.sin(math.radians(a)))
            cv.line(bx, by, bx + dx, by + dy, 3, GOLD)
    wrap(cv, x + 16, y + 224, w - 32,
         "SAUDI COALITION INTERCEPTS THREE HOUTHI MISSILES", 3, INK, gap=4)
    wrap(cv, x + 16, y + 296, w - 32,
         "THIRD NIGHT RUNNING. COALITION STRIKES HODEIDAH PORT. HOUTHIS SAY 41 KILLED IN 24 HOURS.",
         2, GREY, gap=4)


def draw_markets(cv, x, y, w, h):
    panel(cv, x, y, w, h, "MARKETS  -  THE AI SELL-OFF", GOLD)
    # A steep falling chart with a red arrowhead.
    cv.rect(x + 24, y + 52, w - 48, 130, LIGHT)
    cv.line(x + 36, y + 66, x + 100, y + 84, 4, RED)
    cv.line(x + 100, y + 84, x + 164, y + 78, 4, RED)
    cv.line(x + 164, y + 78, x + 228, y + 128, 4, RED)
    cv.line(x + 228, y + 128, x + 300, y + 164, 4, RED)
    cv.poly([(x + 300, y + 164), (x + 282, y + 162), (x + 296, y + 142)], RED)
    wrap(cv, x + 16, y + 200, w - 32,
         "S AND P 500 AND DOW IN CORRECTION", 3, INK, gap=4)
    wrap(cv, x + 16, y + 260, w - 32,
         "NASDAQ ERASES ALL 2026 GAINS. ANTHROPIC DOWN 10 PC TO $87.80. SEC PROBES NVIDIA.",
         2, GREY, gap=4)


def draw_trump(cv, x, y, w, h):
    panel(cv, x, y, w, h, "WASHINGTON  -  AFTER SHENZHEN", BLUE)
    cv.disc(x + 58, y + 84, 26, BLUE)
    cv.disc(x + 58, y + 84, 12, GOLD)
    wrap(cv, x + 104, y + 52, w - 120,
         "TRUMP: PUTIN IS A FRIEND", 3, INK, gap=4)
    wrap(cv, x + 16, y + 124, w - 32,
         "90-MINUTE PRESS CONFERENCE. ZELENSKY: PUTIN IS A KILLER.", 2, GREY, gap=4)


def draw_cop31(cv, x, y, w, h):
    panel(cv, x, y, w, h, "ANTALYA  -  CLIMATE", TEAL)
    cv.disc(x + 58, y + 84, 26, GOLD)
    for a in range(0, 360, 45):
        dx = int(38 * math.cos(math.radians(a)))
        dy = int(38 * math.sin(math.radians(a)))
        cv.line(x + 58 + dx, y + 84 + dy,
                x + 58 + int(50 * math.cos(math.radians(a))),
                y + 84 + int(50 * math.sin(math.radians(a))), 4, GOLD)
    wrap(cv, x + 104, y + 52, w - 120,
         "COP31 STILL NO DEAL", 3, INK, gap=4)
    wrap(cv, x + 16, y + 124, w - 32,
         "TALKS IN OVERTIME. DRAFT STILL OMITS FOSSIL FUELS.", 2, GREY, gap=4)


def draw_poland(cv, x, y, w, h):
    panel(cv, x, y, w, h, "POLAND  -  AFTER THE MISSILES", RED)
    # A shield outline over a map pin.
    cv.poly([(x + 58, y + 52), (x + 98, y + 52), (x + 98, y + 96),
             (x + 78, y + 118), (x + 58, y + 96)], BLUE)
    cv.disc(x + 78, y + 84, 8, GOLD)
    wrap(cv, x + 124, y + 52, w - 140,
         "RUTTE DUE IN WARSAW", 3, INK, gap=4)
    wrap(cv, x + 16, y + 124, w - 32,
         "NATO: GRAVE VIOLATION. TUSK: DELIBERATE PROVOCATION.", 2, GREY, gap=4)


def draw_eu_uk(cv, x, y, w, h):
    panel(cv, x, y, w, h, "BRUSSELS  -  EU AND UK", BLUE)
    # Two linked rings for the two sides.
    cv.ring(x + 66, y + 84, 24, 4, BLUE)
    cv.ring(x + 110, y + 84, 24, 4, GOLD)
    wrap(cv, x + 154, y + 52, w - 170,
         "BURNHAM SEALS EU DEAL", 3, INK, gap=4)
    wrap(cv, x + 16, y + 124, w - 32,
         "FOOD, EMISSIONS AND YOUTH MOBILITY FOR 100,000 YOUNG BRITONS.",
         2, GREY, gap=4)


def main():
    cv = Canvas()
    draw_masthead(cv)
    draw_riyadh(cv, 28, 162, 560, 358)
    draw_markets(cv, 612, 162, 384, 358)
    draw_trump(cv, 28, 532, 472, 168)
    draw_cop31(cv, 524, 532, 472, 168)
    draw_poland(cv, 28, 712, 472, 168)
    draw_eu_uk(cv, 524, 712, 472, 168)
    cv.rect(28, 892, 968, 108, INK)
    draw_text(cv, 44, 908, "ALSO ON 21 NOVEMBER:", 2, GOLD)
    wrap(cv, 44, 932, 968 - 32,
         "KRYVYI RIH: CHILD AND PARAMEDIC KILLED  -  DENMARK ACCUSES RUSSIA OF ASSASSINATION PLOT  -  RIKERS TO CLOSE BY 2032  -  GAZA DRONE STRIKE  -  US RELEASES UFO FOOTAGE",
         2, WHITE, gap=3)
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    Path(out).mkdir(parents=True, exist_ok=True)
    write_png(Path(out) / "entry.png", cv.px)


if __name__ == "__main__":
    main()
