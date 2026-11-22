# Zero · Guía estructurada para formar un compañero que puede hacer de todo en tu PC

## 0. Principio base
Un compañero (no una herramienta) se define por 3 cosas:
1. **Persona estable** (prompt versionado, tono, valores) — quién es.
2. **Capacidades amplias** (tools sobre el sistema) — qué puede hacer.
3. **Auto-mejora controlada** (aprende sin perder identidad) — cómo crece.

## 1. Capas (de abajo a arriba)
| Capa | Responsabilidad | Ejemplo Zero |
|------|-----------------|--------------|
| L0 · Sistema | SO, archivos, procesos, red | shell, filesystem, registry |
| L1 · Tools | Acciones atómicas con permiso | run_command, read_file, click, type |
| L2 · Brains | Razonamiento por dominio | repo_brain, system_brain, companion_brain |
| L3 · Router/Intents | Decide qué brain y qué tools | intents/* modulares |
| L4 · Memoria | Corto plazo (chat) + largo plazo (facts/prefs) | memory/*.json + SQLite FTS |
| L5 · Companion | Persona + prompt versionado + estilo | prompts/companion_v*.txt |
| L6 · Self-improve | Feedback → ajustes acotados | self_improve.py |

## 2. Cómo formar el compañero (pasos)
### A. Definir la persona (raíz)
- Escribe `prompts/companion_v1.txt`: nombre, tono, valores, límites, estilo de respuesta.
- Versiona (v1, v2...). Nunca sobrescribas; crea nueva versión y registra cambio.
- El companion_brain SIEMPRE antepone la persona al contexto.

### B. Capacidades amplias (tools)
- Expón tools atómicas: shell, file read/write, browser, apps, system (volume, windows), GitHub, RAG.
- Cada tool declara: nombre, schema, riesgo (read/write/destructive), confirmación requerida.
- Un "executor" central valida permisos antes de ejecutar.

### C. Memoria
- Corto plazo: últimos N turnos de chat.
- Largo plazo: hechos del usuario, preferencias, proyectos, repos activos.
- Índice (FTS + embeddings) para retrieval relevante.

### D. Verificación flexible (evitar alucinación)
- No exigir 2 fuentes rígidas. Exigir: contexto recuperado con score ≥ umbral.
- Si el retrieval es débil → decir "no tengo suficiente contexto" + proponer qué indexar.
- Marcar afirmaciones con fuente cuando sea posible.

### E. Auto-mejora controlada
- Capturar señales: correcciones del usuario, thumbs up/down, tareas completadas/fallidas, tiempo.
- Aplicar solo ajustes acotados: añadir ejemplos al prompt, nuevos sinónimos de intents, ajustar umbral de retrieval.
- Nunca cambiar la persona base sin aprobación; solo "capa de estilo" (v1.1, v1.2...).
- Log de cambios en `memory/improvement_log.json` (auditable, reversible).

### F. Router modular (evitar monolito)
- Un router ligero clasifica por dominio (repo, system, chat, memory).
- Cada dominio tiene su módulo de intents.
- Añadir un dominio = añadir un módulo, no tocar el router grande.

## 3. Seguridad
- Permisos mínimos por acción; destructivo siempre pide confirmación.
- No indexar secretos (.env, tokens, DBs).
- Sandboxing de shell (allowlist de comandos, working dir controlado).
- Auditoría de acciones en log.

## 4. Métricas de mejora
- Tasa de correcciones del usuario (↓ mejor).
- Tareas completadas sin intervención (↑ mejor).
- Alucinaciones detectadas (↓ mejor).
- Latencia y coste (↓ mejor).

## 5. Roadmap Zero
1. Companion core (prompt versionado) ← Fase 1 (en curso)
2. Self-improvement loop (feedback → ajustes) ← Fase 2
3. Repo RAG (indexar repos) ← Fase 3
4. Brains modulares (repo/system/companion) ← Fase 4
5. Router modular por dominio ← Fase 5
6. UI de memoria/prompts/mejora ← Fase 6
7. Tools de sistema (shell, files, apps, browser) ← Fase 7

## 6. Anti-patrones a evitar (lecciones de Wukong)
- Un solo archivo de intents gigante.
- Verificación rígida de 2 fuentes web.
- Prompts ad-hoc sin versión.
- Aprendizaje que toca el core sin auditoría.
- Tools sin permisos ni confirmación.
