# Deskbee Booking Automation

Automação em Python para agendamento programado de estações de trabalho na plataforma Deskbee via API REST, com execução serverless agendada via GitHub Actions.

---

## 📌 Visão Geral

O objetivo deste projeto é automatizar a reserva recorrente de mesas de trabalho corporativas, operando dentro da janela de antecedência máxima permitida pela política da plataforma (15 dias corridos).

A aplicação realiza a autenticação via JWT, varre os próximos 15 dias úteis, trata colisões de agendamento e implementa uma estratégia de *fallback* em cascata para alocação de estações prioritárias.

---

## 🏗️ Arquitetura e Fluxo de Execução

```
[GitHub Actions (Cron: 00:01 BRT)]
               │
               ▼
       [main.py: POST /api/auth/login] ──► Retorna Bearer Token
               │
               ▼
   [Cálculo de Janela: D+1 até D+15]
               │
               ├── (Ignora Sábado/Domingo)
               │
               ▼
  [Loop de Fallback de Mesas (74 -> 73 -> 72)]
               │
               ├── Status 200/201 ──► Reserva Confirmada (Break)
               ├── Status 412      ──► Já Reservado / Indisponível (Próxima)
               └── Status 4xx/5xx  ──► Trata Exceção e Continua
```

---

## 🚀 Funcionalidades

- **Autenticação Dinâmica:** Sessão autenticada via endpoint `/api/auth/login` gerando token JWT de curta duração.
- **Janela Deslizante (Rolling Window):** Cálculo automático de datas futuras utilizando `datetime` e `timedelta`.
- **Filtro de Dias Úteis:** Validação de dias da semana para evitar requisições desnecessárias aos finais de semana.
- **Estratégia de Fallback:** Priorização de mesas configurada em lista ordenada. Se a mesa primária estiver ocupada, o algoritmo tenta a próxima candidata imediatamente.
- **Execução Serverless (Zero Infra):** Agendamento diário às 00:01 (Horário de Brasília) via GitHub Actions sem dependência de máquina local.
- **Gestão Segura de Credenciais:** Nenhuma credencial trafega em código-fonte; variáveis sensíveis são injetadas via GitHub Secrets / Env Vars.

---

## 🛠️ Stack Tecnológica

- **Linguagem:** Python 3.11+
- **HTTP Client:** `requests`
- **Manipulação de Tempo:** `datetime` (stdlib)
- **CI/CD & Scheduler:** GitHub Actions (Cron triggers)

---

## ⚙️ Configuração e Execução Local

### Pré-requisitos
- Python 3.10+
- Gerenciador de pacotes `pip`

### 1. Clonar o repositório
```bash
git clone https://github.com/DevBolfarini/automacao_deskbee.git
cd automacao_deskbee
```

### 2. Criar e ativar o ambiente virtual
```bash
# Linux/macOS
python3 -m venv .venv
source .venv/bin/activate

# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Instalar dependências
```bash
pip install -r requirements.txt # ou pip install requests
```

### 4. Configurar Variáveis de Ambiente
Defina as variáveis de ambiente no seu terminal ou em um arquivo `.env`:

```bash
export DESKBEE_ACCOUNT="sua_organizacao"
export DESKBEE_EMAIL="seu.email@empresa.com"
export DESKBEE_PASSWORD="sua_senha"
```

No Windows (PowerShell):
```powershell
$env:DESKBEE_ACCOUNT="sua_organizacao"
$env:DESKBEE_EMAIL="seu.email@empresa.com"
$env:DESKBEE_PASSWORD="sua_senha"
```

### 5. Executar
```bash
python main.py
```

---

## ☁️ Configuração do CI/CD (GitHub Actions)

O workflow está configurado em `.github/workflows/reservar.yml`.

### Secrets Necessários
Acesse `Settings > Secrets and variables > Actions` no repositório do GitHub e adicione:

| Secret | Descrição | Exemplo |
| :--- | :--- | :--- |
| `DESKBEE_ACCOUNT` | Slug/identificador da organização | `sua_organizacao` |
| `DESKBEE_EMAIL` | E-mail corporativo cadastrado | `usuario@empresa.com` |
| `DESKBEE_PASSWORD` | Senha da conta Deskbee | `********` |

### Disparo do Cron
O agendamento roda de domingo a quinta-feira às `03:01 UTC` (`00:01 Horário de Brasília`):
```yaml
on:
  schedule:
    - cron: '1 3 * * *'
  workflow_dispatch: # Permite disparo manual
```

---

## 📡 Endpoints Mapeados (Referência de API)

### 1. Login
- **Endpoint:** `POST https://api.deskbee.io/api/auth/login`
- **Body:**
  ```json
  {
    "account": "string",
    "email": "string",
    "password": "string",
    "turnstile_token": ""
  }
  ```
- **Response:** `data.access_token` (JWT)

### 2. Reserva (Booking)
- **Endpoint:** `POST https://api.deskbee.io/api/bookings`
- **Header:** `Authorization: Bearer <access_token>`
- **Body:**
  ```json
  {
    "uuid": "string (UUID da mesa)",
    "start_date": "DD/MM/YYYY",
    "start_hour": "09:00",
    "end_date": "DD/MM/YYYY",
    "end_hour": "18:00",
    "reason": "",
    "booking_uuid_identifier": null
  }
  ```
- **Response:** `data.booking_uuid`

---

## 📄 Licença

Projeto desenvolvido para fins de estudo, automação de produtividade e portfólio técnico.
