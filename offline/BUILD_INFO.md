# Offline bundle build information

Target: Windows x64, CPython 3.12 ABI. The runtime is assembled at build time; no installer or package manager is used at runtime.

| Component | Version / commit | SHA-256 of downloaded archive |
| --- | --- | --- |
| CPython embeddable x64 | 3.12.10 | `4acbed6dd1c744b0376e3b1cf57ce906f9dc9e95e68824584c8099a63025a3c3` |
| wechatauto-replica | 1.2.4 / `01eb06ef464d23bb651040ff76413f7183adf7e3a` | Source snapshot from Git commit |
| cryptography | 46.0.3 | `a9a3008438615669153eb86b26b61e09993921ebdd75385ddd748702c5adfddb` |
| cffi | 2.1.1 | `f53e442b08449d42821fa4a4fba000095af9f62742a500f978a9f557ec44339a` |
| pycparser | 3.0 | `b727414169a36b7d524c1c3e31839a521725078d7b2ff038656844266160a992` |
| colorama | 0.4.6 | `4f1d9991f5acc0ca119f9d443620b77f9d6b33703e51011c16baf57afb285fc6` |
| Pillow | 12.0.0 | `9fe611163f6303d1619bbcb653540a4d60f9e55e622d60a3108be0d5b441017a` |
| zstandard | 0.25.0 | `ffef5a74088f1e09947aecf91011136665152e0b4b359c42be3373897fb39b01` |

The corresponding license files are retained in CPython's `LICENSE.txt`, each wheel's `.dist-info/licenses/` directory, and the upstream source tree's `LICENSE`.
