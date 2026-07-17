# Scrolllock-rgb-fix

Corrige o RGB de teclados gamer genéricos (que usam o LED de **Scroll Lock**
como gatilho de firmware) em sistemas **GNOME/Wayland**, onde o compositor
não sincroniza esse LED com o hardware — mesmo em versões recentes do
Ubuntu (26.04+), onde o GNOME removeu completamente o suporte a Xorg.

## Sobre o Desenvolvimento

A ideia de criar um script em Python para contornar esse problema do RGB partiu de mim. 
Porém, como não tenho conhecimento suficiente na linguagem Python para escrevê-lo do zero,o código foi desenvolvido através de *vibe coding* com a ajuda da inteligência artificial **Claude**. 
Essa parceria serviu para tirar a ideia da minha mente e transformá-la neste script que funciona perfeitamente.

## O problema

Muitos kits de teclado gamer baratos não têm software próprio no Linux.
O efeito RGB é ligado pelo firmware do próprio teclado sempre que o LED
padrão de **Scroll Lock** é aceso pelo sistema operacional. Isso funciona
normalmente:

- No Windows (via driver do fabricante)
- No console de texto puro do Linux / TTY (o kernel liga o LED direto)

Mas **não funciona** no GNOME rodando em Wayland: o compositor simplesmente
não repassa a mudança de estado do LED de Scroll Lock para o dispositivo
físico. Como o GNOME 49 (Ubuntu 25.10+) removeu de vez o suporte a sessões
Xorg, não dá mais para contornar isso trocando de sessão gráfica.

## A solução

Um pequeno serviço em Python que:

1. Encontra automaticamente o teclado e o LED de Scroll Lock certos em
   `/sys/class/leds/` e `/dev/input/`, então continua funcionando mesmo
   que esses índices mudem entre reinicializações.
2. Escuta os eventos de teclado via `evdev`.
3. Toda vez que **Scroll Lock** é pressionado, inverte o estado do LED
   manualmente (escrevendo em `/sys/class/leds/.../brightness`), o que
   aciona o RGB no firmware do teclado.
4. Corrige o LED de volta caso o GNOME o "resete" sem querer ao mudar
   Caps Lock ou Num Lock.
5. Roda como serviço `systemd`, iniciando sozinho no boot.

## Requisitos

- Ubuntu / GNOME em Wayland (testado no Ubuntu 26.04 LTS)
- `python3-evdev`
- Um teclado cujo RGB seja realmente disparado pelo LED de Scroll Lock
  (comum em kits gamer genéricos vendidos como "semi mecânico RGB")

## Instalação

```bash
# 1. Instala a dependência
sudo apt install python3-evdev

# 2. Copia o script
sudo cp scrolllock-rgb.py /usr/local/bin/scrolllock-rgb.py
sudo chmod +x /usr/local/bin/scrolllock-rgb.py

# 3. Instala o serviço
sudo cp scrolllock-rgb.service /etc/systemd/system/scrolllock-rgb.service
sudo systemctl daemon-reload
sudo systemctl enable --now scrolllock-rgb.service
```

## Verificando

```bash
# Ver se está rodando
systemctl status scrolllock-rgb.service --no-pager

# Ver logs
journalctl -u scrolllock-rgb.service --no-pager
```

Aperte Scroll Lock — o RGB deve ligar/desligar. Teste também Caps Lock e
Num Lock para confirmar que eles não derrubam o estado do RGB.

## Como funciona por baixo dos panos

O LED de Scroll Lock existe no kernel como um arquivo em
`/sys/class/leds/<algo>::scrolllock/brightness`. Escrever `1` ou `0` nesse
arquivo liga/desliga o LED (e, no caso desses teclados, o efeito RGB
junto), independente de qualquer coisa que o ambiente gráfico faça. Este
projeto simplesmente automatiza essa escrita, reagindo ao evento de tecla
capturado diretamente do dispositivo `/dev/input/eventX`, sem depender do
GNOME/Wayland sincronizar nada sozinho.
