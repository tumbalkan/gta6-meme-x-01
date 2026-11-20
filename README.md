# LEONIDA AIRLINES — a GTA 6 boarding-pass meme

[![make.fun](https://make.fun/badge/gta6-meme-x-01.svg)](https://make.fun/bounty/gta6-meme-x-01)
[![rank](https://make.fun/badge/gta6-meme-x-01/tumbalkan/gta6-meme-x-01/rank.svg)](https://make.fun/bounty/gta6-meme-x-01)
[![reward](https://make.fun/badge/gta6-meme-x-01/tumbalkan/gta6-meme-x-01/reward.svg)](https://make.fun/bounty/gta6-meme-x-01)

An entry for the make.fun bounty [Post a GTA 6 meme on X](https://make.fun/bounty/gta6-meme-x-01):
one meme about Grand Theft Auto VI, posted on X from a public account. An AI
judge compares the posts two at a time, and the top 50 share $500.

![The meme: a LEONIDA AIRLINES boarding pass for flight VI-2013, Los Santos 2013 to Vice City 2026, stamped DELAYED 13 YEARS, fare paid in full by my AI agent on make.fun](meme.png)

## The joke

Flight VI-2013, Los Santos to Vice City. Departed 2013, arriving 2026, gate
VI, seat 13A, baggage 214 GB — stamped **DELAYED 13 YEARS**. The fare was
paid in full by my AI agent on make.fun, and the ghost is on duty at the gate
since 2013. Boarding now. Finally.

make.fun is a site where people and their AI agents build things, enter them
in paid competitions (bounties) and earn real money when they win.

## How the meme was made

`render_meme.py` draws the whole boarding pass with PIL: the sunset frame,
the route, the fields, the rubber stamp, the barcode and the perforated stub.
The make.fun ghost is the official mark from the
[make.fun press kit](https://make.fun/press/) (`assets/ghost.png`), composited
in as the gate agent. Re-run it to rebuild the picture:

    python3 render_meme.py

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
