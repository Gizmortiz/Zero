# Zero

Mascota de escritorio basada en repositorios de GitHub.

## Ejecutar
```
pip install -r requirements.txt
python main.py
```

## Uso
1. La mascota flotante (Zero) aparece abajo a la derecha. Clic para abrir chat.
2. En la ventana, pestaña **Repos**: escribe `owner/repo` (ej. `anomalyco/opencode`) y pulsa **Cargar**.
3. El contexto del repo (README + árbol de archivos) se carga.
4. En **Chat**, pregunta sobre el repo. Zero responde con el contexto.
5. **Ajustes**: el token de GitHub ya está configurado. Opcionalmente configura un modelo LLM (OpenAI-compatible) para respuestas generadas; sin modelo, Zero muestra el contexto del repo.

## Estructura
- `core/github_client.py` — API de GitHub
- `core/chat_engine.py` — contexto de repo + LLM opcional
- `interfaces/` — ventanas (maestra, chat, repos, ajustes, mascota)
- `assets/zero/sprites/` — sprites de la mascota
- `database/settings/zero.json` — token y modelo
