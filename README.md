# Nexus Infinity Real

**Sistema Operativo per Agenti AI con Groq Integration**

Un'architettura completa e modulare per orchestrare agenti intelligenti con:
- ⚡ **Groq LPU** per inferenza ultra-veloce
- 🧠 **Llama 3.3 70B** come modello principale
- 🔌 **API REST** con FastAPI
- 🛡️ **Security Layer** integrato
- 📊 **Audit Log** completo
- 🔄 **Action Gate** per approvazioni umane

## Quick Start

### 1. Setup

```bash
# Clona il repository
git clone https://github.com/Lucifer-AI-666/nexus-infinity-real.git
cd nexus-infinity-real

# Crea un ambiente virtuale
python -m venv venv
source venv/bin/activate  # su Windows: venv\Scripts\activate

# Installa le dipendenze
pip install -r requirements.txt
```

### 2. Configurazione

```bash
# Copia il file di esempio
cp .env.example .env

# Aggiungi la tua chiave Groq
# Modifica .env e aggiungi: GROQ_API_KEY=your_key_here
```

### 3. Esecuzione

**Modalità interattiva:**
```bash
python main.py
```

**API Server:**
```bash
python api_server.py
# Accedi a: http://localhost:8000/docs
```

## API Endpoints

### POST `/api/chat`
Invia un messaggio e ricevi una risposta da Groq.

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Ciao, come stai?",
    "system_prompt": "Sei un assistente AI amichevole"
  }'
```

### GET `/api/status`
Verifica lo stato dell'API.

```bash
curl http://localhost:8000/api/status
```

## Architettura

```
nexus-infinity-real/
├── main.py              # CLI interattiva
├── api_server.py        # API REST FastAPI
├── requirements.txt     # Dipendenze Python
├── .env                 # Configurazione (con chiave Groq)
└── README.md           # Questo file
```

## Modelli Disponibili

- **llama-3.3-70b-versatile**: Modello principale (consigliato)
- **mixtral-8x7b-32768**: Alternativa veloce
- **gemma-7b-it**: Modello leggero

## Sicurezza

- ✅ Action Gate per azioni sensibili
- ✅ Audit Log completo
- ✅ Permessi granulari
- ✅ Validazione input/output

## Deployment

### Su Manus Webdev

```bash
# Crea un nuovo progetto webdev
manus webdev create --name nexus-infinity-real --template web-db-user

# Deploya l'API
git push origin main
```

### Su Docker

```bash
docker build -t nexus-infinity-real .
docker run -p 8000:8000 -e GROQ_API_KEY=your_key nexus-infinity-real
```

## Troubleshooting

### "GROQ_API_KEY not found"
- Assicurati di aver configurato il file `.env`
- Verifica che la chiave sia valida su https://console.groq.com

### "Connection refused"
- Verifica che l'API server sia in esecuzione
- Controlla la porta 8000

## Contributi

Questo progetto è mantenuto da Lucifer-AI-666.

## Licenza

MIT License
