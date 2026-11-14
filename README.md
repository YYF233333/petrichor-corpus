# petrichor-corpus

[中文](README.zh.md)

This repository holds the evidence behind the design of [Petrichor](https://github.com/YYF233333/Petrichor), a statically typed scripting language for Godot 4 that keeps GDScript's syntax. When real code can answer a design question, Petrichor surveys real Godot 4 projects first. Each survey here is a write-up plus the scripts and results that reproduce it. The [decision index](decisions.md) leads from each spec rule to its evidence and back.

## Surveys

The write-ups are in Chinese. Each ends with the commands that reproduce it.

- [Do scripts see more than one scene structure?](surveys/scene-structures.md)
- [How much code is duplicated because native base classes differ?](surveys/cross-branch-duplication.md)
- [Pitfalls of the engine, GDScript and the C# bridge](surveys/pitfalls.md)
- [How do real Godot 4 projects use property getters and setters?](surveys/property-accessors.md)
- [How often are the results of awaiting multi-argument signals used?](surveys/await-signal-results.md)
- [Where are script members used: in their file, in subclasses, in other scripts?](surveys/member-visibility.md)
- [Members the engine accesses by name](surveys/by-name-access.md)
- [The cost of migrating real code under the current design](surveys/paper-migration-2.md)
- [The cost of migrating real code under spec v0.1](surveys/paper-migration.md)
- [What does computing the constants of real code take?](surveys/constant-expressions.md)
- [Which constructs does real code use that the implementation does not support yet?](surveys/implementation-coverage.md)
- [Single counts in the corpus](surveys/corpus-counts.md)

## Corpus

`corpus/v1.json` pins 20 Godot 4 repositories at fixed commits. Each has a group: game, plugin, demos or tool. Fetch it with Python 3.11 and git:

```
python fetch.py
```

The clones are shallow, blobless and sparse. They hold only `.gd`, `.tscn`, `.tres` and other text files. They go to `corpus/v1/`, which git ignores.

## Rerunning

Several scripts also read the engine's API description. Download it once:

```
curl -sSfL --create-dirs -o inputs/extension_api-4-7.json https://raw.githubusercontent.com/godotengine/godot-cpp/8070599885b6df675fcad033dd032ce44be2b850/gdextension/extension_api-4-7.json
```

`python reproduce.py` reruns the surveys whose committed results reproduce from these inputs. It fails on any difference, and CI runs it on every push. Each write-up's 复现 section lists its own commands. Some need inputs outside the corpus, which that section names:

- a Godot source checkout at a given commit;
- GitHub searches, whose results change over time.

## Method

- A survey runs on a pinned corpus version. A larger corpus gets a new manifest, and the old one stays.
- Scripts read the corpus manifest, so old scripts run on any corpus version unchanged.
- On a new corpus version, every number is rerun in full. Code is read again only where a number moves close to the threshold of the decision it backs.
- Judgments made by reading code are sampled: at most 50 sites per item, chosen with a fixed random seed recorded with the result. The conclusion is stated as a proportion. The full readings already made on v1 stay as they are.
- A survey records the design it evaluated. When Petrichor's design changes, the data stays, and the decision index points to the current rule.

## License

The code in the corpus belongs to its authors, under their own licenses. This repository keeps only manifests, scripts, derived results and short excerpts. It cites corpus code by GitHub links at the pinned commits.

`surveys/paper-migration*/migrated/` holds rewrites of two projects. The rewrite of Kenney's FPS starter kit keeps that kit's license, in `migrated/fps/LICENSE.md`. The rewrite of Ring is published under the MIT License with its author's consent. Everything else here is under the [MIT License](LICENSE).
