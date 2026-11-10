Firmware GP2040-CE v0.7.12 para a Haute42 C16S (placa COSMOX M Ultra, RP2040) com os LEDs dos botões ligados ao pino físico, e não à função.

**Arquivo:** `GP2040-CE_0.7.12_Haute42COSMOXMUltra_LedPorPino.uf2`
**SHA-256:** `44faf2d933f52df4c66312736f2fc795eddb221848aabd918a92338758904a66`

## Como instalar

1. Faça o backup da sua configuração na interface web atual.
2. Coloque o controle em modo BOOTSEL e copie o UF2 para ele.
3. Abra a interface web, vá em Configuração → Configuração de LED. Se aparecer o aviso amarelo dizendo que o mapa de LEDs foi corrigido, clique em **Salvar** no fim da página (só uma vez).

Para voltar atrás, grave o UF2 oficial do GP2040-CE pelo BOOTSEL.

## Avisos

- Serve só para esta placa: a ordem da fita de LED está fixa no código.
- O trecho de código alterado foi validado por emulação. Use por sua conta e risco.
- Veja as limitações e a explicação do patch no README.

Não é um projeto oficial do GP2040-CE nem da Haute42. O GP2040-CE é distribuído sob a licença MIT.
