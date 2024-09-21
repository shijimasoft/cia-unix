import os, sys, struct
from Crypto.Cipher import AES
from Crypto.Util import Counter
from hashlib import sha256
from ctypes import *
from binascii import hexlify, unhexlify
import ssl

context = ssl._create_unverified_context()
import urllib.request, urllib.parse, urllib.error

cmnkeys = [
    b"64c5fd55dd3ad988325baaec5243db98",
    b"4aaa3d0e27d4d728d0b1b433f0f9cbc8",
    b"fbb0ef8cdbb0d8e453cd99344371697f",
    b"25959b7ad0409f72684198ba2ecd7dc6",
    b"7ada22caffc476cc8297a0c7ceeeeebe",
    b"a5051ca1b37dcf3afbcf8cc1edd9ce02"
]

key0x2C = 246647523836745093481291640204864831571
key0x25 = 275024782269591852539264289417494026995
key0x18 = 174013536497093865167571429864564540276
key0x1B = 92615092018138441822550407327763030402

fixedzeros = 0
fixedsys = 109645209274529458878270608689136408907
keys = [[key0x2C, key0x25, key0x18, key0x1B], [fixedzeros, fixedsys]]
mediaUnitSize = 512
ncsdPartitions = [
    "Main",
    "Manual",
    "DownloadPlay",
    "Partition4",
    "Partition5",
    "Partition6",
    "N3DSUpdateData",
    "UpdateData",
]
tab = '\t'


class ncchHdr(Structure):
    _fields_ = [
        ("signature", c_uint8 * 256),
        ("magic", c_char * 4),
        ("ncchSize", c_uint32),
        ("titleId", c_uint8 * 8),
        ("makerCode", c_uint16),
        ("formatVersion", c_uint8),
        ("formatVersion2", c_uint8),
        ("seedcheck", c_char * 4),
        ("programId", c_uint8 * 8),
        ("padding1", c_uint8 * 16),
        ("logoHash", c_uint8 * 32),
        ("productCode", c_uint8 * 16),
        ("exhdrHash", c_uint8 * 32),
        ("exhdrSize", c_uint32),
        ("padding2", c_uint32),
        ("flags", c_uint8 * 8),
        ("plainRegionOffset", c_uint32),
        ("plainRegionSize", c_uint32),
        ("logoOffset", c_uint32),
        ("logoSize", c_uint32),
        ("exefsOffset", c_uint32),
        ("exefsSize", c_uint32),
        ("exefsHashSize", c_uint32),
        ("padding4", c_uint32),
        ("romfsOffset", c_uint32),
        ("romfsSize", c_uint32),
        ("romfsHashSize", c_uint32),
        ("padding5", c_uint32),
        ("exefsHash", c_uint8 * 32),
        ("romfsHash", c_uint8 * 32),
    ]

    def __new__(cls, buf):
        return cls.from_buffer_copy(buf)

    def __init__(self, data):
        pass


class ncchSection:
    exheader = 1
    exefs = 2
    romfs = 3


class ncch_offsetsize(Structure):
    _fields_ = [("offset", c_uint32), ("size", c_uint32)]


class ncsdHdr(Structure):
    _fields_ = [
        ("signature", c_uint8 * 256),
        ("magic", c_char * 4),
        ("mediaSize", c_uint32),
        ("titleId", c_uint8 * 8),
        ("padding0", c_uint8 * 16),
        ("offset_sizeTable", ncch_offsetsize * 8),
        ("padding1", c_uint8 * 40),
        ("flags", c_uint8 * 8),
        ("ncchIdTable", c_uint8 * 64),
        ("padding2", c_uint8 * 48),
    ]


class SeedError(Exception):
    pass


class ciaReader:
    def __init__(self, fhandle, encrypted, titkey, cIdx, contentOff):
        self.fhandle = fhandle
        self.encrypted = encrypted
        self.name = fhandle.name
        self.cIdx = cIdx
        self.contentOff = contentOff
        self.cipher = AES.new(
            titkey,
            AES.MODE_CBC,
            to_bytes(cIdx, 2) + bytes(14),
        )
        
    def seek(self, offs):
        if offs == 0:
            self.fhandle.seek(self.contentOff)
            self.cipher.IV = (to_bytes(self.cIdx, 2) + bytes(14))
        else:
            self.fhandle.seek(self.contentOff + offs - 16)
            self.cipher.IV = self.fhandle.read(16)

    def read(self, nbytes):
        if nbytes == 0:
            return ""
        data = self.fhandle.read(nbytes)
        if self.encrypted:
            data = self.cipher.decrypt(data)
        return data


def from_bytes(data):
    if type(data) == str:
        data = bytearray(data)
    data = reversed(data)
    num = 0
    for offset, byte in enumerate(data):
        num += byte << offset * 8

    return num


def to_bytes(n, length):
    h = "%x" % n
    s = ("0" * (len(h) % 2) + h).zfill(length * 2)
    return bytes.fromhex(s)


def scramblekey(keyX, keyY):
    rol = (
        lambda val, r_bits, max_bits: val << r_bits % max_bits & 2**max_bits - 1
        | (val & 2**max_bits - 1) >> max_bits - r_bits % max_bits
    )
    return rol(
        (rol(keyX, 2, 128) ^ keyY) + 42503689118608475533858958821215598218
        & 340282366920938463463374607431768211455,
        87,
        128,
    )


def reverseCtypeArray(ctypeArray):
    return ("").join("%02X" % x for x in ctypeArray[::-1])


def getNcchAesCounter(header, t):
    counter = bytearray(16)
    if header.formatVersion == 2 or header.formatVersion == 0:
        counter[:8] = bytearray(header.titleId[::-1])
        counter[8:9] = chr(t).encode()
    elif header.formatVersion == 1:
        x = 0
        if t == ncchSection.exheader:
            x = 512
        if t == ncchSection.exefs:
            x = header.exefsOffset * mediaUnitSize
        if t == ncchSection.romfs:
            x = header.romfsOffset * mediaUnitSize
        counter[:8] = bytearray(header.titleId)
        for i in range(4):
            counter[12 + i] = chr(x >> (3 - i) * 8 & 255)

    return bytes(counter)


def getNewkeyY(keyY, header, titleId):
    seeds = {}
    seedif = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "seeddb.bin")
    if os.path.exists(seedif):
        with open(seedif, "rb") as (seeddb):
            seedcount = struct.unpack("<I", seeddb.read(4))[0]
            seeddb.read(12)
            for i in range(seedcount):
                key = hexlify(seeddb.read(8)[::-1])
                seeds[key] = bytearray(seeddb.read(16))
                seeddb.read(8)

    if titleId not in seeds:
        print((tab + "********************************"))
        print((tab + "Couldn't find seed in seeddb, checking online..."))
        print((tab + "********************************"))
        for country in ["JP", "US", "GB", "KR", "TW", "AU", "NZ"]:
            r = urllib.request.urlopen(
                f"https://kagiya-ctr.cdn.nintendo.net/title/0x{titleId}/ext_key?country={country}",
                context=context,
            )
            if r.getcode() == 200:
                seeds[titleId] = r.read()
                break

    if titleId in seeds:
        seedcheck = struct.unpack(">I", header.seedcheck)[0]

        if (int(sha256(seeds[titleId] + unhexlify(titleId)[::-1]).hexdigest()[:8], 16) == seedcheck):
            keystr = sha256(to_bytes(keyY, 16) + seeds[titleId]).hexdigest()[:32]
            newkeyY = unhexlify(keystr)
            return from_bytes(newkeyY)

        raise SeedError("Seed check fail, wrong seed?")
    raise SeedError("Something Happened :/")


def align(x, y):
    mask = ~(y - 1)
    return x + (y - 1) & mask


def parseCIA(fh):
    print(f'Parsing CIA in file "{os.path.basename(fh.name)}":')
    fh.seek(0)
    (
        headerSize,
        t,
        version,
        cachainSize,
        tikSize,
        tmdSize,
        metaSize,
        contentSize,
    ) = struct.unpack("<IHHIIIIQ", fh.read(32))
    cachainOff = align(headerSize, 64)
    tikOff = align(cachainOff + cachainSize, 64)
    tmdOff = align(tikOff + tikSize, 64)
    contentOffs = align(tmdOff + tmdSize, 64)
    metaOff = align(contentOffs + contentSize, 64)
    fh.seek(tikOff + 127 + 320)
    enckey = fh.read(16)
    fh.seek(tikOff + 156 + 320)
    tid = fh.read(8)
    if hexlify(tid)[:5] == b"00048":
        print("Unsupported CIA file")
        return
    fh.seek(tikOff + 177 + 320)
    cmnkeyidx = struct.unpack("B", fh.read(1))[0]
    titkey = AES.new(
        unhexlify(cmnkeys[cmnkeyidx]),
        AES.MODE_CBC,
        tid + bytes(8),
    ).decrypt(enckey)
    fh.seek(tmdOff + 518)
    contentCount = struct.unpack(">H", fh.read(2))[0]
    nextContentOffs = 0
    for i in range(contentCount):
        fh.seek(tmdOff + 2820 + 48 * i)
        cId, cIdx, cType, cSize = struct.unpack(">IHHQ", fh.read(16))
        cEnc = True
        if cType & 1 == 0:
            cEnc = False
        fh.seek(contentOffs + nextContentOffs)
        if cEnc:
            test = AES.new(
                titkey,
                AES.MODE_CBC,
                to_bytes(cIdx, 2) + bytes(14),
            ).decrypt(fh.read(512))
        else:
            test = fh.read(512)
        if not test[256:260] == b"NCCH":
            print("  Problem parsing CIA content, skipping. Sorry about that :/\n")
            continue
        fh.seek(contentOffs + nextContentOffs)
        ciaHandle = ciaReader(fh, cEnc, titkey, cIdx, contentOffs + nextContentOffs)
        nextContentOffs = nextContentOffs + align(cSize, 64)
        parseNCCH(ciaHandle, cSize, 0, cIdx, cId, tid, 0, 0)


def parseNCSD(fh):
    print(f'Parsing NCSD in file "{os.path.basename(fh.name)}":')
    fh.seek(0)
    header = ncsdHdr()
    fh.readinto(header)
    for i in range(len(header.offset_sizeTable)):
        if header.offset_sizeTable[i].offset:
            parseNCCH(
                fh,
                header.offset_sizeTable[i].size * mediaUnitSize,
                header.offset_sizeTable[i].offset * mediaUnitSize,
                i,
                i,
                reverseCtypeArray(header.titleId),
                0,
                1,
            )


def parseNCCH(fh, fsize, offs=0, idx=0, contentId=0, titleId="", standAlone=1, fromNcsd=0):
    tab = '\t' if not standAlone else "  "
    if not standAlone and fromNcsd:
        print(f"  Parsing {ncsdPartitions[idx]} NCCH")
    elif not standAlone:
        print(f"  Parsing NCCH {idx}")
    else:
        print(f'Parsing NCCH in file "{os.path.basename(fh.name)}":')
    fh.seek(offs)
    tmp = fh.read(512)
    header = ncchHdr(tmp)
    if titleId == "":
        titleId = reverseCtypeArray(header.programId)
    ncchKeyY = from_bytes(header.signature[:16])
    print((tab + "Product code: " + bytearray(header.productCode).decode().rstrip("\x00")))
    print((tab + "KeyY: %032X" % ncchKeyY))
    print(tab + f"Title ID: {reverseCtypeArray(header.titleId)}")
    print(tab + f"Format version: {header.formatVersion}")
    print(tab + f"Content Id: %08X" % contentId)
    usesExtraCrypto = bytearray(header.flags)[3]
    if usesExtraCrypto:
        print((tab + "Uses Extra NCCH crypto, keyslot 0x%X" % {1: 37, 10: 24, 11: 27}[usesExtraCrypto]))
    fixedCrypto = 0
    encrypted = 1
    if header.flags[7] & 1:
        fixedCrypto = 2 if header.titleId[3] & 16 else 1
        print((tab + "Uses fixed-key crypto"))
    if header.flags[7] & 4:
        encrypted = 0
        print((tab + "Not Encrypted"))
    useSeedCrypto = header.flags[7] & 32 != 0
    keyY = ncchKeyY
    if useSeedCrypto:
        keyY = getNewkeyY(ncchKeyY, header, hexlify(titleId))
        print((tab + "Uses 9.6 NCCH Seed crypto with KeyY: %032X" % keyY))
    print("")
    base = os.path.splitext(os.path.basename(fh.name))[0]
    base += f".{(idx if fromNcsd == 0 else ncsdPartitions[idx])}.%08X.ncch" % contentId
    base = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), base)
    with open(base, "wb") as (f):
        tmp = tmp[:399] + chr(tmp[399] & 2 | 4).encode() + tmp[400:]
        f.write(tmp)
        if header.exhdrSize != 0:
            counter = getNcchAesCounter(header, ncchSection.exheader)
            dumpSection(
                f,
                fh,
                512,
                header.exhdrSize * 2,
                ncchSection.exheader,
                counter,
                usesExtraCrypto,
                fixedCrypto,
                encrypted,
                [ncchKeyY, keyY],
            )
        if header.exefsSize != 0:
            counter = getNcchAesCounter(header, ncchSection.exefs)
            dumpSection(
                f,
                fh,
                header.exefsOffset * mediaUnitSize,
                header.exefsSize * mediaUnitSize,
                ncchSection.exefs,
                counter,
                usesExtraCrypto,
                fixedCrypto,
                encrypted,
                [ncchKeyY, keyY],
            )
        if header.romfsSize != 0:
            counter = getNcchAesCounter(header, ncchSection.romfs)
            dumpSection(
                f,
                fh,
                header.romfsOffset * mediaUnitSize,
                header.romfsSize * mediaUnitSize,
                ncchSection.romfs,
                counter,
                usesExtraCrypto,
                fixedCrypto,
                encrypted,
                [ncchKeyY, keyY],
            )
    print("")


def dumpSection(f, fh, offset, size, t, ctr, usesExtraCrypto, fixedCrypto, encrypted, keyYs):
    cryptoKeys = {0: 0, 1: 1, 10: 2, 11: 3}
    sections = ["ExHeader", "ExeFS", "RomFS"]
    print(tab + f"{sections[(t - 1)]} offset:  " + ("%08X" % offset))
    print(tab + f"{sections[(t - 1)]} counter: {hexlify(ctr)}")
    print(tab + f"{sections[(t - 1)]} size: {size} bytes")
    tmp = offset - f.tell()
    if tmp > 0:
        f.write(fh.read(tmp))
    if not encrypted:
        sizeleft = size
        while sizeleft > 4194304:
            f.write(fh.read(4194304))
            sizeleft -= 4194304

        if sizeleft > 0:
            f.write(fh.read(sizeleft))
        return
    key0x2C = to_bytes(scramblekey(keys[0][0], keyYs[0]), 16)
    if t == ncchSection.exheader:
        key = key0x2C
        if fixedCrypto:
            key = to_bytes(keys[1][(fixedCrypto - 1)], 16)
        cipher = AES.new(
            key,
            AES.MODE_CTR,
            counter=Counter.new(128, initial_value=from_bytes(ctr)),
        )
        f.write(cipher.decrypt(fh.read(size)))
    if t == ncchSection.exefs:
        key = key0x2C
        if fixedCrypto:
            key = to_bytes(keys[1][(fixedCrypto - 1)], 16)
        cipher = AES.new(
            key,
            AES.MODE_CTR,
            counter=Counter.new(128, initial_value=from_bytes(ctr)),
        )
        exedata = fh.read(size)
        exetmp = cipher.decrypt(exedata)
        if usesExtraCrypto:
            extraCipher = AES.new(
                to_bytes(scramblekey(keys[0][cryptoKeys[usesExtraCrypto]], keyYs[1]), 16),
                AES.MODE_CTR,
                counter=Counter.new(128, initial_value=from_bytes(ctr)),
            )
            exetmp2 = extraCipher.decrypt(exedata)
            for i in range(10):
                fname, off, size = struct.unpack("<8sII", exetmp[i * 16 : (i + 1) * 16])
                off += 512
                if fname.strip(b"\x00") not in ("icon", "banner"):
                    exetmp = (
                        exetmp[:off] + exetmp2[off : off + size] + exetmp[off + size :]
                    )

        f.write(exetmp)
    if t == ncchSection.romfs:
        key = to_bytes(scramblekey(keys[0][cryptoKeys[usesExtraCrypto]], keyYs[1]), 16)
        if fixedCrypto:
            key = to_bytes(keys[1][(fixedCrypto - 1)], 16)
        cipher = AES.new(
            key,
            AES.MODE_CTR,
            counter=Counter.new(128, initial_value=from_bytes(ctr)),
        )
        sizeleft = size
        while sizeleft > 4194304:
            f.write(cipher.decrypt(fh.read(4194304)))
            sizeleft -= 4194304

        if sizeleft > 0:
            f.write(cipher.decrypt(fh.read(sizeleft)))


if len(sys.argv) < 2:
    print("usage: decrypt.py *file*")
    sys.exit()

if os.path.exists(sys.argv[1]):
    file = sys.argv[1] 
    with open(file, "rb") as (fh):
        fh.seek(256)
        magic = fh.read(4)

        if magic == b"NCSD":
            result = parseNCSD(fh)
            print("")
        elif magic == b"NCCH":
            fh.seek(0, 2)
            result = parseNCCH(fh, fh.tell())
            print("")
        elif fh.name.lower().endswith(".cia"):
            fh.seek(0)
            if fh.read(4) == b"  \x00\x00":
                parseCIA(fh)
                print("")
else:
    print("Input file does not exist")
    sys.exit()

print("Partitions extracted")
