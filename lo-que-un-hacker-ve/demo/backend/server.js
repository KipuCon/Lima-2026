const express = require('express');
const cors = require('cors');
const jwt = require('jsonwebtoken');
const path = require('path');
const fs = require('fs');
const { ciudadanos, comercios, transacciones } = require('./seed-data');

const app = express();
const PORT = 3000;

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '..', 'frontend')));

// Request counter — tracks total API hits and start time
let requestCount = 0;
let firstRequestTime = null;

app.use('/api', (req, res, next) => {
  if (!firstRequestTime) firstRequestTime = Date.now();
  requestCount++;
  next();
});

app.get('/api/counter', (req, res) => {
  const elapsed = firstRequestTime ? Math.round((Date.now() - firstRequestTime) / 1000) : 0;
  res.json({ requests: requestCount - 1, seconds: elapsed }); // -1 to exclude this call
});

app.post('/api/counter/reset', (req, res) => {
  requestCount = 0;
  firstRequestTime = null;
  res.json({ status: 'reset' });
});

// ============================================================
// ACT 1: Unauthenticated API — based on ONPE Hackathon / MEF
// No auth, no rate limit, no nothing. Just pass a DNI.
// ============================================================

app.get('/api/v1/ciudadano/:dni', (req, res) => {
  const { dni } = req.params;
  const citizen = ciudadanos[dni];

  if (!citizen) {
    return res.status(404).json({
      error: "Ciudadano no encontrado",
      codigo: "NOT_FOUND",
      dni_consultado: dni
    });
  }

  // Return only what the real ONPE endpoint returned:
  // nombre, sexo, edad/fecha_nacimiento, DNI
  // The real endpoint at hackathon.pe/hackathon_ve/person/{DNI}
  // returned: name, sex, age verification, DNI number
  res.json({
    dni: citizen.dni,
    nombres: citizen.nombre,
    apellido_paterno: citizen.apellido_paterno,
    apellido_materno: citizen.apellido_materno,
    nombre_completo: `${citizen.nombre} ${citizen.apellido_paterno} ${citizen.apellido_materno}`,
    sexo: citizen.sexo,
    fecha_nacimiento: citizen.fecha_nacimiento
  });
});

// ============================================================
// ACT 2: IDOR via Base64 — based on RENIEC Padron Nominal
// DNI encoded in Base64 in the URL path, returns photo.
// The "security" is just Base64 encoding — trivially reversible.
// ============================================================

app.get('/api/foto/:encoded_id', (req, res) => {
  const { encoded_id } = req.params;

  let dni;
  try {
    dni = Buffer.from(encoded_id, 'base64').toString('utf-8');
  } catch {
    return res.status(400).json({ error: "ID invalido" });
  }

  const citizen = ciudadanos[dni];
  if (!citizen) {
    return res.status(404).json({ error: "Foto no encontrada" });
  }

  // Serve the pre-downloaded portrait photo
  const photoPath = path.join(__dirname, '..', 'data', 'fotos', `${dni}.jpg`);
  if (fs.existsSync(photoPath)) {
    res.type('image/jpeg').sendFile(photoPath);
  } else {
    // Fallback: simple SVG placeholder if photo file is missing
    const initials = `${citizen.nombre[0]}${citizen.apellido_paterno[0]}`;
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128"><rect width="128" height="128" fill="#64748b"/><text x="64" y="72" font-family="sans-serif" font-size="48" font-weight="bold" fill="white" text-anchor="middle">${initials}</text></svg>`;
    res.type('image/svg+xml').send(svg);
  }
});

// Also expose metadata alongside the photo (for the demo)
app.get('/api/foto/:encoded_id/info', (req, res) => {
  const { encoded_id } = req.params;
  let dni;
  try {
    dni = Buffer.from(encoded_id, 'base64').toString('utf-8');
  } catch {
    return res.status(400).json({ error: "ID invalido" });
  }

  const citizen = ciudadanos[dni];
  if (!citizen) {
    return res.status(404).json({ error: "Ciudadano no encontrado" });
  }

  res.json({
    dni: citizen.dni,
    nombre_completo: `${citizen.nombre} ${citizen.apellido_paterno} ${citizen.apellido_materno}`,
    foto_url: `/api/foto/${encoded_id}`,
    sistema: "PADRON_NOMINAL",
    ministerio: "MINISTERIO_DE_SALUD"
  });
});

// ============================================================
// ACT 3: Broken OAuth — based on MercadoPago "lalalala"
// ANY secret generates a valid token. The secret is never validated.
// ============================================================

const JWT_SECRET = 'demo-secret-key-kipucon-2026';

app.post('/api/oauth/token', (req, res) => {
  const { client_id, secret } = req.body;

  if (!client_id) {
    return res.status(400).json({
      error: "client_id is required",
      error_code: "MISSING_CLIENT_ID"
    });
  }

  const comercio = comercios[client_id];
  if (!comercio) {
    return res.status(404).json({
      error: "Comercio no encontrado",
      error_code: "INVALID_CLIENT_ID"
    });
  }

  // THE VULNERABILITY: secret is NEVER validated against the real secret.
  // Any non-empty string generates a valid token — "lalalala", "x", "abc123", anything.
  // The original MercadoPago bug was confirmed with arbitrary wrong secrets.
  // We require a non-empty secret since the original API required the parameter to be present.
  if (!secret && secret !== 0) {
    return res.status(400).json({
      error: "client_secret is required",
      error_code: "MISSING_SECRET"
    });
  }
  const token = jwt.sign(
    {
      client_id: comercio.id,
      comercio: comercio.nombre,
      scope: "read write",
      iat: Math.floor(Date.now() / 1000)
    },
    JWT_SECRET,
    { expiresIn: '1h' }
  );

  res.json({
    access_token: token,
    token_type: "bearer",
    expires_in: 3600,
    scope: "read write",
    comercio: comercio.nombre
  });
});

// Protected (supposedly) endpoint — transactions
app.get('/api/collections', (req, res) => {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({
      error: "Token de acceso requerido",
      error_code: "UNAUTHORIZED"
    });
  }

  const token = authHeader.split(' ')[1];
  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    const status = req.query.status;
    let results = transacciones.filter(t => t.comercio_id === decoded.client_id);
    if (status) {
      results = results.filter(t => t.estado === status);
    }

    res.json({
      status: "success",
      comercio: decoded.comercio,
      total_resultados: results.length,
      transacciones: results
    });
  } catch {
    return res.status(401).json({
      error: "Token invalido o expirado",
      error_code: "INVALID_TOKEN"
    });
  }
});

// ============================================================
// Utility endpoints for the frontend
// ============================================================

// List all available DNIs (for the frontend dropdown / enumeration demo)
app.get('/api/stats', (req, res) => {
  const total = Object.keys(ciudadanos).length;
  const dniRange = Object.keys(ciudadanos).sort();
  res.json({
    total_registros: total,
    rango_dni: { desde: dniRange[0], hasta: dniRange[dniRange.length - 1] },
    sistema: "REGISTRO_NACIONAL_DEMO",
    version: "1.0",
    advertencia: "APLICACION EDUCATIVA — DATOS FICTICIOS"
  });
});

// SPA fallback
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '..', 'frontend', 'index.html'));
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`\n  ╔══════════════════════════════════════════════╗`);
  console.log(`  ║  KipuCon Demo — App Vulnerable Educativa     ║`);
  console.log(`  ║  http://localhost:${PORT}                        ║`);
  console.log(`  ║                                              ║`);
  console.log(`  ║  DATOS 100% FICTICIOS — USO EDUCATIVO       ║`);
  console.log(`  ╚══════════════════════════════════════════════╝\n`);
});
