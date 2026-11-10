#!/usr/bin/env python3
"""Gera o firmware "LED por pino" para a Haute42 C16S / COSMOX M Ultra.

Entrada : o UF2 oficial GP2040-CE_0.7.12_Haute42COSMOXMUltra.uf2
          (https://github.com/OpenStickCommunity/GP2040-CE/releases/tag/v0.7.12)
Saída   : GP2040-CE_0.7.12_Haute42COSMOXMUltra_LedPorPino.uf2

O que o patch faz (só biblioteca padrão do Python, nada é recompilado):

1. Código de LED: em NeoPicoLEDAddon::process o firmware calcula
       buttonState = gamepad->state.dpad << 16 | gamepad->state.buttons
   e acende o LED de cada função pressionada. Esse trecho (8 bytes em 0x1005DB20)
   é desviado para um bloco novo no fim da imagem (ver led_hook.S), que monta o
   mesmo valor lendo os 16 pinos direto do SIO. Assim o LED segue o botão
   físico, qualquer que seja a função mapeada nele.

2. Interface web: a seção "ordem dos LEDs" de /led-config é trocada pelo
   componente de led_ui.js, que mostra o desenho do controle e garante o mapa
   de LEDs fixo de que o patch precisa. O JS novo vai para o fim da imagem e a
   entrada do arquivo na tabela do lwIP (fsdata) passa a apontar para ele.

Uso: python3 build_ledporpino.py <uf2 oficial> [uf2 de saída]
"""
import hashlib
import os
import re
import struct
import sys
import zlib

BASE = 0x10000000
RP2040_FAMILY = 0xE48BFF56
OFFICIAL_SHA256 = "6ef14379e95166902ba481b920bdbce318813d9ca9cc0df4cc0ed4e629ce17a6"

# --- endereços no binário oficial 0.7.12 da COSMOX M Ultra -------------------
FS_ROOT = 0xB26D4            # primeiro struct fsdata_file (lista ligada do lwIP)
JS_NAME = b"/assets/index-6038cec7.js"
HOOK = 0x5DB20               # ldrb r3,[r2,#4]; ldr r2,[r2,#8]; lsls r3,#16; orrs r3,r2
HOOK_ORIG = bytes.fromhex("137992681b041343")

# --- fita de LED: posição na fita -> pino do botão físico --------------------
STRIP_PINS = [5, 3, 4, 2, 10, 11, 12, 13, 6, 7, 8, 9, 27, 18, 19, 26]
# Bit de buttonState observado pelo pixel de cada posição, com o mapa de LEDs
# de fábrica: Left, Down, Right, Up, B3, B4, R1, L1, B1, B2, R2, L2, A1, L3, R3, A2
STRIP_BITS = [18, 17, 19, 16, 2, 3, 5, 4, 0, 1, 7, 6, 12, 10, 11, 13]

# Código Thumb (ARMv6-M) de led_hook.S já montado; é independente de posição.
CAVE_CODE = bytes.fromhex(
    "73b40d4949680d4e00230da410252078c200b258d206d20e052a07d10a00c240"
    "d20703d160780122824013430234013dedd173bc704700bf"
)
CAVE_LITERALS = struct.pack("<II", 0xD0000000, 0x40014004)  # SIO, IO_BANK0 GPIO0_CTRL

HERE = os.path.dirname(os.path.abspath(__file__))


def uf2_to_image(data):
    blocks = []
    for i in range(len(data) // 512):
        b = data[i * 512:(i + 1) * 512]
        magic0, magic1, flags, addr, size, _, _, family = struct.unpack("<8I", b[:32])
        if magic0 != 0x0A324655 or magic1 != 0x9E5D5157 or flags & 0x1000:
            continue
        if family != RP2040_FAMILY:
            sys.exit("UF2 não é de RP2040")
        blocks.append((addr, b[32:32 + size]))
    lo = min(a for a, _ in blocks)
    hi = max(a + len(p) for a, p in blocks)
    if lo != BASE:
        sys.exit("endereço inicial inesperado")
    img = bytearray(b"\xff" * (hi - lo))
    for a, p in blocks:
        img[a - lo:a - lo + len(p)] = p
    return img


def image_to_uf2(img):
    n = len(img) // 256
    out = bytearray()
    for i in range(n):
        out += struct.pack("<8I", 0x0A324655, 0x9E5D5157, 0x2000, BASE + i * 256, 256, i, n, RP2040_FAMILY)
        out += img[i * 256:(i + 1) * 256] + b"\0" * 220 + struct.pack("<I", 0x0AB16F30)
    return bytes(out)


def thumb_bl(src, dst):
    """Codifica 'bl dst' (Thumb, 4 bytes) localizado em src."""
    off = dst - (src + 4)
    assert -(1 << 24) <= off < (1 << 24) and off % 2 == 0
    s = (off >> 24) & 1
    i1, i2 = (off >> 23) & 1, (off >> 22) & 1
    j1, j2 = (~(i1 ^ s)) & 1, (~(i2 ^ s)) & 1
    hi = 0xF000 | (s << 10) | ((off >> 12) & 0x3FF)
    lo = 0xD000 | (j1 << 13) | (j2 << 11) | ((off >> 1) & 0x7FF)
    return struct.pack("<HH", hi, lo)


def find_fs_entry(img, name):
    p = FS_ROOT
    while p:
        nxt, name_ptr, data_ptr, length, _flags = struct.unpack_from("<5I", img, p)
        n = name_ptr - BASE
        if bytes(img[n:img.index(b"\0", n)]) == name:
            return p, data_ptr - BASE, length
        p = nxt - BASE if nxt else 0
    sys.exit("arquivo %r não encontrado na tabela fsdata" % name)


def patch_js(js):
    comp = open(os.path.join(HERE, "led_ui.js"), encoding="utf8").read()
    comp = "\n" + "\n".join(l for l in comp.split("\n") if not l.startswith("//")).lstrip("\n")

    def replace_once(text, old, new):
        if text.count(old) != 1:
            sys.exit("trecho esperado não encontrado no JS: %s..." % old[:60])
        return text.replace(old, new)

    js = replace_once(js, "function Nne(){", comp + "function Nne(){")
    js = replace_once(
        js,
        'u.jsx("p",{className:"card-text",children:g("LedConfig:rgb-order.sub-header-text")}),'
        'u.jsx("p",{className:"card-text",children:g("LedConfig:rgb-order.sub-header1-text")}),'
        'u.jsx(hee,{groupName:"test",titles:[g("LedConfig:rgb-order.available-header-text"),'
        'g("LedConfig:rgb-order.assigned-header-text")],dataSources:a,onChange:I=>y(w,I,A.ledsPerButton)})',
        'u.jsx(__LedToggleUI,{ledButtonMap:A.ledButtonMap,labels:a[0].concat(a[1]),'
        'onChange:(m,n)=>{p(n*(A.ledsPerButton||0));w("ledButtonMap",m)}})',
    )
    js = replace_once(js, 'title:g("LedConfig:rgb-order.header-text")', 'title:"LEDs dos botões"')
    return js


def build(official):
    img = uf2_to_image(official)
    orig_len = len(img)

    # 1) interface web: JS novo no fim da imagem, entrada fsdata redirecionada
    entry, data_off, length = find_fs_entry(img, JS_NAME)
    header, _, body = bytes(img[data_off:data_off + length]).partition(b"\r\n\r\n")
    new_js = patch_js(zlib.decompress(body).decode("utf8")).encode("utf8")
    new_body = zlib.compress(new_js, 9)
    blob = re.sub(rb"Content-Length: \d+", b"Content-Length: %d" % len(new_body), header) + b"\r\n\r\n" + new_body
    start = (orig_len + 0xFF) & ~0xFF
    img += b"\xff" * (start - orig_len) + blob
    struct.pack_into("<II", img, entry + 8, BASE + start, len(blob))  # data, len

    # 2) código de LED: bloco novo + desvio
    img += b"\xff" * (-len(img) % 4)
    cave = len(img)
    table = bytes(x for pair in zip(STRIP_PINS, STRIP_BITS) for x in pair)
    img += CAVE_CODE + CAVE_LITERALS + table
    if bytes(img[HOOK:HOOK + 8]) != HOOK_ORIG:
        sys.exit("código no ponto de desvio não é o esperado")
    img[HOOK:HOOK + 8] = thumb_bl(BASE + HOOK, BASE + cave) + bytes.fromhex("00bf00bf")  # bl cave; nop; nop

    img += b"\xff" * (-len(img) % 256)
    return img


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    official = open(sys.argv[1], "rb").read()
    if hashlib.sha256(official).hexdigest() != OFFICIAL_SHA256:
        sys.exit("O UF2 de entrada não é o GP2040-CE_0.7.12_Haute42COSMOXMUltra.uf2 oficial (sha256 diferente).")
    out_path = sys.argv[2] if len(sys.argv) > 2 else "GP2040-CE_0.7.12_Haute42COSMOXMUltra_LedPorPino.uf2"
    img = build(official)
    uf2 = image_to_uf2(img)
    open(out_path, "wb").write(uf2)
    print("gerado %s (%.1f KB de flash usados, sha256 %s)" % (out_path, len(img) / 1024, hashlib.sha256(uf2).hexdigest()))


if __name__ == "__main__":
    main()
