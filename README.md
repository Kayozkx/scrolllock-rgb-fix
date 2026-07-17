# Scrolllock-rgb-fix

Corrige o efeito RGB de teclados gamer genéricos (que utilizam o LED de Scroll Lock como gatilho de firmware) em sistemas operacionais que rodam GNOME/Wayland. É uma solução definitiva mesmo para versões recentes do Ubuntu (26.04+), onde o suporte a sessões Xorg foi completamente removido pelo GNOME.

---

## Guia

Além de disponibilizar os arquivos prontos para uso, este repositório acompanha o arquivo `RGB_ScrollLock_Ubuntu.pdf` contendo:

* Explicação detalhada e linha por linha de como o script Python interage com o hardware.
* Destrinchamento completo do funcionamento do serviço `systemd`.
* Um histórico passo a passo com os 22 comandos de terminal utilizados para diagnosticar o problema e validar a solução.

Se você deseja aprender como a solução foi construída por baixo dos panos ou precisa dar manutenção caso mude de sistema, o PDF é o seu ponto de partida.

---

## Sobre o Desenvolvimento

A ideia de criar um script em Python para contornar esse problema do RGB partiu de mim. Porém, como não tenho conhecimento suficiente na linguagem Python para escrevê-lo do zero, o código foi desenvolvido através de *vibe coding* com a ajuda da inteligência artificial Claude. Essa parceria serviu para tirar a ideia da minha mente e transformá-la neste script que funciona perfeitamente.

---

## O Problema

Muitos kits de teclado gamer de baixo custo não possuem software de controle próprio para Linux. O efeito RGB é ativado pelo próprio firmware do hardware sempre que o LED padrão de Scroll Lock é aceso pelo sistema operacional. Isso funciona perfeitamente no Windows ou no console de texto puro (TTY) do Linux.

No entanto, o GNOME rodando sob o protocolo Wayland não sincroniza as mudanças de estado do LED de Scroll Lock com o dispositivo físico. Como o GNOME 49+ removeu de vez o suporte ao Xorg, não é mais possível contornar o problema apenas alterando a sessão gráfica.

---

## A Solução

Este projeto implementa um serviço leve em Python que roda em segundo plano e resolve o problema falando diretamente com o kernel do Linux:

* **Busca Dinâmica:** Encontra de forma automática o teclado correto e o LED de Scroll Lock em `/sys/class/leds/` e `/dev/input/`, garantindo o funcionamento mesmo que os índices mudem após reiniciar o PC.
* **Intercepção via evdev:** Monitora os eventos de pressionamento de tecla em tempo real.
* **Escrita Direta:** Ao detectar o acionamento do Scroll Lock, altera manualmente o arquivo `/brightness` do LED, ativando o firmware do RGB.
* **Contenção de Conflitos:** Monitora se o GNOME resetou o LED devido ao uso do Caps Lock ou Num Lock e força o estado correto de volta.
* **Automação:** Roda silenciosamente gerenciado pelo `systemd`, iniciando sozinho junto com o boot do sistema.

---

## Requisitos

* Ubuntu / GNOME em Wayland (Testado e validado no Ubuntu 26.04 LTS)
* Biblioteca do sistema `python3-evdev`
* Teclado cujo circuito RGB dependa fisicamente do estado do LED de Scroll Lock

---

## Instalação e Configuração

Siga os passos abaixo no seu terminal para clonar o repositório e instalar o serviço no seu sistema.

### 1. Clonar o repositório e instalar dependências

```bash
# Clone o projeto para a sua máquina
git clone https://github.com/Kayozkx/scrolllock-rgb-fix.git

# Acesse a pasta do projeto
cd scrolllock-rgb-fix

# Instale a biblioteca evdev necessária para o Python
sudo apt install python3-evdev
```

### 2. Copiar os arquivos para os diretórios do sistema

```bash
# Mova o script Python para o diretório de binários locais e dê permissão de execução
sudo cp scrolllock-rgb.py /usr/local/bin/scrolllock-rgb.py
sudo chmod +x /usr/local/bin/scrolllock-rgb.py

# Mova o arquivo de configuração do serviço para o systemd
sudo cp scrolllock-rgb.service /etc/systemd/system/scrolllock-rgb.service
```

### 3. Ativar e iniciar o serviço automático

```bash
# Recarregue as configurações do systemd para reconhecer o novo serviço
sudo systemctl daemon-reload

# Ative para iniciar no boot e inicialize o serviço agora mesmo
sudo systemctl enable --now scrolllock-rgb.service
```

---

## Verificando o Funcionamento

Após a instalação, você pode testar pressionando a tecla Scroll Lock para ver o RGB ligar e desligar.

Se quiser confirmar se o serviço está operando corretamente em segundo plano, utilize os comandos abaixo:

```bash
# Verificar se o status atual do serviço é "active (running)"
systemctl status scrolllock-rgb.service --no-pager

# Monitorar os logs gerados pelo script em tempo real
journalctl -u scrolllock-rgb.service --no-pager
```

Experimente apertar as teclas Caps Lock ou Num Lock repetidamente para garantir que o GNOME não vai quebrar ou derrubar o estado atual do seu RGB.

---

## Como funciona por baixo dos panos

O kernel do Linux expõe o controle do LED de Scroll Lock através de um arquivo localizado em:

```text
/sys/class/leds/<dispositivo>::scrolllock/brightness
```

Escrever o valor `1` ou `0` neste arquivo acende ou apaga o LED (e o circuito do RGB acoplado a ele) instantaneamente, sem precisar de permissões da interface gráfica.

O script automatiza essa tarefa interceptando os sinais enviados ao arquivo `/dev/input/eventX` do teclado e realizando a escrita direta no sistema de arquivos do kernel (sysfs), contornando de forma limpa qualquer limitação imposta pelo Wayland.
