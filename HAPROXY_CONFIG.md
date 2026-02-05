# HAProxy configuration for Judge0 IDE with API proxy
# Add these sections to your haproxy.cfg

# In the frontend section (dove catturi le richieste), aggiungi:
frontend your_frontend
    # ... altre configurazioni ...
    
    # Route per /api (nuovo - used by IDE frontend)
    use_backend judge0_api if { hdr(host) -i code.marconicloud.it } { path_beg /api }
    
    # Route per accesso diretto sulla porta (legacy - per retrocompatibilità)
    use_backend judge0_ipvANY if { hdr(host) -i code.marconicloud.it:2358 }

# ============================================

# Backend per le API (nuovo)
backend judge0_api
    mode                    http
    log                     global
    cookie                  nocache
    timeout connect         30000
    timeout server          30000
    retries                 3
    http-request add-header X-Forwarded-Proto https if { ssl_fc }
    http-request redirect scheme https unless { ssl_fc }
    # Importantissimo: rewrite del path per rimuovere /api prefix
    # Trasforma: /api/languages -> /languages
    http-request set-path %[path,regsub(^/api/,/)]
    # Aggiungi header X-Forwarded-For per il backend
    http-request add-header X-Forwarded-For %[src]
    server judge 10.0.0.23:2358

# ============================================

# Backend originale (mantieni per retrocompatibilità)
backend judge0_ipvANY
    mode                    http
    log                     global
    cookie                  nocache
    timeout connect         30000
    timeout server          30000
    retries                 3
    http-request add-header X-Forwarded-Proto https if { ssl_fc }
    http-request redirect scheme https unless { ssl_fc }
    server judge 10.0.0.23:2358
