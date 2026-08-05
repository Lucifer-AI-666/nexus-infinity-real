#!/usr/bin/env python3
"""
Nexus Infinity Real - Sistema Operativo per Agenti AI
Integrazione Groq per intelligenza ultra-veloce
"""

import os
import sys
from dotenv import load_dotenv
from groq import Groq

# Carica variabili d'ambiente
load_dotenv()

class NexusInfinityCore:
    """Core principale di Nexus Infinity con Groq"""
    
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY non configurato in .env")
        
        self.client = Groq(api_key=self.groq_api_key)
        self.conversation_history = []
        self.model = "llama-3.3-70b-versatile"
        
    def chat(self, user_message: str, system_prompt: str = None) -> str:
        """Invia un messaggio a Groq e riceve una risposta"""
        
        if system_prompt is None:
            system_prompt = """Sei Nexus Infinity, un sistema operativo intelligente per agenti AI.
            Sei esperto in: automazione, sicurezza, analisi dati, orchestrazione di task.
            Rispondi in modo conciso e professionale."""
        
        # Aggiungi il messaggio alla cronologia
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        try:
            # Chiama Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *self.conversation_history
                ],
                temperature=0.7,
                max_tokens=1024,
            )
            
            # Estrai la risposta
            assistant_message = response.choices[0].message.content
            
            # Aggiungi alla cronologia
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            return assistant_message
            
        except Exception as e:
            return f"Errore: {str(e)}"
    
    def run_interactive(self):
        """Modalità interattiva"""
        print("=" * 60)
        print("🚀 NEXUS INFINITY REAL - Sistema Operativo AI")
        print("=" * 60)
        print("Digita 'exit' per uscire\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() == "exit":
                    print("Arrivederci! 👋")
                    break
                
                if not user_input:
                    continue
                
                response = self.chat(user_input)
                print(f"\nNexus: {response}\n")
                
            except KeyboardInterrupt:
                print("\n\nInterrotto dall'utente.")
                break
            except Exception as e:
                print(f"Errore: {e}")

def main():
    """Punto di ingresso principale"""
    try:
        nexus = NexusInfinityCore()
        nexus.run_interactive()
    except ValueError as e:
        print(f"❌ Errore di configurazione: {e}")
        print("\nAssicurati di avere un file .env con GROQ_API_KEY configurato")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Errore: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
