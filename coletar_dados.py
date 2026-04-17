import requests
import json
import os
from datetime import datetime, timedelta, timezone

# URIs dos novos assessores da equipe "Vida com CNPJ"
URIs = [
    "https://api.calendly.com/event_types/48317e5c-0fc5-4300-864d-461e1d41e1e2", 
    "https://api.calendly.com/event_types/0921e0cb-89ef-4552-ae93-1c7f91b78a1d"
]

# Mapeamento (As cores não aparecerão na tela final, mas mantemos por estrutura)
MAPA_NOMES = {
    "48317e5c-0fc5-4300-864d-461e1d41e1e2": {"nome": "Ongoing", "cor": "#007bff"},
    "0921e0cb-89ef-4552-ae93-1c7f91b78a1d": {"nome": "Ongoing-2", "cor": "#007bff"}
}

TOKEN = os.getenv("CALENDLY_TOKEN")
headers = {"Authorization": f"Bearer {TOKEN}"}

def obter_horarios():
    eventos_final = []
    agora_utc = datetime.now(timezone.utc)

    for uri in URIs:
        uuid = uri.split('/')[-1]
        info = MAPA_NOMES.get(uuid)
        
        if not info:
            continue # Pula se o UUID não estiver no mapa
            
        # Dividimos em duas buscas para respeitar o limite de 7 dias do Calendly
        # Dividimos em três buscas para nunca ultrapassar o limite de 7 dias por pedido
        intervalos = [
            (agora_utc + timedelta(minutes=1), agora_utc + timedelta(days=7)),         # Hoje até dia 7
            (agora_utc + timedelta(days=7, minutes=1), agora_utc + timedelta(days=14)),  # Dia 7 até dia 14
            (agora_utc + timedelta(days=14, minutes=1), agora_utc + timedelta(days=15))  # Dia 14 até dia 15
        ]
        
        for start_time, end_time in intervalos:
            params = {
                "event_type": uri,
                "start_time": start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                "end_time": end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            }
            
            try:
                res = requests.get("https://api.calendly.com/event_type_available_times", headers=headers, params=params)
                if res.status_code == 200:
                    slots = res.json().get('collection', [])
                    for slot in slots:
                        eventos_final.append({
                            "title": f"Falar com {info['nome']}",
                            "start": slot['start_time'],
                            "url": slot['scheduling_url']
                        })
            except Exception as e:
                print(f"Erro ao processar {info['nome']}: {e}")

    with open("horarios.json", "w") as f:
        json.dump(eventos_final, f, indent=4)
    print("Arquivo horarios.json atualizado com sucesso (10 dias buscados).")

if __name__ == "__main__":
    obter_horarios()
