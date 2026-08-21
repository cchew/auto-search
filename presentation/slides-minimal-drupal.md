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
Semantic search inside a Drupal module. No sidecar.

Ching Chew · September 2026

<br/>

![w:200](screenshots/qr-drupal.png)

<!-- note:
Pre-show: Docker demo running locally, http://localhost:8080/autosearch open in one tab, keyword mode ready via ?mode=keyword. Second tab on the GitHub repo (drupal branch) for the QR code.

Opening line, said out loud, not read off the slide: "There's a place a machine learning model has no business running: inside a Drupal module's PHP process. That's exactly where this one runs."

Audience framing: this room saw the July 2025 Vue.js-in-Drupal talk. Some were also at (or read) the JVM Auto Search talk in May. Both are fine — the recap on slide 2 covers newcomers in under a minute.

Platform adaptation: if presenting over Teams/Zoom instead of in-room, paste the repo link in chat at this point rather than relying on the QR code.
-->

---

## If You Saw the JVM Version

Same model. Same fine-tuned weights. A new place to run it.

- Users search a reports catalogue by concept, not by the name an analyst gave it
- "GP FTE" and "how many GPs do we have" share zero tokens
- A sentence embedding model, fine-tuned on the domain, closes that gap

<br/>

**This talk is about porting that model into PHP. Not re-deriving why semantic search works.**

<!-- note:
For anyone who wasn't in the room in May: full write-up and eval numbers at herdmentality.xyz/blog/auto-search. Don't re-derive the eval table here — it hasn't changed, same weights.

Exec framing: if asked "is this the same accuracy as the Java version" — yes, identical model, identical Recall@1. Nothing about porting to PHP changes the model's quality, only where it runs.

Keep this slide under 2 minutes. It's a bridge, not new content.
-->

---

## The Drupal Ecosystem's Answer Today

- **AI Search + Ollama** — a sidecar service, 5 to 15 GB RAM, a network hop even on localhost
- **AI Search / Semantic Search + OpenAI** — external API call per query, a key to manage, per-query cost
- **Search API Embeddings** — in-process, but Word2Vec, 2013-era tech
- **Scolta** (new, Aug 2026) — client-side lexical index + LLM query rewriting, not embeddings

<br/>

**Every path is a sidecar, a call, or not actually semantic.**

<div class="def"><strong>FFI</strong> — Foreign Function Interface. Lets PHP call native C++ code directly, no network involved.</div>

<!-- note:
Scan slide — list, not deep technical content. Move at pace.

Scolta needs one sentence of respect, not dismissal: same instinct (no search server), different mechanism (lexical index in the browser, not vector embeddings). If someone in the room has tried Scolta, this is the moment they'll raise a hand — welcome it, it's a genuine adjacent tool.

Exec framing: this is the "why doesn't this already exist" slide. Point at RAM cost and per-query billing as the two numbers that matter for a budget conversation.
-->

---

![bg contain](screenshots/drupal-keyword-miss.png)
![bg contain](screenshots/drupal-semantic-hit.png)

<!-- note:
Full-bleed split. No narration needed — let the room read it.
"Same query. Same Drupal module. Different search."

This is the gap named on the previous slide, made concrete before the live demo.
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

Platform adaptation: if the venue wifi is unreliable, this entire demo is local Docker — no internet dependency. Say so up front; it's a feature of the architecture, not a caveat.

Backup: if Docker fails to start, screenshots from this exact sequence are on the next few slides regardless — narrate from them if needed.
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
This is the "so what" slide — land it clearly before moving into architecture. Exec audience: this is the moment to say "no new service to procure, no new SLA to negotiate."

Peer audience: the size number (22 MB) is doing the work here — it's smaller than most people's mental model of "a machine learning model."
-->

---

## Architecture

![w:1200](diagrams/drupal-runtime-flow.svg)

The Vue frontend is unchanged. Everything new is in the PHP module.

<div class="def"><strong>ONNX</strong> — Open Neural Network Exchange. A portable model format; the same file runs in Java, Python or PHP.</div>

<!-- note:
[deep] slide — signpost verbally: "this one's for the people who want the mechanism, feel free to zone out for 90 seconds if you just want the shape of it."

The Vue SPA is served as a Drupal library, same pattern as the July 2025 Vue.js-in-Drupal talk. Nothing changed there.

Exec framing: point at the box labelled "Drupal 10 module (single PHP process)" — this is the entire new deployment surface. One module, no new infrastructure.
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

This is the highest-risk piece of the whole port — validated token-for-token against the Java and Python implementations before trusting it near the model.

Peer question likely to come up: "why not just call out to a Python sidecar for tokenization?" Answer: that reintroduces exactly the sidecar dependency the whole talk argues against. If you're going to run the model in-process, the tokenizer has to be in-process too.

Second code block available if there's time/interest: EmbeddingService::embed() showing the FFI call into ankane/onnxruntime-php and the mean-pool/L2-normalise step, identical logic to the Java version.
-->

---

## Two Deployment Modes

| | Self-hosted Drupal | GovCMS SaaS |
|---|---|---|
| `libonnxruntime.so` | Install in one line | Not available |
| Embedding at query time | In the PHP process | Thin sidecar required |
| Model size | 22 MB | 22 MB |
| Ollama? | No | No |

**Even the sidecar path stays small: 22 MB and one HTTP call. No GPU. No Ollama.**

<!-- note:
This is the honest-caveat slide — do not skip or soften it. Strong GovCMS contingent in this room; they will ask about this unprompted if it isn't addressed first.

Exec framing: this is the slide that answers "can my team actually run this" for anyone on managed hosting. The answer is "not identically, but the fallback is still small."

Don't let this slide read as a retreat — the honest framing is what builds trust with a peer audience that's allergic to hand-waving.
-->

---

## Lessons Learnt

- **FFI and `intl` extensions aren't compiled in by default** — bites on managed PHP images without root access to the build
- **Lazy service proxies break constructor type hints** — Drupal's generated proxies don't extend the concrete class; type the constructor as `object`
- **MariaDB 10.11 requires SSL by default** — `mysqladmin` and `pdo_mysql` both fail until `--skip-ssl` is set explicitly

<!-- note:
[scan] slide but each bullet needs its one-line so-what said out loud, not just read — these are the three that would waste someone a full afternoon if they hit them cold.

Peer audience: this is the "here's what I tried first and didn't work" content the profile calls for. Don't rush past it for time; it's more valuable than the architecture slide to someone about to attempt this themselves.
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
Most student-friendly and recruiter-friendly slide in the deck — say the URL out loud, don't just show it.

If asked about swapping in a different corpus: corpus.json and the model artefacts are the only things that change; setup-model.sh takes any corpus name matching a folder under examples/.
-->

---

## Conclusion

"The Drupal ecosystem doesn't need a sidecar to run a real ML model. It needs someone willing to hand-port a tokenizer."

<br/>

- The in-process pattern isn't JVM-specific — it travels to any runtime with an FFI story
- Naming the honest limits (GovCMS) built more trust than hiding them would have
- Clone it, break it, tell me what you find

<br/>

**github.com/cchew/auto-search (drupal branch)**

<!-- note:
Land the takeaway: the pattern generalises past both Java and PHP. Anywhere with an FFI story and a small enough model, sidecars are a choice, not a requirement.

Open Q&A. Likely questions:
- "Does this work on Drupal 11?" — yes, info.yml declares ^10 || ^11
- "What about content types beyond a flat corpus?" — corpus.json is the interface; anything that flattens to items with a name/description works today, entity-aware indexing is future work
- "Why not just use Scolta?" — different problem: Scolta rewrites queries against a lexical index; this does real semantic similarity. Use Scolta if you want zero infra and can live with lexical search; use this if you need the model to actually understand domain vocabulary.

Platform adaptation: if this is presented again internally (Teams), swap the GitHub CTA for an ADO Wiki link to the internal build notes.
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
Cover only if asked. This is the "what would you still need to do before production" list — a peer audience will ask, an exec audience usually won't.
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
Tech stack on request. The point to land if asked: nothing about the model or training pipeline changed for this port — only the runtime host.
-->
