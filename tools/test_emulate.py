#!/usr/bin/env python3
"""Emula o trecho alterado do firmware e confere o resultado.

Requer: pip install unicorn
Uso   : python3 test_emulate.py <uf2 oficial>

Executa as instruções de 0x1005DB20 a 0x1005DB28 (o desvio e o bloco novo)
num Cortex-M0+ emulado, com valores simulados nas portas, e verifica que:
  - r3 sai com exatamente os bits dos botões físicos pressionados;
  - pinos sem função (não configurados como SIO) nunca acendem LED;
  - o estado do gamepad (funções) não influencia o resultado;
  - nenhum outro registrador nem a pilha são alterados.
"""
import random
import struct
import sys

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_MCLASS, UC_MODE_THUMB
from unicorn.arm_const import (
    UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_R4,
    UC_ARM_REG_R5, UC_ARM_REG_R6, UC_ARM_REG_R7, UC_ARM_REG_R8, UC_ARM_REG_R10, UC_ARM_REG_SP,
)

import build_ledporpino as b

HOOK = b.BASE + b.HOOK
KEEP = {
    UC_ARM_REG_R0: 0x11111111, UC_ARM_REG_R1: 0x22222222, UC_ARM_REG_R4: 0x44444444,
    UC_ARM_REG_R5: 0x55555555, UC_ARM_REG_R6: 0x66666666, UC_ARM_REG_R7: 0x77777777,
    UC_ARM_REG_R8: 0x88888888, UC_ARM_REG_R10: 0xAAAAAAAA,
}


def run(img, pressed, dpad=0, buttons=0, no_function=()):
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    mu.mem_map(b.BASE, 0x200000)
    mu.mem_write(b.BASE, bytes(img))
    mu.mem_map(0x20000000, 0x10000)   # RAM
    mu.mem_map(0xD0000000, 0x1000)    # SIO
    mu.mem_map(0x40014000, 0x1000)    # IO_BANK0
    gpio = 0x3FFFFFFF
    for pin in pressed:
        gpio &= ~(1 << pin)           # pressionado = nível baixo
    mu.mem_write(0xD0000004, struct.pack("<I", gpio))
    for pin in range(30):
        mu.mem_write(0x40014004 + 8 * pin, struct.pack("<I", 31 if pin in no_function else 5))
    gamepad = 0x20001000
    mu.mem_write(gamepad + 4, bytes([dpad]))
    mu.mem_write(gamepad + 8, struct.pack("<I", buttons))
    for reg, val in KEEP.items():
        mu.reg_write(reg, val)
    mu.reg_write(UC_ARM_REG_R2, gamepad)
    mu.reg_write(UC_ARM_REG_SP, 0x20008000)
    mu.emu_start(HOOK | 1, HOOK + 8, count=2000)
    assert mu.reg_read(UC_ARM_REG_PC) == HOOK + 8
    assert mu.reg_read(UC_ARM_REG_SP) == 0x20008000
    for reg, val in KEEP.items():
        assert mu.reg_read(reg) == val
    return mu.reg_read(UC_ARM_REG_R3)


def expected(pressed, no_function=()):
    value = 0
    for pin, bit in zip(b.STRIP_PINS, b.STRIP_BITS):
        if pin in pressed and pin not in no_function:
            value |= 1 << bit
    return value


def main():
    img = b.build(open(sys.argv[1], "rb").read())
    random.seed(1)
    cases = [set(), set(b.STRIP_PINS), set(range(30))]
    cases += [{pin} for pin in range(30)]
    cases += [set(random.sample(range(30), random.randint(1, 12))) for _ in range(150)]
    n = 0
    for pressed in cases:
        for dpad, buttons in ((0, 0), (15, 0xFFFFFFFF), (5, 0x3000)):
            assert run(img, pressed, dpad, buttons) == expected(pressed), pressed
            n += 1
    for no_function in ({9}, {18, 26}, set(b.STRIP_PINS)):
        assert run(img, set(range(30)), no_function=no_function) == expected(set(range(30)), no_function)
        n += 1
    print("ok: %d casos" % n)


if __name__ == "__main__":
    main()
