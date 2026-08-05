# Guida Installazione - Nexus Infinity Real

## 🚀 Avvio Automatico (Consigliato)

### Windows

1. **Scarica il repository**
   - Clicca su `Code` → `Download ZIP`
   - Estrai la cartella

2. **Doppio click su `START_NEXUS.bat`**
   - Lo script farà tutto automaticamente:
     - ✅ Verifica Python
     - ✅ Clona il repository (se necessario)
     - ✅ Crea ambiente virtuale
     - ✅ Installa dipendenze
     - ✅ Configura .env
     - ✅ Avvia il sistema

3. **Scegli la modalità:**
   - `1` → CLI Interattiva
   - `2` → API Server (http://localhost:8000)
   - `3` → Entrambi in parallelo

### macOS / Linux

```bash
# Rendi lo script eseguibile
chmod +x start.sh

# Esegui
./start.sh
```

## 📋 Prerequisiti

- **Python 3.8+** (scarica da https://www.python.org)
- **Git** (opzionale, per clonare il repo)
- **Chiave Groq API** (ottieni da https://console.groq.com)

## ⚙️ Configurazione Manuale

Se preferisci setup manuale:

```bash
# 1. Crea ambiente virtuale
python -m venv venv

# 2. Attiva venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Installa dipendenze
pip install -r requirements.txt

# 4. Configura .env
cp .env.example .env
# Modifica .env e aggiungi la tua chiave Groq

# 5. Esegui
python main.py
```

## 🔑 Configurazione Chiave Groq

1. Vai a https://console.groq.com
2. Crea una nuova API Key
3. Copia la chiave
4. Modifica il file `.env`:
   ```
   GROQ_API_KEY=your_key_here
   ```

## 🎯 Utilizzo

### CLI Interattiva
```bash
python main.py
```

Digita i tuoi messaggi e ricevi risposte da Groq in tempo reale.

### API Server
```bash
python api_server.py
```

Accedi a:
- **Documentazione interattiva**: http://localhost:8000/docs
- **Endpoint chat**: POST http://localhost:8000/api/chat
- **Status**: GET http://localhost:8000/api/status

### Esempio API
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Ciao, come stai?",
    "system_prompt": "Sei un assistente AI amichevole"
  }'
```

## 🐛 Troubleshooting

### "Python non trovato"
- Installa Python da https://www.python.org
- Assicurati di selezionare "Add Python to PATH"
- Riavvia il computer

### "GROQ_API_KEY not found"
- Verifica che il file `.env` esista
- Controlla che la chiave sia corretta
- Riavvia lo script

### "Port 8000 already in use"
- Cambia la porta in `.env`:
  ```
  API_PORT=8001
  ```

### "Connection refused"
- Verifica che l'API server sia in esecuzione
- Controlla il firewall
- Prova `http://127.0.0.1:8000` invece di `localhost`

## 📚 File Importanti

| File | Descrizione |
|------|-------------|
| `START_NEXUS.bat` | Avvio automatico completo (Windows) |
| `start.bat` | Alias rapido |
| `QUICK_INSTALL.bat` | Setup veloce |
| `main.py` | CLI interattiva |
| `api_server.py` | API REST FastAPI |
| `.env` | Configurazione (crea da .env.example) |
| `requirements.txt` | Dipendenze Python |

## 🔗 Link Utili

- **GitHub**: https://github.com/Lucifer-AI-666/nexus-infinity-real
- **Groq Console**: https://console.groq.com
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Python Docs**: https://docs.python.org

## 💡 Tips

- Usa `QUICK_INSTALL.bat` per setup veloce senza menu
- Usa `START_NEXUS.bat` per menu interattivo
- Prova l'API con Postman o Insomnia
- Leggi i log per debug

## 📞 Supporto

Se hai problemi:
1. Controlla il file `.env`
2. Verifica che Python sia installato
3. Leggi i messaggi di errore
4. Consulta il README.md

---

**Buon utilizzo di Nexus Infinity Real! 🚀**
