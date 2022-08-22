import os, sys, glob, struct
from Crypto.Cipher import AES
from Crypto.Util import Counter
from hashlib import sha256
from ctypes import *
from binascii import hexlify, unhexlify
import ssl

context = ssl._create_unverified_context()
import urllib.request, urllib.parse, urllib.error

devkeys = 0
if devkeys == 0:
    cmnkeys = [
        133950820312113818052254735185268169624,
        99246800502542016961820831682009877448,
        334554929844945050845898870533261453695,
        49958241579738975625263968236998589894,
        163298441886091868932353113880783679166,
        219349161507556771313991622940048346626,
    ]
    key0x2C = 246647523836745093481291640204864831571
    key0x25 = 275024782269591852539264289417494026995
    key0x18 = 174013536497093865167571429864564540276
    key0x1B = 92615092018138441822550407327763030402
else:
    cmnkeys = [
        113835763157985768603715566790521001275,
        90662311705905729160277180104286604325,
        176960587729458970190709525955428573895,
        16565743050834760937649323226713341516,
        297981520825143936698022683828169936983,
        5413407133145539762491762794674946987,
    ]
    key0x2C = 107678000672959294808833481810464881181
    key0x25 = 172220582634352810158581394293866026779
    key0x18 = 64197259709433409621779576860674900598
    key0x1B = 144279189824071929460111192617823391670
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
tab = "    "


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
            to_bytes(cIdx, 2, "big")
            + "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
        )

    def seek(self, offs):
        if offs == 0:
            self.fhandle.seek(self.contentOff)
            self.cipher.IV = (
                to_bytes(self.cIdx, 2, "big")
                + "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
            )
        else:
            self.fhandle.seek(self.contentOff + offs - 16)
            self.cipher.IV = self.fhandle.read(16)

    def read(self, bytes):
        if bytes == 0:
            return ""
        data = self.fhandle.read(bytes)
        if self.encrypted:
            data = self.cipher.decrypt(data)
        return data


def from_bytes(data, endianess="big"):
    if isinstance(data, str):
        data = bytearray(data)
    if endianess == "big":
        data = reversed(data)
    num = 0
    for offset, byte in enumerate(data):
        num += byte << offset * 8

    return num


def to_bytes(n, length, endianess="big"):
    h = "%x" % n
    s = ("0" * (len(h) % 2) + h).zfill(length * 2).encode()
    if endianess == "big":
        return s
    return s[::-1]


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
    counter = bytearray(
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    )
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
                "https://kagiya-ctr.cdn.nintendo.net/title/0x%s/ext_key?country=%s"
                % (titleId, country),
                context=context,
            )
            if r.getcode() == 200:
                seeds[titleId] = r.read()
                break

    if titleId in seeds:
        seedcheck = struct.unpack(">I", header.seedcheck)[0]
        if (
            int(sha256(seeds[titleId] + unhexlify(titleId)[::-1]).hexdigest()[:8], 16)
            == seedcheck
        ):
            keystr = sha256(to_bytes(keyY, 16, "big") + seeds[titleId]).hexdigest()[:32]
            newkeyY = unhexlify(keystr)
            return from_bytes(newkeyY, "big")
        raise SeedError("Seed check fail, wrong seed?")
    raise SeedError("Something Happened :/")


def align(x, y):
    mask = ~(y - 1)
    return x + (y - 1) & mask


def parseCIA(fh):
    print(('Parsing CIA in file "%s":' % os.path.basename(fh.name)))
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
    if hexlify(tid)[:5] == "00048":
        print("Unsupported CIA file")
        return
    fh.seek(tikOff + 177 + 320)
    cmnkeyidx = struct.unpack("B", fh.read(1))[0]
    titkey = AES.new(
        to_bytes(cmnkeys[cmnkeyidx], 16, "big"),
        AES.MODE_CBC,
        tid + "\x00\x00\x00\x00\x00\x00\x00\x00",
    ).decrypt(enckey)
    fh.seek(tmdOff + 518)
    contentCount = struct.unpack(">H", fh.read(2))[0]
    nextContentOffs = 0
    for i in range(contentCount):
        fh.seek(tmdOff + 2820 + 48 * i)
        cId, cIdx, cType, cSize = struct.unpack(">IHHQ", fh.read(16))
        cEnc = 1
        if cType & 1 == 0:
            cEnc = 0
        fh.seek(contentOffs + nextContentOffs)
        if cEnc:
            test = AES.new(
                titkey,
                AES.MODE_CBC,
                to_bytes(cIdx, 2, "big")
                + "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
            ).decrypt(fh.read(512))
        else:
            test = fh.read(512)
        if not test[256:260] == "NCCH":
            print("  Problem parsing CIA content, skipping. Sorry about that :/\n")
            continue
        fh.seek(contentOffs + nextContentOffs)
        ciaHandle = ciaReader(fh, cEnc, titkey, cIdx, contentOffs + nextContentOffs)
        nextContentOffs = nextContentOffs + align(cSize, 64)
        parseNCCH(ciaHandle, cSize, 0, cIdx, tid, 0, 0)


def parseNCSD(fh):
    print(('Parsing NCSD in file "%s":' % os.path.basename(fh.name)))
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
                reverseCtypeArray(header.titleId),
                0,
                1,
            )


def parseNCCH(fh, fsize, offs=0, idx=0, titleId="", standAlone=1, fromNcsd=0):
    tab = "    " if not standAlone else "  "
    if not standAlone and fromNcsd:
        print(("  Parsing %s NCCH" % ncsdPartitions[idx]))
    elif not standAlone:
        print(("  Parsing NCCH %d" % idx))
    else:
        print(('Parsing NCCH in file "%s":' % os.path.basename(fh.name)))
    entries = 0
    data = ""
    fh.seek(offs)
    tmp = fh.read(512)
    header = ncchHdr(tmp)
    if titleId == "":
        titleId = reverseCtypeArray(header.programId)
    ncchKeyY = from_bytes(header.signature[:16], "big")
    print((tab + "Product code: " + str(bytearray(header.productCode)).rstrip("\x00")))
    print((tab + "KeyY: %032X" % ncchKeyY))
    print((tab + "Title ID: %s" % reverseCtypeArray(header.titleId)))
    print((tab + "Format version: %d" % header.formatVersion))
    usesExtraCrypto = bytearray(header.flags)[3]
    if usesExtraCrypto:
        print(
            (
                tab
                + "Uses Extra NCCH crypto, keyslot 0x%X"
                % {1: 37, 10: 24, 11: 27}[usesExtraCrypto]
            )
        )
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
    base += ".%s.ncch" % (idx if fromNcsd == 0 else ncsdPartitions[idx])
    base = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), base)
    with open(base, "wb") as (f):
        fh.seek(offs)
        tmp = fh.read(512)
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


def dumpSection(
    f, fh, offset, size, t, ctr, usesExtraCrypto, fixedCrypto, encrypted, keyYs
):
    cryptoKeys = {0: 0, 1: 1, 10: 2, 11: 3}
    sections = ["ExHeader", "ExeFS", "RomFS"]
    print((tab + "%s offset:  %08X" % (sections[(t - 1)], offset)))
    print((tab + "%s counter: %s" % (sections[(t - 1)], hexlify(ctr))))
    print((tab + "%s size: %d bytes" % (sections[(t - 1)], size)))
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
    key0x2C = to_bytes(scramblekey(keys[0][0], keyYs[0]), 16, "big")
    if t == ncchSection.exheader:
        key = key0x2C
        if fixedCrypto:
            key = to_bytes(keys[1][(fixedCrypto - 1)], 16, "big")
        cipher = AES.new(
            key,
            AES.MODE_CTR,
            counter=Counter.new(128, initial_value=from_bytes(ctr, "big")),
        )
        f.write(cipher.decrypt(fh.read(size)))
    if t == ncchSection.exefs:
        key = key0x2C
        if fixedCrypto:
            key = to_bytes(keys[1][(fixedCrypto - 1)], 16, "big")
        cipher = AES.new(
            key,
            AES.MODE_CTR,
            counter=Counter.new(128, initial_value=from_bytes(ctr, "big")),
        )
        exedata = fh.read(size)
        exetmp = cipher.decrypt(exedata)
        if usesExtraCrypto:
            extraCipher = AES.new(
                to_bytes(
                    scramblekey(keys[0][cryptoKeys[usesExtraCrypto]], keyYs[1]),
                    16,
                    "big",
                ),
                AES.MODE_CTR,
                counter=Counter.new(128, initial_value=from_bytes(ctr, "big")),
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
        key = to_bytes(
            scramblekey(keys[0][cryptoKeys[usesExtraCrypto]], keyYs[1]), 16, "big"
        )
        if fixedCrypto:
            key = to_bytes(keys[1][(fixedCrypto - 1)], 16, "big")
        cipher = AES.new(
            key,
            AES.MODE_CTR,
            counter=Counter.new(128, initial_value=from_bytes(ctr, "big")),
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
inpFiles = []
existFiles = []

for i in range(len(sys.argv) - 1):
    inpFiles = inpFiles + glob.glob(sys.argv[(i + 1)].replace("[", "[[]"))

for i in range(len(inpFiles)):
    if os.path.isfile(inpFiles[i]):
        existFiles.append(inpFiles[i])

if existFiles == []:
    print("Input files don't exist")
    sys.exit()

print("")
for file in existFiles:
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
        elif fh.name.split(".")[(-1)].lower() == "cia":
            fh.seek(0)
            if fh.read(4) == "  \x00\x00":
                parseCIA(fh)
                print("")

print("Partitions extracted")
