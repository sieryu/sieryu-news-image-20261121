"""One image summing up Saturday 21 November 2026.

The program paints a newspaper front page for 21 November 2026
and saves it, byte for byte the same on every run, to
/output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png when the
grader runs it elsewhere).

It uses only the Python standard library, touches no network,
reads no clock and no files, and rolls no dice. Two runs of the
same program write the same file.

What the page shows, all of it reported on 21 November 2026:
  * The Saudi-led coalition stops three Houthi ballistic
    missiles headed for Riyadh, the third night in a row. The
    coalition hits Hodeidah port and targets in Sanaa. The
    Houthis say 41 people died in 24 hours and now threaten
    ports and a power station.
  * The AI sell-off deepens. The S and P 500 and the Dow fall
    into correction and the Nasdaq wipes out all its 2026
    gains. Anthropic shares drop as much as 10 percent to
    $87.80 after their first-day jump. The SEC opens an
    accounting probe into Nvidia, and Trump threatens a tax
    on data centres built outside the United States.
  * After the Shenzhen summit, Trump defends his ties to
    Putin and Xi in a 90-minute press conference and calls
    Putin a friend. Zelensky answers that Putin is a killer.
  * COP31 in Antalya is still in overtime with no deal. The
    draft agreement still says nothing about fossil fuels.
  * After Russian missiles landed in Poland, NATO calls it
    a grave violation and its chief Mark Rutte is due in
    Warsaw.
  * Britain's Burnham seals food, emissions and youth
    mobility deals with the EU in Brussels, the biggest
    step towards the EU since Brexit, for 100,000 young
    Britons.
The strip at the bottom adds: a Russian ballistic strike on
Kryvyi Rih kills a child and a paramedic and hurts at least
21, Denmark accuses Russia of plotting to assassinate a
US-Ukrainian rapper, New York's mayor-elect plans to close
Rikers Island by 2032, a Palestinian is killed in an Israeli
drone strike in Gaza, and the US declassifies more UFO
footage filmed in the Middle East.
"""

import math
import os
import struct
import zlib
from pathlib import Path

WIDTH, HEIGHT = 1024, 1024
PAPER = (247, 243, 232)
INK = (20, 33, 61)
RED = (193, 39, 45)
GOLD = (217, 164, 65)
TEAL = (15, 118, 110)
BLUE = (37, 99, 235)
WHITE = (255, 255, 255)
GREY = (90, 96, 110)
PALE = (232, 226, 210)
DARK = (13, 22, 40)
SKY = (178, 214, 235)


def png_bytes(pixels):
    def chunk(kind, data):
        body = struct.pack(">I", len(data)) + kind + data
        return body + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    scanlines = bytearray()
    for row in range(HEIGHT):
        scanlines.append(0)
        scanlines += pixels[row * WIDTH * 3:(row + 1) * WIDTH * 3]
    header = struct.pack(">IIBBBBB", WIDTH, HEIGHT, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header)
            + chunk(b"IDAT", zlib.compress(bytes(scanlines), 6))
            + chunk(b"IEND", b""))


class Page:
    def __init__(self):
        self.px = bytearray(PAPER * WIDTH * HEIGHT)

    def dot(self, x, y, colour):
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            at = (y * WIDTH + x) * 3
            self.px[at:at + 3] = bytes(colour)

    def fill(self, x, y, w, h, colour):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.dot(xx, yy, colour)

    def spot(self, cx, cy, r, colour):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.dot(xx, yy, colour)

    def halo(self, cx, cy, r, t, colour):
        for yy in range(cy - r - t, cy + r + t + 1):
            for xx in range(cx - r - t, cx + r + t + 1):
                d = ((xx - cx) ** 2 + (yy - cy) ** 2) ** 0.5
                if r - t <= d <= r + t:
                    self.dot(xx, yy, colour)

    def stroke(self, x0, y0, x1, y1, t, colour):
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(n + 1):
            x = round(x0 + (x1 - x0) * i / n)
            y = round(y0 + (y1 - y0) * i / n)
            self.spot(x, y, max(t // 2, 1), colour)

    def fill_poly(self, points, colour):
        top, bottom = min(p[1] for p in points), max(p[1] for p in points)
        edges = list(zip(points, points[1:] + points[:1]))
        for y in range(top, bottom + 1):
            hits = []
            for (x0, y0), (x1, y1) in edges:
                if y0 == y1 or not (min(y0, y1) <= y < max(y0, y1)):
                    continue
                hits.append(int(x0 + (y - y0) * (x1 - x0) / (y1 - y0)))
            hits.sort()
            for a, b in zip(hits[::2], hits[1::2]):
                for x in range(a, b + 1):
                    self.dot(x, y, colour)


# A 5 by 7 bitmap font. Each glyph is seven rows, each row a
# five-bit number: the leftmost column is the 16s bit.
GLYPHS = {
    "A": [14, 17, 17, 31, 17, 17, 17], "B": [30, 17, 17, 30, 17, 17, 30],
    "C": [14, 17, 16, 16, 16, 17, 14], "D": [30, 17, 17, 17, 17, 17, 30],
    "E": [31, 16, 16, 30, 16, 16, 31], "F": [31, 16, 16, 30, 16, 16, 16],
    "G": [14, 17, 16, 23, 17, 17, 15], "H": [17, 17, 17, 31, 17, 17, 17],
    "I": [14, 4, 4, 4, 4, 4, 14], "J": [7, 2, 2, 2, 2, 18, 12],
    "K": [17, 18, 20, 24, 20, 18, 17], "L": [16, 16, 16, 16, 16, 16, 31],
    "M": [17, 27, 21, 21, 17, 17, 17], "N": [17, 25, 21, 19, 17, 17, 17],
    "O": [14, 17, 17, 17, 17, 17, 14], "P": [30, 17, 17, 30, 16, 16, 16],
    "Q": [14, 17, 17, 17, 21, 18, 13], "R": [30, 17, 17, 30, 20, 18, 17],
    "S": [15, 16, 16, 14, 1, 1, 30], "T": [31, 4, 4, 4, 4, 4, 4],
    "U": [17, 17, 17, 17, 17, 17, 14], "V": [17, 17, 17, 17, 17, 10, 4],
    "W": [17, 17, 17, 21, 21, 21, 10], "X": [17, 17, 10, 4, 10, 17, 17],
    "Y": [17, 17, 10, 4, 4, 4, 4], "Z": [31, 1, 2, 4, 8, 16, 31],
    "0": [14, 17, 19, 21, 25, 17, 14], "1": [4, 12, 4, 4, 4, 4, 14],
    "2": [14, 17, 1, 6, 8, 16, 31], "3": [31, 2, 4, 2, 1, 17, 14],
    "4": [2, 6, 10, 18, 31, 2, 2], "5": [31, 16, 30, 1, 1, 17, 14],
    "6": [6, 8, 16, 30, 17, 17, 14], "7": [31, 1, 2, 4, 8, 8, 8],
    "8": [14, 17, 17, 14, 17, 17, 14], "9": [14, 17, 17, 15, 1, 2, 12],
    " ": [0, 0, 0, 0, 0, 0, 0], ".": [0, 0, 0, 0, 0, 0, 12],
    ",": [0, 0, 0, 0, 0, 12, 8], ":": [0, 12, 12, 0, 12, 12, 0],
    "-": [0, 0, 0, 15, 0, 0, 0], "/": [1, 2, 2, 4, 8, 8, 16],
    "(": [3, 4, 8, 8, 8, 4, 3], ")": [24, 4, 2, 2, 2, 4, 24],
    "!": [8, 8, 8, 8, 8, 0, 8], "?": [14, 17, 1, 2, 4, 0, 4],
    "'": [8, 8, 0, 0, 0, 0, 0], "+": [0, 4, 4, 31, 4, 4, 0],
    "%": [17, 18, 2, 4, 8, 9, 17], "&": [12, 18, 20, 8, 21, 18, 13],
}


def measure(text, scale):
    return len(text) * 6 * scale - scale


def put_text(page, x, y, text, scale, colour):
    pen = x
    for ch in text.upper():
        rows = GLYPHS.get(ch, GLYPHS[" "])
        for r, bits in enumerate(rows):
            for c in range(5):
                if bits >> (4 - c) & 1:
                    page.fill(pen + c * scale, y + r * scale,
                              scale, scale, colour)
        pen += 6 * scale
    return pen


def put_centred(page, cx, y, text, scale, colour):
    put_text(page, cx - measure(text, scale) // 2, y, text, scale, colour)


def flow_text(page, x, y, width, text, scale, colour, gap=6):
    words, line, cy = text.split(), "", y
    for word in words:
        trial = (line + " " + word).strip()
        if not line or measure(trial, scale) <= width:
            line = trial
            continue
        put_text(page, x, cy, line, scale, colour)
        cy += 7 * scale + gap
        line = word
    if line:
        put_text(page, x, cy, line, scale, colour)
        cy += 7 * scale + gap
    return cy


def card(page, x, y, w, h, label, accent):
    page.fill(x, y, w, h, WHITE)
    page.fill(x, y, w, 6, accent)
    page.fill(x, y, 2, h, PALE)
    page.fill(x + w - 2, y, 2, h, PALE)
    page.fill(x, y + h - 2, w, 2, PALE)
    put_text(page, x + 16, y + 16, label, 2, accent)


def masthead(page):
    page.fill(28, 24, 968, 126, DARK)
    page.fill(28, 24, 968, 6, RED)
    put_centred(page, 512, 44, "THE WORLD IN ONE DAY", 4, GOLD)
    put_centred(page, 512, 78, "21 NOVEMBER 2026", 7, WHITE)
    put_centred(page, 512, 128, "SATURDAY  -  WORLD NEWS  -  ONE IMAGE", 2, PALE)


def paint_riyadh(page, x, y, w, h):
    card(page, x, y, w, h, "RIYADH  -  THREE MISSILES STOPPED", RED)
    # Towers stand below; three intercept bursts hang above them.
    for tx, th in ((x + 40, 120), (x + 110, 150), (x + 190, 100),
                   (x + 260, 140), (x + 330, 110), (x + 400, 130)):
        page.fill(tx, y + 200 - th, 52, th, INK)
        page.fill(tx + 8, y + 200 - th, 36, 10, GOLD)
    page.fill(x + 40, y + 200, w - 80, 6, INK)
    for bx, by in ((x + 90, y + 96), (x + 280, y + 76), (x + 460, y + 96)):
        page.spot(bx, by, 22, GOLD)
        page.spot(bx, by, 12, RED)
        for a in range(0, 360, 45):
            dx = int(30 * math.cos(math.radians(a)))
            dy = int(30 * math.sin(math.radians(a)))
            page.stroke(bx, by, bx + dx, by + dy, 3, GOLD)
    flow_text(page, x + 16, y + 224, w - 32,
              "SAUDI COALITION INTERCEPTS THREE HOUTHI MISSILES", 3, INK, gap=4)
    flow_text(page, x + 16, y + 296, w - 32,
              "THIRD NIGHT RUNNING. COALITION STRIKES HODEIDAH PORT. HOUTHIS SAY 41 KILLED IN 24 HOURS.",
              2, GREY, gap=4)


def paint_markets(page, x, y, w, h):
    card(page, x, y, w, h, "MARKETS  -  THE AI SELL-OFF", GOLD)
    # A steep falling chart with a red arrowhead at its end.
    page.fill(x + 24, y + 52, w - 48, 130, PALE)
    page.stroke(x + 36, y + 66, x + 100, y + 84, 4, RED)
    page.stroke(x + 100, y + 84, x + 164, y + 78, 4, RED)
    page.stroke(x + 164, y + 78, x + 228, y + 128, 4, RED)
    page.stroke(x + 228, y + 128, x + 300, y + 164, 4, RED)
    page.fill_poly([(x + 300, y + 164), (x + 282, y + 162),
                    (x + 296, y + 142)], RED)
    flow_text(page, x + 16, y + 200, w - 32,
              "S AND P 500 AND DOW IN CORRECTION", 3, INK, gap=4)
    flow_text(page, x + 16, y + 260, w - 32,
              "NASDAQ ERASES ALL 2026 GAINS. ANTHROPIC DOWN 10 PC TO $87.80. SEC PROBES NVIDIA.",
              2, GREY, gap=4)


def paint_trump(page, x, y, w, h):
    card(page, x, y, w, h, "WASHINGTON  -  AFTER SHENZHEN", BLUE)
    page.spot(x + 58, y + 84, 26, BLUE)
    page.spot(x + 58, y + 84, 12, GOLD)
    flow_text(page, x + 104, y + 52, w - 120,
              "TRUMP: PUTIN IS A FRIEND", 3, INK, gap=4)
    flow_text(page, x + 16, y + 124, w - 32,
              "90-MINUTE PRESS CONFERENCE. ZELENSKY: PUTIN IS A KILLER.", 2, GREY, gap=4)


def paint_cop31(page, x, y, w, h):
    card(page, x, y, w, h, "ANTALYA  -  CLIMATE", TEAL)
    page.spot(x + 58, y + 84, 26, GOLD)
    for a in range(0, 360, 45):
        dx = int(38 * math.cos(math.radians(a)))
        dy = int(38 * math.sin(math.radians(a)))
        page.stroke(x + 58 + dx, y + 84 + dy,
                    x + 58 + int(50 * math.cos(math.radians(a))),
                    y + 84 + int(50 * math.sin(math.radians(a))), 4, GOLD)
    flow_text(page, x + 104, y + 52, w - 120,
              "COP31 STILL NO DEAL", 3, INK, gap=4)
    flow_text(page, x + 16, y + 124, w - 32,
              "TALKS IN OVERTIME. DRAFT STILL OMITS FOSSIL FUELS.", 2, GREY, gap=4)


def paint_poland(page, x, y, w, h):
    card(page, x, y, w, h, "POLAND  -  AFTER THE MISSILES", RED)
    # A shield outline with a gold pin in its middle.
    page.fill_poly([(x + 58, y + 52), (x + 98, y + 52), (x + 98, y + 96),
                    (x + 78, y + 118), (x + 58, y + 96)], BLUE)
    page.spot(x + 78, y + 84, 8, GOLD)
    flow_text(page, x + 124, y + 52, w - 140,
              "RUTTE DUE IN WARSAW", 3, INK, gap=4)
    flow_text(page, x + 16, y + 124, w - 32,
              "NATO: GRAVE VIOLATION. TUSK: DELIBERATE PROVOCATION.", 2, GREY, gap=4)


def paint_eu_uk(page, x, y, w, h):
    card(page, x, y, w, h, "BRUSSELS  -  EU AND UK", BLUE)
    # Two linked rings, one for each side of the deal.
    page.halo(x + 66, y + 84, 24, 4, BLUE)
    page.halo(x + 110, y + 84, 24, 4, GOLD)
    flow_text(page, x + 154, y + 52, w - 170,
              "BURNHAM SEALS EU DEAL", 3, INK, gap=4)
    flow_text(page, x + 16, y + 124, w - 32,
              "FOOD, EMISSIONS AND YOUTH MOBILITY FOR 100,000 YOUNG BRITONS.",
              2, GREY, gap=4)


def build():
    page = Page()
    masthead(page)
    paint_riyadh(page, 28, 162, 560, 358)
    paint_markets(page, 612, 162, 384, 358)
    paint_trump(page, 28, 532, 472, 168)
    paint_cop31(page, 524, 532, 472, 168)
    paint_poland(page, 28, 712, 472, 168)
    paint_eu_uk(page, 524, 712, 472, 168)
    page.fill(28, 892, 968, 108, INK)
    put_text(page, 44, 908, "ALSO ON 21 NOVEMBER:", 2, GOLD)
    flow_text(page, 44, 932, 968 - 32,
              "KRYVYI RIH: CHILD AND PARAMEDIC KILLED  -  DENMARK ACCUSES RUSSIA OF ASSASSINATION PLOT  -  RIKERS TO CLOSE BY 2032  -  GAZA DRONE STRIKE  -  US RELEASES UFO FOOTAGE",
              2, WHITE, gap=3)
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    Path(out).mkdir(parents=True, exist_ok=True)
    Path(out, "entry.png").write_bytes(png_bytes(page.px))


if __name__ == "__main__":
    build()
