---
marp: true
theme: default
size: 16:9
paginate: true
---

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400&display=swap');

:root {
  --color-background: #ffffff;
  --color-foreground: #1c1c1c;
  --color-heading: #111111;
  --color-muted: #888888;
  --color-rule: #e8e8e8;
  --color-accent: #0066cc;
  --font-default: 'Inter', 'Segoe UI', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', 'Consolas', monospace;
}

section {
  background-color: var(--color-background);
  color: var(--color-foreground);
  font-family: var(--font-default);
  font-weight: 300;
  box-sizing: border-box;
  padding: 64px 80px 56px;
  font-size: 22px;
  line-height: 1.75;
}

section::after {
  font-size: 13px;
  color: var(--color-muted);
  font-family: var(--font-default);
  font-weight: 300;
}

h1, h2, h3 {
  font-family: var(--font-default);
  margin: 0;
  padding: 0;
  color: var(--color-heading);
}

h1 {
  font-size: 54px;
  font-weight: 300;
  line-height: 1.2;
  letter-spacing: -0.02em;
}

h2 {
  font-size: 36px;
  font-weight: 400;
  letter-spacing: -0.01em;
  margin-bottom: 32px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--color-rule);
}

h3 {
  font-size: 21px;
  font-weight: 500;
  color: var(--color-accent);
  margin-top: 28px;
  margin-bottom: 8px;
}

ul, ol {
  padding-left: 24px;
  margin: 0;
}

li {
  margin-bottom: 10px;
  color: var(--color-foreground);
}

li strong {
  font-weight: 500;
  color: var(--color-heading);
}

p {
  margin: 0 0 14px;
}

code {
  font-family: var(--font-mono);
  font-size: 0.85em;
  background-color: #f4f4f4;
  color: #333;
  padding: 2px 7px;
  border-radius: 3px;
}

pre {
  background-color: #f6f8fa;
  border: 1px solid var(--color-rule);
  border-radius: 4px;
  padding: 16px;
  font-family: var(--font-mono);
  font-size: 24px;
  line-height: 1.5;
}

pre code {
  background: none;
  padding: 0;
  border-radius: 0;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.88em;
  font-weight: 300;
  margin-top: 8px;
}

th {
  font-weight: 500;
  font-size: 0.85em;
  color: var(--color-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 8px 14px;
  border-bottom: 1px solid var(--color-rule);
  text-align: left;
}

td {
  padding: 10px 14px;
  border-bottom: 1px solid var(--color-rule);
  vertical-align: top;
}

/* Title / lead slide */
section.lead {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 80px;
  border-left: 3px solid var(--color-heading);
}

section.lead h1 {
  font-size: 58px;
  font-weight: 300;
  letter-spacing: -0.03em;
  margin-bottom: 24px;
  line-height: 1.15;
}

section.lead p {
  font-size: 20px;
  color: var(--color-muted);
  font-weight: 300;
  margin: 0;
  line-height: 1.6;
}

/* Section break slides */
section.break {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 80px;
  background-color: var(--color-heading);
  color: #ffffff;
}

section.break h1 {
  font-size: 48px;
  font-weight: 300;
  color: #ffffff;
  letter-spacing: -0.02em;
  margin-bottom: 16px;
}

section.break p {
  font-size: 20px;
  color: rgba(255,255,255,0.55);
  margin: 0;
}

/* Appendix */
section.appendix h2 {
  color: var(--color-muted);
  font-size: 28px;
  border-bottom-color: #eeeeee;
}

/* Inline note / callout */
.note {
  border-left: 2px solid var(--color-rule);
  padding-left: 20px;
  color: var(--color-muted);
  font-size: 0.9em;
  margin-top: 20px;
}

/* Definition callout */
.def {
  border-left: 2px solid var(--color-accent);
  padding-left: 14px;
  font-size: 0.82em;
  color: var(--color-muted);
  margin-top: 12px;
}

.def strong {
  color: var(--color-foreground);
}
</style>

<!-- _class: lead -->
<!-- _paginate: false -->

# A Model With No Business Running Here

<br/>
Semantic search inside a Drupal module. No sidecar, APIs or new software.

Ching Chew · September 2026

<br/>

![w:200](screenshots/qr-drupal.png)

<!-- note:
Pre-show: Docker demo running locally, http://localhost:8080/autosearch open in 2 tabs (keyword mode ready via ?mode=keyword with second regular one). Third tab on the GitHub repo (drupal branch) for the QR code.

"Cloud hosting and APIs make semantic search and machine learning models easy to run and consume. What if you don't want to introduce another dependency and want to run this inside Drupal? This is where this presentation comes in."

Audience framing: assume zero prior exposure. This room may include people who know Drupal deeply but have never seen a semantic search demo, and some non-technical attendees. Don't assume anyone read an earlier blog post or saw a prior talk — the next several slides rebuild the concept from scratch before anything Drupal-specific shows up.

Platform adaptation: if presenting over Teams/Zoom instead of in-room, paste the repo link in chat at this point rather than relying on the QR code.
-->

---

![bg contain](screenshots/not-found.jpg)

<!-- note:
"Hands up if anyone here experienced frustration with search: especially trying to find something you are sure exists in the system?"

"No imagine this frustration in your user base, using your website or application."

Non-technical framing: this slide is a feeling, not an explanation. Do not explain tokens, indexing or search internals yet. The explanation builds over the next few slides.
-->

---

## The Naming Problem

A user wants to find "how many GPs we have."

- The data item is called "GP FTE"
- Or "Total practitioner FTE"
- Or something else again, depends who wrote it

<br/>

**Search matches names. Users might know it as something else.**

<!-- note:
Universal in any content-heavy site with specialist vocabulary: a Drupal knowledge base, an intranet, a product catalogue, a policy library.

Don't answer the rhetorical. Let the room think of their own version — a wiki page, a form name, a policy document they've hunted for themselves.

Non-technical framing: no jargon yet. This is a problem everyone in the room has lived, technical or not.
-->

---

![bg contain](screenshots/drupal-keyword-miss.png)
![bg contain](screenshots/drupal-semantic-hit.png)

<!-- note:
Full-bleed split. No narration needed, let the room read it.
"Same query. Same Drupal module. Different search."

This is the destination. Everything between here and the live demo explains how we got there.
-->

---

## The Search Ladder

![w:300](diagrams/search-ladder.svg)

Each rung buys recall. None solve vocabulary mismatch.

<!-- note:
Walk the ladder briefly. Most Drupal sites sit at rung 2 or 3 (core search, or Search API with an index).

Rung 3 (Solr/OpenSearch + synonyms): the synonym list is a bag of intent someone has to maintain forever. Every new acronym is a config change.

Rung 4 is OOTB embeddings (machine representation of meaning, series of numbers), we will demo fine-tuned (improved) version of Rung 4. I will explain how fine-tuning works later.

Definition callout if the room needs it: "Solr" / "OpenSearch" — a dedicated search engine service some Drupal sites index content into, separate from the database.
-->

---

## The Drupal Ecosystem's Answer Today

That's the general shape of the problem and the fix. Here's where Drupal sits today:

- **AI Search + Ollama** — a sidecar service, 5 to 15 GB RAM
- **AI Search / Semantic Search + OpenAI** — external API call per query, a key to manage, per-query cost
- **Search API Embeddings** — in-process, but Word2Vec, 2013-era tech
- **Scolta** (new, Aug 2026) — client-side lexical index + LLM query rewriting, not embeddings

<br/>

**Every path is a sidecar, a call, or not actually semantic.**

<!-- note:
Scan slide, list not deep technical content. Move at pace.

Scolta needs one sentence of respect, not dismissal: same instinct (no search server), different mechanism (lexical index in the browser, not vector embeddings). If someone in the room has tried Scolta, this is the moment they'll raise a hand, welcome it, it's a genuine adjacent tool.

Exec framing: this is the "why doesn't this already exist" slide. Point at RAM cost and per-query billing as the two numbers that matter for a budget conversation.
-->

---

## The Actual Gap

Nobody in the Drupal ecosystem runs the embedding model inside the PHP process itself.

- An INT8-quantised, fine-tuned `all-MiniLM-L6-v2` is ~22 MB
- That is small enough to load once, in-process, on first request
- No Ollama. No external call. No vector database.

<br/>

**This is what that looks like.**

<!-- note:
This is the "so what" slide, land it clearly, then go straight into the demo. Exec audience: this is the moment to say "no new service to procure, no new SLA to negotiate."

Peer audience: the size number (22 MB) is doing the work here, it's smaller than most people's mental model of "a machine learning model."
-->

---

<!-- _class: break -->
<!-- _paginate: false -->

# Live Demo

Keyword vs Semantic, Running Inside Drupal

<!-- note:
1. Confirm Drupal is up: curl localhost:8080/api/v1/search/health
2. Keyword mode (?mode=keyword): type "primary care doctor staffing levels" => "No matches found"
3. Switch to semantic mode, same query => "GP FTE" surfaces, single best match
4. Click through => navigates to the report, scrolls, fades highlight
5. Optional: show /admin/modules with Auto Search enabled — "this is a real module, not a bolt-on"

Platform adaptation: if the venue wifi is unreliable, this entire demo is local Docker, no internet dependency. Say so up front; it's a feature of the architecture, not a caveat.

Backup: if Docker fails to start, the before/after screenshots already shown cover this exact sequence, narrate from memory if needed.
-->

---

## The Vocabulary Problem

![w:550](diagrams/vocabulary-problem.svg)

Off-the-shelf embeddings know "doctor" is close to "physician".

They do not know "GP FTE" means "general practitioner full-time equivalent" in an Australian primary care context.

**That is what fine-tuning fixes.**

<!-- note:
Domain vocabulary is the reason for everything that follows in this talk: the tokenizer port, the FFI wiring, all of it exists to run a fine-tuned model, not a generic one.

OOTB MiniLM: Recall@1 = 0.75. OOTB bge-small (larger model): Recall@1 = 0.80. Both miss one query in five, and the misses cluster on exactly the domain-specific phrasings that matter most.

Fine-tuning teaches the model the vocabulary. Full eval numbers are in the JVM write-up for anyone who wants to go deeper afterwards: herdmentality.xyz/blog/auto-search.
-->

---

## Synthetic Pairs from Claude

No human labelled "golden dataset" exists, so we generate one from an LLM.

```python
prompt = (
  f"Data item:\nName: {item['name']}\n"
  f"Description: {item.get('description', '')}\n\n"
  f"Generate 10 diverse natural-language queries a health "
  f"workforce planner might type to find this item. Include "
  f"acronym expansions, synonyms, colloquial phrasings."
)
```

~5,900 pairs across 350 items (re-runs accumulate). ~30c on Haiku.

<!-- note:
The unglamorous bit that made it work, and the same pipeline as the JVM version. Worth saying out loud: "the training side didn't change at all when this got ported to PHP, only the runtime did."

Loss function for anyone technical: MultipleNegativesRankingLoss, every other item in the batch acts as an implicit negative. Batch size 32, three epochs.

Non-technical framing: don't dwell on the loss function name. The point that lands is "we used one AI model to generate the training examples for a different, much smaller AI model."
-->

---

## Eval Results

| Model | Size | Recall@1 | MRR@5 |
|---|---|---|---|
| all-MiniLM-L6-v2 (OOTB) | 91 MB | 0.750 | 0.808 |
| bge-small-en-v1.5 (OOTB, larger) | 133 MB | 0.800 | 0.850 |
| **all-MiniLM-L6-v2 fine-tuned (INT8 ONNX)** | **22 MB** | **0.850** | **0.908** |

**Roughly 1/6th the size of bge-small, and still more accurate.**

<div class="def"><strong>Recall@1</strong> — how often the correct item is the very top result. 0.85 means 85 times out of 100.</div>
<div class="def"><strong>MRR@5</strong> — Mean Reciprocal Rank across the top 5 results. Rewards a correct answer even if it isn't first: rank 2 scores 0.5, rank 3 scores 0.33.</div>

<!-- note:
Same model, same numbers as the JVM version, nothing about the Drupal port changes accuracy, only where it runs.

Two test sets, both synthetic. LLM holdout (0.93) vs a smaller secondary set (0.85) with shorter, keyword-style queries. The gap is what the model learned about Claude's verbose phrasing vs terser phrasings. Logged queries from a live deployment would be the strongest signal but don't exist yet.

Size numbers: OOTB fp32 checkpoints as downloaded from Hugging Face (91 MB, 133 MB). The 22 MB figure is the fine-tuned model after INT8 quantisation, the actual file running in the demo. Not a like-for-like quantisation comparison, but an honest one: this is what ships vs what you'd get OOTB.

n=20 on the secondary set, directional only, not statistically significant on its own. The larger LLM holdout (n=1182) shows the same ranking.
-->

---

## Architecture

![w:1200](diagrams/drupal-runtime-flow.svg)

The Vue frontend is unchanged. Everything new is in the PHP module.

<div class="def"><strong>ONNX</strong> — Open Neural Network Exchange. A portable model format; the same file runs in Java, Python or PHP.</div>
<div class="def"><strong>FFI</strong> — Foreign Function Interface. Lets PHP call native C++ code directly, no network involved. That's how the box labelled "PHP FFI" in the diagram talks to the ONNX model.</div>

<!-- note:
[deep] slide, signpost verbally: "this one's for the people who want the mechanism, feel free to zone out for 90 seconds if you just want the shape of it."

The Vue SPA is served as a Drupal library, the same pattern as an earlier Vue.js-in-Drupal talk to this group. Nothing changed there. If nobody in the room saw that talk, this is just "the frontend is a normal Drupal library, nothing special."

Exec framing: point at the box labelled "Drupal 10 module (single PHP process)", this is the entire new deployment surface. One module, no new infrastructure.
-->

---

## Code Walk

```php
public function encode(string $text): array {
  $normalized = $this->normalize($text);
  $words = $this->preTokenize($normalized);
  $ids = [self::CLS_ID];
  foreach ($words as $word) {
    foreach ($this->wordPiece($word) as $id) {
      $ids[] = $id;
      if (count($ids) >= self::MAX_LENGTH - 1) break 2;
    }
  }
  $ids[] = self::SEP_ID;
  return ['input_ids' => $ids, ...];
}
```

Hand-ported WordPiece tokenizer. PHP has no HuggingFace Tokenizers equivalent.

<!-- note:
[deep] slide, pairs with the previous one.

This is the highest-risk piece of the whole port, validated token-for-token against the Java and Python implementations before trusting it near the model.

Peer question likely to come up: "why not just call out to a Python sidecar for tokenization?" Answer: that reintroduces exactly the sidecar dependency the whole talk argues against. If you're going to run the model in-process, the tokenizer has to be in-process too.

Second code block available if there's time/interest: EmbeddingService::embed() showing the FFI call into ankane/onnxruntime-php and the mean-pool/L2-normalise step, identical logic to the Java version.
-->

---

## Two Deployment Modes

If you are deploying this to Production:

| | Self-hosted / GovCMS PaaS | GovCMS SaaS |
|---|---|---|
| Custom modules at all | Yes, agency controls the container | Not permitted — approved module set only |
| `libonnxruntime.so` | Install it, same as self-hosted | Moot — custom code isn't an option here |

<!-- note:
Correction worth knowing before this slide is delivered: SaaS and PaaS are genuinely different services, not two flavours of the same constraint. SaaS is fully managed with a fixed approved module and theme set, no custom code, full stop, regardless of what that code does. PaaS runs on Lagoon/Kubernetes and the agency owns its own Docker image, exactly the same model as tonight's local demo, so libonnxruntime.so is exactly as available there as it is self-hosted.

This is the honest-caveat slide, do not skip or soften it. Strong GovCMS contingent in this room; naming SaaS's real constraint (no custom code at all) lands better than an ONNX-specific workaround that doesn't reflect how SaaS actually works.

Exec framing: the answer to "can my team actually run this" is "yes, if you're on PaaS or self-hosted; no, if you're on SaaS, and that's true of any custom module, not just this one."
-->

---

## Clone and Run Tonight

```bash
git clone -b drupal https://github.com/cchew/auto-search
cd auto-search/drupal
bash setup-model.sh health-workforce
docker compose up --build
```

Then open `localhost:8080/autosearch`.

<!-- note:
Most student-friendly and recruiter-friendly slide in the deck, say the URL out loud, don't just show it.

If asked about swapping in a different corpus: corpus.json and the model artefacts are the only things that change; setup-model.sh takes any corpus name matching a folder under examples/.
-->

---

## Conclusion

"The user does not care which rung of the ladder you used. They care that the search worked."

<br/>

- Most search problems are vocabulary problems
- Fine-tuned small models beat off-the-shelf large models on domain tasks
- The infrastructure can stay boring

<br/>

Thank you
Feedback and questions: DM via LinkedIn
Code: github.com/cchew/auto-search (drupal branch)

<!-- note:
Land the takeaway: search is a UX problem dressed up as an ML problem. Solve the vocabulary mismatch and the rest is a for-loop, in PHP just as much as in Java.

Open Q&A. Likely questions:
- "Does this work on Drupal 11?" — yes, info.yml declares ^10 || ^11
- "What about content types beyond a flat corpus?" — corpus.json is the interface; anything that flattens to items with a name/description works today, entity-aware indexing is future work
- "Why not just use Scolta?" — different problem: Scolta rewrites queries against a lexical index; this does real semantic similarity. Use Scolta if you want zero infra and can live with lexical search; use this if you need the model to actually understand domain vocabulary.
- "Why not RAG?" — different problem, retrieval is one part of RAG, this is just retrieval.
- Cost? ~30c training on Haiku, $0 per query.

Platform adaptation: if this is presented again internally (Teams), swap "DM via LinkedIn" for a Teams handle and swap the GitHub CTA for an ADO Wiki link to the internal build notes.
-->

---

<!-- _class: appendix -->
<!-- _paginate: false -->

## Appendix A — Production Considerations

**Not yet built (honest gap list)**
- Config schema (`config/schema/autosearch.schema.yml`) — required before any settings form
- Scoped permission on the search endpoint — all routes currently `_access: 'TRUE'` for the demo
- Uninstall hook — cleans up generated proxy classes and cached embeddings
- CSRF protection on `POST /api/v1/search` — fine for anonymous read-only demo, not for writes

**Ops surface**
- One Drupal module. Model loads lazily on first search request, not every page load
- No external service calls in the search path (self-hosted mode)
- Memory: ~22 MB model + (N items × 384 × 4 bytes) vectors, same envelope as the JVM version

<!-- note:
Cover only if asked. This is the "what would you still need to do before production" list, a peer audience will ask, an exec audience usually won't.
-->

---

<!-- _class: appendix -->
<!-- _paginate: false -->

## Appendix B — Tech Stack

**Drupal module (PHP)**
- PHP 8.3, Drupal 10/11
- `ankane/onnxruntime-php` (FFI binding to ONNX Runtime 1.26.0)
- Hand-ported WordPiece tokenizer (no external dependency)

**Unchanged from the JVM version**
- Model: fine-tuned `all-MiniLM-L6-v2`, INT8, ONNX export
- Training pipeline: Python, sentence-transformers, Claude-generated synthetic pairs
- Frontend: Vue 3, served as a Drupal library

**Infra**
- Docker Compose: Drupal 10 + MariaDB 10.11 (`--skip-ssl`)
- Olivero (front theme) + Claro (admin theme)

<!-- note:
Tech stack on request. The point to land if asked: nothing about the model or training pipeline changed for this port, only the runtime host.
-->

---

<!-- _class: appendix -->
<!-- _paginate: false -->

## Appendix C — Lessons Learnt

- **FFI and `intl` extensions aren't compiled in by default** — bites on managed PHP images without root access to the build
- **Lazy service proxies break constructor type hints** — Drupal's generated proxies don't extend the concrete class; type the constructor as `object`
- **MariaDB 10.11 requires SSL by default** — `mysqladmin` and `pdo_mysql` both fail until `--skip-ssl` is set explicitly

<!-- note:
Cover only if asked, or if there's time to spare, these are the three that would waste someone a full afternoon if they hit them cold.

Peer audience: this is the "here's what I tried first and didn't work" content this profile responds to. Worth surfacing proactively for a technical Q&A even if not asked directly.
-->
