# Third-party notices

## wechatauto-replica

The Windows WeChat 4.x database workflow uses this independent upstream project:

1. Project: `wechatauto-replica`
2. Original author and repository maintainer: **fanyuantaier**
3. Source: https://github.com/fanyuantaier/wechatauto-replica
4. License: Apache License 2.0
5. Bundled version: 1.2.4, commit `01eb06ef464d23bb651040ff76413f7183adf7e3a`

The implementation is not authored by this repository's maintainer. The runtime-required subset of the pinned source is retained under `offline/third_party/wechatauto-replica/` with its original license and is loaded only for local, read-only database access. Unused demos, UI automation modules, tests and media were removed from the optimized offline package; the complete source is available from the original repository above.

No real database key, `keys.json`, WeChat database, wxid, database path, or chat export is bundled. Runtime keys remain on the user's computer.

## 其他离线运行组件

The complete offline edition redistributes CPython 3.12.10, cryptography, cffi, pycparser, colorama, Pillow, and zstandard. Their license texts are preserved beside the binaries. Exact versions and downloaded-archive hashes are listed in `offline/BUILD_INFO.md`.

## 非原创声明

微信数据库密钥的内存扫描、验证、解密与缓存实现来自 `fanyuantaier/wechatauto-replica`，不是本项目原创。本项目只增加离线封装、匿名统计转换和看板生成流程。请仅处理本人或已获明确授权的数据，且不要发布生成的密钥文件。
