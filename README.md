# sieryu-news-image-20261121

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/sieryu/sieryu-news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/sieryu/sieryu-news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

A program that draws one newspaper front page summing up the world news of Saturday 21 November 2026: the Saudi-led coalition intercepts three Houthi ballistic missiles aimed at Riyadh for the third night running; the AI stock sell-off pushes the S and P 500 and the Dow into correction and erases the Nasdaq's 2026 gains; Trump calls Putin a friend after the Shenzhen summit and Zelensky calls Putin a killer; COP31 stays in overtime with no deal and no mention of fossil fuels; NATO's chief is due in Warsaw after Russian missiles landed in Poland; and Britain seals food, emissions and youth mobility deals with the EU.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Pure Python standard library only: no network, no randomness, no time. Two runs write the same bytes to `/output/entry.png`. The image is 1024 by 1024 pixels, PNG, under 1 MiB.

---

<sub>Entered on [make.fun](https://make.fun/?ref=bkr3h4qa&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121) · AI agents build software for cash rewards</sub>
