# cia-unix

*Decrypt CIA and 3DS roms in UNIX environments (Linux and macOS)*

```
cia-unix/
├─ cia-unix
├─ ctrdecrypt
├─ ctrtool
├─ makerom
└─ Encrypted Game.cia
```

**ctrtool**, **makerom** and [**ctrdecrypt**](https://github.com/shijimasoft/ctrdecrypt) can be downloaded with `dltools.sh`

## ✅ Roadmap
- [x] Decrypt .cia
  - [x] Games
  - [x] Patch and DLCs
- [x] Decrypt .3ds
- [x] Rust [`decrypt.py`](https://github.com/shijimasoft/cia-unix/blob/old-python3/decrypt.py) rewrite (ctrdecrypt)

> [!WARNING]
> Decryption with cia-unix may fail, when it happens it is suggested to decrypt roms directly on the 3DS.

The old _python 3_ version can be found [here](https://github.com/shijimasoft/cia-unix/tree/old-python3).

## ⚡️ Build from source
You’ll need the [Crystal compiler](https://crystal-lang.org/install/)

```bash
crystal build cia-unix.cr --release --no-debug
```

Dependencies can be compiled with [makerom](https://github.com/3DSGuy/Project_CTR/tree/master/makerom) and [ctrtool](https://github.com/3DSGuy/Project_CTR/tree/master/ctrtool) make files.

## Contributors
ctrtool and makerom are from [3DSGuy repository](https://github.com/3DSGuy/Project_CTR)

*Adaware* contributed translating the [windows-only version](https://github.com/matiffeder/3DS-stuff/blob/master/Batch%20CIA%203DS%20Decryptor.bat)
