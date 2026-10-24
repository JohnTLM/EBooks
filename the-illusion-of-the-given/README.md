# The Illusion of the Given (bonus article)

A standalone bonus article, separate from *The Observer and the Taste of Presence*. Nothing in this folder is part of that book's build.

## Folders

| Folder | What is in it |
|---|---|
| `source/` | The article as Markdown, one file per part. Edit these. |
| `output/` | The built PDF, `the-illusion-of-the-given.pdf`. |
| `original/` | The Expanded Edition PDF as first circulated, kept for comparison. |

Source files, in reading order:

1. `0-title.md`: title and subtitle
2. `1-part-I.md`: Part I, the core text
3. `2-part-II.md`: Part II, a multi-dimensional worldview
4. `3-part-III.md`: Part III, classical Buddhist traditions on many worlds
5. `4-sources.md`: sources and further reading

## Building the PDF

```
pip install markdown-it-py playwright
python -m playwright install chromium
python build-pdf.py
```

If Chromium is already installed somewhere else, set `CHROMIUM_PATH` to its executable instead of running the install step.

## Changes from the original Expanded Edition

**Part I** is kept as it was, apart from these small factual corrections:

- "foundational-free Dzogchen" now reads "non-foundational Dzogchen".
- Barad's term is the "agential cut", not the "measurement cut".
- The cross-perspective links comparison is softened from "the same function" and "the exact structure" to a similarity, with a pointer to Part II, §3B, which explains where it ends.
- The Critical Caution no longer implies that Barad and Rovelli themselves deny that relations are primary.
- Ticks survive in water for days, so the tick is now held and carried by the water rather than drowned.
- Solidity is described as resistance between systems that share the relevant coupling, not between systems "of similar physical density".
- "In quantum gravity, space is composed of relational networks" is now qualified as loop quantum gravity, one research program among several.
- In the subtitle, "Multi-Dimensional Cosmology" now reads "Multi-Dimensional Worldview".

**Part II** is rewritten and expanded. It defines its terms and says what kind of claim it makes. It no longer places all worlds in "the same location", which had brought back the container that Part I rejects. It is explicit about which claims rest on tradition rather than observation. It gives a corrected account of Everett's Many-Worlds Interpretation (deterministic, with emergent branches; Hilbert space is not a place), and ends with a section on the view's limits.

**Part III** is rewritten. Each tradition is presented with what it says, where it agrees with Parts I and II, and where it differs or needs care. Corrections include:

- The *Abhidharmakośa* is an Abhidharma (Sarvāstivāda/Sautrāntika) text, not a Yogācāra one.
- The Four Dharmadhātus were systematized by Chengguan.
- Tiantai's "three thousand realms" concern a thought-moment, not a place.
- Pure lands are also traditionally described as distant.

The old "Comparative Summary" table at the end has been removed. A corrected comparison with Everett is now in Part II, §5.

**Sources and Further Reading** is new.

### Later revision

Two statements that could not be confirmed against the primary texts were reworded so they no longer depend on a specific source:

- **Location of the hungry ghosts' realm** (Part II §2C and Part III §1): the claim that the *Abhidharmakośa* places it beneath our continent, with some hungry ghosts wandering among humans, now says only that the map gives each realm of rebirth its own place.
- **Asaṅga's use of the example** (Part III §2): the claim that texts linked to Asaṅga list hungry ghosts, animals, humans, and gods now says only that later Yogācāra writers return to the hungry ghosts and the river.

The *Abhidharmakośa* 4.1 quotation (*karmajaṃ lokavaicitryam*) was checked and kept.
