# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v3.29.0] - 2025-06-16

### :bug: Bug Fixes
* fix: Local PIs need to override global ones, not the other way around by @cabo in https://github.com/ietf-tools/xml2rfc/pull/1237
* Fix for #1204 - single letter names  by @TheEnbyperor in https://github.com/ietf-tools/xml2rfc/pull/1246
* fix(pdf): Scale large SVG artwork by @kesara in https://github.com/ietf-tools/xml2rfc/pull/1244

### :wrench: Chores
* chore: Remove v3compat files by @kesara in https://github.com/ietf-tools/xml2rfc/pull/1240
* chore: Delete obsolete INSTALL file by @kesara in https://github.com/ietf-tools/xml2rfc/pull/1234
* ci: Fix release GHA issues by @kesara in https://github.com/ietf-tools/xml2rfc/pull/1249


## [v3.28.1] - 2025-04-01
### :wrench: Chores
* refactor: Unnecessary global declarations by @kesara in https://github.com/ietf-tools/xml2rfc/pull/1233
* chore(pdf): Update WeasyPrint to v65.0 by @kesara in https://github.com/ietf-tools/xml2rfc/pull/1231
* ci: Fix GitHub publish issue by @kesara in https://github.com/ietf-tools/xml2rfc/pull/1232


## [v3.28.0] - 2025-03-01
### :sparkles: New Features
* feat: Remove warning about SVG width and height by @martinthomson in https://github.com/ietf-tools/xml2rfc/pull/1225

### :wrench: Chores
* docs: Update installation instructions by @kesara in https://github.com/ietf-tools/xml2rfc/pull/1221
* ci: Remove setup.cfg publish commit step by @kesara in https://github.com/ietf-tools/xml2rfc/pull/1220
* chore(deps): Update WeasyPrint to v64.1 by @kesara in https://github.com/ietf-tools/xml2rfc/pull/1215
* chore: Add ACKNOWLEDGMENTS.md file by @kesara in https://github.com/ietf-tools/xml2rfc/pull/1214


## [v3.27.0] - 2025-02-09
### :sparkles: New Features
 * feat: Respect `--allow-local-file-access` flag in `artwork` and `sourcecode` ([GHSA-432c-wxpg-m4q3](https://github.com/ietf-tools/xml2rfc/security/advisories/GHSA-432c-wxpg-m4q3)) by @kesara https://github.com/ietf-tools/xml2rfc/commit/ec98f9cb4b9a8658222117df037dda473ca3f4e4

### :bug: Bug Fixes
 * fix: Make warnings respect quite flag by @kesara in https://github.com/ietf-tools/xml2rfc/pull/1217

### :wrench: Chores
* ci: Fix publish GHA issues by @kesara in https://github.com/ietf-tools/xml2rfc/pull/1213
* build: Fix and improve Docker images by @kesara in https://github.com/ietf-tools/xml2rfc/pull/1212
* ci: Run tests daily by @kesara in https://github.com/ietf-tools/xml2rfc/pull/1218


## [v3.26.0] - 2025-01-29
### :sparkles: New Features
* feat: Add option to update datatracker references by @kesara in https://github.com/ietf-tools/xml2rfc/pull/1168
* feat: Migrate to pyproject.toml by @kesara in https://github.com/ietf-tools/xml2rfc/pull/1200

### :bug: Bug Fixes
* fix(html): Use basename for alternative link by @kesara in https://github.com/ietf-tools/xml2rfc/pull/1198
* fix: Add quotes to pip extra command by @kesara in https://github.com/ietf-tools/xml2rfc/pull/1202
* fix: Exit gracefully on artwork and sourcecode src file access errors by @kesara in https://github.com/ietf-tools/xml2rfc/pull/1203
* fix(text): Improve sentence ending logic by @kesara in https://github.com/ietf-tools/xml2rfc/pull/1206
* fix(pdf): Fix suboptimal overflow issues in the header by @kesara in https://github.com/ietf-tools/xml2rfc/pull/1207

### :wrench: Chores
* build: Update Python publish GHA by @kesara in https://github.com/ietf-tools/xml2rfc/pull/1208
* ci: Use correct environment name for testpypi by @kesara in https://github.com/ietf-tools/xml2rfc/pull/1209


## [v3.25.0] - 2024-11-25
### :sparkles: New Features
- [`7b8ed97`](https://github.com/ietf-tools/xml2rfc/commit/7b8ed97716fca1997d4903799145d532d4390740) - Drop support for Python 3.8 *(PR [#1183](https://github.com/ietf-tools/xml2rfc/pull/1183) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *addresses issue [#1146](https://github.com/ietf-tools/xml2rfc/issues/1146) opened by [@kesara](https://github.com/kesara)*

### :bug: Bug Fixes
- [`bf52f86`](https://github.com/ietf-tools/xml2rfc/commit/bf52f861886a19aacc95938d5ba8ea5b62646785) - **pdf**: Fix line height issue with superscripts *(PR [#1165](https://github.com/ietf-tools/xml2rfc/pull/1165) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *fixes issue [#1160](https://github.com/ietf-tools/xml2rfc/issues/1160) opened by [@ajeanmahoney](https://github.com/ajeanmahoney)*
- [`b5381ac`](https://github.com/ietf-tools/xml2rfc/commit/b5381ac89bcc4b339a337544afd39f740ddfe404) - Remove deprecated cgi method *(PR [#1182](https://github.com/ietf-tools/xml2rfc/pull/1182) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *fixes issue [#1153](https://github.com/ietf-tools/xml2rfc/issues/1153) opened by [@kitterma](https://github.com/kitterma)*
- [`2f17276`](https://github.com/ietf-tools/xml2rfc/commit/2f17276c680a7cb201254ec1894314ee28653c3d) - **text**: Fix truncated text issue in cells with rowspan *(PR [#1184](https://github.com/ietf-tools/xml2rfc/pull/1184) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *fixes issue [#1155](https://github.com/ietf-tools/xml2rfc/issues/1155) opened by [@ajeanmahoney](https://github.com/ajeanmahoney)*

### :memo: Documentation Changes
- [`f0aeb65`](https://github.com/ietf-tools/xml2rfc/commit/f0aeb656770d7c26118dedb33d9dcbcc0e66b466) - update CHANGELOG.md + py file versions for v3.24.0 [skip ci] *(commit by [@kesara](https://github.com/kesara))*

### :wrench: Chores
- [`5d38e19`](https://github.com/ietf-tools/xml2rfc/commit/5d38e192342b1b764f14e71eff29f73562db8bb5) - Remove obsolete script *(PR [#1185](https://github.com/ietf-tools/xml2rfc/pull/1185) by [@kesara](https://github.com/kesara))*
- [`8085bcc`](https://github.com/ietf-tools/xml2rfc/commit/8085bcce2f33c3156641fb790b107536ef6b16f5) - Cleanup MANIFEST.in *(PR [#1186](https://github.com/ietf-tools/xml2rfc/pull/1186) by [@kesara](https://github.com/kesara))*


## [v3.24.0] - 2024-10-28
### :sparkles: New Features
- [`dce083d`](https://github.com/ietf-tools/xml2rfc/commit/dce083d139f37ee38c82d61f962c9194d5abaa6d) - Add support for Python 3.13 *(PR [#1175](https://github.com/ietf-tools/xml2rfc/pull/1175) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *addresses issue [#1145](https://github.com/ietf-tools/xml2rfc/issues/1145) opened by [@kesara](https://github.com/kesara)*

### :white_check_mark: Tests
- [`c8f9b7f`](https://github.com/ietf-tools/xml2rfc/commit/c8f9b7fe40ee0afdfba6e6633cff78e3a97d2b0d) - Add RFC 10k test *(PR [#1180](https://github.com/ietf-tools/xml2rfc/pull/1180) by [@kesara](https://github.com/kesara))*

### :construction_worker: Build System
- [`ebc2178`](https://github.com/ietf-tools/xml2rfc/commit/ebc21784087818ba60e81b1d2e5f05d489b46029) - Remove OpenPGP keys *(PR [#1162](https://github.com/ietf-tools/xml2rfc/pull/1162) by [@kesara](https://github.com/kesara))*
- [`2fd70e8`](https://github.com/ietf-tools/xml2rfc/commit/2fd70e8ea00e6a70424fdc8183b251b9893b9d5d) - Enable tests on Windows OS *(PR [#1177](https://github.com/ietf-tools/xml2rfc/pull/1177) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *addresses issue [#1178](https://github.com/ietf-tools/xml2rfc/issues/1178) opened by [@kesara](https://github.com/kesara)*
- [`0e8fee4`](https://github.com/ietf-tools/xml2rfc/commit/0e8fee458e8f76a6273e0daaf8cc8b6a6eb33d62) - Run macOS tests on m1 processor *(PR [#1141](https://github.com/ietf-tools/xml2rfc/pull/1141) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *addresses issue [#1129](https://github.com/ietf-tools/xml2rfc/issues/1129) opened by [@kesara](https://github.com/kesara)*

### :memo: Documentation Changes
- [`0b4bea0`](https://github.com/ietf-tools/xml2rfc/commit/0b4bea011fd4a91c3f7352ee254e6c81e9749c84) - update CHANGELOG.md + py file versions for v3.23.2 [skip ci] *(commit by [@kesara](https://github.com/kesara))*

### :wrench: Chores
- [`3f649a3`](https://github.com/ietf-tools/xml2rfc/commit/3f649a3473d3f99425276f54e52ea0260848288e) - **deps**: Bump up lxml to 5.3.0 *(PR [#1173](https://github.com/ietf-tools/xml2rfc/pull/1173) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *addresses issue [#1070](https://github.com/ietf-tools/xml2rfc/issues/1070) opened by [@kesara](https://github.com/kesara)*
- [`d36244c`](https://github.com/ietf-tools/xml2rfc/commit/d36244cea222812d0cd33b9f57b813400898d56a) - Remove legacy Dockerfile syntax *(PR [#1176](https://github.com/ietf-tools/xml2rfc/pull/1176) by [@kesara](https://github.com/kesara))*


## [v3.23.2] - 2024-10-01
### :bug: Bug Fixes
- [`f297f11`](https://github.com/ietf-tools/xml2rfc/commit/f297f115b34dc3c3391410c2c6c06f903daf5937) - **v2v3**: Use bib.ietf.org for I-D xinclude references *(PR [#1166](https://github.com/ietf-tools/xml2rfc/pull/1166) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *fixes issue [#1008](https://github.com/ietf-tools/xml2rfc/issues/1008) opened by [@ajeanmahoney](https://github.com/ajeanmahoney)*
- [`83e897f`](https://github.com/ietf-tools/xml2rfc/commit/83e897fe523a84630ec7bfd9805a887128897082) - **text**: Capitalize "type" in non-ASCII artwork message *(PR [#1170](https://github.com/ietf-tools/xml2rfc/pull/1170) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *fixes issue [#1169](https://github.com/ietf-tools/xml2rfc/issues/1169) opened by [@ajeanmahoney](https://github.com/ajeanmahoney)*

### :memo: Documentation Changes
- [`29be9c8`](https://github.com/ietf-tools/xml2rfc/commit/29be9c8002ce0313ce5e3ff7b52b582301c4f096) - update CHANGELOG.md + py file versions for v3.23.1 [skip ci] *(commit by [@kesara](https://github.com/kesara))*


## [v3.23.1] - 2024-09-17
### :bug: Bug Fixes
- [`e2b8734`](https://github.com/ietf-tools/xml2rfc/commit/e2b87343c5341d521f3dceb4976fad8054ac7efd) - **text**: Update non-ASCII art text *(PR [#1140](https://github.com/ietf-tools/xml2rfc/pull/1140) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *fixes issue [#617](https://github.com/ietf-tools/xml2rfc/issues/617) opened by [@ietf-svn-bot](https://github.com/ietf-svn-bot)*

### :construction_worker: Build System
- [`3dfb04c`](https://github.com/ietf-tools/xml2rfc/commit/3dfb04cac22302d3c36cc3580e6bab1ec754e337) - Update pydyf version requirement *(PR [#1159](https://github.com/ietf-tools/xml2rfc/pull/1159) by [@kesara](https://github.com/kesara))*
- [`e589691`](https://github.com/ietf-tools/xml2rfc/commit/e589691629377444c499dcb248ef8fef0f84c6e9) - Remove upload artifacts step *(PR [#1161](https://github.com/ietf-tools/xml2rfc/pull/1161) by [@kesara](https://github.com/kesara))*
- [`50c3a44`](https://github.com/ietf-tools/xml2rfc/commit/50c3a44a6131258580064ffe437732f2ae3a266b) - Update GHAs *(PR [#1163](https://github.com/ietf-tools/xml2rfc/pull/1163) by [@kesara](https://github.com/kesara))*

### :memo: Documentation Changes
- [`cbf4137`](https://github.com/ietf-tools/xml2rfc/commit/cbf41377d20295410a09fd8c62fd664632339e7a) - update CHANGELOG.md + py file versions for v3.23.0 [skip ci] *(commit by [@kesara](https://github.com/kesara))*


## [v3.23.0] - 2024-08-21
### :sparkles: New Features
- [`f743092`](https://github.com/ietf-tools/xml2rfc/commit/f7430927ee4d7e8c71bea6b7d76411e5b40cbde5) - Pin WeasyPrint 61.2 *(PR [#1147](https://github.com/ietf-tools/xml2rfc/pull/1147) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *addresses issue [#1131](https://github.com/ietf-tools/xml2rfc/issues/1131) opened by [@kesara](https://github.com/kesara)*

### :bug: Bug Fixes
- [`058479b`](https://github.com/ietf-tools/xml2rfc/commit/058479bf3a8ebcc2b37a145edf246c3417ead5e5) - **text**: Render ol and ul inside blockquote correctly *(PR [#1150](https://github.com/ietf-tools/xml2rfc/pull/1150) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *fixes issue [#1148](https://github.com/ietf-tools/xml2rfc/issues/1148) opened by [@rvanrheenen](https://github.com/rvanrheenen)*
- [`bdafb27`](https://github.com/ietf-tools/xml2rfc/commit/bdafb274b276e875a6f7c55e1c11f03af902022b) - Add background to tt and code inside dt *(PR [#1144](https://github.com/ietf-tools/xml2rfc/pull/1144) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *fixes issue [#1142](https://github.com/ietf-tools/xml2rfc/issues/1142) opened by [@ajeanmahoney](https://github.com/ajeanmahoney)*

### :memo: Documentation Changes
- [`7776234`](https://github.com/ietf-tools/xml2rfc/commit/7776234396bc7b823e81b7d1a08d453f689f0561) - update CHANGELOG.md + py file versions for v3.22.0 [skip ci] *(commit by [@kesara](https://github.com/kesara))*


## [v3.22.0] - 2024-07-02
### :sparkles: New Features
- [`b6391a1`](https://github.com/ietf-tools/xml2rfc/commit/b6391a163dbaba0818f634a33ebafd01a5095b77) - Use fonts from xml2rfc-fonts *(PR [#1124](https://github.com/ietf-tools/xml2rfc/pull/1124) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *addresses issue [#1030](https://github.com/ietf-tools/xml2rfc/issues/1030) opened by [@kesara](https://github.com/kesara)*
  - :arrow_lower_right: *addresses issue [#1121](https://github.com/ietf-tools/xml2rfc/issues/1121) opened by [@kesara](https://github.com/kesara)*
- [`14cf536`](https://github.com/ietf-tools/xml2rfc/commit/14cf53656fb7e7a0115bf224c768b38c502d9476) - Remove dependency on six *(PR [#1134](https://github.com/ietf-tools/xml2rfc/pull/1134) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *addresses issue [#1130](https://github.com/ietf-tools/xml2rfc/issues/1130) opened by [@kesara](https://github.com/kesara)*

### :bug: Bug Fixes
- [`7a30635`](https://github.com/ietf-tools/xml2rfc/commit/7a306352588c4ae3ff5826b7d2848016c4e022d6) - Use correct list style for upper case roman *(PR [#1123](https://github.com/ietf-tools/xml2rfc/pull/1123) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *fixes issue [#1122](https://github.com/ietf-tools/xml2rfc/issues/1122) opened by [@cabo](https://github.com/cabo)*

### :construction_worker: Build System
- [`a768f39`](https://github.com/ietf-tools/xml2rfc/commit/a768f39ac4c51e24d3d9516407513324b795fa18) - Update CodeQL Action to v2 *(PR [#1132](https://github.com/ietf-tools/xml2rfc/pull/1132) by [@kesara](https://github.com/kesara))*

### :memo: Documentation Changes
- [`01661ae`](https://github.com/ietf-tools/xml2rfc/commit/01661ae9c88c948586f70c011d372968ffface6b) - update CHANGELOG.md + py file versions for v3.21.0 [skip ci] *(commit by [@kesara](https://github.com/kesara))*


## [v3.21.0] - 2024-04-08
### :sparkles: New Features
- [`ca39326`](https://github.com/ietf-tools/xml2rfc/commit/ca3932629457a441d2a8797a4d28aa42c1521dce) - Validate docName and seriesInfo value for I-D *(PR [#1116](https://github.com/ietf-tools/xml2rfc/pull/1116) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *addresses issue [#1115](https://github.com/ietf-tools/xml2rfc/issues/1115) opened by [@kesara](https://github.com/kesara)*

### :bug: Bug Fixes
- [`312b01a`](https://github.com/ietf-tools/xml2rfc/commit/312b01a3a941d1f5a8e16594913051ba2ec8a443) - Avoid breaking citation labels *(PR [#1114](https://github.com/ietf-tools/xml2rfc/pull/1114) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *fixes issue [#685](https://github.com/ietf-tools/xml2rfc/issues/685) opened by [@ietf-svn-bot](https://github.com/ietf-svn-bot)*

### :memo: Documentation Changes
- [`c8e2998`](https://github.com/ietf-tools/xml2rfc/commit/c8e2998d86eaa791277e5479c225634c67661816) - update CHANGELOG.md + py file versions for v3.20.1 [skip ci] *(commit by [@kesara](https://github.com/kesara))*


## [v3.20.1] - 2024-03-11
### :bug: Bug Fixes
- [`f58e052`](https://github.com/ietf-tools/xml2rfc/commit/f58e052ebc5a6b07cd0cd51f82f470a0af8d61bd) - Change non-current year error to a warning *(PR [#1109](https://github.com/ietf-tools/xml2rfc/pull/1109) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *fixes issue [#704](https://github.com/ietf-tools/xml2rfc/issues/704) opened by [@ietf-svn-bot](https://github.com/ietf-svn-bot)*

### :white_check_mark: Tests
- [`a809924`](https://github.com/ietf-tools/xml2rfc/commit/a809924d8ff627bfd0493a3067d0f1780ca5794f) - Fix recursion issue in walkpdf *(PR [#1112](https://github.com/ietf-tools/xml2rfc/pull/1112) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *addresses issue [#1111](https://github.com/ietf-tools/xml2rfc/issues/1111) opened by [@kitterma](https://github.com/kitterma)*

### :memo: Documentation Changes
- [`37f406c`](https://github.com/ietf-tools/xml2rfc/commit/37f406c5e1e036eab9162940e563bf349c1bd1b2) - update CHANGELOG.md + py file versions for v3.20.0 [skip ci] *(commit by [@kesara](https://github.com/kesara))*


## [v3.20.0] - 2024-02-21
### :sparkles: New Features
- [`e4542c2`](https://github.com/ietf-tools/xml2rfc/commit/e4542c29e217f09aeca5a0ae423fc45c73dee8a2) - Update subseries presentation *(PR [#1102](https://github.com/ietf-tools/xml2rfc/pull/1102) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *addresses issue [#1100](https://github.com/ietf-tools/xml2rfc/issues/1100) opened by [@ajeanmahoney](https://github.com/ajeanmahoney)*

### :bug: Bug Fixes
- [`20a5b30`](https://github.com/ietf-tools/xml2rfc/commit/20a5b30d9e08bd21184335fb12918ed0d4fe7c4c) - Allow non-ASCII values in all attributes *(PR [#1106](https://github.com/ietf-tools/xml2rfc/pull/1106) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *fixes issue [#1105](https://github.com/ietf-tools/xml2rfc/issues/1105) opened by [@cabo](https://github.com/cabo)*
- [`4278f7b`](https://github.com/ietf-tools/xml2rfc/commit/4278f7b7e0b64293646ac13d0c5dceb946927c5c) - **text**: Don't break URLs in annotation *(PR [#1104](https://github.com/ietf-tools/xml2rfc/pull/1104) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *fixes issue [#1101](https://github.com/ietf-tools/xml2rfc/issues/1101) opened by [@apaloma-rpc](https://github.com/apaloma-rpc)*

### :construction_worker: Build System
- [`75971ca`](https://github.com/ietf-tools/xml2rfc/commit/75971ca5d980a7ee90fa25f82720706927750dda) - PyPI publish GHA should not run on push to main branch *(PR [#1107](https://github.com/ietf-tools/xml2rfc/pull/1107) by [@kesara](https://github.com/kesara))*

### :memo: Documentation Changes
- [`c7dd9a1`](https://github.com/ietf-tools/xml2rfc/commit/c7dd9a1548bffcbcdebf109eb6def1a1f680a085) - update CHANGELOG.md + py file versions for v3.19.4 [skip ci] *(commit by [@kesara](https://github.com/kesara))*
- [`ec6d921`](https://github.com/ietf-tools/xml2rfc/commit/ec6d92162ba57cd9fb65a5cd91d4e7948c330f7f) - Update CHANGELOG.md *(commit by [@kesara](https://github.com/kesara))*


## [v3.19.4] - 2024-02-06

### :bug: Bug Fixes
- [`f319275`](https://github.com/ietf-tools/xml2rfc/commit/f319275b97bf9c0223d7b298404d7c00eb3b16cb) - revert: #1089 (Treat referencegroup entries similarly to reference entries) *(PR #1098 by @kesara)*
  - :arrow_lower_right: *fixes issue #1097 opened by @ajeanmahoney*

### :construction_worker: Build System
- [`8125806`](https://github.com/ietf-tools/xml2rfc/commit/8125806f3764ffcbb3bffb68111022d913870765) - Add revert to version bump list. *(commit by [@kesara](https://github.com/kesara))*

### :memo: Documentation Changes
- [`4cdfbbf`](https://github.com/ietf-tools/xml2rfc/commit/4cdfbbfd691736ce81edbd6c676528062e84e4f5) - update CHANGELOG.md + py file versions for v3.19.3 [skip ci] *(commit by [@kesara](https://github.com/kesara))*


## [v3.19.3] - 2024-02-04
### :bug: Bug Fixes
- [`1652d99`](https://github.com/ietf-tools/xml2rfc/commit/1652d99054928f9b218079db6788a2b5d0aa328a) - Silently pass when weasyprint is not installed *(PR [#1092](https://github.com/ietf-tools/xml2rfc/pull/1092) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *fixes issue [#1091](undefined) opened by [@kesara](https://github.com/kesara)*

### :recycle: Refactors
- [`534b366`](https://github.com/ietf-tools/xml2rfc/commit/534b36623382be8fe22bffd552d03b8ea3b81da9) - Use context managers when opening files *(PR [#1093](https://github.com/ietf-tools/xml2rfc/pull/1093) by [@kesara](https://github.com/kesara))*

### :memo: Documentation Changes
- [`a26d266`](https://github.com/ietf-tools/xml2rfc/commit/a26d26612aa164be4e37638a30b0af6a45b47f49) - update CHANGELOG.md + py file versions for v3.19.2 [skip ci] *(commit by [@kesara](https://github.com/kesara))*
- [`f7e4e7e`](https://github.com/ietf-tools/xml2rfc/commit/f7e4e7e2978aaf4b5c14521e020bf7470a5117e1) - Update README.md *(commit by [@kesara](https://github.com/kesara))*


## [v3.19.2] - 2024-01-31
### :bug: Bug Fixes
- [`f33c697`](https://github.com/ietf-tools/xml2rfc/commit/f33c6972a95eed84bc406fe0ae256c48bf25e45c) - Use importlib.metadata *(PR [#1079](https://github.com/ietf-tools/xml2rfc/pull/1079) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *fixes issue [#1072](undefined) opened by [@kitterma](https://github.com/kitterma)*
- [`007abf6`](https://github.com/ietf-tools/xml2rfc/commit/007abf625d2f7d626687d94c1dacaec9e660b77f) - Use raw string notation for regex *(PR [#1083](https://github.com/ietf-tools/xml2rfc/pull/1083) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *fixes issue [#1073](undefined) opened by [@kitterma](https://github.com/kitterma)*
- [`9c47d64`](https://github.com/ietf-tools/xml2rfc/commit/9c47d64ac0b2d090e68a47e9497935bebe8ac875) - Improve xml2rfc version information logic *(PR [#1084](https://github.com/ietf-tools/xml2rfc/pull/1084) by [@kesara](https://github.com/kesara))*
- [`8f14554`](https://github.com/ietf-tools/xml2rfc/commit/8f14554c289f5e0a968665fa414ba706cd590400) - Treat referencegroup entries similarly to reference entries *(PR [#1089](https://github.com/ietf-tools/xml2rfc/pull/1089) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *fixes issue [#1067](undefined) opened by [@cabo](https://github.com/cabo)*

### :construction_worker: Build System
- [`3c26a7d`](https://github.com/ietf-tools/xml2rfc/commit/3c26a7db39c528863db38f9ead8914752e920f1c) - Use PyPI trusted publishing *(PR [#1077](https://github.com/ietf-tools/xml2rfc/pull/1077) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *addresses issue [#1041](undefined) opened by [@kesara](https://github.com/kesara)*
- [`2893d3d`](https://github.com/ietf-tools/xml2rfc/commit/2893d3d03f73ec25c489859c09fb6174872f7876) - Remove redundant doc publish job *(PR [#1078](https://github.com/ietf-tools/xml2rfc/pull/1078) by [@kesara](https://github.com/kesara))*
- [`08a54f6`](https://github.com/ietf-tools/xml2rfc/commit/08a54f6a50c6447316ab7db9f9180068881eaa73) - Give permission to write packages and content to pypi-publish GHA. *(commit by [@kesara](https://github.com/kesara))*

### :memo: Documentation Changes
- [`cd66aec`](https://github.com/ietf-tools/xml2rfc/commit/cd66aece9db0079a320203ea87cedfe04517fc5f) - update CHANGELOG.md + py file versions for v3.19.1 [skip ci] *(commit by [@kesara](https://github.com/kesara))*

### :wrench: Chores
- [`ef1b3a2`](https://github.com/ietf-tools/xml2rfc/commit/ef1b3a2cf166578b81cec462f4e73e16f7127b65) - Remove stale bin directory *(PR [#1082](https://github.com/ietf-tools/xml2rfc/pull/1082) by [@kesara](https://github.com/kesara))*
- [`986fe07`](https://github.com/ietf-tools/xml2rfc/commit/986fe07cd24a6da453fb377d2420482035eef057) - Remove stale doc directory *(PR [#1081](https://github.com/ietf-tools/xml2rfc/pull/1081) by [@kesara](https://github.com/kesara))*
- [`4c7e638`](https://github.com/ietf-tools/xml2rfc/commit/4c7e63828766cf722a73fb736899a0878b72498b) - Use inclusive language *(PR [#1080](https://github.com/ietf-tools/xml2rfc/pull/1080) by [@kesara](https://github.com/kesara))*


## [v3.19.1] - 2024-01-09
### :construction_worker: Build System
- [`6024a93`](https://github.com/ietf-tools/xml2rfc/commit/6024a93f1afd18cb233331b09ebd00ac37653485) - Update pypi-publish.yml *(PR [#1076](https://github.com/ietf-tools/xml2rfc/pull/1076) by [@kesara](https://github.com/kesara))*

### :memo: Documentation Changes
- [`70e7148`](https://github.com/ietf-tools/xml2rfc/commit/70e714813eb0bec157db58000aa19d16859b4a6b) - update CHANGELOG.md + py file versions for v3.19.0 [skip ci] *(commit by [@kesara](https://github.com/kesara))*

### :wrench: Chores
- [`161487d`](https://github.com/ietf-tools/xml2rfc/commit/161487da6bd89e980435eee426b1f549be84fbc8) - Restrict lxml *(PR [#1075](https://github.com/ietf-tools/xml2rfc/pull/1075) by [@kesara](https://github.com/kesara))*


## [v3.19.0] - 2023-12-18
### :sparkles: New Features
- [`18c45a9`](https://github.com/ietf-tools/xml2rfc/commit/18c45a9f0804d05d998fe981abfc66d33e06d466) - Drop support for Python 3.7 *(PR [#1051](https://github.com/ietf-tools/xml2rfc/pull/1051) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *addresses issue [#1037](undefined) opened by [@kesara](https://github.com/kesara)*
- [`f3152b0`](https://github.com/ietf-tools/xml2rfc/commit/f3152b087250bb74903d9151ff24cc7299cc6dc7) - Add support for Python 3.12 *(PR [#1052](https://github.com/ietf-tools/xml2rfc/pull/1052) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *addresses issue [#1044](undefined) opened by [@kesara](https://github.com/kesara)*

### :bug: Bug Fixes
- [`a5d46ad`](https://github.com/ietf-tools/xml2rfc/commit/a5d46ad3af92dd01ffaff13318ac9030002a78ea) - Deduplicate index entries *(PR [#1050](https://github.com/ietf-tools/xml2rfc/pull/1050) by [@jennifer-richards](https://github.com/jennifer-richards))*
  - :arrow_lower_right: *fixes issue [#988](undefined) opened by [@martinthomson](https://github.com/martinthomson)*
- [`161abdf`](https://github.com/ietf-tools/xml2rfc/commit/161abdf9c40fff2a05fcc53d39edb7f934131621) - Follow HTML presentational hints in PDF *(PR [#1055](https://github.com/ietf-tools/xml2rfc/pull/1055) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *fixes issue [#1054](undefined) opened by [@rvanrheenen](https://github.com/rvanrheenen)*
- [`e067417`](https://github.com/ietf-tools/xml2rfc/commit/e067417f3533d2a42075940aae56b7579830ec52) - Remove emphasis from xref in headings and fix xrefs in headings  *(PR [#1029](https://github.com/ietf-tools/xml2rfc/pull/1029) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *fixes issue [#683](undefined) opened by [@ietf-svn-bot](https://github.com/ietf-svn-bot)*

### :memo: Documentation Changes
- [`0a5b463`](https://github.com/ietf-tools/xml2rfc/commit/0a5b463c5af9763dae25d7c706c236e3aa3cdd74) - update CHANGELOG.md + py file versions for v3.18.2 [skip ci] *(commit by [@rjsparks](https://github.com/rjsparks))*

### :wrench: Chores
- [`880d20d`](https://github.com/ietf-tools/xml2rfc/commit/880d20d16957f75a211ea24f71a72a5b3866a3a8) - List required dependencies *(PR [#1057](https://github.com/ietf-tools/xml2rfc/pull/1057) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *addresses issue [#1049](undefined) opened by [@yaronf](https://github.com/yaronf)*
- [`ea5f4cf`](https://github.com/ietf-tools/xml2rfc/commit/ea5f4cfd058217b6922174ce34efef16efd19bcf) - Get version for setup from xml2rfc source *(PR [#1062](https://github.com/ietf-tools/xml2rfc/pull/1062) by [@kesara](https://github.com/kesara))*
- [`23d51a1`](https://github.com/ietf-tools/xml2rfc/commit/23d51a12dc72308ac9647ab57cc60035b4397b95) - Update docs-publish GHA *(PR [#1064](https://github.com/ietf-tools/xml2rfc/pull/1064) by [@kesara](https://github.com/kesara))*
- [`77a83dc`](https://github.com/ietf-tools/xml2rfc/commit/77a83dc1e199a728e1c24776246f3b776c8ecc44) - Update docs-publish.yml *(commit by [@kesara](https://github.com/kesara))*
- [`73a758a`](https://github.com/ietf-tools/xml2rfc/commit/73a758a3504484b62be3bc74939e88a0889f55f7) - Update docs-publish.yml *(commit by [@kesara](https://github.com/kesara))*


## [v3.18.2] - 2023-10-12
### :bug: Bug Fixes
- [`cb10344`](https://github.com/ietf-tools/xml2rfc/commit/cb103440813166343ded946f3a6c007497da12bf) - Respect newline attr on dl tag *(PR [#1047](https://github.com/ietf-tools/xml2rfc/pull/1047) by [@jennifer-richards](https://github.com/jennifer-richards))*
  - :arrow_lower_right: *fixes issue [#1045](undefined) opened by [@lbartholomew-rpc](https://github.com/lbartholomew-rpc)*

### :memo: Documentation Changes
- [`ff2ceff`](https://github.com/ietf-tools/xml2rfc/commit/ff2ceff11459cf39296988e0cd4db4cd4f0149dd) - update CHANGELOG.md + py file versions for v3.18.1 [skip ci] *(commit by [@kesara](https://github.com/kesara))*


## [v3.18.1] - 2023-09-29
### :bug: Bug Fixes
- [`02253d8`](https://github.com/ietf-tools/xml2rfc/commit/02253d8c7dbd8c3bcf2a7d60ae7dc0c71c78d73d) - **text**: Preserve NBSP in dd *(PR [#1023](https://github.com/ietf-tools/xml2rfc/pull/1023) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *fixes issue [#1022](undefined) opened by [@d3e3e3](https://github.com/d3e3e3)*
- [`0704155`](https://github.com/ietf-tools/xml2rfc/commit/070415586f37914b5bbe7a1379f33f2c9ff00258) - **v2v3**: Preserve t element in ol and li  *(PR [#972](https://github.com/ietf-tools/xml2rfc/pull/972) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *fixes issue [#850](undefined) opened by [@cabo](https://github.com/cabo)*
- [`c10a50c`](https://github.com/ietf-tools/xml2rfc/commit/c10a50c427f8b4002d51f020e506dd2c317e615a) - Make block quotes symmetric *(PR [#1027](https://github.com/ietf-tools/xml2rfc/pull/1027) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *fixes issue [#1018](undefined) opened by [@cabo](https://github.com/cabo)*
- [`9ea862c`](https://github.com/ietf-tools/xml2rfc/commit/9ea862cae29ed2c4f750ca82cb6c01c42d9cb094) - Render child elements in the xref element *(PR [#1036](https://github.com/ietf-tools/xml2rfc/pull/1036) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *fixes issue [#1034](undefined) opened by [@cabo](https://github.com/cabo)*

### :memo: Documentation Changes
- [`31059d5`](https://github.com/ietf-tools/xml2rfc/commit/31059d5adbdb36c9407e63535208e6c51af1ff94) - update CHANGELOG.md + py file versions for v3.18.0 [skip ci] *(commit by [@kesara](https://github.com/kesara))*

### :wrench: Chores
- [`b6bdd70`](https://github.com/ietf-tools/xml2rfc/commit/b6bdd700fe9e62de7682847a288e3eed63900737) - Restrict WeasyPrint versions *(PR [#1038](https://github.com/ietf-tools/xml2rfc/pull/1038) by [@kesara](https://github.com/kesara))*
- [`4f52a7b`](https://github.com/ietf-tools/xml2rfc/commit/4f52a7b552086db144092a311a64f1abbad3eacf) - Allow WeasyPrint v60.1 *(PR [#1040](https://github.com/ietf-tools/xml2rfc/pull/1040) by [@kesara](https://github.com/kesara))*


## [v3.18.0] - 2023-08-04
### :sparkles: New Features
- [`46aecfb`](https://github.com/ietf-tools/xml2rfc/commit/46aecfb64d3ef678c17e85f8d7b9de362a7ee07b) - Allow Unicode characters everywhere  *(PR [#1017](https://github.com/ietf-tools/xml2rfc/pull/1017) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *addresses issue [#960](undefined) opened by [@kesara](https://github.com/kesara)*

### :bug: Bug Fixes
- [`47ff383`](https://github.com/ietf-tools/xml2rfc/commit/47ff3830349884387b78517194a8d856721efb05) - Avoid running v2v3 conversion and preptool on prepped documents *(PR [#1014](https://github.com/ietf-tools/xml2rfc/pull/1014) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *fixes issue [#1013](undefined) opened by [@kesara](https://github.com/kesara)*
- [`43c82f0`](https://github.com/ietf-tools/xml2rfc/commit/43c82f02fac8176c0a8ecaa6984f6f7511ab916c) - Break word when line overflows *(PR [#1021](https://github.com/ietf-tools/xml2rfc/pull/1021) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *fixes issue [#687](undefined) opened by [@ietf-svn-bot](https://github.com/ietf-svn-bot)*

### :construction_worker: Build System
- [`5662408`](https://github.com/ietf-tools/xml2rfc/commit/56624086a80de13847fa27b3f80a160a0b2c0d9f) - Mark the released version as the latest *(commit by [@kesara](https://github.com/kesara))*

### :memo: Documentation Changes
- [`a5d5532`](https://github.com/ietf-tools/xml2rfc/commit/a5d5532833fca867fe4f54f234df1b93a6bfa6cc) - update CHANGELOG.md + py file versions for v3.17.5 [skip ci] *(commit by [@kesara](https://github.com/kesara))*

### :wrench: Chores
- [`b0d198c`](https://github.com/ietf-tools/xml2rfc/commit/b0d198c868911c5fbf9bf0f43e879386209aa8fb) - Remove unused variable *(PR [#1020](https://github.com/ietf-tools/xml2rfc/pull/1020) by [@kesara](https://github.com/kesara))*


## [v3.17.5] - 2023-07-27
### :bug: Bug Fixes
- [`656a6ba`](https://github.com/ietf-tools/xml2rfc/commit/656a6ba65749c7c869e647134a2ff749aa10cf05) - Include page numbers in the TOC when generating PDF. *(PR [#993](https://github.com/ietf-tools/xml2rfc/pull/993) by [@teythoon](https://github.com/teythoon))*
- [`fa1ad02`](https://github.com/ietf-tools/xml2rfc/commit/fa1ad029e9dc011f4dc253687b0b4de2842e8e8a) - Improve pagination in text output *(PR [#1019](https://github.com/ietf-tools/xml2rfc/pull/1019) by [@kesara](https://github.com/kesara))*

### :memo: Documentation Changes
- [`4971ae2`](https://github.com/ietf-tools/xml2rfc/commit/4971ae2d3f3b091150e0a14515b9bc24791b22df) - update CHANGELOG.md + py file versions for v3.17.4 [skip ci] *(commit by [@kesara](https://github.com/kesara))*


## [v3.17.4] - 2023-06-22
### :bug: Bug Fixes
- [`fb360a1`](https://github.com/ietf-tools/xml2rfc/commit/fb360a1cb08f9f8b6d929018ae12844f6b4b9960) - Remove old tools server from BibXML lookup locations *(PR [#1004](https://github.com/ietf-tools/xml2rfc/pull/1004) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *fixes issue [#1002](undefined) opened by [@kesara](https://github.com/kesara)*
- [`8cbc6c6`](https://github.com/ietf-tools/xml2rfc/commit/8cbc6c6e44ed88cf82ba9f0cb21c9bc0dc1c6742) - Switch from appdirs to platformdirs, since it is maintained *(PR [#1009](https://github.com/ietf-tools/xml2rfc/pull/1009) by [@kitterma](https://github.com/kitterma))*
- [`f92f551`](https://github.com/ietf-tools/xml2rfc/commit/f92f5512473990fa17516d291c6a29e3042c8b64) - Warn when reference uses PIs *(PR [#1007](https://github.com/ietf-tools/xml2rfc/pull/1007) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *fixes issue [#1006](undefined) opened by [@kesara](https://github.com/kesara)*
- [`393b68b`](https://github.com/ietf-tools/xml2rfc/commit/393b68bc2439f019690f5679ecd7893caa6e624a) - Reset seen_slugs cache on every prep run *(PR [#1011](https://github.com/ietf-tools/xml2rfc/pull/1011) by [@jennifer-richards](https://github.com/jennifer-richards))*
- [`aef14d2`](https://github.com/ietf-tools/xml2rfc/commit/aef14d28754d5a76e8d737e76e964e4a87efdfda) - Add xml extension to BibXML requests *(PR [#1005](https://github.com/ietf-tools/xml2rfc/pull/1005) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *fixes issue [#1003](undefined) opened by [@kesara](https://github.com/kesara)*

### :memo: Documentation Changes
- [`5fbc3ce`](https://github.com/ietf-tools/xml2rfc/commit/5fbc3ceffa6c4713b425472111b746ef9f675cf5) - update CHANGELOG.md + py file versions for v3.17.3 [skip ci] *(commit by [@kesara](https://github.com/kesara))*


## [v3.17.3] - 2023-06-06
### :bug: Bug Fixes
- [`9a8c2f0`](https://github.com/ietf-tools/xml2rfc/commit/9a8c2f0decf2efcd59cfe5c5f7ae2f25892c73d6) - Update for google-i18n-address 3.0.0 *(PR [#998](https://github.com/ietf-tools/xml2rfc/pull/998) by [@jennifer-richards](https://github.com/jennifer-richards))*
  - :arrow_lower_right: *fixes issue [#997](undefined) opened by [@jennifer-richards](https://github.com/jennifer-richards)*

### :memo: Documentation Changes
- [`897404d`](https://github.com/ietf-tools/xml2rfc/commit/897404dcbd437a56130337b8a723c3cb8779950c) - update CHANGELOG.md + py file versions for v3.17.2 [skip ci] *(commit by [@kesara](https://github.com/kesara))*


## [v3.17.2] - 2023-05-31
### :bug: Bug Fixes
- [`f902725`](https://github.com/ietf-tools/xml2rfc/commit/f90272530b9e93f98e42c73fd1b6b8eabdf58eab) - Avoid memory issues in BaseV3Writer validator process *(PR [#995](https://github.com/ietf-tools/xml2rfc/pull/995) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *fixes issue [#994](undefined) opened by [@kesara](https://github.com/kesara)*

### :memo: Documentation Changes
- [`be9682f`](https://github.com/ietf-tools/xml2rfc/commit/be9682f10ed4cbcced3907d66207dcaa1918fcfa) - update CHANGELOG.md + py file versions for v3.17.1 [skip ci] *(commit by [@kesara](https://github.com/kesara))*


## [v3.17.1] - 2023-04-13
### :bug: Bug Fixes
- [`87e206e`](https://github.com/ietf-tools/xml2rfc/commit/87e206e09271bd9c9771b4d00d5ec7f61fbe8ea1) - Remove extend-to-zoom from viewport in CSS *(PR [#980](https://github.com/ietf-tools/xml2rfc/pull/980) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *fixes issue [#974](undefined) opened by [@kesara](https://github.com/kesara)*

### :construction_worker: Build System
- [`2b112e2`](https://github.com/ietf-tools/xml2rfc/commit/2b112e21474c77f84c492e1c399e7d9cb4e480b8) - Migrate to setup.cfg *(PR [#979](https://github.com/ietf-tools/xml2rfc/pull/979) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *addresses issue [#781](undefined) opened by [@kesara](https://github.com/kesara)*
- [`c014b7a`](https://github.com/ietf-tools/xml2rfc/commit/c014b7a1ad87ac8f3d9526fac0dcb0ffbe83d05f) - Update package version in setup.cfg *(PR [#981](https://github.com/ietf-tools/xml2rfc/pull/981) by [@kesara](https://github.com/kesara))*

### :memo: Documentation Changes
- [`5f90492`](https://github.com/ietf-tools/xml2rfc/commit/5f904921201f7080681c03190a7f945e48299ee0) - update CHANGELOG.md + py file versions for v3.17.0 [skip ci] *(commit by [@kesara](https://github.com/kesara))*


## [v3.17.0] - 2023-03-14
### :sparkles: New Features
- [`dbdda51`](https://github.com/ietf-tools/xml2rfc/commit/dbdda51a16083da0762355ebe0902c3bc2a78a39) - Lighter styling on internal iref links *(PR [#963](https://github.com/ietf-tools/xml2rfc/pull/963) by [@martinthomson](https://github.com/martinthomson))*
- [`ff1c061`](https://github.com/ietf-tools/xml2rfc/commit/ff1c0610ef67cab21e80fc2106137b103dabb30b) - Add support for Noto Math font *(PR [#971](https://github.com/ietf-tools/xml2rfc/pull/971) by [@kesara](https://github.com/kesara))*

### :memo: Documentation Changes
- [`636dd08`](https://github.com/ietf-tools/xml2rfc/commit/636dd08cf10d61fc7354dfc0575a61714270b4c6) - update CHANGELOG.md + py file versions for v3.16.0 [skip ci] *(commit by [@kesara](https://github.com/kesara))*

### :wrench: Chores
- [`7cae8ad`](https://github.com/ietf-tools/xml2rfc/commit/7cae8add36feaf9d1eed08c820708748ac9ec868) - Remove mt.css and mt.js *(PR [#976](https://github.com/ietf-tools/xml2rfc/pull/976) by [@martinthomson](https://github.com/martinthomson))*


## [v3.16.0] - 2023-01-18
### :sparkles: New Features
- [`ad2e035`](https://github.com/ietf-tools/xml2rfc/commit/ad2e0359fde4687e07491a1ada0ec0d4f6ee5fcc) - Permit non-ASCII within <t> without the use of <u> *(PR [#895](https://github.com/ietf-tools/xml2rfc/pull/895) by [@cabo](https://github.com/cabo))*
- [`6b9aede`](https://github.com/ietf-tools/xml2rfc/commit/6b9aede79e25665c199064c362fc6524f8292882) - Add editorial stream *(PR [#958](https://github.com/ietf-tools/xml2rfc/pull/958) by [@kesara](https://github.com/kesara))*
  - :arrow_lower_right: *addresses issue [#896](undefined) opened by [@alicerusso](https://github.com/alicerusso)*

### :bug: Bug Fixes
- [`5b687b1`](https://github.com/ietf-tools/xml2rfc/commit/5b687b12053a5607cff4e83fd6a6ab767668c5a8) - Add 'auto' class for (most) parenthesized xref links *(PR [#948](https://github.com/ietf-tools/xml2rfc/pull/948) by [@martinthomson](https://github.com/martinthomson))*
- [`388d4b9`](https://github.com/ietf-tools/xml2rfc/commit/388d4b9b1521c7b7a5bb27a6f64b1c74f39433b2) - Update to pypdf>=3.2.1 on base docker file *(PR [#954](https://github.com/ietf-tools/xml2rfc/pull/954) by [@kesara](https://github.com/kesara))*

### :white_check_mark: Tests
- [`6c9be77`](https://github.com/ietf-tools/xml2rfc/commit/6c9be77f09fa23d6d9c46652582328027cd962f5) - Expand a problematic reference *(PR [#959](https://github.com/ietf-tools/xml2rfc/pull/959) by [@kesara](https://github.com/kesara))*

### :memo: Documentation Changes
- [`b811bfd`](https://github.com/ietf-tools/xml2rfc/commit/b811bfda5d8215b0d4060ba7a7e42558fb373b36) - update CHANGELOG.md + py file versions for v3.15.3 [skip ci] *(commit by [@kesara](https://github.com/kesara))*

### :wrench: Chores
- [`5bbf3f7`](https://github.com/ietf-tools/xml2rfc/commit/5bbf3f74bbf3568f79aa8c4293ce3a2d73f3bf48) - **deps**: Move from PyPDF2 to pypdf>=3.2.1 *(PR [#953](https://github.com/ietf-tools/xml2rfc/pull/953) by [@kesara](https://github.com/kesara))*


## [v3.15.3] - 2022-11-24
### :bug: Bug Fixes
- [`1381bb8`](https://github.com/ietf-tools/xml2rfc/commit/1381bb86056d56c86624e5483926878a274ee137) - Move sourcecode classes *(PR [#839](https://github.com/ietf-tools/xml2rfc/pull/839) by [@martinthomson](https://github.com/martinthomson))*
- [`592ab81`](https://github.com/ietf-tools/xml2rfc/commit/592ab81a6fba182c7cdee3ce340b130b3d362ced) - Only overwrite font-family when producing PDFs *(PR [#937](https://github.com/ietf-tools/xml2rfc/pull/937) by [@martinthomson](https://github.com/martinthomson))*
- [`a3adb84`](https://github.com/ietf-tools/xml2rfc/commit/a3adb840848b6e6f6585310055b7013277a014a2) - Fix margin issue with dl after p inside a li  *(PR [#941](https://github.com/ietf-tools/xml2rfc/pull/941) by [@kesara](https://github.com/kesara))*

### :white_check_mark: Tests
- [`9308e40`](https://github.com/ietf-tools/xml2rfc/commit/9308e402b6658a36bffaddaff6131226f622f119) - Update walkpdf to fix PyPDF deprecation warnings *(PR [#934](https://github.com/ietf-tools/xml2rfc/pull/934) by [@kesara](https://github.com/kesara))*

### :construction_worker: Build System
- [`0d3958c`](https://github.com/ietf-tools/xml2rfc/commit/0d3958c0f55e9329e6d0c19364f73c7d2a4b003d) - Include OpenPGP certificates for signing the project in each release *(PR [#931](https://github.com/ietf-tools/xml2rfc/pull/931) by [@dkg](https://github.com/dkg))*
- [`b451ded`](https://github.com/ietf-tools/xml2rfc/commit/b451deda56d8d38276d6554043adb8c3325dcdd2) - Add support for Python 3.11 *(PR [#942](https://github.com/ietf-tools/xml2rfc/pull/942) by [@kesara](https://github.com/kesara))*
- [`9ff2476`](https://github.com/ietf-tools/xml2rfc/commit/9ff247654048593eedf1dcd847a0764ed1c80973) - Include all changes in Changelog *(PR [#944](https://github.com/ietf-tools/xml2rfc/pull/944) by [@kesara](https://github.com/kesara))*

### :memo: Documentation Changes
- [`d86b1f2`](https://github.com/ietf-tools/xml2rfc/commit/d86b1f24fce077b967c0ed480f93143ff81eecb0) - update CHANGELOG.md + py file versions for v3.15.2 [skip ci] *(commit by [@kesara](https://github.com/kesara))*

### :wrench: Chores
- [`af9d83e`](https://github.com/ietf-tools/xml2rfc/commit/af9d83ed49c30303dab52e5240d19d324dbd8adc) - Skip Weasyprint 57.0 in tests *(PR [#932](https://github.com/ietf-tools/xml2rfc/pull/932) by [@kesara](https://github.com/kesara))*


## [v3.15.2] - 2022-10-28
### :bug: Bug Fixes
- [`908365f`](https://github.com/ietf-tools/xml2rfc/commit/908365f065fa54a4ce43472e72542bea4aa79730) - Use wcwidth to determine the monospace textual length of a string *(PR [#914](https://github.com/ietf-tools/xml2rfc/pull/914) by [@Flowdalic](https://github.com/Flowdalic))*
- [`0b42319`](https://github.com/ietf-tools/xml2rfc/commit/0b42319ce70b2f5d4d58b271973b291a75f02aa7) - Drop dependency on kitchen *(PR [#913](https://github.com/ietf-tools/xml2rfc/pull/913) by [@Flowdalic](https://github.com/Flowdalic))*
- [`1a910d9`](https://github.com/ietf-tools/xml2rfc/commit/1a910d986fe891bed467c493877cfac3abae57ba) - Expand table columns in text output  *(PR [#919](https://github.com/ietf-tools/xml2rfc/pull/919) by [@kesara](https://github.com/kesara))*
- [`4f9e700`](https://github.com/ietf-tools/xml2rfc/commit/4f9e700d35e26ac12e1b7bd5a803148ea091a2c3) - Add Noto Sans Symbols 2 font to PDF template *(PR [#926](https://github.com/ietf-tools/xml2rfc/pull/926) by [@kesara](https://github.com/kesara))*

### :white_check_mark: Tests
- [`18b34d8`](https://github.com/ietf-tools/xml2rfc/commit/18b34d8e744ef47cbac3ee11c98bb86622856f9b) - Fix PDF tests *(PR [#920](https://github.com/ietf-tools/xml2rfc/pull/920) by [@kesara](https://github.com/kesara))*

### :wrench: Chores
- [`7337517`](https://github.com/ietf-tools/xml2rfc/commit/7337517aa28168d69f14de84073eaa5c11d0a399) - Correct spelling mistakes *(PR [#917](https://github.com/ietf-tools/xml2rfc/pull/917) by [@jsoref](https://github.com/jsoref))*


## [v3.15.1] - 2022-10-12
### :bug: Bug Fixes
- [`08605de`](https://github.com/ietf-tools/xml2rfc/commit/08605de0a38380d58d77ad9e271096e43c852a10) - Improve PDF generation debug logs *(PR [#907](https://github.com/ietf-tools/xml2rfc/pull/907) by [@kesara](https://github.com/kesara))*
- [`12a960e`](https://github.com/ietf-tools/xml2rfc/commit/12a960ed3a9829b6770c55be24a6ba0c5ad631b5) - Use specified font families on SVG *(PR [#910](https://github.com/ietf-tools/xml2rfc/pull/910) by [@kesara](https://github.com/kesara))*
- [`70de803`](https://github.com/ietf-tools/xml2rfc/commit/70de803f9d2774dda2581e87c8b43af6a49d972c) - Use noto fonts for non-latin unicode monospaced characters *(PR [#909](https://github.com/ietf-tools/xml2rfc/pull/909) by [@kesara](https://github.com/kesara))*
- [`dd2b0fe`](https://github.com/ietf-tools/xml2rfc/commit/dd2b0fe1de487b2b43623cc4669f997a34c7c960) - Add bottom margin to .artwork > pre *(PR [#912](https://github.com/ietf-tools/xml2rfc/pull/912) by [@kesara](https://github.com/kesara))*
- [`58706b8`](https://github.com/ietf-tools/xml2rfc/commit/58706b80e322e49a9aeacba22a61e9db7ff701b7) - Remove redundant code labels from CSS *(PR [#916](https://github.com/ietf-tools/xml2rfc/pull/916) by [@kesara](https://github.com/kesara))*


## [v3.15.0] - 2022-09-22
### :sparkles: New Features
- [`055d64d`](https://github.com/ietf-tools/xml2rfc/commit/055d64d2e5fc1187ef90cfada9446515362695ac) - Add xml2rfc class to HTML body element *(PR [#847](https://github.com/ietf-tools/xml2rfc/pull/847) by [@martinthomson](https://github.com/martinthomson))*
- [`7fec225`](https://github.com/ietf-tools/xml2rfc/commit/7fec2255b7cf2eefa0a1a6ce770d01a157adce39) - Add classes to xref *(PR [#867](https://github.com/ietf-tools/xml2rfc/pull/867) by [@martinthomson](https://github.com/martinthomson))*

### :bug: Bug Fixes
- [`cc6b083`](https://github.com/ietf-tools/xml2rfc/commit/cc6b083cdf58be559d8d6011f9adedfa583bbc6f) - Fix table colspan issue in text format  *(PR [#886](https://github.com/ietf-tools/xml2rfc/pull/886) by [@kesara](https://github.com/kesara))*
- [`2475447`](https://github.com/ietf-tools/xml2rfc/commit/24754473224b2db603f910c0282f90ba013ddcc8) - Include the published date when ipr is none *(PR [#897](https://github.com/ietf-tools/xml2rfc/pull/897) by [@kesara](https://github.com/kesara))*


## [v3.14.2] - 2022-08-29
### :bug: Bug Fixes
- [`20cdb44`](https://github.com/ietf-tools/xml2rfc/commit/20cdb4460436a7edbebc9807d1c3305e90d0269d) - Fix odd page break inside rows in PDF output *(PR [#879](https://github.com/ietf-tools/xml2rfc/pull/879) by [@kesara](https://github.com/kesara))*
- [`2c9dfaf`](https://github.com/ietf-tools/xml2rfc/commit/2c9dfafa0f4c32399f9b8e31ef9926c3e5ea7b65) - Return orgnization for orgnization only contacts *(PR [#837](https://github.com/ietf-tools/xml2rfc/pull/837) by [@kesara](https://github.com/kesara))*
- [`9821dc6`](https://github.com/ietf-tools/xml2rfc/commit/9821dc6cd19e905cf05c3d92223311520575d2f2) - RTL unicode issue in PDF *(PR [#884](https://github.com/ietf-tools/xml2rfc/pull/884) by [@kesara](https://github.com/kesara))*


## [v3.14.1] - 2022-08-22
### :bug: Bug Fixes
- [`c67f5fd`](https://github.com/ietf-tools/xml2rfc/commit/c67f5fd40c605637043c1692974256ebc9f7af41) - Align center aligned ASCII art correctly *(PR [#838](https://github.com/ietf-tools/xml2rfc/pull/838) by [@kesara](https://github.com/kesara))*

### :wrench: Chores
- [`701d5ce`](https://github.com/ietf-tools/xml2rfc/commit/701d5cedda73befe1341b02842f32d2888c5e860) - Add github issue templates *(commit by [@kesara](https://github.com/kesara))*


## [v3.14.0] - 2022-08-10
### :sparkles: New Features
- [`c6343a9`](https://github.com/ietf-tools/xml2rfc/commit/c6343a909dc66887eafe2d4e905cd5134c2d2c95) - Update WeasyPrint *(PR [#802](https://github.com/ietf-tools/xml2rfc/pull/802) by [@kesara](https://github.com/kesara))*

### :bug: Bug Fixes
- [`95dba00`](https://github.com/ietf-tools/xml2rfc/commit/95dba00e3007ae65af6d1795f5723c0af1db1988) - Fix typo in README file *(PR [#843](https://github.com/ietf-tools/xml2rfc/pull/843) by [@bkmgit](https://github.com/bkmgit))*
- [`0f06e27`](https://github.com/ietf-tools/xml2rfc/commit/0f06e27ca16272887d64179098c4a9c7262e372b) - Prevent submission date warnings for RFCs  *(PR [#842](https://github.com/ietf-tools/xml2rfc/pull/842) by [@kesara](https://github.com/kesara))*
- [`e5c45d4`](https://github.com/ietf-tools/xml2rfc/commit/e5c45d41592e6db13af41134f73611ca619b6822) - Add an option to disable rfc-local.css link *(PR [#840](https://github.com/ietf-tools/xml2rfc/pull/840) by [@martinthomson](https://github.com/martinthomson))*

### :white_check_mark: Tests
- [`41b177a`](https://github.com/ietf-tools/xml2rfc/commit/41b177a302f0c6c61767cd3c326f20893210602d) - Fix tests to adapt bib.ietf.org *(PR [#852](https://github.com/ietf-tools/xml2rfc/pull/852) by [@kesara](https://github.com/kesara))*
- [`c9b9d09`](https://github.com/ietf-tools/xml2rfc/commit/c9b9d093d9b8d96b1eab0296cabb2ed6f4996dcf) - Update valid tests for --no-rfc-local option *(PR [#854](https://github.com/ietf-tools/xml2rfc/pull/854) by [@kesara](https://github.com/kesara))*


## [v3.13.1] - 2022-07-19
### :bug: Bug Fixes
- [`63de72a`](https://github.com/ietf-tools/xml2rfc/commit/63de72a05452d47bb71845e855b723bd3b87c3d9) - Use bib.ietf.org for citations  *(PR [#804](https://github.com/ietf-tools/xml2rfc/pull/804) by [@kesara](https://github.com/kesara))*
- [`ad44bb8`](https://github.com/ietf-tools/xml2rfc/commit/ad44bb8d3e42a7a3a045eb1471e8e3311365133f) - Render unicode characters in SVG elements correctly  *(PR [#832](https://github.com/ietf-tools/xml2rfc/pull/832) by [@kesara](https://github.com/kesara))*


## [v3.13.0] - 2022-06-22
### :sparkles: New Features
- [`6938d80`](https://github.com/ietf-tools/xml2rfc/commit/6938d806e5d84ea892f3eabe8dc6c10426d3b5ca) - Drop support for Python 3.6 *(PR [#796](https://github.com/ietf-tools/xml2rfc/pull/796) by [@kesara](https://github.com/kesara))*

### :bug: Bug Fixes
- [`47270ba`](https://github.com/ietf-tools/xml2rfc/commit/47270ba4a79daa59bfc39cd8a2c7de1567c0aa5b) - Handle date type errors gracefully *(PR [#795](https://github.com/ietf-tools/xml2rfc/pull/795) by [@cabo](https://github.com/cabo))*
- [`79fd4d9`](https://github.com/ietf-tools/xml2rfc/commit/79fd4d9b9c0a09ef041559e8e47abba11aad7fd4) - Stop crashing when author element doesn't have a name *(PR [#800](https://github.com/ietf-tools/xml2rfc/pull/800) by [@cabo](https://github.com/cabo))*
- [`d5f8a1c`](https://github.com/ietf-tools/xml2rfc/commit/d5f8a1c16a48e9f2acf1ea0b8f3940f85265cb20) - Use bib.ietf.org for citations *(PR [#799](https://github.com/ietf-tools/xml2rfc/pull/799) by [@kesara](https://github.com/kesara))*

### :wrench: Chores
- [`b94d6bb`](https://github.com/ietf-tools/xml2rfc/commit/b94d6bb05804c7dece0e6ad93e5431058ce271d6) - **deps**: Update Python dependencies *(PR [#797](https://github.com/ietf-tools/xml2rfc/pull/797) by [@kesara](https://github.com/kesara))*


## [v3.12.10] - 2022-06-03
### :bug: Bug Fixes
- [`f73ece7`](https://github.com/ietf-tools/xml2rfc/commit/f73ece708dd45ed0830a5ffceb89998d16bcb4ff) - Update setuptools metadata *(PR [#789](https://github.com/ietf-tools/xml2rfc/pull/789) by [@kesara](https://github.com/kesara))*


## [v3.12.9] - 2022-06-02
### :bug: Bug Fixes
- [`1643d68`](https://github.com/ietf-tools/xml2rfc/commit/1643d6845e2309f79f4ddc34f22749372b359a2b) - Display long ASCII art correctly in PDF *(PR [#788](https://github.com/ietf-tools/xml2rfc/pull/788) by [@kesara](https://github.com/kesara))*


## [v3.12.8] - 2022-05-25
### ✨ New Features
- [`51e8b24`](https://github.com/ietf-tools/xml2rfc/commit/51e8b24fd25e5cffaadba415374aa7e5cc24c9a8) - Add support for Python 3.10 *(PR [#772](https://github.com/ietf-tools/xml2rfc/pull/772) by [@dkg](https://github.com/dkg))*

### :bug: Bug Fixes
- [`46399d7`](https://github.com/ietf-tools/xml2rfc/commit/46399d7efaf77f21b0de01c42226d0bf44e699a4) - Implement emboldening primary iref entries *(PR [#778](https://github.com/ietf-tools/xml2rfc/pull/778) by [@cabo](https://github.com/cabo))*

### :white_check_mark: Tests
- [`e0095fd`](https://github.com/ietf-tools/xml2rfc/commit/e0095fdf9ece092a57746aa4313339b7191f9aff) - Remove Python version specific test results *(PR [#780](https://github.com/ietf-tools/xml2rfc/pull/780) by [@kesara](https://github.com/kesara))*


## [v3.12.7] - 2022-05-11
### :bug: Bug Fixes
- [`42568b3`](https://github.com/ietf-tools/xml2rfc/commit/42568b3787ae549c8e718e43ac8f164a9b195067) - evaluate date.today() on class init, not import *(PR [#774](https://github.com/ietf-tools/xml2rfc/pull/774) by [@jennifer-richards](https://github.com/jennifer-richards))*
- [`07ef95e`](https://github.com/ietf-tools/xml2rfc/commit/07ef95e8fb4a0bbbadac9ee4ffcd7478405eb1fd) - Fix warnings in text and manpage *(PR [#775](https://github.com/ietf-tools/xml2rfc/pull/775) by [@kesara](https://github.com/kesara))*


## [v3.12.6] - 2022-05-10
### :bug: Bug Fixes
- [`6b32a5d`](https://github.com/ietf-tools/xml2rfc/commit/6b32a5d789925f5f74b7898b556cf7b8f3bd1d10) - Render text without toc *(PR [#766](https://github.com/ietf-tools/xml2rfc/pull/766) by [@cabo](https://github.com/cabo))*
- [`384399c`](https://github.com/ietf-tools/xml2rfc/commit/384399cae4a52fbb689abacfdf1a55c3217276db) - Display ASCII names for authors in references *(PR [#771](https://github.com/ietf-tools/xml2rfc/pull/771) by [@kesara](https://github.com/kesara))*


## [v3.12.5] - 2022-05-02
### :bug: Bug Fixes
- [`8436c2f`](https://github.com/ietf-tools/xml2rfc/commit/8436c2f9716b5c7a73d5587bc6201c7e56fb6ac0) - Make index sort case insensitive *(PR [#763](https://github.com/ietf-tools/xml2rfc/pull/763) by [@kesara](https://github.com/kesara))*
- [`0884e8d`](https://github.com/ietf-tools/xml2rfc/commit/0884e8dc11f7040986b208961275a7cb3af07f92) - Don't attempt to select initials when fullname contains non Latin characters *(PR [#760](https://github.com/ietf-tools/xml2rfc/pull/760) by [@kesara](https://github.com/kesara))*
- [`9e12093`](https://github.com/ietf-tools/xml2rfc/commit/9e120937f5a66e180a7522f9d7e7066a5486c4de) - Make long sourcecode sections breakable *(PR [#764](https://github.com/ietf-tools/xml2rfc/pull/764) by [@kesara](https://github.com/kesara))*

### :white_check_mark: Tests
- [`24406e5`](https://github.com/ietf-tools/xml2rfc/commit/24406e5007ec5acefa331565a082a48207b055dd) - Bug fix in tests/input/draft-miek-test.v3.xml *(PR [#738](https://github.com/ietf-tools/xml2rfc/pull/738) by [@kesara](https://github.com/kesara))*
- [`72255eb`](https://github.com/ietf-tools/xml2rfc/commit/72255ebd479f4a8c87f1e7b6352d4abc6e1d4622) - Pin PyPDF2 to 2.16.* versions *(PR [#762](https://github.com/ietf-tools/xml2rfc/pull/762) by [@kesara](https://github.com/kesara))*

### :wrench: Chores
- [`8fc7efb`](https://github.com/ietf-tools/xml2rfc/commit/8fc7efbd37ca746cf4b9f97793b7236c013a0388) - Update deprecated tox configuration option *(PR [#746](https://github.com/ietf-tools/xml2rfc/pull/746) by [@kesara](https://github.com/kesara))*


## [v3.12.4] - 2022-04-12
### :bug: Bug Fixes
- [`bf6ee73`](https://github.com/ietf-tools/xml2rfc/commit/bf6ee731b0d643598267e2eb267cb3ddc8f67d26) - Fix an edge case in the table of contents in text output *(PR [#735](https://github.com/ietf-tools/xml2rfc/pull/735) by [@kesara](https://github.com/kesara))*
- [`6e64a1c`](https://github.com/ietf-tools/xml2rfc/commit/6e64a1c667892a9600c2a772615c1be3df855936) - Render cref elements correctly in text output *(PR [#744](https://github.com/ietf-tools/xml2rfc/pull/744) by [@cabo](https://github.com/cabo))*
- [`df99f94`](https://github.com/ietf-tools/xml2rfc/commit/df99f948b53ca4836d830ac55ec84eb4023e81da) - Terminate if SVG data includes a script tag (GHSA-cf4q-4cqr-7g7w) *(commit by [@kesara](https://github.com/kesara))*

### :white_check_mark: Tests
- [`3badf55`](https://github.com/ietf-tools/xml2rfc/commit/3badf559aabab15270702deccf2922961c2c2c34) - Improve cref tests *(PR [#747](https://github.com/ietf-tools/xml2rfc/pull/747) by [@kesara](https://github.com/kesara))*

### :wrench: Chores
- [`4262e58`](https://github.com/ietf-tools/xml2rfc/commit/4262e58c198fc9c72d25036cf4c42fecc91ac2e4) - add vscode dev debug configs *(PR [#737](https://github.com/ietf-tools/xml2rfc/pull/737) by [@NGPixel](https://github.com/NGPixel))*


## [v3.12.3] - 2022-02-23
### Bug Fixes
- [`dc1231174d`](https://github.com/ietf-tools/xml2rfc/commit/dc1231174d9df01b96ad8cf341633978d8fc1af9) - make xml2rfc/run.py executable ([#726](https://github.com/ietf-tools/xml2rfc/pull/726) by [@dkg](https://github.com/dkg))
- [`1ed938433c`](https://github.com/ietf-tools/xml2rfc/commit/1ed938433c792055d9bbc930f5d99e6909b9f3fc) - sourcecode element definition copy-paste error ([#731](https://github.com/ietf-tools/xml2rfc/pull/731) by [@cabo](https://github.com/cabo))

### Chores
- [`3ae5c77751`](https://github.com/ietf-tools/xml2rfc/commit/3ae5c77751c7118a817a52ae165756e9b37f7fd0) - add vscode dev container config ([#730](https://github.com/ietf-tools/xml2rfc/pull/730) by [@NGPixel](https://github.com/NGPixel))
- [`e6e07375b3`](https://github.com/ietf-tools/xml2rfc/commit/e6e07375b32c265ef3d42516d003fa24cb507b77) - Revert Jinja2 3.* update ([#732](https://github.com/ietf-tools/xml2rfc/pull/732) by [@kesara](https://github.com/kesara))


## [v3.12.2] - 2022-02-16
### Bug Fixes
- [`fe71b28365`](https://github.com/ietf-tools/xml2rfc/commit/fe71b2836576826a1cc82e35255d492d3b560bb1) - Remove the blank line from the contact information in text output ([#720](https://github.com/ietf-tools/xml2rfc/pull/720) by [@kesara](https://github.com/kesara))

### Chores
- [`895a85d9d4`](https://github.com/ietf-tools/xml2rfc/commit/895a85d9d40ea8c6df376533c67dd559d5376d6e) - move /cli to root
- [`0dee2ce130`](https://github.com/ietf-tools/xml2rfc/commit/0dee2ce1305900bda399c27d0cbe79dbfa6b826b) - remove gui and package folders
- [`ed7051a0b0`](https://github.com/ietf-tools/xml2rfc/commit/ed7051a0b05dee9c89ef93d6a877395ff471c008) - Docker build script updates
- [`ff7bb5785b`](https://github.com/ietf-tools/xml2rfc/commit/ff7bb5785bdc9621325093b79427cb24e7137adf) - Add executable permission to fix.pl ([#718](https://github.com/ietf-tools/xml2rfc/pull/718) by [@kesara](https://github.com/kesara))
- [`a6227f88fc`](https://github.com/ietf-tools/xml2rfc/commit/a6227f88fcd2130592a0947b4dcedb3ea4517f9b) - remove font-install binary from repo


## [3.12.1] - 2022-02-01

- Improve local file lookup: Add source directory to the allowed list, Disallow any files that are on child directories of the source directory, Add a warning when including `.ent` files. Fixes [#703](https://github.com/ietf-tools/xml2rfc/issues/703). (by [@kesara](https://github.com/kesara))
- Update bibxml subdirectories list. Fixes [#701](https://github.com/ietf-tools/xml2rfc/issues/701). (by [@kesara](https://github.com/kesara))
- Fixes manpage generation issue. Fixes [#694](https://github.com/ietf-tools/xml2rfc/issues/694). (by [@kesara](https://github.com/kesara))

## [3.12.0] - 2021-12-08

- Security release - disallow includes from local filesystem by default. Adds a `--allow-local-file-access` flag (and associated library configuration option) to allow it. (by [@rjsparks](https://github.com/rjsparks))

## [3.11.1] - 2021-10-29

- Cosmetic release to address changelog formatting (by [@rjsparks](https://github.com/rjsparks))

## [3.11.0] - 2021-10-29

- Fixes a case where an infinite loop could occur in text rendering.  Fixes [#684](https://github.com/ietf-tools/xml2rfc/issues/684). (by [@kesara](https://github.com/kesara))
- Updates TPL 5 boilerplate text from Simplified to Revised. Fixes [#676](https://github.com/ietf-tools/xml2rfc/issues/676). (by [@kesara](https://github.com/kesara))
- Reverts back Apple M1 specific changes from docker/run. (by [@kesara](https://github.com/kesara))

## [3.10.0] - 2021-09-21

- Fixes Python compatibility issues in `bin/uglifycall`.  (by [@kesara](https://github.com/kesara))
- Updates docker/run command to support Apple M1. Fixes  [#675](https://github.com/ietf-tools/xml2rfc/issues/675). (by [@kesara](https://github.com/kesara))
- Adds missing line joiner settings for `<ol>` and `<ul>`. Fixes [#673](https://github.com/ietf-tools/xml2rfc/issues/673). (by [@kesara](https://github.com/kesara))
- Fix Makefile rule precedence and repair canonical.xml test to  work with yestest. Fixes [#671](https://github.com/ietf-tools/xml2rfc/issues/671). (by [@jennifer-richards](https://github.com/jennifer-richards))
- Changes RFC regression test to be a separate test. (by [@kesara](https://github.com/kesara)) (by [@kesara](https://github.com/kesara))
- Adds RFC regression tests. Fixes [#667](https://github.com/ietf-tools/xml2rfc/issues/667). (by [@kesara](https://github.com/kesara))
- Fix for bad PDF breaks. (by [@kesara](https://github.com/kesara))
- pin weasyprint<53 for tox tests (by [@rjsparks](https://github.com/rjsparks))
- Sort class values in HTML output. Fixes [#553](https://github.com/ietf-tools/xml2rfc/issues/553). (by [@kesara](https://github.com/kesara))
- Keep pns from incoming xml when present; handle case that an author  does not have an after-next element. Fixes [#664](https://github.com/ietf-tools/xml2rfc/issues/664). (by [@jennifer-richards](https://github.com/jennifer-richards))
- Remove quotes from the text rendering of `<tt>`. Fixes [#600](https://github.com/ietf-tools/xml2rfc/issues/600) and [#647](https://github.com/ietf-tools/xml2rfc/issues/647). (by [@kesara](https://github.com/kesara))
- Fix info block runoff issue in PDFs. Fixes [#606](https://github.com/ietf-tools/xml2rfc/issues/606). (by [@kesara](https://github.com/kesara))
- Remove unicode entity replacement step from v2v3 conversion. Fixes [#641](https://github.com/ietf-tools/xml2rfc/issues/641). (by [@kesara](https://github.com/kesara))
- Cache XML XInclude files with referencegroup. Fixes [#653](https://github.com/ietf-tools/xml2rfc/issues/653). (by [@kesara](https://github.com/kesara))

## [3.9.1] - 2021-06-25

- This is a cosmetic release, only to correct issues with the changelog formatting in 3.9.0 (by [@rjsparks](https://github.com/rjsparks))

## [3.9.0] - 2021-06-25

- Stop stripping CDATA with v2v3 option. Fixes [#601](https://github.com/ietf-tools/xml2rfc/issues/601). (by [@kesara](https://github.com/kesara))
- Implement bare attribute rendering in HTML and PDF. Fixes [#609](https://github.com/ietf-tools/xml2rfc/issues/609). (by [@kesara](https://github.com/kesara))
- Add `https://datatracker.ietf.org/doc/html/` as default `id-base-url` and `id-reference-base-url`. Fixes [#618](https://github.com/ietf-tools/xml2rfc/issues/618). (by [@kesara](https://github.com/kesara))
- Use 'appendix-A.1' format for section ids in HTML output. Use '`section-appendix-...`' as XML id both for all appendixes, not just top level. Fixes [#581](https://github.com/ietf-tools/xml2rfc/issues/581). (by [@jennifer-richards](https://github.com/jennifer-richards))
- Define entities in v2v3 output instead of referencing an external DTD. Fixes [#548](https://github.com/ietf-tools/xml2rfc/issues/548). (by [@jennifer-richards](https://github.com/jennifer-richards))
- Properly reflect the updates to headers and boilerplate reflecting  erratum 5258. Fixes [#648](https://github.com/ietf-tools/xml2rfc/issues/648). (by [@rjsparks](https://github.com/rjsparks))

## [3.8.0] - 2021-05-20

- Fix indentation error that prevented normalizing ascii-art whitespace. Fixes [#403](https://github.com/ietf-tools/xml2rfc/issues/403). (by [@jennifer-richards](https://github.com/jennifer-richards))
- Insert removeInRFC notice as first child even when `<name>` tag is absent. Fixes [#622](https://github.com/ietf-tools/xml2rfc/issues/622). (by [@jennifer-richards](https://github.com/jennifer-richards))
- Handle `<iref>` as child of most of its allowed parent elements. An `<aside>` parent is still not handled properly. Fixes [#620](https://github.com/ietf-tools/xml2rfc/issues/620). (by [@jennifer-richards](https://github.com/jennifer-richards))
- Refer to un-numbered sections by name rather than number. Fixes [#572](https://github.com/ietf-tools/xml2rfc/issues/572). (by [@jennifer-richards](https://github.com/jennifer-richards))
- Create tests-no-network and clear-cache Makefile targets to support network-free testing. Updates to tests/cache and tests/valid so tests pass with and without network. Fixes [#561](https://github.com/ietf-tools/xml2rfc/issues/561). (by [@jennifer-richards](https://github.com/jennifer-richards))

## [3.7.0] - 2021-04-05

- Updated manpage.txt and docfiles
- Remove mention of Python2.7 from the README. Add pointer to self-generated documentation. (by [@rjsparks](https://github.com/rjsparks))
- Restore xref format for cref target from r3890 (was accidentally reverted in r3910).  Fixes [#431](https://github.com/ietf-tools/xml2rfc/issues/431). (by [@rjsparks](https://github.com/rjsparks))
- Handle iref items starting with special characters when constructing index. Fixes [#603](https://github.com/ietf-tools/xml2rfc/issues/603). (by [@jennifer-richards](https://github.com/jennifer-richards))
- Include the index in the toc and retain index in prepped XML.  Fixes [#607](https://github.com/ietf-tools/xml2rfc/issues/607). (by [@jennifer-richards](https://github.com/jennifer-richards))
- Correctly gather irefs by item/subitem. Improve index rendering. Use section numbers for xref text in index. Fixes [#418](https://github.com/ietf-tools/xml2rfc/issues/418). Fixes [#610](https://github.com/ietf-tools/xml2rfc/issues/610). (by [@jennifer-richards](https://github.com/jennifer-richards))
- Changed the Makefile's use of bash builtin read to only test for non-zero responses, instead of looking for responses higher than 128. Not all bash, and in particular not the bash available on osx, return error codes higher than 1 for the read builtin. (by [@rjsparks](https://github.com/rjsparks))

## [3.6.0] - 2021-03-17

**Add pagination, bugfixes, drops Python 3.5**

- Prevent crash when column count varies between table rows. Fixes [#512](https://github.com/ietf-tools/xml2rfc/issues/512). (by [@jennifer-richards](https://github.com/jennifer-richards))
- Cite the abstract as 'Abstract' instead of 'Appendix Abstract'.  Fixes [#429](https://github.com/ietf-tools/xml2rfc/issues/429). (by [@jennifer-richards](https://github.com/jennifer-richards))
- Modify selector to include rfc element in yes/no to true/false conversion. Fixes [#457](https://github.com/ietf-tools/xml2rfc/issues/457). (by [@jennifer-richards](https://github.com/jennifer-richards))
- Move conjunctions out of author `<span>` elements in reference citations. Fixes [#575](https://github.com/ietf-tools/xml2rfc/issues/575). (by [@jennifer-richards](https://github.com/jennifer-richards))
- Remove quotes from `<xref format='title'>` in text writer. Fixes [#563](https://github.com/ietf-tools/xml2rfc/issues/563). (by [@jennifer-richards](https://github.com/jennifer-richards))
- Label xref to a cref with the anchor instead of 'Section X.Y'. Fixes [#431](https://github.com/ietf-tools/xml2rfc/issues/431). (by [@jennifer-richards](https://github.com/jennifer-richards))
- Simplify text rendering of super/subscripts. Based on patch submitted by martin.thomson@gmail.com and refinement from subsequent list discussion. Fixes [#590](https://github.com/ietf-tools/xml2rfc/issues/590). (by [@jennifer-richards](https://github.com/jennifer-richards))
- moved away test targets for untested versions of python (by [@rjsparks](https://github.com/rjsparks))
- Remove pilcrows from tables of contents In addition to searching list item descendants for the existence of previously-added pilcrows, the code now  also searches the list item ancestors for any node that has the 'toc'  class to indicate that it is part of a table of contents.  If either are found, the pilcrow is not added.  Fixes [#568](https://github.com/ietf-tools/xml2rfc/issues/568). (by mark@painless-security.com)
- Made a --paginate/--pagination switch available, to force pagination for text output. (by [@levkowetz](https://github.com/levkowetz))
- Adjusted li > p margin to fit better with other list spacing, and to not let the `<p>` margin spill out from inside a `<li>`.  FIxes issue [#580](https://github.com/ietf-tools/xml2rfc/issues/580). (by [@levkowetz](https://github.com/levkowetz))
- Drop python 35 from tests (by [@rjsparks](https://github.com/rjsparks))
- Updated manpage.txt and docfiles (by [@rjsparks](https://github.com/rjsparks))

## [3.5.0] - 2020-11-18

- Added some missing test cache entries.
- Added missing line joiner settings for `<artwork>`, `<artset>` and  `<sourcecode>` within `<blockquote>`.  Fixes issue [#569](https://github.com/ietf-tools/xml2rfc/issues/569)
- Fixed a diff exclusion regex in the Makefile, and added a Makefile target to update manpage and docfiles, and a mkrelease step to update those files with the new release version as part of the release actions.
- Changed the output text for `<xref>` with text content equal to the  reference tag to output both, rather than suppressing one.  Fixes issue  [#571](https://github.com/ietf-tools/xml2rfc/issues/571).

## [3.4.0] - 2020-11-06

- Added handling for 'indent' attributes that have been set to the empty string.  Fixes issue [#564](https://github.com/ietf-tools/xml2rfc/issues/564).
- Added some new unlisted switches to make some test cases easier to  maintain.
- Changed the default handling for draft reference XIncludes to use  revision-agnostic bibxml URLs in v2-to-v3 conversions, and added a switch  to use explicit revisions instead if desired.
- Tweaked doc.py and doc.xml to suppress mention of switches with  argparse.SUPPRESS help settings, for consistency between --help and --doc  output.
- Changed the text output for `<xref format='title'/>` on request from the  RPC.  Fixes issue [#563](https://github.com/ietf-tools/xml2rfc/issues/563).

## [3.3.0] - 2020-10-19

- Removed validation before unprepping in order to be able to process source files that use XInclude without failing validation because of missing IDREF targets.
- Fixed a problem where some name entries permitted Latin script names,  but not all.  Fixed a misleading error message for `<iref>` elements that lack a useful anchor to refer back to.
- Fixed some diff exclusion patterns in the Makefile.
- Added a couple of test cases.

## [3.2.1] - 2020-09-29

- Removed code dependent on libmagic and the python-magic requirement, as installation of python-magic doesn't always succeed.
- Tweaked the error message emitted for unexpected content in elements  that don't permit text content to be slightly more readable for minor erroneous content by quoting the errant characters and placing short strings on the same line as the error message.
- Refactored the code for the --version switch, to make it more  straightforward to include generator version information in generated html  pages, and added generator version information to generated HTML.


## [3.2.0] - 2020-09-24

- Added a utility script that checks some test suite prerequisites, to  avoid for instance test errors because of missing python modules or fonts.   Related to issue [#549](https://github.com/ietf-tools/xml2rfc/issues/549).
- Updated the list of tags that permit Latin script content without an  'ascii' attribute.
- Changed the acceptable length of the title abbreviation for the running  page header in PDF output, and changed the warning to a note.

## [3.1.1] - 2020-09-13

- Fixed an issue with empty table cells that could cause an exception.

## [3.1.0] - 2020-09-13

- Fixed an issue with an extra comma rendered in HTML for empty date  elements.  Fixes issue [#542](https://github.com/ietf-tools/xml2rfc/issues/542).
- Added escaping of quotes in page footer and header components when generating the @page CSS for PDF output, in order to avoid issues when building quoted CSS content strings from the components.   Fixes issue [#544](https://github.com/ietf-tools/xml2rfc/issues/544).
- Added a CSS workaround for an unexpected HTML rendering behaviour in  some browsers, where a `<dt>` following an empty `<dd>` would be indented.   Fixes issue [#545](https://github.com/ietf-tools/xml2rfc/issues/545).
- Improved error messages and the handling of artwork with no "type"  attribute value when "binary-art" would have been correct. Fixes issue [#535](https://github.com/ietf-tools/xml2rfc/issues/535).
- Reverted the default value for the --legacy-date-format to false, on  request from the RPC.
- Fixed table cell padding to not add left padding for left-aligned  columns if not all lines in the column can be padded in the same manner, and similarly for right-aligned columns.  Fixes issue [#543](https://github.com/ietf-tools/xml2rfc/issues/543).
- Tweaked utils.build_dataurl() to give consistent results across Python  versions (tilde was added to the default safe characters in Python 3.7, so the default percentage-escape results of binary content differed if it contained a 0x7e (tilde) character.
- Fixed a bug in finding the length of the longest word in a table cell,  used to determine minimum cell width for text output.
- Added a new test case with a tightly constrained table to excercise the  issue in [#543](https://github.com/ietf-tools/xml2rfc/issues/543).
- Added `<title>` to the list of elements that can have Latin script  content without needing the 'ascii' attribute set.  Fixes issue [#525](https://github.com/ietf-tools/xml2rfc/issues/525).
- Refined the rendering of `<xref>` with `format='title'` for the text  formatter.
- Added docfile and manpage information about elements that are permitted  to have Latin script content without an ascii attribute equivalent being  set.
- Expanded on the docfile description of elements that can have Latin  script content without ASCII fallback.
- Added a test case related to issue [#525](https://github.com/ietf-tools/xml2rfc/issues/525).
- Changed the HTML rendering of `<xref>` within `<name>` to use square  brackets.  Fixes issue [#498](https://github.com/ietf-tools/xml2rfc/issues/498).

## [3.0.0] - 2020-09-02

**Transition to using the new schema v3 output formatters by default**

This release provides the functionality that the 2.47.0 release had (with some enhancements), but is backwards incompatible because the default settings for some switches has changed. The `--legacy` switch must now be set explicitly in order to use the old output formatters. By default, XML input files with schema v2 content will be converted to v3 on the fly and the output formatting of the converted XML will be done with the new schema v3 formatters. With this release, support of Python 2.7, which is past end-of-life, will no longer be part of the test suite.

There are also a number of other changes. From the commit log:

- Replaced the use of the deprecated optparse module with the newer  argparse python module.
- Removed testing with Python 2.7, and added Python 3.8
- Updated the bin/mkrelease script to generate documentation HTML and text for the release, place it on xml2rfc.tools.ietf.org, and mention the documentation URL in the release notes.
- Updated the major revision to 3, given that we no longer support Py27 and have switched default output formatters.
- Changed bin/mkrelease to install using pip3.6 on the tools servers (the  default pip might be for Py2.7).
- Added an 'indent' attribute for `<t>`, in order to support indented paragraphs without the one-item unordered list workaround, as approved by the schema change board.  Added default values for the 'indent' attributes for `<dl>`, `<ul>`, `<ol>`, `<t>`.  For the `<t>` element, the 'indent' attribute indicates any extra amount of indentation to be used when rendering the paragraph of text.  The indentation amount is interpreted as characters when rendering plain-text documents, and en-space units when rendering in formats that have richer typographic support such as HTML or PDF.  One en-space is assumed to be the length of 0.5 em-space in CSS units.  Only non-negative integer amounts of indentation are supported.
- Improved an error message about bad attribute values to show the line  of XML source on which the error was found.
- Added information about command-line switches that have negations  (--no-foo... versions) to the context handed to the documentation template.
- Changed the default of some switches for the 3.0.0 release: --v3 =>  true; --legacy-date => true; --external-js => false.
- Improved the documentation file output for switch default values and  for options with negation switches.
- Updated the Makefile to use the appropriate 3.x release series switches.
- Updated the requirements for a number of python modules.
- Fixed an issue where hrefs without matching ids could be generated by  the HTML renderer from empty `<name>` elements.  This also fixed an issue  with missing figure and table captions in some unusual cases.
- Added support for multi-level ordered lists through a '%p' (for parent)  code for use in the `<ol>` 'type' attribute.  Fixes issue [#465](https://github.com/ietf-tools/xml2rfc/issues/465).
- Added more documentation for the --version switch
- Updated the schema and tests to permit `<blockquote>` within `<aside>`.   Fixes issue [#524](https://github.com/ietf-tools/xml2rfc/issues/524).
- Added a list of available postal elements for a country to the warning  for unused postal address parts.
- Added a length limitation for the running header title in paginated  text documents, to avoid overwriting other parts of the running header.
- Changed the schema to permit nested `<sub>` and `<sup>`, as approved by the v3 schema change board.
- Added support for outdent handling to propagate upwards to parent  elements if the full needed outdent amount could not be done in the local  context, in order to be able to apply artwork outdenting to `<artwork>`  elements which aren't situated immediately under `<section>`.
- Changed many instances of reference source indications (xml:base) from "xml2rfc.tools.ietf.org" to just "xml2rfc.ietf.org".  Removed the massaging of reference XML to place seriesInfo elements in the backwards-incompatible location inside reference/front.  Changed the --add-xinclude flag to use datatracker.ietf.org/doc/bibxml3/ as the location of draft reference entries.
- Added a couple of entries to the test suite reference cache.
- Improved the handling of missing day information for `<date>` to make sure we  don't pick days outside the acceptable range for the given month and also  pick a reasonable value based on whether the year and month is in the past,  present or future.
- Improved an error message for a case of disallowed XML text content.   Tweaked the 'block_tags' list.
- Changed the manpage template to not use comma before 'and' when  rendering a list of 2 elements.
- Changed the schema to permit `<aside>` within `<dl>` on request from the  RPC, with schema change board approval.  Updated renderers, CSS and tests  accordingly.
- Tweaked the CSS for block elements that are direct first children of  `<dd>` to render the same way in HTML as in text (i.e., vertically distinct,  not on the same line as `<dt>`).

## [2.47.0] - 2020-07-17

**CSS fixes, Built-in documentation, manpage mode, and more**

The major feature in this release is the addition of built-in documentation generated from:

- the actual XML schema distributed with the tool
- the differences between the current schema and the RFC7991 schema
- the code's settings for which elements and attributes are deprecated
- text snippets describing the schema parts and how the code handles them.

There are new --doc/--docfile and --man/--manpage switches; the first will generate documentation in the form of a v3 XML document that can then itself be processed to generate the various supported formats. The second, --man, will generate the documentation XML internally and then process it to text output which is shown with a pager, like 'man'.

From the commit log:

- Corrected the CSS line height of compact lists (it should not be different than for non-compact lists; compact should only affect spacing between items, not line height).  Also corrected the CSS top margin for nested lists; extra top margin is desired for a top-level list, but not when nesting them, due to the resulting inconsistency in apparent line height variations.
- Changed `<section>` within `<toc>` from oneOrMore to zeroOrMore, in order to make it possible to honour the tocInclude setting, and reordered some true/false entries for consistency, and changed the line breaking of some lines in the RNG compact representation to fit on 72-character lines.
- Added .rng and .rnc files with the RFC7991 schema, in order to be able to automatically determine which elements and attributes are new in the schema since 7991.
- Added a new writer, 'doc', and template and text snippet files for  autogenerated documentation.
- Updated the requirements file with some new module requirements.
- Refactored the code a bit to make it more straightforward to generate  text without writing it out to file.
- Moved the list of deprecated attributes to writers/base.py, and did some slight refactoring for consistent naming of some class variables and avoidance of duplicate parsing of the schema file.
- Did some minor code cleanup and dead code removal, and corrected the  header generation for non-IETF documents (using `<rfc ipr=''>`).
- Fixed an issue where XML parser errors could be reported for '`<string>`'  instead of the actual input file name.
- Added new options --docfile/--doc and --manpage/--man, used to trigger generation and display of the built-in documentation.  Reorganised the option grouping.  Updated some option help strings.  Made it possible to propagate all command-line option information to the documentation template.
- Corrected the default templates path.  This is related to [fae96d4](https://github.com/ietf-tools/xml2rfc/commit/fae96d430f00d23e407ce88bf1790a90081a01cf).
- Reverted a change from [c51345a](https://github.com/ietf-tools/xml2rfc/commit/c51345ae3a908a7e6bed382f213412ca311b6ac0) in the v2v3 converter.
- Added a custom Jinja2 filter 'capfirst()', for use in the documentation  template.
- Tweaked the documentation template: Some changed wording, support for  sub-items not wrapped in `<t>`, corrected capitalisation using the 'capfirst'  filter.
- Updated hastext() and iscomment() to do the right thing if given  content with embedded xml processing instructions.
- Tweaked the handling of default values for --date, so as to give better  documentation of the option, and also tweaked the help text for  --table-borders.
- Added a class utility method to get any current PI related to a given  setting, and fixed another case of template path default value, related to  [c51345a](https://github.com/ietf-tools/xml2rfc/commit/c51345ae3a908a7e6bed382f213412ca311b6ac0).
- Added PI support for text table borders setting, and improved the text  table output for transitions between `<th>` and `<td>` rows for 'light' and  'minimal' borders.
- Added makefile support for testing of the --manpage and --docfile  switches.  Added silencing of one unavoidable warning in the test of  --unprep.

## [2.46.0] - 2020-06-23

- Added `<dd class='break'/>` and `<span class='break'/>` entries in additional places, as a workaround for WeasyPrint's eagerness to break between `<dt>` and `<dd>`.  Fixes issue [#529](https://github.com/ietf-tools/xml2rfc/issues/529).
- Tweaked the rendering of `<tt>` inside table cells in text mode to not  use double quotes to distinguish the `<tt>` content from surrounding text  when the only cell content is the `<tt>` element.
- Modified the text rendering of table cells.  `<thead>` and `<tfoot>` now  implies no special rendering (earlier, they caused a change in table border  on transition) while `<th>` now always renders with distinct borders compared  with `<td>`.  Also added 'light', and 'minimal' table renderings, with  different table border settings when compared to the previous rendering,  which now is available as 'full'.  The 'light' rendering is closer to the  v2 formatter table rendering, but does not permit table cells with colspan  or rowspan different from 1 to be properly distinguished.  The changes in  `<th>` rendering fixes issue [#527](https://github.com/ietf-tools/xml2rfc/issues/527).
- Added a --table-borders option with possible values 'full', 'light',  'minimal', to control the table rendering of the text renderer.  The  current default value is 'full', but 'light' is closer to the v2 text  renderer's output.
- Added a new internal join/indent setting to the Joiner nametuple to control outdenting.  Used the outdenting setting to enable outdenting for artwork wider than 69 characters in the v3 text renderer.  Fixes issue [#518](https://github.com/ietf-tools/xml2rfc/issues/518).
- Added missing support for @indent for `<ul>` in the HTML renderer, and  tweaked the same for `<ol>`.  Fixes issue [#528](https://github.com/ietf-tools/xml2rfc/issues/528).
- Corrected is_htmlblock() to not count `<dt>`, `<dd>`, and `<li>` as block  elements as they cannot be wrapped in `<div>`.
- Updated and refined the div-wrapping used to introduce additional IDs to deal better with anchors on `<dt>`, `<dd>`, and `<li>`.  Fixes issue [#530](https://github.com/ietf-tools/xml2rfc/issues/530).
- Made the CSS setting of background colour on `<tt>` and `<code>` more  selective in order not to interfere with background colour in tables, for  instance.
- Removed CSS that made URLs in references not break across lines -- the  drawbacks turn out to be more of a bother than the original reason not to  let these wrap.
- Did some HTML cleanup to make the w3.org validator happy.
- Fixed a few places in the HTML renderer where an empty tag could cause  an exception.
- Added test cases for empty and double email addresses, and added support for multiple email addresses within an author's address block. Fixes issue [#522](https://github.com/ietf-tools/xml2rfc/issues/522).

## [2.45.3] - 2020-06-08

- Fixed an issue with rendering empty `<dd/>` elements.

## [2.45.2] - 2020-06-02

- Fixed the HTML styling of `<ul spacing="compact"/>` lists, which wasn't  really compact.

## [2.45.1] - 2020-05-30

- Changed the handling of hyphens in table cells, so as to introduce line  breaks on hyphens if necessary to keep a table from becoming too wide (but  not otherwise).  The --table-hyphen-breaks switch can be used to permit  line breaks on hyphens in table cells also for tables that would not  otherwise become too wide.
- Added a switch --table-hyphen-breaks that will make the text renderer  more eager to break on hyphens in table cells.
- Using a pilcrow on an otherwise empty element added unwanted vertical space in the HTML output; avoid this.  Related to issue [#508](https://github.com/ietf-tools/xml2rfc/issues/508).
- Added a parameter to TextSplitter to control whether text is split on  hyphens or not.

## [2.45.0] - 2020-05-27

- Fixed the html rendering of `<cref>` with display=false. Fixes issue [#516](https://github.com/ietf-tools/xml2rfc/issues/516).
- Fixed the text rendering of `<cref>` with display=false. Fixes issue [#515](https://github.com/ietf-tools/xml2rfc/issues/515).
- Fixed an error in postal address rendering for Sweden. Fixes issue [#520](https://github.com/ietf-tools/xml2rfc/issues/520).
- Changed the internals of the text formatter to retain `<br>` information  for longer internally, in order to make `<br>` have effect in for instance  `<dd>` and `<td>` element text.  Fixes issues [#508](https://github.com/ietf-tools/xml2rfc/issues/508) and [#513](https://github.com/ietf-tools/xml2rfc/issues/513).
- Fixed erroneous indentation of first line of second and following  paragraphs of multi-paragraph `<dd>` elements, and changed code to retain  `<br>` in filled text.
- Added a font-family setting for @page in PDF mode, and added code to  warn about missing Roboto Mono fonts if the python-fontconfig package is available
- Added instructions for RobotoMono to the installation help for the  --pdf switch.

## [2.44.0] - 2020-04-22

- Added an '--unprep' switch and formatter to undo changes made by '--prep' which make a file unsuitable for continued editing.  This will help the RPC when the .xml file received from draft authors for an upcoming RFC is in 'prepped' format.
- Updated the v3 --expand formatter to expand external sourcecode and  artwork, in addition to handling XIncludes.  This should make it possible to produce single consolidated .xml files without using the --prep workaround.
- Did some refactoring, moving the dispatch method that calls processing  methods based on XPath expressions, and some other generic methods, into  the V3 formatter base class.
- Moved slugify() function, used in several writers, from v2v3 to  utils.py.
- Did a minor CSS tweak to improve orphan/widow handling of `<dl>` elements.

## [2.43.0] - 2020-04-14

- Added a workaround for weasyprint's extreme unwillingness to break  between `<dd>` and `<dt>`, which looks like a bug.  Fixes issue [#514](https://github.com/ietf-tools/xml2rfc/issues/514).
- Fixed a discrepancy in address handling between text and html output.   Fixes issue [#509](https://github.com/ietf-tools/xml2rfc/issues/509)
- Added more flexible text formatter handling of orphans and widows, and changed the default orphans/widows setting to 2 (matching the default CSS setting).
- Changed the CSS to not page break before the ToC, support keepWithPrevious, and deal better with how some artwork, figures and tables break across pages. Fixes issue [#511](https://github.com/ietf-tools/xml2rfc/issues/511).
- Changed the keepWithNext handling for the generated ToC to group the first 3 lines together, to avoid one-line orphans when page-breaking the ToC.  Also fixed some pyflakes issues with regex strings.
- Added text formatter support for 'keepWithPrevious', even if the preptool generally converts 'keepWithPrevious' to 'keepWithNext' on the previous element.
- Added setting '.keepWithPrevious' on html elements when set on the precursor xml element.
- Added v2v3 converter code to set 'keepWithNext' and 'keepWithPrevious' when converting `<preamble>` and `<postamble>` elements to `<t>` elements, to keep the grouping.
- Added code to the command-line runner to set some option default values that don't have matching command-line switches.
- Added default settings for orphans and widows during text rendering.
- Reduced the CSS font-family for body to only Noto Serif.  Addresses issue [#500](https://github.com/ietf-tools/xml2rfc/issues/500).

## [2.42.0] - 2020-04-02

- Changed the minimum whitespace distance between Updates/Obsoletes/etc.  and Author/Organization in the document header in text rendering back to  the value used in the v2 renderer (4 spaces) instead of the value used  recently (3 spaces).
- Added a guard against trying to normalize whitespace text that is None.
- Added a guard against trying to create `<iref>` entries for reference content, avoiding a later exception.  Fixes issue [#501](https://github.com/ietf-tools/xml2rfc/issues/501).
- Changed the approach to avoiding page breaks inside artwork etc., and  added styling to prevent page breaks between `<dt>` and `<dd>` in a `<dl>`.   Fixes issues [#461](https://github.com/ietf-tools/xml2rfc/issues/461), [#463](https://github.com/ietf-tools/xml2rfc/issues/463), and [#491](https://github.com/ietf-tools/xml2rfc/issues/491)
- Did a variable name change and removed a 'del', to deal with a pyflakes issue under 2.7.  Fixes issue [#504](https://github.com/ietf-tools/xml2rfc/issues/504).
- Added missing keepWithNext support for PDF output.
- Added a `--v2` switch with the same meaning as `--legacy`.

## [2.41.0] - 2020-03-20

- Added `<sourcecode>` to the tags that may have bare unicode content.   Fixes issue [#499](https://github.com/ietf-tools/xml2rfc/issues/499).
- Tweaked the CSS for dl.olPercent dd.  Fixes issue [#458](https://github.com/ietf-tools/xml2rfc/issues/458).
- Fixed an issue with rendering `<iref>` entries without trailing text or  whitespace.
- Fixed an issue in the v2v3 converter that could occur if no `<front>`  element is present.
- Fixed an issue with using Latin content in `<city>`, also addressing the  same issue for other `<postal>` sub-elements.  Related to issue [#493](https://github.com/ietf-tools/xml2rfc/issues/493).
- Fixed an issue with the formatting of a warning message.
- Fixed a Py2/3 issue with the `--country-help` output.

## [2.40.1] - 2020-02-27

- Applied patch from mt@lowentropy.net to simplify javascript and handle  more page width responsiveness in CSS.
- Made table and row borders the same for print and HTML on request from  the RPC, and increased the contrast between borders and odd row background  colour slightly.  Fixes issue [#494](https://github.com/ietf-tools/xml2rfc/issues/494).


## [2.40.0] - 2020-02-18

- Worked around weasyprint's failure to honour `<ol>` type attributes by  using the appropriate CSS list-style-type to control the list style.  Fixes  issue [#489](https://github.com/ietf-tools/xml2rfc/issues/489).
- Added `<br/>` to the v3 grammar.  Fixes issue [#492](https://github.com/ietf-tools/xml2rfc/issues/492).
- Fixed an issue where comments inside ascii-art artwork would cause  following artwork not to be rendered.
- Fixed an issue where use of .splitlines() instead of .split('\n')  caused unexpected removal of blank lines at the beginning or end of artwork.
- Allowed Latin script content in `<organization>` without requiring an ascii  attribute, to match the treatment of author and contact names.  Fixes issue  [#493](https://github.com/ietf-tools/xml2rfc/issues/493)
- Added additional error information when text content is found where  the schema does not allow it.
- Fixed an issue where trailing whitespace in artwork can trigger bad rendering, by removing whitespace at the end of lines in `<artwork>` and `<sourcecode>`.  Fixes issue [#490](https://github.com/ietf-tools/xml2rfc/issues/490)
- Changed the plain text URL for the trust license-info in TLP  boilerplate to an `<eref>` also for IAB documents.  Fixes issue [#456](https://github.com/ietf-tools/xml2rfc/issues/456).
- Removed indentation from lists rendered in table cells.
- Fixed an incorrect attribute grouping in the v3 schema
- Fixed two off-by-one errors in the calculation of the length of  Updates/Obsoletes lists.  Addresses issue [#472](https://github.com/ietf-tools/xml2rfc/issues/472)

## [2.39.0] - 2020-01-31

- Provided a rendering for `<xref>` with reference targets which are part of  a `<referencegroup>` and don't have a reference tag.
- Added a --pdf-help command-like option, and tweaked the order of some  command-line options in the --help output.
- Added a new filter for pdf-generation library warnings, to avoid it  appearing on every xml2rfc invocation.
- Added a v2v3 converter for dates with non-numeric years.
- Added an error for attempting to insert a missing XInclude namespace  prefix when 'xi' is already defined as something else.
- Fixed a bug introduced with the refactoring in [c01225d](https://github.com/ietf-tools/xml2rfc/commit/c01225d06afa7390217c743af2a271e649e2626e).

## [2.38.2] - 2020-01-27

- Provided a rendering for `<xref>` with reference targets which are part of a `<referencegroup>` and don't have a reference tag.
- Added a --pdf-help command-line option, and tweaked the order of some command-line options in the --help output.
- Added a new filter for pdf-generation library warnings, to avoid it  appearing on every xml2rfc invocation.
- Added a v2v3 converter for dates with non-numeric years.
- Added an error for attempting to insert a missing XInclude namespace  prefix when 'xi' is already defined as something else.
- Fixed a bug introduced with the refactoring in [c01225d](https://github.com/ietf-tools/xml2rfc/commit/c01225d06afa7390217c743af2a271e649e2626e).

## [2.38.1] - 2020-01-20

- Added a preptool check for numbered sections occurring after or under unnumbered sections, and changed the code for Reference sections to not emit section numbers if the previous section was unnumbered.   Fixes issue [#433](https://github.com/ietf-tools/xml2rfc/issues/433)
- Refactored the code for reference anchor to display string mapping, locating it in a base class method.  Updated it to honour the symRefs setting.  Fixes issue [#476](https://github.com/ietf-tools/xml2rfc/issues/476).
- Added installation of Python 3.8 to Dockerfile, and updated the minor version numbers for the other Python installation stanzas.
- Fixed a problem rendering multiple authors with organization  `showOnFrontPage='false`  Further addresses issue [#483](https://github.com/ietf-tools/xml2rfc/issues/483).
- Added a switch `--no-external-js`, and some other `--no-*` switches to  invert boolean settings.  Fixes issue [#486](https://github.com/ietf-tools/xml2rfc/issues/486).
- Added an early return from `cache()` when repeated attempts to fetch an  URL fails.


## [2.38.0] - 2020-01-14

- Tweaked the preptool handling of `<xref>` in `<toc>`.  Further addresses issue [#466](https://github.com/ietf-tools/xml2rfc/issues/466), fixing an issue that could occur if a section used for instance `<sub>` or `<sup>`.
- Fixed an off-by-one error in list indexing during text wrapping of first page header content.  Fixes issue [#483](https://github.com/ietf-tools/xml2rfc/issues/483).
- Tweaked the output for `<xref format='title'>` when referring to Reference  entries.
- Fixed a Py2/Py3 code compatibility issue
- Tweaked the handling of `<artwork type='ascii-art'>` to insert '(Artwork  only available as ...)' text also for text content which is only whitespace.
- Changed utils.isblock() to use a list of element tags derived from the  schema instead of a static list, to avoid discrepancies between schema and code.
- Changed the parser's handling of inter-element blank text to keep instead  of remove, in order to not drop intentional blank space between for  instance `<xref>` instances.
- Reverted the silencing of warnings related to postal address input.   Addresses issue [#437](https://github.com/ietf-tools/xml2rfc/issues/437).
- Added code to deal better with `<iref>` as a direct child of `<section>`.   Fixes issue [#479](https://github.com/ietf-tools/xml2rfc/issues/479).
- Fixed a bug where text after `<iref>` was lost by the text formatter.   Fixes issue [#480](https://github.com/ietf-tools/xml2rfc/issues/480)
- Added an option to list recognised country names for use with  `<country>`, and changed the note() emitted for unrecognized countries to a  warning.  Added some new alternative country strings.
- Updated test masters
- Fixed a problem with `<author>` entries with only `<organization>`  information.  Fixes issue [#424](https://github.com/ietf-tools/xml2rfc/issues/424).
- Added a minimum width setting for tables, in order to avoid table  captions rendering in very narrow space when the table itself is narrow.   Fixes issue [#482](https://github.com/ietf-tools/xml2rfc/issues/482).
- Avoid double space after initial when `<contact>` is rendered inline.   Fixes issue [#478](https://github.com/ietf-tools/xml2rfc/issues/478).
- Added code to recognise another case of inconsistent table row cell  counts and report the issue.
- Added 'P.R. China' as a recognized country name.
- From Python 3.2 and later, cgi.encode() is deprecated.  Changed to use html.encode() instead.

## [2.37.3] - 2019-12-22

- Undid margin-left: 0 for `<dd>` from the original supplied CSS, which caused nested lists to not have any distinction between levels.  Fixes issue [#458](https://github.com/ietf-tools/xml2rfc/issues/458).
- Tweaked the margin of block elements within `<aside>`.  Fixes issue [#469](https://github.com/ietf-tools/xml2rfc/issues/469).
- Added `<dt>` and `<li>` to list of block elements.  Fixes issue [#453](https://github.com/ietf-tools/xml2rfc/issues/453).
- Treated pilcrows on sourcecode within figure the same way as artwork within figure (don't add a pilcrow, since the figure title already provides an anchor).  Fixes issue [#475](https://github.com/ietf-tools/xml2rfc/issues/475).
- Don't use both @seriesNo and `<seriesInfo>` to emit series number.  Fixes  issue [#477](https://github.com/ietf-tools/xml2rfc/issues/477).
- Added code to adapt the line break position for long Updates: and  Obsoletes: entries for long right-column entries.  Fixes issue [#472](https://github.com/ietf-tools/xml2rfc/issues/472).
- Added normalization before the comparison that determines if `<xref>`  text content is different from derivedContent or not, and should be emitted  in addition to the derivedContent.  Fixes issue [#466](https://github.com/ietf-tools/xml2rfc/issues/466).
- Fixed a case where simple derivedContent was used instead of fully  rendered explicit `<xref>` text content where available.  Fixes issue [#474](https://github.com/ietf-tools/xml2rfc/issues/474).

## [2.37.2] - 2019-12-17

- Refined the non-ascii punctuation (smart-quotes, etc.) downcoding, and  eliminated a couple of bugs that could lead to infinite looping or crash.  Fixes issue [#473](https://github.com/ietf-tools/xml2rfc/issues/473).
- Made the xref labels used for different @section values work for  additional value types.
- Fixed a couple of preptool bugs found during debugging of issue [#473](https://github.com/ietf-tools/xml2rfc/issues/473).

## [2.37.1] - 2019-12-12

- Fixed a bug in the text formatter pagination code where it incorrectly  tried to annotate Comment and PI nodes with page number information.
- Updated the v2v3 converter to do essentially what it did before v2.37 with respect to unicode downcoding, but with more explicit calls.
- Added a base writer method to downcode reference punctuation.
- Moved the list of (tag, attr) combinations that permit unicode values  into util.unicode.  Rewrote docwncode_punctuation() to only touch  punctuation.
- Restored lost trailing text after `<contact>` in `<t>` context for text  output.

## [2.37.0] - 2019-12-10

- Added a new element `<contact>` with the same attributes and child elements as `<author>`, except for @role.  As a child element of `<section>` it will create a name and address block, as for authors in the Authors' Addresses section; as a child of `<t>` it will create an inline name entry, similar to `<author>` in citations.
- Changed the handling of block elements within table cells to re-wrap for better column fit.  Fixes issue [#454](https://github.com/ietf-tools/xml2rfc/issues/454).
- Added an error for references without anchor (in v2; in v3 this will be caught by the schema validation step).  Fixes issue [#412](https://github.com/ietf-tools/xml2rfc/issues/412).
- Changed error handling in a couple of places so as to result in non-zero command-line exit values on errors.  Fixes issue [#464](https://github.com/ietf-tools/xml2rfc/issues/464).
- Tweaked the `<cref>` text renderer to not apply `<t>` paragraph filling to the `<cref>` content.  Fixes an issue raised by resnick@episteme.net.
- Changed layout of multiple instances of `<extaddr>` and ``<street>`` to show on separate lines instead of one line, comma-separated.  Changed one notice message to warning.
- Added an option to silence warnings and notices starting with given strings.
- Changed the HTML renderer to not emit email information in both primary and alternative author address blocks.
- Added a test case using the new `<contact>` element, and added a couple of email addresses for increased coverage of email address placement when non-ascii address information is present.
- Updated the handling of non-latin address information in the text format to follow RFC7997 and the HTML output more closely.
- Added generation of v3.rng from v3.rnc to the Makefile, and fixed a schema error in the .rng file
- Changed the default content downcoding done for things like 'smart quotes' to only apply to text content, not to XML element attributes.

## [2.36.0] - 2019-12-02

- Improved support for internal xref to `<li>`, giving 'Section X, Paragraph Y, Item Z'.  Tweaked the output for xrefs to `<li>` with format='counter' to not include trailing period.
- Stripped away some cases of leading punctuation on incomplete postal  address lines.
- Fixed an issue with multi-part `<ol>` lists with the same group setting.
- Added support for tables in list items, on request from the RPC, in  order to match the needs of a couple of recent RFCs-to-be.
- Improved output format handling of postal addresses for countries with non-latin scripts where the XML address content is ASCII, rather than the expected native script.
- Fixed the isempty() utility function to correctly return False for  elements containing comments with trailing text.  Fixes issue [#455](https://github.com/ietf-tools/xml2rfc/issues/455).
- Added some cases of normalization of postal code during v2v3 conversion.
- Added bottom margin space for artwork in print output, to match that for sourcecode.

## [2.35.0] - 2019-11-12

- Changed the pn numbers for ToC entries to use 'section-toc.1-...'  instead of 'section-boilerplate.3-...'.
- Fixed schema and code so as to correctly show `<name>` entries with  superscript (and more) in the ToC.
- Added code to clean out instances of `&nbsp;` and other special  characters when rendering ToC, title, xref and reference.
- Eliminated postal address lines with only template content, i.e., no `<postal>` content, from output renderings.
- Fixed a typo in the v2v3 converter which caused conversion of the  tocdepth PI to fail.
- Added handling of `<sourcecode>` name attributes which were too long to fit on the same line as the marker, and added a specific indentation setting for `<sourcecode>` within `<section>`, to avoid extra indentation.
- For source code with markers and file name, only emit file name if  actually set.  Fixes an issue with the HTML renderer.
- Added the same in-figure indent for sourcecode as for artwork, to avoid  extra indentation.
- Removed an extraneous leading comma in reference rendering for  references without author information.
- Added CSS for bottom margin after `<sourcecode>` rendering in print.
- Added a missing conversion of attribute value 'no' to 'false' in the  v2v3 converter.
- Tweaked the text width when folding hang text.
- Changed the location and method of checking and catching non-ascii  characters in XML input declared with encoding='us-ascii'.
- Added warnings for tabs in artwork and sourcecode.
- Added a warning for long lines in v3 text ouput.
- Added a new metadata.js file from the RPC, with copyright and license  information and a code tweak.
- Refactored extract_date() into one extraction function and one  augmentation function, in order to render references with missing date info  correctly.  Also updated renderers to handle this case appropriately.
- Fixed an inconsistency in requiring the ascii attribute for Latin script non-ascii names.
- Corrected a buggy format string.  Fixes issue [#449](https://github.com/ietf-tools/xml2rfc/issues/449).
- Added an error if pn numbers are present in a file which is not marked  with prepTime.
- Corrected the indentation for `<t>` in table cells.
- Fixed an issue with duplicate pn numbers for `<t>` in table cells.

## [2.34.0] - 2019-10-23

- Made preptool reference sorting honour the sortRefs `<rfc>` attribute when symRefs is true.
- Fixed an issue with v2v3 conversion of PIs to `<xml>` attributes, where  PIs occurring before `<rfc>` would not be processed.
- Fixed the v3 text output for authors with no organization to output  blank lines, as for v2.
- Changed the rendering of `<xref>` with section reference and text  content, based on input from the RPC.
- Fixed an issue with `&nbsp;` in section headers not being handled properly by PDF viewers, by using plain space instead of non-breaking space.
- Fixed an issue with sizing of SVG artwork in PDF renderings.
- Fixed a validation problem for an empty boilerplate element for ipr='none'.
- Added a `<toc>` entry in `<rfc>``<front>`, and moved table of contents XML  from `<boilerplate>` to `<toc>`.
- Fixed an issue with the use of seriesInfo for top first page of v3 text output.
- Added support for a new attribute 'brackets { "none" | "angle" }? for `<eref>`, on request from the RPC.
- Changed the rendering of `<dt>``<dd>` so as to insert a newline if the `<dt>`  entry extends too close to the right-hand margin.
- Tweaked the removal of PIs during the preptool phase to occur before writing prepped content out to file, rather than earlier, in order to preserve PIs when prep() is used by xml2rfc internally.
- Added a warning for SVG content that won't scale.
- Added 'dd' to is_htmlblock().  One effect of this is to let `<dd>` to  be link targets for `<xref>` when generating HTML output.
- Changed the schema for `<postal>` to a workable but less precise  expression because the RFC7991bis generation scripts don't support the RNG  `<interleave>` construct.

## [2.33.0] - 2019-10-16

- Added an error message for a case that would otherwise break text table  generation.
- Added whitespace normalization for postal address tags, bcp14, and  similar.
- Fixed an issue with some special names like S/MIME in artwork.
- Removed conditional insertion of `<svg>` width= and height=, leaving that  up to the author.
- Removed a page break restriction that could cause unwanted page breaks  after reference section titles.
- Fixed issues with added or omitted spaces in line-broken URLs and other  items.
- Updated metadata.js to a new version received from the RPC
- Added conversion of some unicode code points to XML entities to the  v2v3 converter, in order to make later editing easier.

## [2.32.0] - 2019-10-04

- Adjusted print font sizes, which were in some cases overly large.  
- Added CSS page-break settings to avoid PDF page breaks inside tables and references.
- Tweaked the styling of `<aside>` to be more aligned with the W3C description of the element.
- Added support for the --legacy-date-format when generating the boilerplate expiry date.
- Fixed an issue with the text width in `<aside>` text rendering.
- Improved the handling of U+2028 in text output, and fixed a bug in the handling of U+2028 in the HTML output.
- Changed default value for --id-is-work-in-progress to True
- Fixed an issue with incorrect section links to appendices.
- Fixed a misspelling of "don't".  Fixes issue [#434](https://github.com/ietf-tools/xml2rfc/issues/434).
- Added styling to make HTML `<dl>` rendering of XML `<ol type='%d'>` more like the HTML `<ol>` and `<ul>` rendering.

## [2.31.0] - 2019-09-25

This release adds a feature to help with conditional line breaking inside table cells, and tweaks the layout of text in cells slightly.  It also fixes an incorrect line-break point and second-line indentation for long section titles in the v3 text formatter.  From the commit log:

- Fixed an issue with leading and trailing space padding in table cells,  and refined it to consider the alignment setting.
- Modified the text formatter to accept `&zwsp;` as a potential line-break  point.
- Included zwsp in allowed special characters (in addition to nbsp, nbhy,  word-joiner and line-separator).
- Fixed the line-breaking and second-line indentation of section titles  in v3 text output.
- The start of an emacs nXML mode schema which explicitly mentions xinclude in a couple of places.
- Removed code left in pdf.py by mistake, and set options.pdf=True when  in the PdfWriter.

## [2.30.0] - 2019-09-19

- Added logging configuration for weasyprint.  This controls the logging level based on the --quiet and --verbose flags, and should make weasyprint logging ouput more consistent across systems.
- Weasyprint reports ERROR if a CSS `<link>` URL isn't available, so we won't insert a `<link>` for "rfc-local.css" when generating PDF if the file doesn't exist.
- Tweaked the Makefile to use --add-include in some cases, for regression  testing.
- Corrected the `<xi:include>` links produced during v2v3 conversion with the --add-xinclude switch, 
- Changed the code to not retain <!ENTITY> declarations after v2v3 conversion.
- Changed BaseV3Writer.die() to raise an exception, rather than exit on  the spot, in order to do the right thing when called as a library.
- Tweaked the command-line messages when a fatal error is raised in a  writer.

## [2.29.1] - 2019-09-18

- Fixed an issue with pagination that could occur if a table (or other  block) longer than a page ended on the last page.

## [2.29.0] - 2019-09-17

- Adjusted the handling of ASCII, Latin, and non-Latin names and abbreviation in the v3 text formatter to act the same way as the v3 HTML formatter.
- Added RFC #### to the HTML rendered document title (for RFCs).
- Added `<artset>` in the schema in two places that were missed when  first introducing it.
- Changed the metadata json URL to avoid CORS issues due to redirects. Added a missing JS 'var' keyword and fixed a typo.
- Handled a file open mode deprecation issue.  Fixes issue [#427](https://github.com/ietf-tools/xml2rfc/issues/427).
- Added 'table' to the internal list of block-level elements.
- Added the traditional default 'Network Working Group' to the top of  HTML output for drafts.


## [2.28.0] - 2019-09-15

- Fixed the handling of empty `<workgroup>` entries when writing HTML, and  added handling for multiple `<workgroup>` entries for text output.  Fixes  issue [#425](https://github.com/ietf-tools/xml2rfc/issues/425).
- Fixed an inconsistency in the handling of non-ASCII author initials.
- Added some XML cleanup before writing prepped output.
- Fixed a case where for instance 'Section b.2' would be emitted instead  of the correct 'Appendix B.2'
- Changed the restricted right margin for `<dt>` terms.
- Added a check for conflicting schema information for v3 input files,  and fixed a failure to heed the presence of preptool errors when genreating  v3 format outputs.
- Adjusted the library call default value for --legacy-date-format to match the command line setting.
- Added a script to minify javascript (through an external service), and  added a javascript minification step to the Makefile.
- Added a html `<div>` for external metadata, and updated metadata.js to  look for online metadata also for documents served from disk.
- Fixed a problem with authors without any name, with only organization  information present.

## [2.27.1] - 2019-09-10

- Refined the preptool code that inserts reference target URLs to use an more appropriate guess at the extension, depending on the base URL.
- Corrected a mismatch between the default value for a switch in run.py and base.py.
- Changed the code for the --id-is-work-in-progress to avoid duplicate  `<refcontent>` insertion.

## [2.27.0] - 2019-09-09

- Added a test for handling of `&wj;` and `&nbsp;` during text linebreaking.
- Corrected the line break handling for &wj; and &zwsp; and changed to using a unicode private use code for internal "don't break" handling, in order to make use of &wj; possible in the XML source input.
- Added country name aliases for South Korea.
- In text renderer: Reverted 'Internet Draft' to 'Internet-Draft' for series name rendering.  Stripped empty parts from Updates: and Obsoletes: lists.  Added removal of U+2060 (word joiner) before emitting rendered text.
- Adjusted the preptool inserted reference target value for  Internet-Drafts to include a trailing '.txt' to avoid 404s
- Added U+2060 (word joiner) to the list of code points that should not trigger non-ASCII warnings
- Added an --id-is-work-in-progress switch to let the RPC automatically add a `<refcontent>` element indicating "Work in Progress" for Internet-Drafts.
- In HTML output, removed blank items from Updates and Obsoletes lists,  and reverted 'Internet Draft' in reference rendering to 'Internet-Draft'.
- Added entity definitions for &wj; and &zwsp;
- Fixed pyflakes issue; a variable name mismatch.
- Updated the installation instructions emitted when --pdf is specified  without having the necessary libraries in place to also include  instructions for Noto font installation.
- Fixed an issue with the ToC generation where sections without numbers  might still be rendered with the whitespace intended to go between number  and section title.
- Fixed an issue with the HTML ToC where sections without numbers might  still be rendered with the whitespace intended to go between number and  section title.
- Removed pilcrows from print layout to avoid spurious extra lines for  paragraphs where the pilcrow would not fit at the end of the last line.
- Fixed an insufficient test for URL vs. local file when handling the  --metadata-js-url switch.
- Tweaked the CSS for print to avoid reference entries beginning on a new  line, below the reference tag.

## [2.26.0] - 2019-09-03

- Fixed a broken rendering of Obsoletes: and Updates:, broken in different  ways in v3 HTML and v3 text output.  Fixes issue [#423](https://github.com/ietf-tools/xml2rfc/issues/423).
- Added an alternative style sheet from Martin Thomson (reachable with --css=mt) and rewrote the code to read in alternative style sheets to look in more places. Also added a mt.js file to go with the mt.css file, and tweaked the html renderer to load an alternative .js file if an alternative .css file is set and a matching .js exists.
- Fixed an issue with nested `<ul>` with emtpy="true".
- Added a test, with error exit, for duplicate `<displayreference>`  replacement terms.  Fixes issue [#421](https://github.com/ietf-tools/xml2rfc/issues/421).
- Changed the rendering of Internet-Draft references to follow draft-flanagan-7322bis-03 (RFC Style Guide bis) more closely.
- Made the address pane for authors' addresses wider, to accomodate very  long email addresses.  Changed the bottom margin for some styles used by  figures in order to get the same caption placement for figures and tables.
- Removed the computed `<dl><dd>` text mode indentation, and replaced it  with a fixed indentation of 3.
- Added an example section using `<aside>` to element.xml.  Updated the  `<xref>` examples that use the section attribute.
- Updated the prepping and rendering of `<xref>` with section settings to better handle sectionFormat="bare", and changed the handlin of the metadata.js script in HTML output.
- Added a minified version of the metadata.js script, updated the help text for the --external-css switch, and changed the default for the --metadata-js-url switch to use the minified metadata.js file, and changed the metadata_js_url setting for invocation of xml2rfc renderers as library modules to use the minified metadata.js
- Updated metadata.js with a new copy received from the RFC Editor staff.
- Added a warning for mismatch between `<rfc number="...">` and  `<seriesInfo name="RFC" value="...">`.
- Modified the v2v3 conversion code to deal correctly with multiple  instances of `<artwork>` within an unlabelled Figure.  Modified the converter  to avoid some lxml-related issues under python 3.x.
- Updated `XmlRfc.__init__()` with a new keyword argument to set source  file, needed when using the v2v3 converter as a library function (such as  from id2xml in v3 mode).
- Incorporated a new updated copy of the original CSS stylesheet received  from the original contractor.

## [2.25.0] - 2019-08-26

This rounds up the remaining known issues raised by the RFC Editor staff. Commit log excerpt:

- Rolled back an earlier requirements change, and added a restriction on  pycountry due to a buggy release.
- Fixed a number of issues with the xml generated for ToC and Index.  This makes the ToC output from prepped files the same as from unprepped files, which was not the case earlier.
- Fixed an log() argument error.
- Modified test input files to silence known issues with legacy rfc xml test files, in order to more easily be able to see newly appearing errors.
- Fixed a string formatting error.  Fixes issue [#417](https://github.com/ietf-tools/xml2rfc/issues/417).
- Changed processing progress messages to more consistently obey --quiet,  and to be visually distinct from errors and warnings.
- Modified the PI stripping so as to be able to silence warnings during  preptool processing.
- Added indentation handling for variations of `<ol>` on request from the rfc-editor staff.
- Moved the check for appropriate `<bcp14>` content from the text renderer  to the preptool, and tweaked it to permit `&nbsp;`, e.g., `MUST&nbsp;NOT`.
- Added a base_url setting to avoid an error message during pdf generation.
- Added an option --id-reference-base-url to set base url for rendering  of `<xref>` with I-D section references, with a sensible default; and set a  default value for --rfc-reference-base-url for `<xref>` with section= ease of  use.
- Tweaked the conditions for a preptool warning about missing docName to only apply in non-rfc mode, and added generation of any missing `<link rel='prev'>` element from docName if present.
- Widened the search for seriesInfo elements when handling the  `--rfc-reference-base-url` option, in order to handle all possible  placements, and fixed a bug in the creation of target URL when using this option.
- Added a warning for `<vspace>` elements without proper v3 alternatives  during v2v3 conversion.
- Fixed a bug introduced in [295fd79](https://github.com/ietf-tools/xml2rfc/commit/295fd7930474de10d24d42a6a68a264d4409a44f) when stabilizing attribute order, which could cause errors when running v2v3 conversion with XInclude insertion.
- Changed the code for --info dump to work for both py27 and py3x.
- The --legacy-list-symbols option was checked for validity before the  version attribute of the input file was seen.  Moved this check (and some  similar cases) later, in order to permit it to be used with v3 input  without giving the --v3 option.  Fixes issue [#414](https://github.com/ietf-tools/xml2rfc/issues/414).

## [2.24.0] - 2019-08-10

This release addresses a number of issues and minor feature requests from the RFC Editor.  Excerpt from the commit log:

- Added a switch --rfc-reference-base-url to specify an alternative base url when using `<xref>` section links.
- Stabilized XML and HTML output attribute order.  With lxml 4.40, the handling of attribute order changed for Py 3.6 and higher, to match the use of ordered dictionaries in Py3.6+.  Initial attributes set on an element are now sorted by key value.  This matches what lxml did previously, and still does for Py 2.7 and Py 3.[0-5].  Enforcing sorted initial attributes under Py 3.6+ makes our output more stable under varying versions of lxml and Python.
- Added support for `<xref>` section references in the v3 text formatter. Refactored some of the xref handling in preptool.  Added warnings for some xref attribute and content combinations that don't make sense.
- Tweaked the error message for use of -o with multiple output formats.
- Tweaked the layout of v3 text front page to correctly handle unicode codepoints of different width than 1, in order to get correct line lengths for authors with CJK names.
- Handled a problem with an unwanted space between year and the following comma in HTML ``<reference>`<date>` rendering.
- When using the built-in lxml Element remove() method, it unexpectedly removes not only the element, but also the element's tail.  Dealt with this by using our own remove() where needed.
- Added pilcrows on `<dd>`, to match pilcrows on other list entries.
- Removed address lines with only punctuation from the author address rendering, eliminating for instance lines containing only a comma.
- Added a viewport meta tag, to improve rendering on some devices.
- Added class 'selfRef' on some Figure and Table links that were missing it.
- Changed the address format to always start with the author name, according to a conversation with the RFC-Editor staff in Prague.
- Changed the V3 writer note() method to obey quiet and verbose in the same manner as log.note().
- Changed the v3 validate() from being separate methods for the v2v3 converter and the preptool to a common method on BaseV3Writer.
- Tweaked the `<date>` handling to make year ranges and fuzzy dates possible.
- Fixed an issue where text was lost when immediately preceded by `<xref>`.
- Added a `--bom` text format option, to insert a BOM mark at the beginning of the text format output.  Also added a BOM test, and removed some irrelevant switches.
- Made the line spacing of `<sourcecode>` the same as for `<artwork>`.
- Removed stripping of horizontal whitespace at the start of artwork in list items.
- Removed an unwanted attribute inheritance of 'ulEmpty' for `<ul>`.
- Fixed an issue with the CSS stylesheet for compact `<dl>` lists.
- Removed an unintentional change that would permit a 'contributor' author role.

## [2.23.1] - 2019-07-07

- Fixed a bug in the handling of sha1 and base64 methods when generating  cache names for references with query arguments.
- Updated the license file to more strictly follow the BSD 3-Clause  license, and changed the license field in the setup.py file to be more  precise.

## [2.23.0] - 2019-06-27

This release adds v2v3 support for conversion of v2 code with both text and external image sources to v3 `<artset>` format, and provides improved cache handling.  It also contains a long list of bugfixes.  Here is an excerpt from the commit log:

- Fixed an issue where cache clearing did not consider custom cache  locations.
- Added retry on connection error for external includes.  This fixes an issue which has appearing more often recently, where the first connection to fetch a reference file has failed to provide the right redirect.
- Added inclusion of metadata.js in the html renderer, for future handling of dynamic metadata (updated-by and obsoleted-by information, for instance).  Added a default instance of the metadata javascript file to the distribution, and added an command-line option to specify an alternative version of the javascript metadata script.
- Added `<script>` to the list of elements treated as blocks for HTML output formatting purposes.
- Show 'US' as "United States of America" (official name rather than short  name according to ISO 3166-1)
- Changed the default RFC base URL in run.py, and the extension used in  html.py.
- Added code to the v2v3 converter to create an `<artset>` for legacy  artwork with both a 'src' attribute and text content.
- Changed `<reference>` rendering when part of a `<referencegroup>` to not  include the DOI.
- Fixed a crash that could occur during index building with multiple levels of `<references>`.
- Tweaked the text format `<artwork>` placeholder (when no text format  artwork is present) to look at both 'src' and 'originalSrc' for an URL for alternative artwork.
- Changed the handling of pilcrow links at end of paragraphs and similar  to follow immediately after the content, without wrappable space, to avoid  the appearance of having double blandk lines when the pilcrow would be  wrapped to sit by itself on a line.
- Added a HTML div to hold artset anchor, fixing an issue where artset anchors would not always be present.
- Refined the preptool warnings regarding artset/artwork anchor handling.
- Eliminated toc update work when tocInclude is false.
- Only apply validation of cache entries as references if they are  `<reference>` entries.
- Refined the reference URL cache handling for URLs with query arguments,  to avoid cache collisions.
- Eliminated an incorrect check for page break after section header at end of document.  Fixes issue [#409](https://github.com/ietf-tools/xml2rfc/issues/409).
- Handled authors without address elements for v3 text.  Fixes issue [#408](https://github.com/ietf-tools/xml2rfc/issues/408).
- Dealt better with `<workgroup>` without content.
- Changed the schema to require at least one instance of `<artwork>` within  `<artset>`.  Fixes issue [#405](https://github.com/ietf-tools/xml2rfc/issues/405).
- Added a default rendering (code point number) for code points without  unicode code point names.  Fixes issues [#401](https://github.com/ietf-tools/xml2rfc/issues/401) and [#402](https://github.com/ietf-tools/xml2rfc/issues/402).

## [2.22.3] - 2019-04-08

This release brings further tweaks and improvements to the v3 text format output in the area of Table of Content formatting, and fixes a number of bugs.

- Tweaked the handling of ToC page numbers in the v3 text format.
- Tweaked the xml inserted by the preptool for the ToC to give ToC indentation and spacing which better match the legacy text format (and also looks better).
- Added a rewrite of `<svg>` viewBox values to the simplest acceptable format, to make sure it will be understood by our pdf generation libs.
- Added a test case for `<xref section=...>`
- Tweaked the section label for fragment `<xref>` rendering to say 'Appendix' instead of 'Section' for appendix references.
- Added a pre-rfc1272 reference to elements.xml to test the author initials handling for early RFCs.
- Tweaked the get_initials() code for use on `<reference>` authors. Refactored part of the text.render_reference() code to support get_initials() properly.
- Added special initials handling for RFCs 1272 and below, to apply the single initials handling enforced at that time.

## [2.22.2] - 2019-03-27

This release fixes a couple of issues discovered by users who are now starting to excercise the v3 processing chain.  Thanks for reporting bugs!  From the commit log:

- Fixed an issue with xref rendering where the 'pageno' parameter had  been given a non-numeric default value.  Fixes issue [#399](https://github.com/ietf-tools/xml2rfc/issues/399).
- Removed an unnecessary docker volume binding.
- Added slightly more verbosity when converting v2v3, and tweaked an  import statement.
- Fixed an issue with `<references>` sections where duplicate name entries  could be created during the prep` phase, leading to schema validation  failure.  Fixes issue [#398](https://github.com/ietf-tools/xml2rfc/issues/398).

## [2.22.1] - 2019-03-25

- Fixed an issue with section title rendering when there are comments  between `<section>` and `<name/>`.
- Added a DTD approximation to the v3 schema.  It omits sschema for SVG and does not permit text content without `<t>` inside blockquotes, table cells, and list elements, as the full RelaxNG for this cannot be translated to the DTD format.  This DTD is not used by xml2rfc, but is provided as part of the distribution in order to make it available to legacy tools.

## [2.22.0] - 2019-03-22

This release adds pagination of internet-drafts in --v3 --text mode.  It does not affect text output of RFCs, which remains unpaginated.  There are also some changes in order to make generated html validate in the W3C validator (validator.w3.org), and other bugfixes.

Details from the commit log:

- Tweaked the makefile to provide better diffs.
- Did a substantial refactoring of the text formatter, to carry  information of the origin element of each line of code down to the  generated text level, in order to be able to correctly implement page  breaking for tables and keepWith* labelled elements.  Added page breaking for drafts, and added page numbers to the Table of Contents when in page breaking mode.
- Moved warnings for missing `<rfc>` docName attributes from v3 renderers  to preptool, in order to always issue these warnings.
- Fixed a problem with local file name resolution that prevented the use  of xinclude href without path.
- Removed invalid CSS, and tweaked the invisible space above H* in order  not to overlay links in earlier text.

## [2.21.1] - 2019-03-11

This is a bugfix release, containing a number of fixes and adjustments in response to issues reported by the RFC Editor staff.  Excerpt from the commit log:

- Fixed an incorrect `<u>` format in a test file.
- Broadened the handling of `<svg>` viewBox attribute values, to permit  commas and enclosing parentheses.
- Added some missing default_options settings.  Moved the calculation of  various element tag sets (inline tags, for instance) out of the  BaseV3Writer class to avoid doing the same thing repeatedly when not  necessary.
- Fixed a flawed check for the presence of at least one required element  in the `<u>` format specification.
- Added a z-index setting to avoid links being overlaid by h* padding  stretching up over previous elements.
- Added a new option --no-pagination, and a startup check for missing  default options.

## [2.21.0] - 2019-03-04

This release introduces the switch --no-org-info to control the display of author organization information on the front page, for vocabulary v2 documents, and the `<organization>` attribute "showOnFrontPage" to do the same for v3 documents.  The handling is different for the two in order
to avoid retrofitting new attributes to the v2 DTD.  From the commit log:

- Added support for a --no-org-info switch, to suppress organization  rendering on the first page for v2 renderers.
- Added support for the showOnFrontPage attribute to v3 renderers, and a test case for the showOnFrontPage attribute.
- Added `<organization>` attribute "showOnFirstPage" (default "true") to  the schema.

## [2.20.1] - 2019-02-27

- Handle initials==Null return value from short_author_name_parts().   Fixes issue [#397](https://github.com/ietf-tools/xml2rfc/issues/397)

## [2.20.0] - 2019-02-26

This release changes the rendering of `<xref>` elements with text content by v3 formatters, and reintroduces `<xref format="none">` under v3 in order to properly cover the combinatorial space of rendering of `<xref>` with and without text content.  It fixes a number of issues, including a somewhat unexpected issue with namespace normalization, and improves the rendering output in some edge cases.  More details from the commit log:

- Removed namespace cleanup and normalisation during the v2v3 conversion, as it can have negative effects for inlined `<svg>` when the SVG namespace is specified in multiple places.
- Changed handling of reference//author entries with fullname but without initials and surname in order to derive those the same way for references as it's done in other places.
- Dropped support for Py34.  Support is now Py27 (untill end 2019), and Python 3.5 - 3.7.
- Tweaked the CSS for bcp14 keyword elements.
- Fixed a problem where a temporary valuable name stomped on a  method-wide name.
- Fixed a problem where `<xref>` "relative" attributes were treated as  fragment identifiers instead of as relative URL paths.
- Improved the placeholder text emitted by the v3 text renderer for  artwork without ascii-art.
- Removed stripping of the now (again) functional `<xref>` format value "none" from the v2v3 converter.
- Tweaked the rendering of `<xref>` having both derivedContent (section information, for instance) and text content, to generate hyperlinks to the xref target for both of them.  Simplified the html renderer by eliminating extra code for `<relref>`, now covered by the generic `<xref>` code.
- Fixed a problem with a missing hash character between path and fragment  identifiers in derivedLink generation.
- Added a conversion of `<relref>` elements to the generic `<xref>` form to  preptool.  Tweaked a debug print statement.
- Added An SVG diagram of the processing flow for v2 and v3 documents, used by xml2rfc3.rst, to doc/
- Added an rST-formatted Introduction to xml2rfc version 3 to doc/

## [2.19.1] - 2019-02-16

This is a small bugfix release.  From the commit log:

- Removed some linux-specific code.
- Fixed a problem with the handling of comments and PIs inside text  blocks.

## [2.19.0] - 2019-02-14

**Changed handling of alternative artwork**

The way `<artwork>` has been specified to handle the presence of both SVG artwork and text fallback (in Section 2.5 of [RFC7991]) has the result that any SVG content has to be placed as a data: URL in the "src" attribute when an ascii-art fallback is present.  This makes the SVG effectively uneditable once the preptool has been run, even if the SVG artwork was originally provided as a regular SVG XML file external to the document XML file.

In order to be able to more easily deal with alternative instances of artwork, and in the future possibly deal smoothly with a wider number of alternative artwork formats than is currently provided for, a new element `<artset>` could be introduced, presenting a set of alternative artwork executions.  This would let the renderer pick the most appropriate `<artwork>` instance for its format from the alternatives present within an `<artset>` element, based on the "type" attribute of each enclosed `<artwork>` element.

If more than one `<artwork>` element is found within an `<artset>` element, with the same "type" attribute, the renderer could select the first one, or possibly choose between the alternative instances based on the output format and some quality of the alternative instances that made one more suitable than the other for that particular format, such as size, aspect ratio, or whatnot.

Implementation: 
```
Xml2rfc as of version 2.18.0 implements this, with a   preference list when rendering to HTML and PDF of ( "svg",   "binary-art", "ascii-art" ), while the text renderer uses the list   ( "ascii-art", ) -- i.e., one entry only.  The Relax-NG compact   schema used for `<artset>` is this::
     artset =       element artset {         attribute xml:base { text }?,         attribute xml:lang { text }?,         attribute anchor { xsd:ID }?,         attribute pn { xsd:ID }?,         artwork*       }
   The `<artset>` element can occur anywhere an `<artwork>` element can   occur.  The first anchor on an `<artwork>` element within an   `<artset>` element will be promoted to the `<artset>` element if it   has none; apart from that, anchors on `<artwork>` elements within an   `<artset>` element will be removed by the preptool.
```

Additionally, this release contains some other fixes and changes.  From the commit log:

- Normalized the expansion of `<xref>` to be more consistent conceptually  and across renderings.  Added back rendering support for format='none'.
- Added another exception class to the import exception catch for pango, to avoid a crash in some environments.
- Applied a patch from rjs@nostrum.com to improve the xml2rfc description.
- Disallow lxml 4.3.1, as it can cause segfaults with some Python  versions.  Fixes issue [#393](https://github.com/ietf-tools/xml2rfc/issues/393).
- Put back LICENCE which has been lost from the source distribution tarball at some point.
- Adjusted the `<xref format="counter"/>` output for appendices.
- Added code to remove any usage of Unicode U+2028 LINE SEPARATOR from the text output also in legacy mode.
- Fixed a problem with the text format rendering of `<xref>` for an appendix.
- Added a get_element_tags() method in BaseV3Writer, and commented out  some debug code.
- Removed a warning about missing country that would appear even if no  `<address>` or `<postal>` was supplied.

## [2.18.0] - 2019-02-06

This release provides additional support for `<referencegroup>` rendering, and adds validation of fetched reference files before they are used or put in the reference cache.  A warning for un-cited references was added to the preptool; this has been present for v2 renderers for a long time, but was absent from the v3 specification.  A number of bugs have also been fixed. From the commit log:

- Fixed an issue with the v3 html renderer when given an author without  an address entry.  Fixes issue [#390](https://github.com/ietf-tools/xml2rfc/issues/390).
- Fixed a bug in the HTML renderer's SVG reading exception code.  Added support for a `<referencegroup>` target attribute, and suppression of target URLs for individual entries within a `<referencegroup>`.
- Adjusted the text rendering of reference annotations to match the html  rendering better.  Added support for `<referencegroup>` target rendering.   Suppressed rendering of target URLs for individual entries in a  referencegroup.
- Added a preptool check for reference citations, as earlier provided by v2 renderers.  Made the reference section numbering code more general, to support additional levels in the future.
- Added an attribute 'target' to `<referencegroup>`, in order to be able to link out to for instance IETF STD and BCP documents.
- Added ValueError to the exceptions caught on 'import weasyprint' as a  workaround for a problem in Python's locale.py file under 3.7.
- Added the Python version to the version list emitted with --version  --verbose.
- Added validation of included reference files before usage, to prevent html files fetched from dns-spoofing captive portals from being used.

## [2.17.2] - 2019-01-28

- Added a v3 text renderer for `<referencegroup>`, and made it possible to  refer to a reference group anchor with `<xref>`.

## [2.17.1] - 2019-01-23

This release addresses a couple of issues with SCG rendering in HTML and PDF formats, pointed out by sginoza@amsl.com, and adds testing under Python 3.7:

- Added code to add missing `<svg>` element attribute viewBox, and scale  down large svg images for use in html and pdf renderings.  Added an error  case when the svg element doesn't contain sufficient information (width and  height, or viewBox) to do so.  This improves the rendering in general, and  in particular lets the PDF rendering show the full image, which was not  always the case when viewBox was missing for a large image.
- Added Python 3.7 to the tox test settings.

## [2.17.0] - 2019-01-21

- Added rudimentary support for ipr="none", in order to not shut out other standards bodies, such as the OpenID Foundation, that uses xml2rfc to produce documents.  Idnits will make sure documents produced with ipr="none" are not used in IETF submissions.
- Updated docker/* files with additional packages, tweaks to permit docker builds to discard cache, and other minor changes.
- Changed the url used to set xml:base in cached reference files to use  the actual retrieval url, rather than the initially requested url, in order  to correctly reflect redirects.  Also added some related messages when  running with --verbose.
- Added a comment in v2v3 converted xml output giving the converter version, and made sure the root element always has a declaration of the XInclude namespace to make later insertion of `<xi:include/>` statements easy.

## [2.16.3] - 2019-01-13

This release fixes a number of bugs in the v3 output formats, found thanks to review and testing done by the RFC Production Center (Alice, Sandy, and Megan).  Thanks!

- Added CSS styling to avoid page breaks inside dl entries (which implies not breaking a reference entry) and inside author address entries.  Also added styling to avoid line breaks in reference URLs.  This fixes a number of line- and page-break issues in the PDF output.
- When rendering a reference, don't run seriesInfo name and value together; separate with a space.
- Added a missing colon to the Figure and Table captions when caption text has been specified.
- Provided boilerplate templates as xml instead of as a text/plain blob internally, in order to make boilerplate URLs render as links in formats that supports it.
- Added missing section numbers in the HTML output of reference sections.
- Removed stripping of leading and trailing whitespace from `<sourcecode>` content.
- Added 'RFC NNNN: ' to the HTML document title for RFCs.
- Added code to prevent line-breaking of reference tags containing dash in the text format.
- Fixed rendering of author names in authors' addresses section when the `<address>` element does not have a `<postal>` child element.
- Fixed an issue with missing whitespace in text rendering of references  with reference tags of length 9.
- Fixed an issue where TLP version 4.0 was used instead of 5.0 used by preptool when inserting boilerplate text, causing the use of http:// instead of https:// URLs in modern document boilerplate.
- Silenced some warnings that could occur during xml2rfc startup, triggered by pdf lib imports when the available external libs have old versions.
- Fixed a bug in preptool.check_attribute_values(), and added code to strip leading and trailing whitespace for attribute values where whitespace is not meaningful.  This will cause accidentally included leading and trailing whitespace to be accepted (with a comment during the preptool phase).

## [2.16.2] - 2019-01-08

- Added exception handling for a command in setup.py that may fail in  some circumstances.

## [2.16.1] - 2019-01-08

This is a minor release. prompted mostly by a change in the BaseV3Writer class in order to better be able to override logging when subclassing it.

- Updated docker files.
- Refactored some logging functionality.
- Tweaked BaseV3Writer to make it possible to override all error output.
- Added a `__str__` method for an exception class, and fixed an error case  return value.
- Tweaked the mkrelease script

## [2.16.0] - 2018-12-22

This release provides support for generation of xml2rfc PDF output. However, a default pip install will only install the xml2rfc module itself; additional installation work is needed to enable PDF generation:

In order to generate PDFs, xml2rfc uses the WeasyPrint module, which depends on external libraries that must be installed as native packages on your platform, separately from the xml2rfc install.

First, install the Cairo, Pango, and GDK-PixBuf libs on your system. See installation instructions on the WeasyPrint Docs: https://weasyprint.readthedocs.io/en/stable/install.html

(Python 3 is not needed if your system Python is 2.7, though).

(On some OS X systems with System Integrity Protection active, you may need to create a symlink from your home directory to the library installation directory (often /opt/local/lib): `ln -s /opt/local/lib ~/lib`

in order for weasyprint to find the installed cairo and pango libraries. Whether this is needed or not depends on whether you used macports or homebrew to install cairo and pango, and the homebrew / macport version.)

Next, install the pycairo and weasyprint python modules using pip. Depending on your system, you may need to use 'sudo' or install in user-specific directories, using the --user switch.  On OS X in particular, you may also need to install a newer version of setuptools using --user switch before weasyprint can be installed.  If you install with the --user switch, you may also need to set PYTHONPATH in your shell environment, e.g., `PYTHONPATH=/Users/username/Library/Python/2.7/lib/python/site-packages` for Python 2.7.

The basic pip command (modify as needed according to the text above) is: `pip install 'pycairo>=1.18' 'weasyprint<=0.42.3'`

With these installed and available to xml2rfc, the --pdf switch will be enabled.

For correct PDF output, you also need to install the Noto font set. Download the full set from: https://noto-website-2.storage.googleapis.com/pkgs/Noto-unhinted.zip, and install as appropriate for your platform.

## [2.15.5] - 2018-12-21

- Added code to look for input marked as v3, and process that as v3  without requiring an explicit --v3 switch.  This should make it easier to  transition to v3 draft submissions.
- Fixed a bug related to cref handling.  Fixes issue [#389](https://github.com/ietf-tools/xml2rfc/issues/389).
- Ensured propagation of options to parser and url resolver, and improved  the error message for externals without .xml extension that give 404.
- Fixed an include without explicit extension in a test input file, in  order to work with the stricter v3 formatter include processing.

## [2.15.4] - 2018-12-18

- Tweaked the mkrelease script to prevent inclusion of temporary editor  files.
- Fixed a problem with string vs byte for reference file output.
- Added a limitation on the intervaltree requirements to avoid a broken version.

## [2.15.3] - 2018-12-05

This release fixes some issues found when running the html renderer over a corpus of all drafts submitted with xml format over the last 30 days, and an installation issue.

- Handled utf-8 reloading in setup.py under py27 without using six, which  might be unavailable before the installation completes.
- Always convert python lists to comma-separated strings before calling  on i18n address validation.
- Added some guards to prevent operations on None.

## [2.15.2] - 2018-12-02

- Added a v3 version of the expansion renderer, to handle xi:include  processing and prettify the output for v3 xml files.
- Fixed an issue with blank lines around the text rendering of artwork.
- Introduced new pretty-print code which provide better indentation consistency between beginning and end tags.
- Added a html() method to the html writer, for library model use, and did some minor refactoring.
- Added a missing file.

## [2.15.1] - 2018-12-01

- Added downcoding of punctuation followed by wrapping of other non-ascii  text in `<u>` for the v2v3 converter.
- Added BaseV3Writer methods: downcode() and downcode_punctuation(),  get_text_tags() and get_inline_tags() (works this out from the schema), and  added a list of deprecated elements.
- Fixed a typo in an error message.  Added asciification of smart quotes  and other punctuation for the v3 renderers  to match that done for v2.   Some class refactoring.
- Changed the workaround for non-ascii metadata in setup.py to only be  active under py2.  Fixes a problem with setup.py under python 3.x
- Reverted [00f9a47](https://github.com/ietf-tools/xml2rfc/commit/00f9a47d93b380f2c402536c039bc3ff4cf671f9), which permitted non-ascii characters inside artwork for the v2 renderers, but broke when trying to write to file without utf-8 encoding.  Fixes issue [#387](https://github.com/ietf-tools/xml2rfc/issues/387).

## [2.15.0] - 2018-11-30

- Added support for a new element `<u>`, to be used to insert unicode in protocol descriptions.

In xml2rfc vocabulary version 3, the elements `<author>`, `<organisation>`, `<street>`, `<city>`, `<region>`, `<code>`, `<country>`, `<postalLine>`, `<email>`, and `<seriesInfo>` may contain non-ascii characters for the purpose of rendering author names, addresses, and reference titles correctly.  They also have an additional "ascii" attribute for the purpose of proper rendering in ascii-only media.
In order to insert Unicode characters in any other context, xml2rfc v3 formatters now require that the Unicode string be enclosed within an `<u>` element.  The element will be expanded inline based on the value of a "format" attribute.  This provides a generalized means of generating the 6 methods of Unicode renderings listed in RFC7997, Section 3.4 (http://rfc-editor.org/rfc/rfc7997.pdf), and also several others found in for instance the RFC Format Tools example rendering of RFC 7700, at  https://rfc-format.github.io/draft-iab-rfc-css-bis/sample2-v2.html.
The "format" attribute accepts either a simplified format specification, or a full format string with placeholders for the various possible unicode expansions.
The simplified format consists of dash-separated keywords, where each keyword represents a possible expansion of the unicode character or string; use for example ``<u "lit-num-name">foo</u>`` to expand the text to its literal value, code point values, and code point names.
A combination of up to 3 of the following keywords may be used, separated by dashes: "num", "lit", "name", "ascii", "char".  The keywords are expanded as follows and combined, with the second and third enclosed in parentheses (if present):

- "num": The numeric value(s) of the element text, in `U+1234` notation
- "name": The unicode name(s) of the element text
- "lit": The literal element text, enclosed in quotes
- "char": The literal element text, without quotes
- "ascii": The provided ASCII value

In order to ensure that no specification mistakes can result for rendering methods that cannot render all unicode code points, "num" must always be part of the specified format.
The default value of the "format" attribute is "lit-name-num". For instance: `format="lit-name-num"`: Temperature changes in the Temperature Control Protocol are indicated by the character "Δ" (GREEK CAPITAL LETTER DELTA, U+0394).
If the `<u>` element encloses a Unicode string, rather than a single code point, the rendering reflects this.  The element `<u format="num-lit">ᏚᎢᎵᎬᎢᎬᏒ</u>` will be expanded to '`U+13DA U+13A2 U+13B5 U+13AC U+13A2 U+13AC U+13D2 ("ᏚᎢᎵᎬᎢᎬᏒ")`'.
In order to provide for cases where the simplified format above is insufficient, without relinquishing the requirement that the number of a code point always must be rendered, the "format" attribute can also accept a full format string.  This format uses placeholders which consist of any of the key words above enclosed in in curly braces; outside of this, any ascii text is permissible.  For example: The `<u format="{lit} character ({num})">Δ</u>.` will be rendered as: `The "Δ" character (U+0394).`

- Added support for v3xml2rfc PIs that silence notices and warnings.  For instance, adding `<?v3xml2rfc silence="The document date .* is more than 3 days" ?>` in front of a `<date>` element with an old date will suppress the warning message about an outdated date.  If the value of the silence attribute matches the start of a notice or warning message, as a string or as a regex, the message is suppressed.
- Some warnings have been downgraded to notices, and can be suppressed with a `--quiet` switch.
- Added header and footer information for the tentative support for the  W3C Paged Media Module described in RFC 7992, Section 6.4.
- Added support for older versions of pycountry.
- Added more information to the `--version` display when used with `--verbose`.

## [2.14.1] - 2018-11-23

- The v3 attribute xml:base of `<reference>` is not compatible with the v2 DTD.  Added xml:base to the DTD for `<reference>` in order to be able to work from the same reference cache for v2 and v3, without backing out the issue [#381](https://github.com/ietf-tools/xml2rfc/issues/381) resolution.

## [2.14.0] - 2018-11-23

- Added missing '(if approved)' annotations for obsoleted and updated lines in v3 html rendering of drafts.
- Fixed the case of appendix section numbers in v3 html output.
- Removed rfc2629 dtd validation for input files with `<rfc version="3">` set.
- Tweaked the lxml resolver callback to not accept xi:include names lacking an '.xml' extension under v3.  Added setting of xml:base before caching xi:include content, in order to not loose the origin.  Fixes issue [#381](https://github.com/ietf-tools/xml2rfc/issues/381).
- Sorted the entries in requirements.txt lexicographically.
- Added a check for duplicate id attribute values after each include of svg content into generated html, as duplicates may cause display problems with some browsers.
- Added back the ability to place `<iref>` elements in a location where they  will translate to invalid HTML.  Avoided invalid HTML by pushing the span  up one level, as a previous sibling, when needed.  Fixes issue [#378](https://github.com/ietf-tools/xml2rfc/issues/378).

## [2.13.1] - 2018-11-17

- Filled in missing rendering values for the case when cref is being  rendered in inline context in the v3 text renderer.  Fixes issue [#380](https://github.com/ietf-tools/xml2rfc/issues/380).
- Under python 3.6, dictionary keys() return a set-like object that  cannot be indexed.  Convert to list for our purposes.  Fixes issue [#379](https://github.com/ietf-tools/xml2rfc/issues/379)
- Remove the 'alt' attribute on `<artwork>` with SVG after setting `<desc>`.
- Fixed an issue with missing svg namespace when inserting `<desc>`.

## [2.13.0] - 2018-11-17

This release provides an number of improvements.  Rendering of all v3 elements should now be in place for the v3 text and html formatters, and the renderers have been updated to follow the issue resolutions so far. A bug in the generation of boilerplate for BCPs has been fixed.  Feedback on unexpected postal address data has been improved, as has feedback on unexpected combinations of stream, category, and consensus settings.

Details from the commit log:

- In the html formatter:
  - Added indentation support for `<dl>` to the v3 html renderer.  
  - Fixed a bug in the display of author names in the author addresses   section when no postal information is given.  
  - Improved `<eref>` rendering for the case when no eref text is provided.  
  - Corrected the anchor placement for slugified names of figures and   tables.  
  - Added support for `<referencegroup>`.  
  - Added a missing CSS class for `<seriesInfo>` rendering.  
  - Added support for right and center alignment of tables.

- In the text formatter:
  - Added v3 text formatter support for rendering of blockquote and cref.  
  - Minor other tweaks.

- In the preptool: 
  - Added support for `<referencegroup>` elements.  
  - Added support for the `<rfc>` version attribute.  
  - Fixed a string formatting bug.  
  - Added attribute validity checking for integer-valued attributes.  
  - Removed the forced inclusion of day for RFC publication dates, reverting   to permitting publication with only year and month.
  - Added more sophisticated checking and setting of consensus, based on   what is valid for the given stream and category.  
  - Refined the handling when given input that already contains boilerplate,   authors addresses and index.

- In the v2v3 converter:
  - Added setting of the `<rfc>` version attribute.
  - Removed dubious elimination of `<format>` elements pointing to alternative   reference URLs.
  - Fixed a couple of instances of buggy error reporting.

- Changed util.postal.get_normalized_address() to return a filled-in adr  structure even if no country could be identified, for more consistent code  in other places.

- In the Relax NG schema files:
  - Changed the v3 schema default value for `<dl>` newline so that the effect    is the same as for the old 'hanging' default value.
  - Added a 'derivedAnchor' attribute for `<referencegroup>`, matching that of   `<reference>`.

- In the CSS style sheet:
  - Changed the CSS class for Reference Section definition lists from   'reference' to 'references'.  
  - Added styling for table alignment and   applied the same styling for table labels as for figure labels.

- Added bcp14, em, iref, strong, sub, and sup to the permitted elements  in `<name>`.
- Fixed some issues with the error messages for combinations of stream,  category, and consensus.
- Added code to honour the "display" attribute of `<cref>`.
- Added a preptool action to check the `<rfc>` attributes submissionType  (i.e., stream), category, and consensus for validity.  Invalid combinations  are called out, and warnings are issued about setting missing settings to  default values.
- With v2 formatters, treat consensus for BCPs the same way as STD  documents, 
- Refactored some logging and address functionality, improved address warnings and other address-related tweaks.

## [2.12.3] - 2018-10-30

This release fixes a schema issue.

## [2.12.2] - 2018-10-30

This bugfix release corrects a default setting for --v3 modes so they do not try to apply DTD validation.  It refines the internationalised address layout, and does re-factoring in a number of places.  Non-Latin author names and addresses in Right-To-Left scripts are now properly aligned in the Authors' Addresses section.  It also fixes an issue where needLines PI settings were ineffectual under python2.7, and caused exceptions under python3.5 and higher.  

Excerpted from the commit log:

- Changed the HTML renderer to properly place organisation in i18n  address layout, and added back the role indication that was lost in  previous i18n address layout work.
- Updated run.py to apply the --no-dtd option to all --v3 formats, fixing  an issue in 2.12.1 with running --html --v3 on a converted --v2v3 file.
- Fixed an issue with needLines when set to a string value.
- Added simple bidi-support to author addresses, in order to have  addresses in right-to-left scripts align properly.  Fixed a bug in the  handling of non-Latin address information.
- Tweaked the vcard width to avoid having author names and addresses in  right-to-left script end up far to the right, away from the ASCII  information.

## [2.12.1] - 2018-10-29

This release provides some additional polish over release 2.12.0, and also a few bugfixes.  The primary focus for this release has been HTML compliance based on the W3C validator at https://validator.w3.org/.  Valid HTML 5 is now generated for all documents used during testing.  From the commit log:

- Fixed a number of issues with the v3 html renderer, to improve the  generated html.  Many of these were caught by the W3C validator at validator.w3.org:
  - removed the `<meta http-equiv="Content-Type" ...>` element, as it should   not appear when there is a `<meta charset=...>` element
  - removed type="text/javascript" from a `<script>` element (superfluous)
  - removed a number of extraneous wrapping divs with identical id attributes
  - corrected the generation of `<dt>``<dd>` items for xml `<ol>` entries with   percentage list types
  - removed some attributes on html entries for xml `<ol>` lists that had   incorrectly been transferred from the xml
  - corrected the block element generated for `<references>` to `<section>`
  - fixed an issue where `<xref>` in `<name>` would generate nested html `<a>`   elements

- Also fixed some other issue:
  - added a newline tail for block elements, to improve readability
  - added missing space between author name and (editor)
  - fixed the renderer for `<note>` to generate html `<section>` elements with   the right class attribute
  - refactored the generation of enclosing divs to hold id="$anchor" to be   more consistent, with less code
  - modified the rendering of `<xref>` with text content to more closely match   the historic rendering

- Updated python-version specific test masters.  Tox runs for py27, py34, py35, and py36 aren now all clean.
- Changed some invalid `<link>` rel= values to valid ones in the preptool
- Tweaked the list of html block-level elements we use to control `<div>` wrapping
- Disallowed `<iref>` as a direct child of `<table>` in the schema, as it results in invalid html with the rendering specified in RFC 7992.

## [2.12.0] - 2018-10-28

This release introduces the vocabulary v3 html formatter.  In order to invoke this formatter, use the regular --html switch for html output, and add the --v3 switch to specify the v3 html formatter.

In v3 html formatter mode, xml2rfc accepts any valid xml2rfc input file, but since the actual formatter only understands the XML elements and attributes which have not been deprecated by RFC7991, it first applies the xml2rfc v2v3 converter in order to transform any deprecated markup to the elements and attributes it understands, and then applies the preptool in order to normalize the input before it starts rendering.

This is the first release of the v3 html formatter.  It is quite feature complete, but has been tested only on a limited number of documents, so expect that there could be some rough edges.

In building the html v3 formatter, a number of rough edges were also discovered in the schema, RFC 7991; html format output, RFC 7992; and preptool specification, RFC 7998.  The modifications applied in the code are described in draft-levkowetz-xml2rfc-v3-implementation-notes-05. 

## [2.11.1] - 2018-10-11

- Changed linebreaking for URLs in boilerplate and references to the old  behaviour (don't break), added stream abbreviations according to RFC5741,  and changed EMail: to Email: in RFC mode.
- Added the align attribute for element `<table>` to the schema.
- Changed the v2v3 converter handling of the table align attribute, and  fixed an issue with lost whitespace after `<spanx>`.
- Added STD to the seriesInfo sort order list.
- Added an error message for `<date>` month content that is neither a month  name or a number.

## [2.11.0] - 2018-10-07

This release is a result of the issue discussions on xml2rfc-dev, and attempt to follow the discussion and projected resolution of issues #36-[#40](https://github.com/ietf-tools/xml2rfc/issues/40). This results in a number of incompatibilities with previous releases, with respect to the v3 tools, as expected.  The v2 tools are unaffected. Details:

- Changed the default table alignment to 'center', in order to match v2.
- Changed the `<dl>` 'hanging' attribute name to 'newline', based on the  discussion of issue #38, in the schema, v2v3 converter and text formatter.
- Added an attribute 'indent' to `<dl>` in the schema, according to the  discussion of issue [#39](https://github.com/ietf-tools/xml2rfc/issues/39).  Added v2v3 and text support for the same.
- Added markers='true' in the v2v3 converter for sourcecode with markers, and tweaked render_sourcecode() to honour the 'markers' setting.
- Removed the disallowed align attribute on sourcecode.
- Removed `<br>` from the schema, according to the resolution of issue [#37](https://github.com/ietf-tools/xml2rfc/issues/37).
- Tweaked the handling of the document title to only reflow if needed,  with some refactoring.
- Corrected the handling of the align attribute on `<artwork>` and `<figure>`.
- Changed `<prepTime>` to hold an RFC 3339 timestamp with seconds  resolution.
- Fixed a couple of issues with v2v3 conversion warnings, and added  source line information for all elements created during conversion.
- Fixed a buglet in sourcecode rendering.
- Added a warning about lxml versions that lack validation error xpath  information, and tweaked the warn() method.

## [2.10.3] - 2018-09-22

This bugfix release works around a problem with lxml versions before 3.8.0, and brings some other fixes and tweaks:

- Tweaked validation output to not break if validation error log elements lack xpath information. Fixes issue [#376](https://github.com/ietf-tools/xml2rfc/issues/376).  (lxml<3.8.0 does not provide the xpath of the offending element in error.path).
- Fixed a couple of issues with v2v3 conversion warnings, and added  element sourceline information for all elements created during conversion.
- Fixed a buglet in sourcecode rendering.
- Added a warning about lxml versions that lack validation error xpath  information, and tweaked the warn() method.
- Tweaked the rendering of `<eref>`.
- Added `<blockquote>` to the list of block level elements in isblock().
- Added some values to xml2rfc.base.default_options, necessary when using  xml2rfc as a library module (i.e., not getting options from run.py through  command-line invocation).
- Added attribute markers="true"|"false" to `<sourcecode>` and changed the v3 text formatter to only output code markers if `<sourcecode>` has attribute markers set to true.

## [2.10.2] - 2018-09-19

- Added a full listing of validation errors found, rather than just the first, when running v3 validation on an (possibly v2v3 converted) input file in preptool.  Also improved the error messages by providing the xpath to the offending element.
- Added normalization of RFC 2119 phrases before checking for validity, and updated tests files to include a `<bcp14>` test.
- Fixed several places where unexpected input could cause exceptions.   Also turned the invalid input document warning into an error.  Fixes issue  [#375](https://github.com/ietf-tools/xml2rfc/issues/375).
- Preserved the element tail when rendering `<bcp14>`.  Fixes issue [#374](https://github.com/ietf-tools/xml2rfc/issues/374).
- Fixed an issue where an empty `<references/>` section could cause an  exception in the v2 text formatter.

## [2.10.1] - 2018-09-18

This is primarily a bugfix release, to handle issues people have reported with the new vocabulary v3 text formatter:

- Fixed an issue where the v2 text formatter could blow up for some v3 documents, rather than exit with a message.
- Fixed a problem in the v2v3 converter that could cause an Internet-Draft `<seriesInfo>` element to be inserted even if one was already present.
- Tweaked the `<seriesInfo>` insertion code slightly, and expanded an error message slightly.
- Fixed a couple of places where bad input could cause exceptions.  Fixes  issue [#366](https://github.com/ietf-tools/xml2rfc/issues/366).
- Fixed a case where max() could be given an empty sequence.
- Tweaked the handling of `<ul>` with structured `<li>` content.  Fixes issue  [#365](https://github.com/ietf-tools/xml2rfc/issues/365).
- Improved the handling of `<br>`.
- Added render_blockquote().  This fixes issue [#359](https://github.com/ietf-tools/xml2rfc/issues/359).
- Fixed a problem in the plaintext formatter where table cells were not  filled in if the table was wider than the available width.  Also added  support for formatted table cell content.
- Added a check in preptool for `<keyword>` elements containing multiple  keywords.  Fixes issue [#353](https://github.com/ietf-tools/xml2rfc/issues/353).
- Moved the reading of input files to avoid multiple reads.  Fixes issue  [#352](https://github.com/ietf-tools/xml2rfc/issues/352).
- Added a renderer for `<bcp14>` elements.
- Added error messages for empty artwork files.  Tweaked the error  message for missing artwork text.  Addresses issue [#370](https://github.com/ietf-tools/xml2rfc/issues/370)
- Forced no_dtd when running v2v3 to avoid complaints when converting an  already converted file, and also with the v3 text formatter.
- Added a try/except around xinclude in order to provide error message   without traceback on missing include files.
- Removed an assert that prevented rendering of document top when some  elements are so long that the line width will be more than 72 characters.   Added support for `<note>` with `<name>`.  Added `<xref>` format default for  included references.  Added a warning for `<xref>`s without 'pn' attribute  (which can happen if the `<xref>` is pointing at an element for which pn is  not generated (this is probably an error in RFC 7998).  Fixes issue [#346](https://github.com/ietf-tools/xml2rfc/issues/346)
- Tweaked the preptool to handle removeInRFC='true' elements that lacks `<t>`  children.
- Added xml2rfc-dev@ietf.org to the release notification addresses.

## [2.10.0] - 2018-07-12

This release introduces the vocabulary v3 text formatter.  In order to invoke this formatter, use the regular --text switch for text output, and add the --v3 switch to specify the v3 text formatter.

Xml2rfc in v3 text formatter mode accepts any valid xml2rfc input file, but since the actual formatter only understands the XML elements and attributes which have not been deprecated by RFC7991, it first applies the xml2rfc v2v3 converter in order to transform any deprecated markup to the elements and attributes it understands, and then applies the preptool in order to normalize the input before it starts rendering.

This is the first release of the v3 text formatter, and there are some known rough edges and deficiencies:

- The current table output renders all table borders.  This differs from the v2 formatter, and will be remedied in a later release.  The reason for doing the first release with this rendering of tables is that the table layout options have changed substantially with the possibility of using rowspans, and the table layout code is much more complex than for v2 as a consequence.  With all table borders visible, the initial testing of the layout code has been easier than if horizontal borders were not rendered.
- The statement of work for the text formatter coding does not include paginated output, and as a consequence the Table of Contents is much less informative than it would be if it was able to show the page for each ToC entry.
- The xml2rfc v3 vocabulary (RFC 7991) does not provide 'align' attributes for tables, which means that the ability to center and right-align tables is lost.  All tables are left-aligned. (Alignment of text within each cell is still supported, though.)
- The index generation (using `<iref>` elements) has some known issues, which will also be fixed in a subsequent release.

The v3 schema used in this release differs from the schema specified in RFC7991 in some respects.  A separate document will be published with details about the changes: draft-levkowetz-xml2rfc-v3-implementation-notes. The issues leading to the changes will also be entered in the document issue trackers and sent to the xml2rfc-dev mailing list for discussion.

Feedback on the v3 text formatter will be appreciated.  Please send feedback to xml2rfc-dev@ietf.org or henrik@levkowetz.com.

## [2.9.9] - 2018-06-25

- Applied patch from scott@kitterman.com to let run.py run under python  3.  Fixes issue [#345](https://github.com/ietf-tools/xml2rfc/issues/345).
- Removed cc:codesprints@ietf.org from xml2rfc notifications.

## [2.9.8] - 2018-06-17

- Fixed a problem with release 2.9.7 when processing private mode input files

## [2.9.7] - 2018-06-15

- Added 2 warnings for problems with the `<rfc/>` docName string.
- Skipped extracting the longest word from empty table columns.

## [2.9.6] - 2018-02-21

- Fixed another `<date>` issue, where a `<date>` without a year would generate a bad date string.

## [2.9.5] - 2018-02-21

- Fixed an issue where a `<date>` without a year attribute would generate a copyright stanza without year.
- Tweaked the --version output to include the program name, to be closer  to common practice.

## [2.9.4] - 2018-02-16

- Fixed a bug in the date output format when no month or numeric month is given in `<date>`.

## [2.9.3] - 2018-02-15

- Changed the way `<date>` defaults are calculated.  Previously, today's date were used to populate missing day if month and year matched, and to populate month if year matched.  However, if today's date lay in an adjoining month, even if it was within days of that month, the day would be set to the first of the given month.  This commit changes that, to use the last day of the month instead of the first of the month, if the month is the previous month to today's date.  This will result in a different derived date than earlier, closer to today's date.  This fixes issue [#337](https://github.com/ietf-tools/xml2rfc/issues/337).
- Fixed a bug in a preptool.py error message.  Reverted a prettyprinting  change which caused inconsistent behaviour between writers.
- Moved normalize_month() to utils, for use in multiple writers.
- Made the makefile less verbose.
- Improved the pretty-printing of v2v3 output.  Fixed a bug in the  attribute_xref_target() handler name that prevented it from being called.
- Removed whitespace normalization from v2v3 writer.
- Moved handling of exempted default attributes in preptool inside  get_attribute_defaults(), for consistency.
- Added an option --liberal to permit re-processing of prepped source  without error exit.  This mode will be needed when we make the preptool  part of the default processing pipeline.  Also removed whitespace  normalization for v2v3, exp, and preptool output, in order to not change  authors' text formatting when not needed.
- Lowered the requirement on six to 1.4.1 in order to make installation easier on some systems with locked system python libs that include six.

## [2.9.2] - 2018-02-09

- Fixed issues with packaging and with execution under python 2.7.   Fixes issue [#342](https://github.com/ietf-tools/xml2rfc/issues/342) and [#343](https://github.com/ietf-tools/xml2rfc/issues/343).

## [2.9.1] - 2018-02-09

- Boilerplate grammar fix, see https://www.rfc-editor.org/errata/eid5248

## [2.9.0] - 2018-02-09

This release introduces preptool functionality, through a --preptool output mode.  With reservation for some points for which issues has been raised, this follows the specification in RFC7998.

The preptool currently takes vocabulary v3 input, and produces prepped output.  When work on the text formatter commences, the idea is that the input xml source will always be run through v2v3 conversion and preptool processing before the output formatting, in order to increase consistency and reduce complexity of the output formatter.

There are also some changes which are not related to the preptool functionality: The tox tests have been changed to add testing under Python 3.6, and removed test runs for Python 3.3.  Although there is no intention of breaking compatibility with Python 3.3, it may happen eventually since there will not be any release testing with that version of Python.

The v2v3 converter in some cases could insert `<seriesInfo>` elements with only a name= attribute, because the required seriesNo= attribute on `<rfc>` was missing.  This has been changed.

In order to work around a debilitating issue with relax-ng validation in libxml2 (time to validate increases exponentially with number of attributes on the root element: https://bugzilla.gnome.org/show_bug.cgi?id=133736) some empty attributes on `<rfc>` are removed during processing; for instance obsoletes="" and updates="".  They don't contribute information, but increase validation time with a factor ~20.

In order to identify the unicode scripts needed to display a document, a module to efficiently identify the scripts related to unicode codepoints has been written.  The 'uniscripts' module which was originally intended to be used for this turned out not to be viable.  The new 'scripts' module can be broken out for separate release as a library module, if desired.

In order to work with vocabulary v3 input, the parser has been slightly modified to not do input validation according to rfc2629.dtd if not appropriate.

## [2.8.5] - 2018-01-21

- Changed a file open under python3 to use the newline= parameter to open() instead of the deprecated 'U' mode (thanks to spf2@kitterman.com for pointing that out).  Also changed the code to avoid a dangling open file handle.

## [2.8.4] - 2018-01-14

- Included test.py and tox.ini in the package MANIFEST in order to make  testing possible during distro packaging.  Fixes issue [#339](https://github.com/ietf-tools/xml2rfc/issues/339).

## [2.8.3] - 2018-01-04

- Changed the python 3 code that reads in an xml file to read as binary,  in order to not run into issues with unicode conversion before we have had  time to look at the encoding attribute of the `<xml/>` element.

## [2.8.2] - 2017-09-23

- Modified the V2v3 conversion writer to work with generic lxml.etree instances.
- Fixed a failure that could occur for hanging style lists without hangText attributes.
- Tweaked mkrelease to work without the old tools control files and tools  feeds being present.

## [2.8.1] - 2017-09-18

This release improves the v2 to v3 conversion of `<artwork/>` elements which contains `<CODE BEGINS>`; these are now converted to `<sourcecode/>` elements.

## [2.8.0] - 2017-09-04

This is a small feature release which changes URLs in boilerplate to use https: instead of http:.  There are also some bugfixes.

- Include notes when doing index processing.  Fixes issue [#335](https://github.com/ietf-tools/xml2rfc/issues/335).
- Include erefs with text equal to the URL in the URIs section.  See  issue [#334](https://github.com/ietf-tools/xml2rfc/issues/334).
- Changed the use of http: to https: in many places.  In the generation  of RFCs, the code uses a switchover date of August 21, 2017 when deciding  whether to insert http: or https: URLs.  In practice, this means that RFCs  with a date of September 2017 or later will get https:.  Also fixed URL  line-breaking prevention to apply to https: URLS.  Fixes issue [#333](https://github.com/ietf-tools/xml2rfc/issues/333).
- In urlkeep(), prevent breaking also for https:, not only http: URLs

## [2.7.0] - 2017-07-01

This introduces the vocabulary v2 to v3 converter, which reads RFC7749-compliant xml input, and writes RFC7991-compliant xml output, converting elements marked as deprecated in RFC7991 to the equivalent new constructs, or removing attributes and elements if no equivalent construct exists.  Use the format switch --v2v3 to request v2v3 conversion.  Use --verbose to have comments added to the converted xml detailing the conversions which have been done.

## [2.6.2] - 2017-06-19

- Refactored the input file reading to accept files with Mac line  endings, using python's Universal Newline support.  This should make  xml2rfc deal correctly with input files following DOS, MAC and Linux  line-ending conventions.

## [2.6.1] - 2017-06-03

- Initialised the widow and orphan limit settings from PIs.  Did some related refactoring.
- Added an option to show the known PIs, and their default values.  Also commented out PIs for which there are no implementations from the internal PI list, and did some refactoring of the option parser setup.
- Changed a number of numeric constants related to page breaking which occurred inline in the code, so that appropriate settings on the writer are used instead: self.page_end_blank_lines, self.orphan_limit, self.widow_limit.  Some refactoring.
- Restored support for the quiet= argument to writers, as this is used by other tools that invoke writers, and backwards compatibility is desired.
- Added a mkrelease script.
- Limited the changelog on the pypi page to the 2 latest releases.

## [2.6.0] - 2017-05-31

- The implementation of the 'authorship' PI in the original TCL tool would suppress the Author's Address section when set to "no", while in the current implementation it removed author information on the first page. Changed to the original semantics.  Also author organisation handling on the first page changed to use the submissionType setting to trigger the behaviour described in issue [#311](https://github.com/ietf-tools/xml2rfc/issues/311).  Fixes issue [#311](https://github.com/ietf-tools/xml2rfc/issues/311) without overlaying this on the 'authorship' PI.
- Added a check for the 'needLines' PI within lists.
- Fixed a bug in the code for the 'sectionorphans' PI. Added a PI 'tocpagebreak' to force a page break before the ToC.  This, together with the fix for [#311](https://github.com/ietf-tools/xml2rfc/issues/311) and needLines within lists, lets xml2rfc produce rfc7754.txt correctly from suitable xml without postprocessing.
- Tweaked the eref output in text mode to avoid generating extraneous  space characters.  Fixes issue [#329](https://github.com/ietf-tools/xml2rfc/issues/329).
- Changed to use the emph character in spanex so that the same thing happens in both html and text if an unknown attribute is given.  Fixes issue [#297](https://github.com/ietf-tools/xml2rfc/issues/297)"
- Added code to emit sections in two sections, numbered and un-numbered, separately.  Then emit the numbered appendixes, the index, the unnumbered appendixes, cref items, authors at the end of the document.  Fixes issue [#310](https://github.com/ietf-tools/xml2rfc/issues/310).
- If you have an xref or similar element in an annotation in a reference, any text that follows the xref is absent from the output HTML file.  Text files emit correctly.  Fixed the html generation.
- The HTML rendering for `<xref>` elements were inconsistent with the text rendering.  Fixed this by doing something completely different than is called for in the bug report: We follow the layout of what the V3 HTML document says to do.  This means that we use the child text of the xref when it exists to the exclusion of any generated text.  When the child text does not exist then we use the synthesized text string as the text for the anchor element.  In all cases the anchor element is emitted with an href of the target.  Fixes issue [#293](https://github.com/ietf-tools/xml2rfc/issues/293).
- Added true and false as legal values for the attribute numbered on a section.xml Fixes issue [#313](https://github.com/ietf-tools/xml2rfc/issues/313)
- Eliminated redundant PI parsing, now that each element carries the local  PI settings.
- Fixed a problem where if there are no authors, references in HTML are badly formatted.  Fixes issue [#307](https://github.com/ietf-tools/xml2rfc/issues/307) and [#309](https://github.com/ietf-tools/xml2rfc/issues/309).
- things work under python 3.x: Don't split special terms with embedded forward slash on the slash character.  Fixes issue [#288](https://github.com/ietf-tools/xml2rfc/issues/288).  Also added code to deal with an extra tab in the middle of a sentence.
- Changed the handling of PIs such that each element in the parsed xml  tree holds the PI state at that point of the xml document.  This provides  the ability to use different PI settings at different points in the  document.  This only makes sense for some PIs, though.  The following PIs  will now be honoured if changed inside the document, in order to provide  more flexibility: 'multiple-initials', 'artworkdelimiter', 'compact',  'subcompact', 'text-list-symbols', 'colonspace'.
- Honour the way double initials are given in the XML, with or without  interleaved spaces.  See issue [#303](https://github.com/ietf-tools/xml2rfc/issues/303), which says of multiple initials '...  Expectation was that it would exactly match the initials attribute in the  XML'
- Enabled the multiple-initial PI again.  The code now also looks for the PI as the first element of the author element, to apply for that author entry only, with a default of 'no'.
- Added handling for absent author initials for the html generator.
- This commit provides support for multiple author initials.  Fixes issue [#303](https://github.com/ietf-tools/xml2rfc/issues/303).  Also fixes the issue of extra commas showing up when there are no initials, just a surname.
- Changet to emit html not xhtml.  Addresses issues [#263](https://github.com/ietf-tools/xml2rfc/issues/263) and [#279](https://github.com/ietf-tools/xml2rfc/issues/279).
- Updated additional test masters needed to make the tox tests pass, and changed the html encoding and decoding to use utf-8, to work with the unicode and utf-8 tests.
- Removed python 2.6 from tox texting (a previous commit added python 3.5).
- Don't let the value of 'title' be None, make it an empty string if that  happens.  Fixes issue [#328](https://github.com/ietf-tools/xml2rfc/issues/328)
- Someone might want to set hangIndent to zero.  Test the value against None explicitly to permit this to succeed.
- Added an --utf8 switch to xml2rfc.  In nroff mode, the output will  contain utf-8 characters, not `\[u8FD9]` escapes; use groff with the -Kutf8  switch to process the resulting nroff.
- Removed all references to xml.resource.org; it is not useful for  fallback purposes any more.

## [2.5.2] - 2016-10-07

This is a maintenance release.  It changes the RFC boilerplate for stream information to refer to RFC 7841 instead of RFC 5741, for RFCs dated July 2016 or later.

## [2.5.1] - 2015-10-19

This is a bugfix maintenance release.

- Handled a situation where xml2rfc could crash if no source file name was available.

From tonyh@att.com:
- Modified some tests to match Jim's recent changes

From ietf@augustcellars.com:
- Add the valid versions of the text files for the unicode test file.
- Fixes URIs which didn't add up.  This includes correcting code to deal with the difference in unicode strings on Python 2.7 vs Python 3.4.  Build the abstract when doing the indexing pass so that any references in it will be included both times through Add the start of a unicode test file. Fixes issue [#290](https://github.com/ietf-tools/xml2rfc/issues/290)
- Fixed an xref generation failure: Check to see if there is text, and do the right thing if there isn't.  The HTML version seems to be producing adequate results.  It does an `<a>` element around an empty piece of text. That is what was asked for.  Fixes issue [#226](https://github.com/ietf-tools/xml2rfc/issues/226).
- Fixed an exception on out-of-date dates.  1.  We make it an error instead of a warning to have an incomplete and not this year date.  2.  We catch the type exception and continue.  Fixes issue [#285](https://github.com/ietf-tools/xml2rfc/issues/285)
- Replaced the space between the series info and the series value with a non-breaking space.  Changed any slashes in the series value so that there is a non-breaking zero width space following it.  If a URL is placed in the series value, then it is still not going to do correct breaking on this.  However this is not something that people should do.  Fixes issue [#296](https://github.com/ietf-tools/xml2rfc/issues/296)

## [2.5.0] - 2015-05-18

This release uses different installation settings than previous releases, which should make installation under MS Window easier.  It also contains a few bugfixes.  For details, see below:

- Applied patches from julian.reschke@gmx.de: Render `<eref target='uri'>`  without text as inline `<uri>`.  Fixes issue [#234](https://github.com/ietf-tools/xml2rfc/issues/234).
- Changed setup.py to use the entry_points option instead of the scripts  option, in order to work better on mswin systems.  Fixes issue [#291](https://github.com/ietf-tools/xml2rfc/issues/291).
- Made the reference sorting when using symrefs=yes and sortrefs=yes  case-insensitive by mapping the reference keys to lowercase.  This is  correct for ASCII keys but not necessarily for non-ASCII keys, depending on  locale.  Fixes issue [#295](https://github.com/ietf-tools/xml2rfc/issues/295) (for now).
- Changed the path through reference resolution so that too old cached references will be updated in the same block where it was discovered that they were too old, rather than (erroneously) relying on this happening on a later attempt.
- Set things up so that the processing instruction dictionary isn't shared between the index-building and the document-building runs, which they were earlier, with the result that pi values could be different at the start of the document-building than they should have been.  Fixes issue [#292](https://github.com/ietf-tools/xml2rfc/issues/292).

## [2.4.12] - 2015-04-19

- Modified the nroff table output for PI subcompact=yes so as to produce  a list, rather than a paragraph of run-together list entries.  Fixes issue  [#287](https://github.com/ietf-tools/xml2rfc/issues/287).
- Fixed a bug where a local variable would not always be set.
- Fixed the bug in 2.4.10 where xml2rfc wouldn't fetch references.
- Changed the cachetest so it exposes the bug found in 2.4.10 where  reference resolution would fail without even attempting network access.

## [2.4.11] - 2015-04-10

- Corrected when the deprecation message about using -f and --file is emitted.
- Changed where warnings about missing cache entry and --no-network is emitted, in order to not emit warnings too early.

## [2.4.10] - 2015-03-08

- Catch bad arguments to the 'needlines' processing instruction.  Fixes  issue [#282](https://github.com/ietf-tools/xml2rfc/issues/282).
- Make sure we don't ask textwrap to wrap text with within a width of  zero.  Fixes issue [#277](https://github.com/ietf-tools/xml2rfc/issues/277).
- Reorganized the presentation of options, and corrected some of the help  strings.  Marked the -f, --filename options in use for output filename as  deprecated.
- Added a switch --no-network to turn off all attempts to use the network  to resolve references.  When using this, processing will fail if the  references required by the source file aren't available in the file cache.   Also added code to refresh cached content if it's older than 14 days.   Modified some tests to suit.  This closes issues [#275](https://github.com/ietf-tools/xml2rfc/issues/275) and [#284](https://github.com/ietf-tools/xml2rfc/issues/284).
- Fixed a bug where leading whitespace in title attributes weren't  handled properly.  Fixes issue [#274](https://github.com/ietf-tools/xml2rfc/issues/274).
- Tweaked tox.ini to work around an issue with the py27 and py33  environments after upgrading to 2.7.8 and 3.3.5, respectively.
- Added the attribute quote-title (default: true) to schema and writers,  and updated the tests accordingly.  Fixes issue [#283](https://github.com/ietf-tools/xml2rfc/issues/283).

## [2.4.9] - 2015-02-28

- Applied a patch from Martin Thompson to render the ToC with sublevel  indentation, instead of as a flat list, for html output, and updated the  html regression test masters to match.
- Added a --no-headers switch, valid only for paginated text.   Specifying this omits the output of headers and footers, but retains form  feed and top-of-page line padding.
- Consistently use utf-8 as output encoding.  As long as all content is  forced to be ascii, this doesn't change anything; if we permit non-ascii  content, this ensures it's utf-8 encoded.
- Issue a warning for input containing tab characters, and expand to 8,  not 4 characters.  Fixes issue [#276](https://github.com/ietf-tools/xml2rfc/issues/276).
- Added 'i.e.' as a non-sentence-ending string.  Added a test for some  abbreviations, including 'i.e.'.  Fixes issue [#115](https://github.com/ietf-tools/xml2rfc/issues/115)
- Changed the handling of rfcedstyle so as to include the Authors'  Addresses section in the TOC.  Fixes issue [#273](https://github.com/ietf-tools/xml2rfc/issues/273).
- Added the ability to create unnumbered sections by using the attribute  numbered="no" on the section element, with the constraints specified in  draft-hoffman-xml2rfc-15.  Fixes issue [#105](https://github.com/ietf-tools/xml2rfc/issues/105).
- In the front page top right-hand matter, don't keep the blank line  between authors and date that would otherwise be used for authors without  affiliation.  Fixes issue [#272](https://github.com/ietf-tools/xml2rfc/issues/272).
- Rewrote the network access code to use the requests package instead of  urllib.  Added cache cleaning to the tox test actions.

## [2.4.8] - 2014-06-05

- From Tony Hansen tonyh@att.com: Added check of line_num+i against len(self.buf) before looking at `self.buf[line_num+i]`.  Resolves issue [#258](https://github.com/ietf-tools/xml2rfc/issues/258).
- Tweaked the word separator regex to handle words containing both '.'  and '-' internally more correctly. Fixes issue [#256](https://github.com/ietf-tools/xml2rfc/issues/256).
- Now only emitting texttable word splitting warning once.
- Changed the sort order of iref index items to not be case sensitive.   Fixes issue [#255](https://github.com/ietf-tools/xml2rfc/issues/255).
- Generally, changed http: URLs to https:, for improved security.

## [2.4.7] - 2014-05-22

This release changes the reference resolution code to try 3 different network hosts when trying to find bibxml reference files on the net, instead of trying only xml.reference.org.  It now tries, in order:
- http://xml2rfc.ietf.org/
- http://xml2rfc.tools.ietf.org/
- http://xml.reference.org/

The next release is expected to change this to using `https:` instead of `http:`, but that change requires both that the resources be available over https, and that there's been explicit testing of access over https, something which is absent from the current test suite.

## [2.4.6] - 2014-05-18

This release addresses the known bugs in xml2rfc which has hindered the RFC-Editor staff from consistently using xml2rfc v2 in production (and a number of other bugs, too).  There still remains a number of open issues, and these will be addressed in upcoming releases.  Here are some details about the issues fixed:

- Tweaked the forward-slash part of the word-separator regex to handle IP  address prefix length indications better.  Related to issue [#252](https://github.com/ietf-tools/xml2rfc/issues/252). Thanks to Brian Carpenter for pointing this aspect out.
- Changed the code so as to not blow up on empty section titles.  Fixes issue [#245](https://github.com/ietf-tools/xml2rfc/issues/245).
- Updated the textwrapping word-separator regex to handle slash-separated words in a similar manner as hyphenated words, to avoid line-breaks that place the forward slash at the start of a line.  Fixes issue [#252](https://github.com/ietf-tools/xml2rfc/issues/252).
- Updated the regex for end-of-sentence exceptions to treat a single alphabetic character followed by period as end-of-sentence, rather than considering it to be the abbreviation of a given name.  This fixes issue [#251](https://github.com/ietf-tools/xml2rfc/issues/251).
- Updated the sorting to not sort the ref keys surrounded by square brackets, instead sorting only the key strings.  Fixes issue [#250](https://github.com/ietf-tools/xml2rfc/issues/250).  
- Added iref handling directly under section, and for figures, both of which were missing previously.  Fixes issue [#249](https://github.com/ietf-tools/xml2rfc/issues/249).  Also modified the format in which iref index page lists are emitted, to combine consecutive page numbers into range indications, and eliminate repeat mentions of the same page number.  Finally, changed things to avoid compressing the double space between index item and page list to a single space.  This should bring the iref output closer to that of xml2rfc v1.
- Removed a static copy of the initial text-list-symbols PI, instead consulting the master PI dictionary every time, in order to catch changes in the text-list-symbols setting.  Fixes issue [#246](https://github.com/ietf-tools/xml2rfc/issues/246)
- Made a warning conditional on not building the indexes, to avoid duplicate error messages.  Fixes issue [#242](https://github.com/ietf-tools/xml2rfc/issues/242).
- Provided the relevant counter when creating _RfcItem objects for Figures, Tables, numbered References, and Crefs, to make it possible to refer to them by xref elements with format='counter'.  Fixes issue [#241](https://github.com/ietf-tools/xml2rfc/issues/241).
- Added wrapping and indentation of long Obsoletes: and Updates: list in the text formats.  Fixes issue [#232](https://github.com/ietf-tools/xml2rfc/issues/232).
- Tweaked the top_rfc test to require proper line wrapping for long Obsoletes: lines; see issue [#232](https://github.com/ietf-tools/xml2rfc/issues/232).
- We're now using a blank string for source when rendering a cref element with no source given, rather failing to concatenate None to a string. Fixes issue [#225](https://github.com/ietf-tools/xml2rfc/issues/225).
- Rewrote the xml expansion code to use the same serialization mechanism under python 2.x and 3.x, and removed external references by replacing the doctype declaration during lxml serialization.
- Fixed some code that didn't work correctly under python 3.3, by making sure to insert unicode strings instead of byte strings into unicode templates.
- Fixed a bug where text was compared with an integer when handling the needLines PI.

From Jim Schaad ietf@augustcellars:

- Fixed ticket [#186](https://github.com/ietf-tools/xml2rfc/issues/186) based on diffs provided by Leif Johansson leifj@mnt.se: If the first parse of the XML tree generates a syntax error, then we now  produce a warning of that fact.  This is in part to help me track down what  is happening at odd intervolts on my system where it generates an error and  then has entity resolution problems.
- Fixed the case of one reference section occurring with an eref.  In this case we need to emit the extra header in both locations.  Fixes ticket [#222](https://github.com/ietf-tools/xml2rfc/issues/222).
- Fixed a bug where text following a cref is missing.

## [2.4.5] - 2014-01-17

Another bugfix release, with a majority of the contributions from Jim Schaad.

- If there is not an RFC number then XXXX is used for the RFC number for to internal:/rfc.number - matches v1 behavior.  Fixes issue [#114](https://github.com/ietf-tools/xml2rfc/issues/114).
- We now do a better (but not perfect) job of mking sure that section headings are not orphaned.  If you have two section headings in a row then the first may still be orphaned.  Fixes issue [#166](https://github.com/ietf-tools/xml2rfc/issues/166).
- All known page breaking issues have been fixed.  Closes issue [#172](https://github.com/ietf-tools/xml2rfc/issues/172).
- Fixed a number of places where the code has to be made to work with both Python 2.7 unicode and string whitespace, and Python 3.3. whitespace strings, which are always unicode.  Fixes issue [#217](https://github.com/ietf-tools/xml2rfc/issues/217).
- Don't count formatting lines (which we can now tell) when computing  break hints.
- Catch any syntax errors raised while we're looking for an RFC number  attribute on `<rfc/>`, so that we'll show all syntax errors found (during the  next parse) instead of just one and one.
- Added tests which generate .txt from .nroff and compares that to the  xml2rfc-generated .txt (with some tweaks to handle different number of  starting blanklines.  Also corrected the number of initial blank lines  output for RFCs in the raw text writer.
- Not all files on Windows systems have a common root.  This means that one cannot always get a relative path between to absolute path file names. Catch the error that occurs in these circumstances and just use the absolute path name.
- Nested "format" style lists now include the level in the auto-generated counter value.  Fixes issue [#218](https://github.com/ietf-tools/xml2rfc/issues/218).
- EREFs are now put into the references section for text based output. Fixes issue [#133](https://github.com/ietf-tools/xml2rfc/issues/133).
- cref elements are not dealt with when inline is either yes or no for text files.  They are also now populated for html files as well.  Fixes issue [#201](https://github.com/ietf-tools/xml2rfc/issues/201).

## [2.4.4] - 2013-12-19

Another release with major contributions from Jim Schaad.  This release primarily addresses page-breaking issues, but also improves the reporting of syntax errors (if any) in the xml input.

From Jim Schaad <ietf@augustcellars.com>:

- We now do a better (but not perfect) job of mking sure that section headings are not orphaned.  If you have two section headings in a row then the first may still be orphaned.  Fixes issue [#166](https://github.com/ietf-tools/xml2rfc/issues/166).
- Improved autobreaking, in a number of different places.  Fixes issue [#172](https://github.com/ietf-tools/xml2rfc/issues/172).
- In all examples in the test suite, the .txt and .nroff output now have the same page breaks.
- Eliminated the line-breaking of 'Section N' in text-tables which was introduced in 2.4.4.  Fixes ticket [#217](https://github.com/ietf-tools/xml2rfc/issues/217).
- If there is not an RFC number then XXXX is used for the RFC number for to internal:/rfc.number - matches v1 behavior.  Fixes issue [#114](https://github.com/ietf-tools/xml2rfc/issues/114).

From Henrik Levkowetz <henrik@levkowetz.com>:

- Instead of previously only showing one single syntax error per invocation of xml2rfc, we're now showing all syntax errors found throughout the xml file at once.
- Added tests which generate .txt from .nroff and compares that to the  xml2rfc-generated .txt (with some tweaks to handle different number of  starting blanklines.  Also corrected the number of initial blank lines  output for RFCs in the raw text writer.

## [2.4.4] - 2013-12-11

This is a bugfix release, with code fixes almost entirely from Jim Schaad.

From Jim Schaad <ietf@augustcellars.com>:

- Annotations now output more than just the first text field.  It now expands all of the child elements as part of the output. Fixes issue [#183](https://github.com/ietf-tools/xml2rfc/issues/183).
- If the authors string is zero length, then we do not emit the comma separating the authors and the title. Fixes issue [#137](https://github.com/ietf-tools/xml2rfc/issues/137).
- Each street line is now tagged as class vcardline so it is emitted on a separate line. Fixes issue [#153](https://github.com/ietf-tools/xml2rfc/issues/153).
- Fixed a problem with unreferenced references warnings being emitted twice if there were two references sections.
- Fixed some list indentation problems.  We now default to an indent of 3 for hanging lists which is the same thing that v1 did.  We also use a value based on the bullet for format lists rather than using the 3 of a default hang indent - this also now matches v1 behavior.
- Use width of bullet not default to 3*level+3
- Fixed issue [#147](https://github.com/ietf-tools/xml2rfc/issues/147) - a hangingText without any text in the body now emits the hangingText. Fixes issue [#117](https://github.com/ietf-tools/xml2rfc/issues/117).
- Set of fixes that deal with xref in documents.
- Set of fixes that deal with references.
- We now use the anchor rather than the generated bullet as the id of the reference element. Fixes issue [#209](https://github.com/ietf-tools/xml2rfc/issues/209).
- The html did not have the same check for symrefs when sorting references that the text version did.  Copy it over so they both only sort if symrefs is yes. Fixes issue [#210](https://github.com/ietf-tools/xml2rfc/issues/210) and [#170](https://github.com/ietf-tools/xml2rfc/issues/170).
- Anchors on t elements in a section were referenceable, but no those in lists.  They are now referenceable. Fixes issue [#149](https://github.com/ietf-tools/xml2rfc/issues/149).
- We now generate a warning when we get a target in an xref that we have not created an indexable reference for.  This basically gives us an internal error check.
- We now generate a warning when a reference is created that is not targeted by an xref in the document.
- Fixed the centering algorithm so that the nroff and txt output files are more consistent.
- Left shift artwork that is greater than 69 characters wide and steal space from the left margin. Fixes issue [#129](https://github.com/ietf-tools/xml2rfc/issues/129).
- ` & 194` which deal with how figures are layout
- Fixed issue [#132](https://github.com/ietf-tools/xml2rfc/issues/132) - if the artwork has an alignment - then it overrides the figure's version for the purpose of the artwork itself. Fixes issue [#151](https://github.com/ietf-tools/xml2rfc/issues/151).
- Suppress-title kills the title decoration (i.e. Figure 1:) which matches v1 behavior. Fixes issue [#213](https://github.com/ietf-tools/xml2rfc/issues/213).
- Convert all non-ASCII characters to entities when building the HTML body. We now are correct when we advertise it as being a us-ascii file.
- Mixed two fixes back to the real source tree.
- Rewrite of the basic low level code to use unicode strings in many places rather than convert the unicode characters into xml entity codes and try to use them.  Doing so cleans up much of the line wrapping problems.
- URLs, when tagged to be not wrapped, now use different Unicode markers on the slashes and hyphens so that they will preferentially break on slashes rather than hyphens when a URL is too long to fit into a single line of text.
- Tracker issues addressed: [#192](https://github.com/ietf-tools/xml2rfc/issues/192), [#167](https://github.com/ietf-tools/xml2rfc/issues/167), [#168](https://github.com/ietf-tools/xml2rfc/issues/168), [#193](https://github.com/ietf-tools/xml2rfc/issues/193), [#200](https://github.com/ietf-tools/xml2rfc/issues/200), [#122](https://github.com/ietf-tools/xml2rfc/issues/122), [#139](https://github.com/ietf-tools/xml2rfc/issues/139)
- Increase the amount of text in the INSTALL document to deal with more information on how to install for windows. Fixes issue [#184](https://github.com/ietf-tools/xml2rfc/issues/184).
- Don't emit the references section and TOC entry if there are no references to be emitted. Fixes issue [#205](https://github.com/ietf-tools/xml2rfc/issues/205).
- Centering code did not take into account the .in X nroff command.  Always use .in 0 for emission of raw text. Fixes issue [#203](https://github.com/ietf-tools/xml2rfc/issues/203).
- The TCL code for deciding on table column widths has been moved into the new code. Fixes issue [#173](https://github.com/ietf-tools/xml2rfc/issues/173).
- We now look for and do expansions for header cells just like normal cells. Fixes issue [#131](https://github.com/ietf-tools/xml2rfc/issues/131).
- We now remove all entity references when doing an xml output
- Fixed issue [#146](https://github.com/ietf-tools/xml2rfc/issues/146) - The code now allows for the assumption that the file name given is what it really is and then tries with the .xml appended if it is not found. Fixes issue [#154](https://github.com/ietf-tools/xml2rfc/issues/154).
- Lots of errors added to tell about bad table layouts
- allow make to run without pyflakes. Fixes issue [#199](https://github.com/ietf-tools/xml2rfc/issues/199).

From Henrik Levkowetz <henrik@levkowetz.com>:

- Modified the code that saves page-break hints when building the unpaginated text so that it doesn't overwrite existing hints used for artwork and tables (which should not be broken across pages if at all possible) with hints that indicate regular text paragraphs (which may be broken except if that creates a widow or orphan).  Fixes issue [#179](https://github.com/ietf-tools/xml2rfc/issues/179) by making the code do for artwork and tables what needLines used to do, without needing the manual needLines hint.

## [2.4.3] - 2013-11-17

This release adds compatibility with Python 3.3; the test suite has been run for Python 2.6, 2.7 and 3.3 using the 'tox' tool.

This release also includes a large number of bugfixes, from people working at improving xml2rfc during the IETF-88 code sprint.

Details:

From Tony Hansen <tony@att.com>:

- Eliminated spurious dots before author names on page 1.  Fixes issue [#189](https://github.com/ietf-tools/xml2rfc/issues/189).
- Fixed the style of nested letter-style lists.  Fixes issue [#127](https://github.com/ietf-tools/xml2rfc/issues/127)
- Added a handling for empty <?rfc?> PIs within references.  Fixes issue [#181](https://github.com/ietf-tools/xml2rfc/issues/181).
- Removed trailing whitespace from reference title, organization.  Fixes issue [#171](https://github.com/ietf-tools/xml2rfc/issues/171).
- Added support v1 list formats %o, %x, and %X.  Fixes issue [#204](https://github.com/ietf-tools/xml2rfc/issues/204).
- Fixed a bad html selector which had a trailing '3'.  Fixes issue [#197](https://github.com/ietf-tools/xml2rfc/issues/197).

From Jim Schaad <ietf@augustcellars>:

- Removed leading zeros on dates.  Fixes issue [#206](https://github.com/ietf-tools/xml2rfc/issues/206).
- Fixed a crash when a new page had just been created, and it was totally empty.  It is unknown if this can occur someplace other than for the last page, but it should have check in other locations to look for that.  In addition we needed a change to figure out that we had already emitted a header for the page we are not going to use any longer and delete it.  Fixes issue [#187](https://github.com/ietf-tools/xml2rfc/issues/187).
- Handled the missing \& to escape a period at the beginning of a line.  If we do a raw emission (i.e. inside of a figure) then we need to go back over the lines we just put into the buffer and check to see if any of them have leading periods and quote them.  Fixes issue [#191](https://github.com/ietf-tools/xml2rfc/issues/191).
- Removed extraneous .ce 0 and blank lines in the nroff.  Since it was using the paging formatter in the process of building the nroff output, it kept all of the blank lines at the end of each page and emitted them.  There is no check in the nroff page_break function which removes any empty lines at the end of the array prior to emitting the ".bp" directive (or not emitting it if it is the last thing in the file.  Fixes issue [#180](https://github.com/ietf-tools/xml2rfc/issues/180).
- Now correctly picks up the day if a day is provided and uses the current day for a draft if the month and year are current.  We now allow for both the full name of the month and the abbreviated name of the month to be used, however there may be some interesting questions to look at if November is not in the current locale.  Fixes issue [#195](https://github.com/ietf-tools/xml2rfc/issues/195).
- Fixed the text-list-symbols PI to work at all levels.  The list should inherit style from the nearest parent that has one.  Fixes issue [#126](https://github.com/ietf-tools/xml2rfc/issues/126).

From Elwyn Davies <elwynd@dial.pipex.com>: 

- Don't emit '\%' before 'Section' for xrefs in the nroff writer.  Fixes issue [#169](https://github.com/ietf-tools/xml2rfc/issues/169).

From Henrik Levkowetz <henrik@levkowetz.com>:

- Modified the iref index output to use consistent sorting for items and subitems.
- Removed the restriction to python 2.x from setup.py
- Ported xml2rfc to python 3.3 while maintaining compatibility with 2.6  and 2.7.
- Added support for tox testing covering python versions 2.6, 2.7 and 3.3

## [2.4.2] - 2013-05-26

This release fixes all major and critical issues registered in the issue tracker as of 26 May 2013.  Details:

- Applied a patch from ht@inf.ed.ac.uk to sort references (when PI sortrefs==yes), and added code to insert a link target if the reference has a 'target' attribute. Fixes issue [#175](https://github.com/ietf-tools/xml2rfc/issues/175).
- Added pre-installation requirements to the INSTALL file.  Added code to scripts/xml2rfc in order to avoid problems if that file is renamed to scripts/xml2rfc.py.  This fixes issue [#152](https://github.com/ietf-tools/xml2rfc/issues/152).
- Added a setup requirement for python <3.0, as things don't currently work if trying to run setup.py or xml2rfc with python 3.X.
- Added special cases to avoid adding double spaces after many common abbreviations.  Refined the sentence-end double-space fixup further, to look at whether what follows looks like the start of a new sentence. This fixes issue [#115](https://github.com/ietf-tools/xml2rfc/issues/115).  
- Moved the get_initials() function to the BaseRfcWriter, as it now needs to look at a PI.  Added code to return one initial only, or multiple, depending on the PI 'multiple-initials' setting.  Fixes issue [#138](https://github.com/ietf-tools/xml2rfc/issues/138) (for now).  It is possible that this resolution is too simpleminded, and a cleaner way is needed to differentiate the handling of initials in the current document versus initials in references.
- Added new undocumented PI multiple-initials to control whether multiple initials will be shown for an author, or not.  The default is 'no', matching the xml2rfc v1.x behaviour.
- Fixed the code which determines when an author affiliation doesn't need to be listed again in the front page author list, and removes the redundant affiliation (the old code would remove the *first* matching organization, rather than the immediately preceeding organization name). Also fixed a buggy test of when an organization element is present. Fixes issue [#135](https://github.com/ietf-tools/xml2rfc/issues/135).
- Made appearance of 'Authors Address' (etc.) in ToC dependent on PI 'rfcedstyle' == 'yes'.  Fixes issue [#125](https://github.com/ietf-tools/xml2rfc/issues/125).
- Updated write_text() to handle long bullets that need to be wrapped across lines better.  Fixes issue [#124](https://github.com/ietf-tools/xml2rfc/issues/124).
- Fixed two other cases of missing blank lines when PI 'compact' is 'no'. Fixes issue #82 (some more).
- Disabled the iprnotified IP.  See issue [#123](https://github.com/ietf-tools/xml2rfc/issues/123); closes [#123](https://github.com/ietf-tools/xml2rfc/issues/123).
- When protecting http: URLs from line-breaking in nroff output, place the \% outside enclosing parentheses, if any.  Fixes issue [#120](https://github.com/ietf-tools/xml2rfc/issues/120).
- Added a warning for incomplete and out-of-date `<date/>` elements.  Fixed an issue with changeset r792.
- Issue a warning when the source file isn't for an RFC, but doesn't have a docName attribute in the `<rfc/>` element.
- Fixed the use of separating lines in table drawing, to match v1 for text and nroff output.  (There is no specification for the meaning of the different styles though...).  Fixes issue [#113](https://github.com/ietf-tools/xml2rfc/issues/113).  Note that additional style definitions are needed to get the correct results for the html output.
- Refactored and re-wrote the paginated text writer and the nroff writer in order to generate a ToC in nroff by re-using the fairly complex post-rendering code which inserts the ToC (and iref entries) in the paginated text writer.  As a side effect, the page-breaking calculations for the nroff writer becomes the same as for the paginated writer. Re-factored the line and page-break emitting code to be cleaner and more readable.  Changed the code to not start inserting a ToC too close to the end of a page (currently hardcoded to require at least 10 lines), otherwise skip to a new page.  Fixes issue [#109](https://github.com/ietf-tools/xml2rfc/issues/109).
- Changed the author list in first-page header to show a blank line if no organization has been given.  Fixes issue [#108](https://github.com/ietf-tools/xml2rfc/issues/108).
- Changed the wrapping of nroff output to match text output closely, in order to minimize insertion of .bp in the middle of a line.  Fixes issue [#150](https://github.com/ietf-tools/xml2rfc/issues/150) (mostly -- line breaks on hyphens may still cause .bp to be emitted in the middle of a line in very rare cases).
- Changed nroff output for long titles (which will wrap) so that the wrapped title text will be indented appropriately.  Fixes issue [#128](https://github.com/ietf-tools/xml2rfc/issues/128).
- Changed the handling of special characters (nbsp, nbhy) so as to emit the proper non-breaking escapes for nroff.  Fixes issue [#121](https://github.com/ietf-tools/xml2rfc/issues/121).
- Changed start-of-line nroff escape handling, see issue [#118](https://github.com/ietf-tools/xml2rfc/issues/118).
- Changed the generation of xref text to use the same numeric indexes as in the references section when symrefs='no'.  Don't start numbering over again when starting a new references section (i.e., when moving from normative to informative).  Don't re-sort numeric references alphabetically; they are already sorted numerically.  Fixes issue [#107](https://github.com/ietf-tools/xml2rfc/issues/107).
- Changed os.linesep to '`<NL>`' when writing lines to text files.  The library takes care of doing the right thing on different platforms; writing os.linesep on the other hand will result in the file containing '`<CR><CR><NL>`', which is wrong.  Fixes issue [#141](https://github.com/ietf-tools/xml2rfc/issues/141).
- Changed handling of include PIs to replace the PI instead of just appending the included tree.  Updated a test file to match updated test case.  Fixes issue [#136](https://github.com/ietf-tools/xml2rfc/issues/136).

## [2.4.1] - 2013-02-13

- Fixed a problem with very long hangindent bullet text followed by `<vspace/>`, which could make xml2rfc abort with a traceback for certain inputs.
- Fixed a mismatched argument count for string formatting which could make xml2rfc abort with a traceback for certain inputs.

## [2.4.0] - 2013-01-27

With this release, all issues against the 2.x series of xml2rfc has been resolved.  Without doubt there will be new issues in the issue tracker, but the current clean slate is nice to have.

For full details on all tickets, there's always the issue tracker: https://trac.tools.ietf.org/tools/xml2rfc/trac/report/

An extract from the commit log is available below:

- In some cases, the error messages when validating an xml document are  correct, but too obscure.  If a required element is absent, the error  message could say for instance 'Element references content does not follow  the DTD, expecting (reference)+, got ', which is correct -- the DTD  validator  got nothing, when it required something, so it says 'got ', with  nothing after 'got'.  But for a regular user, we now add on 'nothing.' to  make things clearer.  Fixes issue [#102](https://github.com/ietf-tools/xml2rfc/issues/102).
- It seems there could be a bug in separate invocation of  lxml.etree.DTD.validate(tree) after parsing, compared to doing parsing with  dtd_validation=True.  The former fails in a case when it shouldn't, while  the latter succeeds in validating a valid document.  Declaring validation  as successful if the dtd.error_log is empty, even if validation returned  False.  This resolves issue [#103](https://github.com/ietf-tools/xml2rfc/issues/103).
- Factored out the code which gets an author's initials from the xml  author element, and made the get_initials() utility function return  initials fixed up with trailing spaces, if missing.  The current code does  not mangle initials by removing any initials but the first one.  Fixes  issue #63, closes issue [#10](https://github.com/ietf-tools/xml2rfc/issues/10).
- Added code to avoid breaking URLs in boilerplate across lines.  Fixes  issue [#78](https://github.com/ietf-tools/xml2rfc/issues/78).
- Added PI defaults for 'figurecount' and 'tablecount' (not listed in the  xml2rfc readme...)  Also removed coupling between explicitly set  rfcedstyle, compact, and subcompact settings, to follow v1 practice.
- Refactored the PI defaults to appear all in the same place, rather than  spread out throughout the code.
- Updated draw_table to insert blank rows when PI compact is 'no'. Fixes  issue [#82](https://github.com/ietf-tools/xml2rfc/issues/82).
- Added tests and special handling for the case when a hanging type list  has less space left on the first line, after the bullet, than what's needed  for the first following word.  In that case, start the list text on the  following line.  Fixes issue [#85](https://github.com/ietf-tools/xml2rfc/issues/85).
- Modified the page-breaking code to better keep section titles together  with the section text, and keep figure preamble, figure, postamble and  caption together.  Updated tests.  Fixes issue [#100](https://github.com/ietf-tools/xml2rfc/issues/100).
- Added handling of tocdepth to the html writer.  Fixes issue [#101](https://github.com/ietf-tools/xml2rfc/issues/101).
- Modified how the --base switch to the xml2rfc script works, to make it  easier to generate multiple output formats and place them all in the same  target directory.  Also changed the default extensions for two output  formats (.raw.txt and .exp.xml).
- Tweaked the html template to not permit crazy wide pages.
- Rewrote parts of the parsing in order to get hold of the number  attribute of the `<rfc/>` tag before the full parsing is done, in order to be  able to later resolve the &rfc.number; entity (which, based on how  convoluted it is to get that right, I'd like to deprecate.)  Fixes issue  [#86](https://github.com/ietf-tools/xml2rfc/issues/86).
- Numerous small fixes to indentation and wrapping of references.  Avoid  wrapping URLs in references if possible.  Avoid wrapping 'Section 3.14.' if  possible.  Indent more like xml2rfc v1.
- Added reduction of doublespaces in regular text, except when they might  be at the end of a sentence.  Xml2rfc v1 would do this, v2 didn't till now.
- Generalized the _format_counter() method to consistently handle list  counter field-widths internally, and made it adjust the field-width to the  max counter width based on the list length and counter type.  Fixes an v1  to -v2 incompatibility for numbered lists with 10 items or more, and other  similar cases.
- Added generic base conversion code, and used that to generate list  letters which will work for lists with more than 26 items.
- Reworked code to render roman numerals in lists, to place whitespace  correctly in justification field.  Fixes issue [#94](https://github.com/ietf-tools/xml2rfc/issues/94).
- Added consensus vs. no-consensus options for IAB RFCs' Status of This  Memo section.  Fixes issue [#88](https://github.com/ietf-tools/xml2rfc/issues/88).
- Made `<t/>` elements with an anchor attribute generate html with an `<a name='...'/>` element, for linking.  Closes issue [#67](https://github.com/ietf-tools/xml2rfc/issues/67).
- Applied boilerplate URL-splitting prevention only in the raw writer  where later do paragraph line-wrapping, instead of generically.  Fixes  issue [#62](https://github.com/ietf-tools/xml2rfc/issues/62).
- Now permitting all versions of lxml >= 2.2.8, but notice that there may  be missing build dependencies for lxml 3.x which may cause installation of  lxml to fail.  (That's an lxml issue, rather than an xml2rfc issue,  though...)  This fixes issue [#99](https://github.com/ietf-tools/xml2rfc/issues/99).

## [2.3.11.3] - 2013-01-18

- Tweaked the install_required setting in setup.py to not pull down lxml 3.x (as it's not been tested with xml2rfc) and bumped the version.

## [2.3.11] - 2013-01-18

This release fixes all outstanding major bugs, details below. The issue tracker is at https://tools.ietf.org/tools/xml2rfc/trac/.

- Updated the nroff writer to do backslash escaping on source text, to  avoid escaping nroff control characters.  Fixes issue [#77](https://github.com/ietf-tools/xml2rfc/issues/77).
- Added a modified xref writer to the nroff output writer, in order to  handle xref targets which should not be broken across lines.  This,  together with changeset [b6f3b0d](https://github.com/ietf-tools/xml2rfc/commit/b6f3b0d556dfe72e1c3638bd7cf812843388b38f), fixes issue [#80](https://github.com/ietf-tools/xml2rfc/issues/80).
- Added text to the section test case to trigger the second part of issue  [#79](https://github.com/ietf-tools/xml2rfc/issues/79).  It turns out that the changes in [b6f3b0d](https://github.com/ietf-tools/xml2rfc/commit/b6f3b0d556dfe72e1c3638bd7cf812843388b38f) fixed this, too; this closes  issue [#79](https://github.com/ietf-tools/xml2rfc/issues/79).
- Tweaked the nroff generation to not break on hyphens, in order to avoid  hyphenated words ending up with embedded spaces: 'pre-processing' becoming  'pre- processing' if 'pre-' occurred at the end of an nroff text line.   Also tweaked the line-width used in line-breaking to have matching  line-breaks between .txt and .nroff output (with exception for lines ending  in hyphens).
- Tweaked roman number list counter to output roman numbers in a field 5  spaces wide, instead of having varied widths.  This is different from  version 1, so may have to be reverted, depending on how people react.
- Added a warning for too long lines in figures and tables.  No  outdenting for now; I'd like to consult some about that. Fixes issue [#76](https://github.com/ietf-tools/xml2rfc/issues/76).
- Updated tests showing that all list format specifiers mentioned in  issue #70 now works.  Closes issue [#70](https://github.com/ietf-tools/xml2rfc/issues/70).
- Changed spanx emphasis back to `_this_` instead of `-this-`, matching the v1  behaviour.  Addresses issue [#70](https://github.com/ietf-tools/xml2rfc/issues/70).
- Make `<vspace/>` in a hangindent list reset the indentation to the  hang-indent, even if the bullet text is longer than the hang-indent.   Addresses issue [#70](https://github.com/ietf-tools/xml2rfc/issues/70).
- Refined the page-breaking to not insert an extra page break for artwork that won't fit on a page anyway.
- Refined the page-breaking to avoid breaking artwork and tables across  pages, if possible.
- Fixed a problem with centering of titles and labels.  Fixes issue [#73](https://github.com/ietf-tools/xml2rfc/issues/73).
- Changed the leading and trailing whitespace lines of a page to better  match legacy output.  Fixed the autobreaking algorithm to correctly avoid  orphans and widows; fixes issue [#72](https://github.com/ietf-tools/xml2rfc/issues/72).  Removed an extra blank line at the  top of the page following an early page break to avoid orphan or widow.
- Tweaked the generation of ToC dot-lines and page numbers to better  match legacy xml2rfc.  Fixed a bug in the generation of xref text where  trailing whitespace could cause double spaces.  Tweaked the output format  to produce the correct number of leading blank lines on the first page of a  document.
- Modified the handling of figure titles, so that given titles will be  written also without anchor or figure counting.  Fixes issue [#75](https://github.com/ietf-tools/xml2rfc/issues/75).
- Tweaked the html writer to have a buffer interface that provides a  self.buf similar to the other writers, for test purposes.
- Reworked the WriterElementTest suite to test all the output formats,  not only paginated text.
- Added a note about /usr/local/bin permissions.  This closes issue [#65](https://github.com/ietf-tools/xml2rfc/issues/65).
- Added files describing possible install methods (INSTALL), and possible  build commands (Makefile).
- The syntax that was used to specify the version of the lxml dependency  ('>=') is not supported in python distutil setup.py files, and caused setup  to try to find an lxml version greater than =2.2.8, which couldn't succeed.  Fixed to say '>2.2.7' instead.  This was probably the cause of always  reinstalling lxml even when it was present.
- Updated README.rst to cover the new --date option, and tweaked it a bit.
- Added some files to provide an enhanced source distribution package.
- Updated setup.py with maintainer and licence information.

## [2.3.10] - 2013-01-03

- Changed the output text for Internet-Draft references to omit the  series name, but add (work in progress).  Updated the test case to match  draft revision number.
- Updated all the rfc editor boilerplate in valid test facets to match the  correct outcome (which is also what the code actually produces).
- Changed the diff test error message so that the valid text is output as  the original, not as the changed text of a diff.
- Corrected test cases to match correct expiry using 185 days instead of  183 days from document date.
- Added missing attributes to the XmlRfcError Exception subclass,  necessary in order to make it resemble lxml's error class and provide  consistent error messages to the user whether they come from lxml or our  own code.
- Added a licence file, indicating the licencing used by the IETF for the  xml2rfc code.
- Fixed up the xml2rfc cli script to provide better help texts by telling  the option parser the appropriate option variable names.
- Fixed up the help text formatting by explicitly providing an appropriate help text formatter to the option parser.  
- Added an option (--date=DATE)to provide the document date on the command line.
- Added an option (--no-dtd) to disable the DTD validation step.  
- Added code to catch additional exceptions and provide appropriate user information, instead of an exception traceback.

[3.12.1]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/3.12.1
[3.12.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/3.12.0
[3.11.1]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/3.11.1
[3.11.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/3.11.0
[3.10.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/3.10.0
[3.9.1]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/3.9.1
[3.9.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/3.9.0
[3.8.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/3.8.0
[3.7.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/3.7.0
[3.6.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/3.6.0
[3.5.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/3.5.0
[3.4.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/3.4.0
[3.3.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/3.3.0
[3.2.1]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/3.2.1
[3.2.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/3.2.0
[3.1.1]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/3.1.1
[3.1.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/3.1.0
[3.0.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/3.0.0
[2.47.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.47.0
[2.46.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.46.0
[2.45.3]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.45.3
[2.45.2]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.45.2
[2.45.1]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.45.1
[2.45.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.45.0
[2.44.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.44.0
[2.43.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.43.0
[2.42.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.42.0
[2.41.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.41.0
[2.40.1]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.40.1
[2.40.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.40.0
[2.39.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.39.0
[2.38.2]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.38.2
[2.38.1]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.38.1
[2.38.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.38.0
[2.37.3]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.37.3
[2.37.2]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.37.2
[2.37.1]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.37.1
[2.37.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.37.0
[2.36.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.36.0
[2.35.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.35.0
[2.34.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.34.0
[2.33.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.33.0
[2.32.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.32.0
[2.31.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.31.0
[2.30.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.30.0
[2.29.1]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.29.1
[2.29.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.29.0
[2.28.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.28.0
[2.27.1]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.27.1
[2.27.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.27.0
[2.26.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.26.0
[2.25.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.25.0
[2.24.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.24.0
[2.23.1]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.23.1
[2.23.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.23.0
[2.22.3]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.22.3
[2.22.2]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.22.2
[2.22.1]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.22.1
[2.22.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.22.0
[2.21.1]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.21.1
[2.21.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.21.0
[2.20.1]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.20.1
[2.20.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.20.0
[2.19.1]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.19.1
[2.19.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.19.0
[2.18.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.18.0
[2.17.2]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.17.2
[2.17.1]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.17.1
[2.17.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.17.0
[2.16.3]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.16.3
[2.16.2]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.16.2
[2.16.1]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.16.1
[2.16.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.16.0
[2.15.5]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.15.5
[2.15.4]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.15.4
[2.15.3]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.15.3
[2.15.2]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.15.2
[2.15.1]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.15.1
[2.15.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.15.0
[2.14.1]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.14.1
[2.14.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.14.0
[2.13.1]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.13.1
[2.13.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.13.0
[2.12.3]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.12.3
[2.12.2]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.12.2
[2.12.1]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.12.1
[2.12.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.12.0
[2.11.1]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.11.1
[2.11.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.11.0
[2.10.3]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.10.3
[2.10.2]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.10.2
[2.10.1]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.10.1
[2.10.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.10.0
[2.9.9]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.9.9
[2.9.8]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.9.8
[2.9.7]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.9.7
[2.9.6]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.9.6
[2.9.5]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.9.5
[2.9.4]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.9.4
[2.9.3]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.9.3
[2.9.2]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.9.2
[2.9.1]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.9.1
[2.9.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.9.0
[2.8.5]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.8.5
[2.8.4]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.8.4
[2.8.3]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.8.3
[2.8.2]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.8.2
[2.8.1]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.8.1
[2.8.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.8.0
[2.7.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.7.0
[2.6.2]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.6.2
[2.6.1]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.6.1
[2.6.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.6.0
[2.5.2]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.5.2
[2.5.1]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.5.1
[2.5.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.5.0
[2.4.12]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.4.12
[2.4.11]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.4.11
[2.4.10]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.4.10
[2.4.9]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.4.9
[2.4.8]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.4.8
[2.4.7]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.4.7
[2.4.6]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.4.6
[2.4.5]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.4.5
[2.4.4]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.4.4
[2.4.4]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.4.4
[2.4.3]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.4.3
[2.4.2]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.4.2
[2.4.1]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.4.1
[2.4.0]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.4.0
[2.3.11.3]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.3.11.3
[2.3.11]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.3.11
[2.3.10]: https://trac.ietf.org/trac/xml2rfc/browser/tags/cli/2.3.10
[v3.12.2]: https://github.com/ietf-tools/xml2rfc/compare/v3.12.1...v3.12.2
[v3.12.3]: https://github.com/ietf-tools/xml2rfc/compare/v3.12.2...v3.12.3

[v3.12.4]: https://github.com/ietf-tools/xml2rfc/compare/v3.12.3...v3.12.4
[v3.12.5]: https://github.com/ietf-tools/xml2rfc/compare/v3.12.4...v3.12.5
[v3.12.6]: https://github.com/ietf-tools/xml2rfc/compare/v3.12.5...v3.12.6
[v3.12.7]: https://github.com/ietf-tools/xml2rfc/compare/v3.12.6...v3.12.7
[v3.12.8]: https://github.com/ietf-tools/xml2rfc/compare/v3.12.7...v3.12.8

[v3.12.9]: https://github.com/ietf-tools/xml2rfc/compare/v3.12.8...v3.12.9
[v3.12.10]: https://github.com/ietf-tools/xml2rfc/compare/v3.12.9...v3.12.10
[v3.13.0]: https://github.com/ietf-tools/xml2rfc/compare/v3.12.10...v3.13.0
[v3.13.1]: https://github.com/ietf-tools/xml2rfc/compare/v3.13.0...v3.13.1
[v3.14.0]: https://github.com/ietf-tools/xml2rfc/compare/v3.13.1...v3.14.0

[v3.14.1]: https://github.com/ietf-tools/xml2rfc/compare/v3.14.0...v3.14.1
[v3.14.2]: https://github.com/ietf-tools/xml2rfc/compare/v3.14.1...v3.14.2
[v3.15.0]: https://github.com/ietf-tools/xml2rfc/compare/v3.14.2...v3.15.0
[v3.15.1]: https://github.com/ietf-tools/xml2rfc/compare/v3.15.0...v3.15.1
[v3.15.2]: https://github.com/ietf-tools/xml2rfc/compare/v3.15.1...v3.15.2
[v3.15.3]: https://github.com/ietf-tools/xml2rfc/compare/v3.15.2...v3.15.3
[v3.16.0]: https://github.com/ietf-tools/xml2rfc/compare/v3.15.3...v3.16.0
[v3.17.0]: https://github.com/ietf-tools/xml2rfc/compare/v3.16.0...v3.17.0
[v3.17.1]: https://github.com/ietf-tools/xml2rfc/compare/v3.17.0...v3.17.1
[v3.17.2]: https://github.com/ietf-tools/xml2rfc/compare/v3.17.1...v3.17.2
[v3.17.3]: https://github.com/ietf-tools/xml2rfc/compare/v3.17.2...v3.17.3
[v3.17.4]: https://github.com/ietf-tools/xml2rfc/compare/v3.17.3...v3.17.4
[v3.17.5]: https://github.com/ietf-tools/xml2rfc/compare/v3.17.4...v3.17.5
[v3.18.0]: https://github.com/ietf-tools/xml2rfc/compare/v3.17.5...v3.18.0
[v3.18.1]: https://github.com/ietf-tools/xml2rfc/compare/v3.18.0...v3.18.1
[v3.18.2]: https://github.com/ietf-tools/xml2rfc/compare/v3.18.1...v3.18.2
[v3.19.0]: https://github.com/ietf-tools/xml2rfc/compare/v3.18.2...v3.19.0
[v3.19.1]: https://github.com/ietf-tools/xml2rfc/compare/v3.19.0...v3.19.1
[v3.19.2]: https://github.com/ietf-tools/xml2rfc/compare/v3.19.1...v3.19.2
[v3.19.3]: https://github.com/ietf-tools/xml2rfc/compare/v3.19.2...v3.19.3
[v3.19.4]: https://github.com/ietf-tools/xml2rfc/compare/v3.19.3...v3.19.4

[v3.20.0]: https://github.com/ietf-tools/xml2rfc/compare/v3.19.4...v3.20.0
[v3.20.1]: https://github.com/ietf-tools/xml2rfc/compare/v3.20.0...v3.20.1
[v3.21.0]: https://github.com/ietf-tools/xml2rfc/compare/v3.20.1...v3.21.0
[v3.22.0]: https://github.com/ietf-tools/xml2rfc/compare/v3.21.0...v3.22.0
[v3.23.0]: https://github.com/ietf-tools/xml2rfc/compare/v3.22.0...v3.23.0
[v3.23.1]: https://github.com/ietf-tools/xml2rfc/compare/v3.23.0...v3.23.1
[v3.23.2]: https://github.com/ietf-tools/xml2rfc/compare/v3.23.1...v3.23.2
[v3.24.0]: https://github.com/ietf-tools/xml2rfc/compare/v3.23.2...v3.24.0
[v3.25.0]: https://github.com/ietf-tools/xml2rfc/compare/v3.24.0...v3.25.0
[v3.26.0]: https://github.com/ietf-tools/xml2rfc/compare/v3.25.0...v3.26.0
[v3.27.0]: https://github.com/ietf-tools/xml2rfc/compare/v3.26.0...v3.27.0
[v3.28.0]: https://github.com/ietf-tools/xml2rfc/compare/v3.27.0...v3.28.0
[v3.28.1]: https://github.com/ietf-tools/xml2rfc/compare/v3.28.0...v3.28.1
[v3.29.0]: https://github.com/ietf-tools/xml2rfc/compare/v3.28.1...v3.29.0
