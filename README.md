# cia-unix

*Decrypt CIA roms in UNIX environments* 🪐

#### Requirements
* [Python 2.7](https://www.python.org/downloads/release/python-2718/)
* [PyCrypto](https://pypi.org/project/pycrypto/) 
  * `pip install pycrypto` or `easy_install pycrypto`

> **Note**
> A new Python 3 (unstable) version has been released, you can find the experimental code [here](https://github.com/shijimasoft/cia-unix/tree/experimental).

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
- [ ] Rust/C++ 'decrypt.py' rewrite

## ⚡️ Build from source
You’ll need the [Crystal compiler](https://crystal-lang.org/install/)

```
crystal build cia-unix.cr --release --no-debug
```

Dependencies can be compiled with [makerom](https://github.com/3DSGuy/Project_CTR/tree/master/makerom) and [ctrtool](https://github.com/3DSGuy/Project_CTR/tree/master/ctrtool) make files

## Contributors
ctrtool and makerom are from [3DSGuy repository](https://github.com/3DSGuy/Project_CTR)

*Adaware* contributed translating the [windows-only version](https://github.com/matiffeder/3DS-stuff/blob/master/Batch%20CIA%203DS%20Decryptor.bat)
