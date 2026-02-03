# Modifiche per Hosting Locale - code.marconicloud.it

Questo documento descrive le modifiche apportate al progetto Judge0 IDE Marconi per rimuovere le dipendenze da servizi esterni e permettere l'hosting su un'istanza locale.

## Modifiche Effettuate

### 1. Rimozione dipendenze da Google Fonts

**File modificati:**
- `ide/index.html`
- `ide/assets/css2-local.css` (nuovo)

**Dettagli:**
- Rimossi i link `preconnect` a `https://fonts.googleapis.com` e `https://fonts.gstatic.com`
- Creato nuovo file `css2-local.css` che referenzia font locali in `ide/assets/fonts/`
- I file dei font JetBrains Mono devono essere scaricati manualmente e posizionati in `ide/assets/fonts/`

**Font da scaricare:**
- Font italici (pesi: 100, 200, 300, 400, 500, 600, 700, 800)
- Font normali (pesi: 100, 200, 300, 400, 500, 600, 700, 800)

I nomi dei file dovrebbero seguire il pattern:
- `jetbrainsmono-italic-{PESO}.ttf`
- `jetbrainsmono-normal-{PESO}.ttf`

### 2. Disabilitazione integrazione Puter

**File modificati:**
- `ide/index.html`
- `ide/js/puter.js`
- `ide/js/puter-stub.js` (nuovo)

**Dettagli:**
- Rimosso lo script `resource_14a55d1e.js` che caricava l'SDK di Puter (contenente `https://puter-net.b-cdn.net/` e `https://api.puter.com/`)
- Modificato `puter.js` per fare in modo che `usePuter()` ritorni sempre `false`
- Creato `puter-stub.js` per fornire stub delle funzioni di Puter e evitare errori di "puter is not defined"
- Commentato il container della chat UI che dipendeva da Puter
- Nascosto il pulsante di sign-in/sign-out di Puter

### 3. Disabilitazione funzionalità AI Chat

**File modificati:**
- `ide/index.html`

**Dettagli:**
- Commentato il container `judge0-chat-container` e tutti gli elementi correlati
- La funzionalità di chat dipendeva da `puter.ai.chat()` che accede a `https://api.puter.com/`

### 4. Aggiornamento metadati

**File modificati:**
- `ide/index.html`

**Dettagli:**
- Aggiornato il metadato `twitter:url` da `https://ide.judge0.com` a `https://code.marconicloud.it`

## Configurazione Attuale

Il progetto è configurato per utilizzare:
- **Endpoint API:** `https://code.marconicloud.it:2358`
- **GUI:** Locale (nessuna dipendenza da servizi remoti)

Tutti gli URL sono già configurati in `ide/js/ide.js`:
```javascript
const AUTHENTICATED_CE_BASE_URL = "https://code.marconicloud.it:2358";
const UNAUTHENTICATED_CE_BASE_URL = "https://code.marconicloud.it:2358";
```

## Domini Accessibili

Dopo queste modifiche, il progetto accede **SOLO** a:
- ✅ `code.marconicloud.it` (locale)
- ✅ GitHub (solo per link di documentazione e bug report - esterni)

Rimossi accessi a:
- ❌ `api.puter.com`
- ❌ `fonts.googleapis.com`
- ❌ `fonts.gstatic.com`
- ❌ `puter-net.b-cdn.net`

## Prossimi Passi

1. Scaricare i file dei font JetBrains Mono e posizionarli in `ide/assets/fonts/`
2. Testare l'applicazione per verificare il corretto funzionamento
3. Verificare che le risorse locali si carichino correttamente

## Note

- I link a GitHub (judge0.com, etc.) rimangono disponibili ma sono per scopi informativi e non critici per il funzionamento
- Se desideri rimuovere completamente anche questi link, puoi commentarli in `ide/index.html`
- L'applicazione funzionerà completamente senza accesso a Internet per le funzionalità di base
