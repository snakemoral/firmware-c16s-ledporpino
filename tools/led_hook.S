@ Bloco de código anexado ao fim da imagem (Thumb, ARMv6-M / Cortex-M0+).
@ Chamado por "bl" a partir de 0x1005DB20, dentro de NeoPicoLEDAddon::process,
@ no lugar de:
@       ldrb r3, [r2, #4]      @ gamepad->state.dpad
@       ldr  r2, [r2, #8]      @ gamepad->state.buttons
@       lsls r3, r3, #16
@       orrs r3, r2            @ buttonState
@
@ Saída: r3 = buttonState montado a partir dos pinos físicos. Só r2 e r3 são
@ alterados (r2 é recarregado logo depois pelo código original).
@
@ Para cada entrada (pino, bit) da tabela: se o pino está configurado como
@ SIO (ou seja, tem alguma função no mapeamento) e está em nível baixo
@ (pressionado, pull-up), liga o bit correspondente.
@
@ Montagem usada em build_ledporpino.py (CAVE_CODE):
@   arm-none-eabi-as -mcpu=cortex-m0plus -mthumb led_hook.S

    .syntax unified
    .thumb
    push {r0, r1, r4, r5, r6}
    ldr  r1, sio
    ldr  r1, [r1, #4]          @ SIO GPIO_IN
    ldr  r6, iobank            @ IO_BANK0 GPIO0_CTRL
    movs r3, #0
    adr  r4, table
    movs r5, #16
loop:
    ldrb r0, [r4, #0]          @ pino
    lsls r2, r0, #3
    ldr  r2, [r6, r2]          @ GPIOx_CTRL
    lsls r2, r2, #27
    lsrs r2, r2, #27           @ FUNCSEL
    cmp  r2, #5                @ 5 = SIO (pino inicializado como botão)
    bne  next
    movs r2, r1
    lsrs r2, r0
    lsls r2, r2, #31           @ bit do pino
    bne  next                  @ nível alto = solto
    ldrb r0, [r4, #1]          @ bit de buttonState
    movs r2, #1
    lsls r2, r0
    orrs r3, r2
next:
    adds r4, #2
    subs r5, #1
    bne  loop
    pop  {r0, r1, r4, r5, r6}
    bx   lr
    .align 2
sio:    .word 0xd0000000
iobank: .word 0x40014004
table:                          @ pino, bit  (ordem da fita de LED)
    .byte  5, 18   @ LED 1   (mapa de fábrica: Left)
    .byte  3, 17   @ LED 2   (Down)
    .byte  4, 19   @ LED 3   (Right)
    .byte  2, 16   @ LED 4   (Up)
    .byte 10,  2   @ LED 5   (B3)
    .byte 11,  3   @ LED 6   (B4)
    .byte 12,  5   @ LED 7   (R1)
    .byte 13,  4   @ LED 8   (L1)
    .byte  6,  0   @ LED 9   (B1)
    .byte  7,  1   @ LED 10  (B2)
    .byte  8,  7   @ LED 11  (R2)
    .byte  9,  6   @ LED 12  (L2)
    .byte 27, 12   @ LED 13  (A1)
    .byte 18, 10   @ LED 14  (L3)
    .byte 19, 11   @ LED 15  (R3)
    .byte 26, 13   @ LED 16  (A2)
