# Guía de setup — agent-testing-digest

Esta guía te lleva desde cero hasta tener el digest corriendo. No hace falta experiencia previa con la terminal.

---

## 1. Pre-requisitos

Antes de empezar, necesitás tener instalado:

**Node.js** (para Claude Code)
- Bajalo desde https://nodejs.org — elegí la versión LTS
- Para verificar que quedó instalado: `node --version`

**Python 3.11 o superior**
- Bajalo desde https://python.org
- Para verificar: `python3 --version`

**Cuentas necesarias:**
- **xAI** — el proyecto usa Grok para generar el digest. Creá una cuenta en https://console.x.ai y generá una API key.
- **GitHub** (opcional pero recomendado) — sin token, la API de GitHub tiene un límite de 60 requests por hora. Con token sube a 5000. Podés crear uno en https://github.com/settings/tokens.

---

## 2. Instalación de Claude Code

Claude Code es la CLI de Anthropic que podés usar para trabajar con este proyecto.

```bash
sudo npm install -g @anthropic-ai/claude-code
```

> **Nota:** `sudo` es necesario porque la instalación es global. Si no lo usás, vas a ver un error de permisos (ver sección de errores comunes).

Para verificar que quedó instalado:

```bash
claude --version
```

---

## 3. Setup del proyecto

**Cloná o descargá el repositorio**, luego abrí una terminal en la carpeta del proyecto.

Creá un entorno virtual de Python (esto aísla las dependencias del proyecto):

```bash
python3 -m venv .venv
```

Activá el entorno virtual:

```bash
# Mac / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

Cuando el entorno está activo, vas a ver `(.venv)` al principio de la línea en la terminal.

Instalá las dependencias:

```bash
pip install -r requirements.txt
```

---

## 4. Configuración del .env

El proyecto necesita un archivo `.env` en la raíz con tus API keys. Ya hay un archivo de ejemplo llamado `.env.example`. Copialo y renombralo:

```bash
cp .env.example .env
```

Abrí `.env` con cualquier editor de texto y completá los valores:

```
# Requerido — tu API key de xAI (https://console.x.ai)
XAI_API_KEY=xai-tu-clave-real-acá

# Opcional — token de GitHub para aumentar el rate limit
# Crealo en: https://github.com/settings/tokens
# Permisos necesarios: "repo" (si querés monitorear repos privados) o "public_repo" (solo públicos)
GITHUB_TOKEN=ghp_tu-token-acá

# Opcional — cuántos días hacia atrás buscar (por defecto: 1)
LOOKBACK_DAYS=1

# Opcional — puntaje mínimo de relevancia para incluir un item (por defecto: 2)
MIN_SCORE=2

# Opcional — máximo de items por fuente antes del ranking (por defecto: 30)
MAX_ITEMS_PER_SOURCE=30
```

Guardá el archivo. **No lo subas a Git** — ya está en el `.gitignore`.

---

## 5. Cómo correr el digest

Con el entorno virtual activo, desde la raíz del proyecto:

```bash
python main.py
```

El digest del día se genera en `reports/digest_YYYY-MM-DD.md`.

Si querés correrlo para una fecha específica:

```bash
python main.py --date 2024-01-15
```

---

## 6. Errores comunes

### `EACCES: permission denied` al instalar Claude Code

**Causa:** falta el `sudo` en el comando de instalación.

**Solución:**
```bash
sudo npm install -g @anthropic-ai/claude-code
```

---

### `load_dotenv()` no carga el `.env` / `KeyError: 'XAI_API_KEY'`

**Causa:** cuando `load_dotenv()` se llama sin una ruta explícita, busca el `.env` relativo al directorio de trabajo actual — si corrés el script desde otra carpeta, no lo encuentra.

**Solución:** este proyecto ya usa una ruta absoluta en `config.py` (`ROOT_DIR / ".env"`), así que no debería pasar. Si lo ves igual, verificá que el archivo `.env` existe en la raíz del proyecto (no dentro de `sources/` ni en otro lado) y que tiene el nombre exacto `.env` (no `.env.txt`).

---

### Token de GitHub con length 14 — `[debug] Token length: 14`

**Causa:** copiaste el placeholder `ghp_...` del `.env.example` en lugar de tu token real. `ghp_...` tiene exactamente 7 caracteres, "Bearer " más eso da 14.

**Solución:** abrí `.env` y reemplazá `ghp_...` con tu token real de GitHub. Los tokens de GitHub tienen el formato `ghp_` seguido de unos 36 caracteres.

---

### GitHub devuelve 401 (Unauthorized)

**Causa:** el token existe pero no tiene los permisos necesarios.

**Solución:** andá a https://github.com/settings/tokens, editá tu token y asegurate de que tenga el scope `public_repo` (para repos públicos) o `repo` completo (para repos privados). Después de cambiar los scopes, copiá el token nuevamente al `.env` — GitHub no te lo muestra dos veces.

---

### GitHub devuelve 301 (Moved Permanently)

**Causa:** la URL de algún repositorio en `GITHUB_REPOS` cambió (repo renombrado o movido) y el cliente HTTP no siguió el redirect automáticamente.

**Solución:** esto ya está corregido en el código (`follow_redirects=True`). Si lo ves igual, verificá que tenés la última versión del archivo `sources/github_releases.py`. También podés actualizar la URL del repo en `config.py` por la nueva.

---

### `git push` devuelve 403 en un repo privado

**Causa:** el token de GitHub tiene scope `public_repo` solamente, que no da acceso a repos privados.

**Solución:** andá a https://github.com/settings/tokens, editá el token y cambiá el scope de `public_repo` a `repo` (que incluye repos privados). Volvé a copiar el token al `.env`.

---

### Expusiste una API key en el chat o en un archivo

**Causa:** pegaste o mostraste una key real en una conversación, commit, o log.

**Qué hacer:**
1. **Rotá la key de inmediato** — no esperés. Una key expuesta hay que considerarla comprometida.
   - xAI: https://console.x.ai — eliminá la key y creá una nueva.
   - GitHub: https://github.com/settings/tokens — eliminá el token y creá uno nuevo.
2. Actualizá tu `.env` con la nueva key.
3. Si la subiste a Git, eliminala del historial (o considerá el repo comprometido y rotá igualmente).
