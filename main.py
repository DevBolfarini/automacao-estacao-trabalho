import os
import requests
from datetime import datetime, timedelta

# Tenta carregar o .env para testes locais no seu PC
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # No GitHub Actions, ignora se não tiver dotenv instalado

# URLs da API
URL_LOGIN = "https://api.deskbee.io/api/auth/login"
URL_BOOKINGS = "https://api.deskbee.io/api/bookings"
# Lê exclusivamente das variáveis de ambiente (injetadas via GitHub Secrets ou .env)
ACCOUNT = os.getenv("DESKBEE_ACCOUNT")
EMAIL = os.getenv("DESKBEE_EMAIL")
PASSWORD = os.getenv("DESKBEE_PASSWORD")

# Lista de mesas na ordem de prioridade (Fallback)
MESAS_PRIORIDADE = [
    {"nome": "EST 2.074", "uuid": "8a2ba8a3-5918-4f22-ab9b-692d2131466d"},
    {"nome": "EST 2.073", "uuid": "85c798f8-6ed2-4c40-b0b0-a5a4b807e85b"},
    {"nome": "EST 2.072", "uuid": "e7daa2af-ccc8-4001-9053-d650da7422b9"},
]

HORA_INICIO = "09:00"
HORA_FIM = "18:00"

def fazer_login(email, password, account):
    payload = {
        "account": account,
        "email": email,
        "password": password,
        "turnstile_token": ""
    }

    print(f"[*] Fazendo login para: {email}...")
    resposta = requests.post(URL_LOGIN, json=payload)

    if resposta.status_code == 200:
        dados = resposta.json()
        token = dados.get("data", {}).get("access_token")
        print("[+] Login realizado com sucesso!")
        return token
    else:
        print(f"[-] Erro no login. Código: {resposta.status_code}")
        print("Detalhes:", resposta.text)
        return None

def calcular_data_alvo(dias_a_frente=15):
    """
    Calcula a data exata de daqui a 15 dias e formata para 'DD/MM/YYYY'.
    """
    # 1. Soma a quantidade de dias à data atual
    data_alvo = datetime.now() + timedelta(days=dias_a_frente)
    
    # 2. Converte para o formato de texto que o Deskbee espera (ex: "31/08/2026")
    data_formatada = data_alvo.strftime("%d/%m/%Y")
    
    # 3. Identifica o dia da semana (0 = Segunda, 5 = Sábado, 6 = Domingo)
    dia_semana = data_alvo.weekday()
    nomes_dias = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
    
    print(f"[*] Data calculada ({dias_a_frente} dias à frente): {data_formatada} ({nomes_dias[dia_semana]})")
    return data_formatada, dia_semana

def agendar_mesa(token, mesa_uuid, data_str, hora_inicio, hora_fim):
    """
    Dispara o POST para criar a reserva da mesa usando o Bearer Token.
    """
    # Cabeçalhos com o Token de autorização
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Corpo da requisição com os dados do agendamento
    payload = {
        "uuid": mesa_uuid,
        "start_date": data_str,
        "start_hour": hora_inicio,
        "end_date": data_str,
        "end_hour": hora_fim,
        "reason": "",
        "booking_uuid_identifier": None
    }

    resposta = requests.post(URL_BOOKINGS, headers=headers, json=payload)
    return resposta

if __name__ == "__main__":
    # 1. Faz login uma única vez e pega o token
    token = fazer_login(EMAIL, PASSWORD, ACCOUNT)
    
    if token:
        print("\n" + "="*50)
        print("🔍 INICIANDO VARREDURA DOS PRÓXIMOS 15 DIAS")
        print("="*50)

        # 2. Loop pelos próximos 15 dias (1 até 15)
        for dias in range(1, 16):
            data_reserva, dia_semana = calcular_data_alvo(dias_a_frente=dias)
            
            # Pula sábados (5) e domingos (6)
            if dia_semana in [5, 6]:
                print(f"⏩ Pulando {data_reserva}: Fim de semana.\n")
                continue  # Vai direto para o próximo dia

            # 3. Tenta reservar as mesas na ordem de prioridade para esta data
            reserva_feita = False
            for mesa in MESAS_PRIORIDADE:
                print(f"[*] Tentando {mesa['nome']} para o dia {data_reserva}...")
                resposta = agendar_mesa(token, mesa["uuid"], data_reserva, HORA_INICIO, HORA_FIM)

                if resposta.status_code in [200, 201]:
                    dados = resposta.json()
                    booking_uuid = dados.get("data", {}).get("booking_uuid")
                    print(f"[🎉] SUCESSO! {mesa['nome']} reservada para {data_reserva}!")
                    print(f"[+] ID da Reserva: {booking_uuid}\n")
                    reserva_feita = True
                    break  # Conseguiu a mesa, parte para o próximo dia!
                else:
                    # Se a API disser que já existe reserva sua nesse dia ou limite atingido
                    print(f"[-] Não foi possível reservar {mesa['nome']}. (Status {resposta.status_code})")
                    # Se você já tem uma reserva nesse dia, interrompe as tentativas para esse dia
                    if "já possui" in resposta.text.lower() or "already" in resposta.text.lower():
                        print(f"[i] Você já tem reserva para o dia {data_reserva}.\n")
                        break

            if not reserva_feita:
                print(f"[-] Nenhuma mesa prioritária disponível para {data_reserva}.\n")

        print("="*50)
        print("🏁 VARREDURA CONCLUÍDA COM SUCESSO!")
        print("="*50)
