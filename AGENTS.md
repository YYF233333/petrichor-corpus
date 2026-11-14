# AGENTS.md

This file is the whole context an agent needs to work here. Links point to background, not to further rules.

## Project

petrichor-corpus holds the evidence behind the design of [Petrichor](https://github.com/YYF233333/Petrichor), a statically typed successor to GDScript. Petrichor's [spec](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md) is the source of truth for the rules. This repository answers design questions with real Godot 4 code and records the answers.

- `corpus/vN.json`: corpus manifest version N. It lists the sparse-checkout patterns and, per repository, `name`, `url`, `commit` and `group`.
- `fetch.py`: `python fetch.py vN` clones manifest N into `corpus/vN/`, which git ignores.
- `surveys/<name>.md`: a write-up. `surveys/<name>/`: its scripts and committed results.
- `surveys/corpus-counts.md`: single counts, each backing one spec rule, named in its "用于" column.
- `surveys/cross-branch-duplication/gdcorpus.py`: corpus access most scripts share: the manifest, first-party rules, a GDScript tokenizer and scene composition.
- `reproduce.py`: reruns the surveys whose committed results reproduce and compares them. CI runs it on every push.
- `decisions.md`, `decisions.zh.md`: the decision index, one row per spec rule backed by corpus evidence.
- `inputs/`, `work/`, `out/`: inputs and outputs outside the corpus, ignored by git.

Requirements: Python 3.11 with the standard library only, and git. `README.md` gives the setup commands.

## Surveys

- A survey is a write-up plus the scripts and results that reproduce it, on a pinned corpus version.
- The write-up states the question, the corpus version, the method, the numbers and the conclusions. It ends with a 复现 section giving the exact commands.
- A single count that backs one rule is a row in `surveys/corpus-counts.md`, with its script under `surveys/corpus-counts/`.
- A survey records the design it evaluated. When Petrichor's design changes, do not rewrite the data. Point to the current rule instead.
- Pin every input outside the corpus by commit or date, and name it in the write-up: a Godot source checkout, `extension_api.json`, GitHub issues.
- Never commit corpus code. Commit manifests, scripts, derived results and short excerpts.
- Cite corpus code by GitHub links at the pinned commit: `https://github.com/<owner>/<repo>/blob/<commit>/<path>#L<line>`.

## Method

- Judgments made by reading code are sampled. This covers the "经阅读" parts of counts and hand labels such as `classification.json` or `labels.csv`.
  - Draw at most 50 sites per item.
  - Draw them with a fixed random seed, and record the seed with the result.
  - State the conclusion as a proportion of the sample.
  - The full readings already made on corpus v1 stay as they are.
- On a new corpus version, rerun every number in full. Read code again only where a number moves close to the threshold of the decision it backs.
- Surveys count at most 20,000 first-party lines per repository, drawn by file with the fixed seed recorded in the manifest.
- Survey scripts read the corpus manifest, so old scripts run on any corpus version unchanged. `gdcorpus.REPOS` reads `corpus/v1.json`, or the manifest named by the `CORPUS_MANIFEST` environment variable.
- A script moves to a shared parsing layer only when it must change anyway. New surveys use the shared layer once it exists.

## Results

- Committed results are compared without regard to line endings.
- A changed script must reproduce its committed results exactly. Otherwise the same commit explains each difference and updates the write-up's numbers.
- A ported script is accepted only if it reproduces the committed results exactly, or each difference is explained. Porting covers a new language, the shared parsing layer and a new corpus version.
- Never overwrite a committed result that differs without finding the cause.

## Documentation

- `README.md` (English) and `README.zh.md` (Chinese) say the same thing and change in the same commit.
- `decisions.md` and `decisions.zh.md` hold the same rows and change in the same commit. A row gives the rule (spec section and concept, linked to the spec), its evidence (a link to the survey or count) and the Petrichor commit that decided it.
- When a survey adds or changes evidence for a rule, update the decision index in the same commit.
- Write-ups are in Chinese.
- Write one idea per sentence. Keep sentences under 60 Chinese characters or 30 English words.
  - Turn an embedded list or a chain of "or" into a list.
  - Put the condition before the result.
  - Put citations and links at the end, in brackets.
- Decided content carries no marker. Mark open questions 【待定】/[Open].

## Commits

- Commit messages are in English: a subject, a blank line and a body wrapped at 72 columns.
  - The subject is `Area: Imperative summary` within 72 characters, capitalized and without a full stop.
  - `Area` is one of `Survey`, `Corpus`, `Index`, `Tools` and `Docs`. A commit spanning several areas names the primary one.
  - The body gives the problem, the decision with its evidence and the alternatives rejected. Use `-` lists for parallel points.
  - Do not retell the diff; a small change needs no body.
- Other sessions may share the working tree. Commit only your own files, by path: `git commit -m "..." -- <paths>`.
- Push to main after committing. Keep CI green.
