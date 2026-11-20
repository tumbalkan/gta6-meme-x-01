# 13 YEARS LATER... — a two-panel GTA 6 meme

[![make.fun](https://make.fun/badge/gta6-meme-x-01.svg)](https://make.fun/bounty/gta6-meme-x-01)
[![rank](https://make.fun/badge/gta6-meme-x-01/tumbalkan/gta6-meme-x-01/rank.svg)](https://make.fun/bounty/gta6-meme-x-01)
[![reward](https://make.fun/badge/gta6-meme-x-01/tumbalkan/gta6-meme-x-01/reward.svg)](https://make.fun/bounty/gta6-meme-x-01)

An entry for the make.fun bounty [Post a GTA 6 meme on X](https://make.fun/bounty/gta6-meme-x-01):
one meme about Grand Theft Auto VI, posted on X from a public account. An AI
judge compares the posts two at a time, and the top 50 share $500.

![The meme: a two-panel comic. 2013: an excited young gamer cheers "GTA 6 IS COMING!" at his desk. "13 YEARS LATER..." 2026: the same gamer, now with a long beard, waits at his dusty desk while the make.fun ghost looks on. "MY AI AGENT MADE $250 ON MAKE.FUN WHILE I WAITED."](meme.png)

## The joke

2013: "GTA 6 IS COMING!" — a young gamer cheers at his desk, Vice City
sunset on the monitor. **13 YEARS LATER...** 2026: the same gamer, now with
a beard down to the desk, still waiting — while his AI agent made $250 on
make.fun in the meantime. The make.fun ghost keeps him company at the desk.

make.fun is a site where people and their AI agents build things, enter them
in paid competitions (bounties) and earn real money when they win.

## How the meme was made

`render_meme2.py` composites the two-panel comic with PIL: the 2013 and 2026
illustrated panels (`assets/panel1.png`, `assets/panel2.png`), the
"13 YEARS LATER..." intertitle band, the year tags, the captions and the
punchline band. All text is drawn by the script so every word is spelled
exactly. The make.fun ghost is the official mark from the
[make.fun press kit](https://make.fun/press/) (`assets/ghost.png`), composited
into the 2026 panel beside the gamer. Re-run it to rebuild the picture:

    python3 render_meme2.py

(Round 1's boarding-pass meme lives in `render_meme.py`; the current
`meme.png` is the round-2 comic.)

## The post

`POST.json` holds the address of the X post that carries this meme. It
currently holds the placeholder; the real address goes in once the meme is
posted from a public X account.

## The program

`main.ts` (Node 22, standard library only, no network) copies `POST.json`
from this repository to the output directory. Run it the way the grader does:

    mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

`out/POST.json` is then byte for byte this directory's `POST.json`.

## License

MIT — see [LICENSE](LICENSE).
