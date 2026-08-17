# 📘 Guia de Desenvolvimento: Automação Deskbee

Este documento contém todas as informações da API do Deskbee, as regras de negócio do projeto e o passo a passo detalhado para você construir o seu script em Python.

---

## 🎯 Regras de Negócio e Arquitetura

1. **Ciclo de Autenticação (Token):**
   - O e-mail e a senha são enviados **uma única vez** por execução para obter o `access_token`.
   - Todas as ações seguintes (consultar mesas, fazer reserva) usam apenas o `access_token` no cabeçalho.
2. **Cálculo da Data Alvo (Janela de 15 dias):**
   - A reserva deve ser feita para o último dia disponível na janela permitida (hoje + 15 dias).
   - Deve considerar dias úteis (segunda a sexta).
3. **Lista de Preferência de Mesas (Fallback):**
   - **Prioridade 1:** Mesa 74 (`EST 2.074`): `8a2ba8a3-5918-4f22-ab9b-692d2131466d`
   - **Prioridade 2:** Mesa 73 (`EST 2.073`): `85c798f8-6ed2-4c40-b0b0-a5a4b807e85b`
   - **Prioridade 3:** Mesa 72 (`EST 2.072`): `e7daa2af-ccc8-4001-9053-d650da7422b9`
   - Se a principal falhar ou estiver ocupada, tenta a próxima da lista.
4. **Agendamento da Execução:**
   - O script deve ser disparado diariamente às 00:01.

---

## 📌 1. Mapeamento das Requisições HTTP

### 1.1. Login (Autenticação)
* **URL (Endpoint):** `https://api.deskbee.io/api/auth/login`
* **Método:** `POST`
* **Corpo da Requisição (JSON Payload):**
  ```json
  {
    "account": "sua_conta",
    "email": "seu_email",
    "password": "sua_senha",
    "turnstile_token": ""
  }
  ```
* **O que extrair da resposta:**
  - O campo `data.access_token` (token JWT necessário para as chamadas seguintes).

---

### 1.2. Agendamento de Mesa (Booking)
* **URL (Endpoint):** `https://api.deskbee.io/api/bookings`
* **Método:** `POST`
* **Cabeçalhos (Headers):**
  * `Authorization`: `Bearer <SEU_ACCESS_TOKEN>`
  * `Content-Type`: `application/json`
* **Corpo da Requisição (JSON Payload):**
  ```json
  {
    "uuid": "<UUID_DA_MESA>",
    "start_date": "DD/MM/YYYY",
    "start_hour": "09:00",
    "end_date": "DD/MM/YYYY",
    "end_hour": "18:00",
    "reason": "",
    "booking_uuid_identifier": null
  }
  ```
* **Resposta esperada:** `data.booking_uuid` (confirmação do agendamento).
