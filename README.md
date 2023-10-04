# cia-unix

*Decrypt CIA roms in UNIX environments* 🪐

> **Warning**
> This `cia-unix` version is under development, and it may not work.

#### Requirements
* [Python 3](https://www.python.org/downloads/)
* [PyCryptodome](https://pypi.org/project/pycryptodome/) 
  * `pip3 install pycryptodome`

```
cia-unix/
├─ cia-unix
├─ decrypt.py
├─ ctrtool
├─ makerom
└─ Encrypted Game.cia
```

**ctrtool**, **makerom** and **decrypt.py** can be downloaded with `dltools.sh`

## 📋 Roadmap
- [x] Decrypt .cia
  - [x] Games
  - [x] Patch and DLCs
- [x] Decrypt .3ds
- [ ] Rust `decrypt.py` rewrite (*[in progress](https://github.com/shijimasoft/ctrdecrypt)*)

> **Warning**
> Decryption with cia-unix may fail, when it happens it is suggested to decrypt roms directly on the 3DS.

## ⚡️ Build from source
You’ll need the [Crystal compiler](https://crystal-lang.org/install/)

```sh
crystal build cia-unix.cr --release --no-debug
```

Dependencies can be compiled with [makerom](https://github.com/3DSGuy/Project_CTR/tree/master/makerom) and [ctrtool](https://github.com/3DSGuy/Project_CTR/tree/master/ctrtool) make files

## Contributors
ctrtool and makerom are from [3DSGuy repository](https://github.com/3DSGuy/Project_CTR)

*Adaware* contributed translating the [windows-only version](https://github.com/matiffeder/3DS-stuff/blob/master/Batch%20CIA%203DS%20Decryptor.bat)
