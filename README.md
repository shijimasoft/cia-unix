# cia-unix

*Decrypt CIA roms in UNIX environments* ðª

#### Requirements
* Python 2.7
* [PyCrypto](https://pypi.org/project/pycrypto/)

```
cia-unix/
ââ cia-unix
ââ decrypt.py
ââ ctrtool
ââ makerom
ââ Encrypted Game.cia
```
**ctrtool** and **makerom** can be downloaded with `dltools.sh`

## ð Roadmap
- [x] Decrypt .cia
  - [x] Games
  - [x] Patch and DLCs
- [x] Decrypt .3ds
- [ ] Rust 'decrypt.py' rewrite

## â¡ï¸ Build from source
Youâll need the [Crystal compiler](https://crystal-lang.org/install/)

`crystal build cia-unix.cr --release`

Dependencies can be compiled with [makerom](https://github.com/3DSGuy/Project_CTR/tree/master/makerom) and [ctrtool](https://github.com/3DSGuy/Project_CTR/tree/master/ctrtool) make files

## Contributors
ctrtool and makerom are from [*3DSGuy* repository](https://github.com/3DSGuy/Project_CTR)

*[AdawareDeveloper](https://github.com/AdawareDeveloper)* contributed translating the [windows-only version](https://github.com/matiffeder/3DS-stuff/blob/master/Batch%20CIA%203DS%20Decryptor.bat)
