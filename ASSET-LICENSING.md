[English](ASSET-LICENSING.md) · [한국어](ASSET-LICENSING.ko.md)

# Designated artwork register

2026-11-08. This register separates artwork from [MIT code](LICENSE). The unmodified [official CC BY-NC-SA 4.0 legal text](licenses/CC-BY-NC-SA-4.0.txt) and the [separate ordinary-work-use permission](CHARACTER-POLICY.md) accompany designated assets.

| Component/path | Version and license | Reason, permissions and obligations |
| --- | --- | --- |
| `pomodoro/art/sprout-tomato-v1.json` | Sprout Tomato — mint apron edition v1; CC BY-NC-SA 4.0 | New body/crown/face/boot/apron/pocket geometry and paired standing/seated poses. Noncommercial sharing/adaptation with attribution, license link, changes marked, ShareAlike; ordinary paid-work app use separately permitted. |
| `pomodoro/character.py`, `posture.py`, all original app code | MIT | Reusable renderer and behavior; commercial use/modification/distribution permitted with MIT notice. |
| Rendered new character, generated app icon and new alpha-3 demo character imagery | CC BY-NC-SA 4.0, to the extent they reproduce protected expression in the registered asset | Rendering or format conversion does not remove the character terms. Demo text/composition and code retain MIT; third-party fonts/runtime retain their terms. |
| Historical plain tomato in [`pomodoro/surfaces.py` at alpha 2](https://github.com/hobby-programmer-5000/pawzura-pomodoro/blob/23cec9d547204b726c636a496ac14efb5452b622/pomodoro/surfaces.py) and previous demos/releases | Existing MIT | Earlier grants are preserved, including commercial use. No retroactive noncommercial restriction. |

Exact JSON SHA-256: `9e298737c4b93f5702143c4d8562315abfed21a799c3adf7602218eb97dc99f9`.

First designation/release: **0.1.0a3 / v0.1.0-alpha.3**, 2026-11-08. The version tag identifies the first committed record; this does not assert a release has already been published. Licensor: **hobby-programmer-5000**. Credit: **Sprout Tomato — mint apron edition v1, hobby-programmer-5000; AI-assisted vector artwork with ChatGPT/Codex**. Source: this JSON and [repository](https://github.com/hobby-programmer-5000/pawzura-pomodoro). No external artwork or model weights were imported; the design is procedural vector data implemented with AI assistance under user direction. No claim of exclusive rights in AI output is made.

Excluded: pre-existing MIT expression, generic shapes/styles/colors, independent art, renderer/motion code, screen layouts/text, Windows font software and Qt/Python/Pawzura material. Those components are not relicensed by this register. The new arrangement is distinguishable from the old plain tomato, but a new edition cannot withdraw any pre-existing MIT rights in overlapping expression. Copyrightability and enforcement remain unverified legal questions, not guaranteed protection against imitation or registration.

For new demo file hashes and exact licensed layers see [media notes](media/README.md); component notices are in [THIRD-PARTY-NOTICES](THIRD-PARTY-NOTICES.md). The standard license is from [Creative Commons](https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode.txt), SHA-256 `e66c269d4819aaab34b49ef5220c4ddab6756f21bb5180761a4eb8561f2b7bbd`. CC's [FAQ](https://creativecommons.org/faq/) explains license boundaries and separate permissions. Keep this register and notices with shared assets. No new runtime dependency was added.

Selectable classic artwork lives in `pomodoro/classic.py`: restored standing geometry/palette from the historical alpha-2 renderer, with new seated interpolation implemented under MIT. It is excluded from the CC designation. Options > General > Character saves the chosen skin; selecting it does not change either asset’s license. The fixed executable file icon is mint-apron artwork, while the running companion/tray/reminders follow your selection.
