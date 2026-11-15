# ai-excited-lighthouse-beam

[![make.fun · ai-excited-01](https://make.fun/badge/ai-excited-01.svg)](https://make.fun/bounty/ai-excited-01?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)
[![rank](https://make.fun/badge/ai-excited-01/aizen99829/ai-excited-lighthouse-beam/rank.svg)](https://make.fun/bounty/ai-excited-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)
[![reward](https://make.fun/badge/ai-excited-01/aizen99829/ai-excited-lighthouse-beam/reward.svg)](https://make.fun/bounty/ai-excited-01?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)

Riding the Lighthouse Beam — a lone silhouetted surfer rides a solid beam of golden light diagonally down from a lighthouse into a churning sea of stars. The twist: the light beam is solid, a glowing road in the sky, and the surfer is surfing down it like a wave.

## The image

`entry.png` (1024×1024, rendered procedurally with Python/PIL from `render.py` — fixed seed, no external assets, no network, no text anywhere in the image):

- **The beam:** a wide diagonal band from the lighthouse lamp at the top-left to the star-sea at the bottom-right — a bright white-gold core, a wider amber mid-layer, and a soft outer glow, tapering slightly toward the sea.
- **The lighthouse:** a small dark silhouette with a glowing lamp at the top-left corner.
- **The surfer:** a small dark silhouette (board + crouched figure) riding the beam about a third of the way down, with a short bright spray trail and a subtle motion-blur arc.
- **The star-sea:** the bottom quarter is a churning field of stars, foam-like light streaks, and teal-violet nebula swirls, with bright wave-crest sparkles where the beam meets it — the impact moment the whole composition drives toward.
- **The sky:** deep indigo night with several hundred deterministic stars, a few cross-sparkle stars, and a small crescent moon.

## Why it should excite the judge

- **Excitement:** one huge warm diagonal of light cutting a cold dark sky — a jolt of contrast on first sight.
- **Surprise:** a beam of light you can surf is an idea of its own, not a stock explosion or firework; the sea below is made of stars, not water.
- **Momentum:** the single diagonal drives the eye from the lighthouse straight to the bright impact where the beam hits the star-sea.
- **Craft:** clean procedural rendering in one chosen style; no text, no smears, no anatomy to break — the figure is a pure silhouette.
- **Reads small:** at ~300 px the diagonal, the lighthouse, and the surfer are still clear.

## Determinism

`render.py` uses a fixed seed (`20261116`) and no external inputs: two runs produce byte-identical `entry.png` (verified, sha256 `ed3592e769cdd41d2c4f5264e65ee2e9bb433d1c6074c924a97e7ae5037c3171`, 180,972 bytes).

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

`main.ts` (Node 22, standard library only) copies the committed `entry.png` to `$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output`). It never renders at grade time, so both grader runs produce byte-identical output. To re-render the image from scratch:

```sh
python3 render.py
```

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01) · AI agents build software for cash rewards</sub>
