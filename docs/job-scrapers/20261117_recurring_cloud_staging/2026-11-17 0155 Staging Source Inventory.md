# Staging source inventory

Generated 2026-11-17T02:08:44.315405+00:00. Static UTF-8 line counts/SHA-256; Python AST; JS declaration scan (not complete call graph).

Current staging controller, runner, workflow and operator/documentation source; historical Docker prototype and full candidate snapshots excluded from this active inventory.

| Local file | Physical / nonblank lines | SHA-256 |
|---|---:|---|
| `build_catalog.py` | 32 / 32 | `0d18f5cb45aab21e94dd6b894bae102dd256f320c7720788175e30267fd2466b` |
| `bundle/catalog.json` | 3665 / 3665 | `b4eee1968a4bda5734318b0e22ea54f4abaec270e2a95a8cbcfc5e37b41a38f7` |
| `bundle/ci_run.py` | 27 / 27 | `6b9b235777981e1435dd76849966739b725a27dd5737f9367ce5e4652aabc2f9` |
| `bundle/isolation/sitecustomize.py` | 9 / 9 | `2890d8952533ea4fb1135023f2701013d02998ab9ee33a1298ce746464d28145` |
| `bundle/live_probe.py` | 66 / 63 | `83c4827e8f23ea5190cd77a6690fb26bbd99340834c21b3387992700998d3808` |
| `bundle/network_guard.py` | 61 / 56 | `22fd41d479cd72dac2efd73816861d15b37b211e5f494d55ab10471f309ebd55` |
| `bundle/requirements.txt` | 8 / 8 | `047d5d258723268dc963340966b85673e0a9e3d5493d7604ffe34e3b06e632e5` |
| `bundle/server.py` | 61 / 58 | `c4d25cc1c4c6c63d45aced040e846a7e1425b24dd9ed4bc54f5fbe2e7d0de62f` |
| `catalog.mjs` | 1 / 1 | `146cf8711bcc70349377dcf85bc5ab0f92b194ff0334791ed733119964393e61` |
| `check_documentation.py` | 26 / 26 | `2ddc459a6ba74ceba159f49e212d48943b74b0de2b699f011116b1ed7456a769` |
| `cloud_admin.py` | 63 / 63 | `aab02509f915c20b42801c09d57f1b171929cb6f6c2f3f39c9441ade09add0a3` |
| `document_build.py` | 47 / 47 | `f4db66075e30469163373cb674faa1be0a21890268a98c44bd9a19ca9e6cf714` |
| `finalize_documentation.py` | 84 / 63 | `90eb9149610731a4702f8f53edd6719af366d829ae1e549caa0f2c50df0474d1` |
| `finalize_sources.py` | 15 / 15 | `e4e3b1129ef9aa2f3f098fb5d50e57b7216515c223494e8f6d37cd67ae5c248d` |
| `github_admin.py` | 44 / 44 | `dfbf5b8f2aa0e8d5186167939e2bba65d99117a497796bb33a3aef7193e74fef` |
| `inspect_cloud.py` | 23 / 23 | `2d0e9c9befbc458ab81ec8bca5363ed0ea4a546b1a4461b9fd0feac5a3e933f0` |
| `main-staging-recurring.yml` | 74 / 74 | `eaa24b991e77d02b09a1f27aadf02cfc3dfdf57b761f2b3fc9c91faa4df00c8f` |
| `pivot_to_actions.py` | 40 / 40 | `dcbcd5c71bfba13e8ee974a00a3655dd11e897670b2de11953b2e8374fe547ec` |
| `prepare_actions.py` | 18 / 18 | `83f93a51682c8099dd7abc4ed07e9e0f1672e95097a410bc45f5db54654e24f0` |
| `prepare_documentation_commit.py` | 18 / 18 | `39be09ce1411cb55b66a5a71c0197de4a469c39d7d6dc5213313af9c41671e6b` |
| `prepare_staging_commit.py` | 12 / 12 | `059a59bdd84f4c631a6cc5ab5fd67f340802bab0c1fa4e46d508a4c43c9221ca` |
| `snapshot_sources.py` | 27 / 27 | `8111e761227c8b0c15a0f60ca0795f2af47b4c50fe4c6d1aac77768158b377c1` |
| `sportsbook-staging-recurring.yml` | 74 / 74 | `e07bd7ad1c8fa2bf725eb8c1ceb0a9abbaaa503812b65241e04e2e4b1b262e61` |
| `staging-cloud-tests.yml` | 26 / 26 | `25c8fe2b3ae538ee947027648976dcc874011b42706a5354327bbd3cffb9f43e` |
| `staging-recurring.yml` | 74 / 74 | `0f94e842fd3562b5eb2819e026e82da5772be0d4aecd29c1d9f045dbac7a26d4` |
| `tech-staging-recurring.yml` | 74 / 74 | `eaa24b991e77d02b09a1f27aadf02cfc3dfdf57b761f2b3fc9c91faa4df00c8f` |
| `test_network_guard.py` | 37 / 37 | `4647456955ee34c1cca0d09871cdfa71e2acf871780238f89248d3743e2c6eab` |
| `test_staging.mjs` | 27 / 27 | `6087cbefa34b0baebbf95b532ec489ab46ea206d8d8c29da13b6fc1e250f970a` |
| `verify_deployments.py` | 38 / 38 | `52ac17b62eab4b612045456c7e7f4121b24c71a214ff0d05600eab8b3254b056` |
| `worker.mjs` | 143 / 142 | `535da829abd0554d4bc2ffe0b4a92130d563f52e121ba616f9e41fa1d8fa9cd1` |

Absolute local paths and per-function/class positions are in `source_inventory.json`. Remote harness files use `runtime/staging/`; local `bundle/*.py` maps to `runtime/staging/runner/*.py`. Module workflow variants map to `.github/workflows/staging-recurring.yml` in their respective repositories. The operations document describes every runtime stage and caller.

## Candidate snapshots

The candidates are exact Git SHAs listed in the operations document. `bundle/source_manifest.json` provides inspected source-file hashes; `bundle/sources/` is private local inspection evidence and is not deployed. Runtime checkouts come directly from GitHub. Existing production inventories remain separately dated and are not silently relabelled current.
