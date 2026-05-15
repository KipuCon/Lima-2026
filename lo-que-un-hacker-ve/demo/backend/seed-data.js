// Fake citizen data for the demo — all fictional
// Names generated to sound realistic but are not real people

const ciudadanos = {
  // Lima
  "44556670": { dni: "44556670", nombre: "Maria Elena", apellido_paterno: "Gutierrez", apellido_materno: "Flores", fecha_nacimiento: "1985-03-14", sexo: "F", estado_civil: "Casada", direccion: "Av. Javier Prado Este 1234, San Isidro", departamento: "Lima", provincia: "Lima", distrito: "San Isidro", telefono: "987654321", email: "m.gutierrez85@gmail.com" },
  "44556671": { dni: "44556671", nombre: "Carlos Alberto", apellido_paterno: "Quispe", apellido_materno: "Mamani", fecha_nacimiento: "1990-07-22", sexo: "M", estado_civil: "Soltero", direccion: "Jr. Huallaga 456, Cercado de Lima", departamento: "Lima", provincia: "Lima", distrito: "Cercado de Lima", telefono: "912345678", email: "carlos.quispe90@hotmail.com" },
  "44556672": { dni: "44556672", nombre: "Rosa Luz", apellido_paterno: "Huaman", apellido_materno: "Condori", fecha_nacimiento: "1978-11-03", sexo: "F", estado_civil: "Viuda", direccion: "Calle Los Pinos 789, Miraflores", departamento: "Lima", provincia: "Lima", distrito: "Miraflores", telefono: "945678123", email: "rosa.huaman78@yahoo.com" },
  "44556673": { dni: "44556673", nombre: "Jorge Luis", apellido_paterno: "Fernandez", apellido_materno: "Torres", fecha_nacimiento: "1995-01-30", sexo: "M", estado_civil: "Soltero", direccion: "Av. Arequipa 3456, Lince", departamento: "Lima", provincia: "Lima", distrito: "Lince", telefono: "976543210", email: "jfernandez95@gmail.com" },
  "44556674": { dni: "44556674", nombre: "Patricia Carmen", apellido_paterno: "Rojas", apellido_materno: "Vargas", fecha_nacimiento: "1982-06-18", sexo: "F", estado_civil: "Casada", direccion: "Av. La Marina 567, San Miguel", departamento: "Lima", provincia: "Lima", distrito: "San Miguel", telefono: "923456789", email: "patricia.rojas82@outlook.com" },
  "44556675": { dni: "44556675", nombre: "Ricardo Javier", apellido_paterno: "Mendoza", apellido_materno: "Castillo", fecha_nacimiento: "1988-09-05", sexo: "M", estado_civil: "Casado", direccion: "Jr. Cusco 890, Brena", departamento: "Lima", provincia: "Lima", distrito: "Brena", telefono: "934567890", email: "ricardo.mendoza@gmail.com" },
  "44556676": { dni: "44556676", nombre: "Ana Cecilia", apellido_paterno: "Diaz", apellido_materno: "Paredes", fecha_nacimiento: "1993-12-25", sexo: "F", estado_civil: "Soltera", direccion: "Calle Schell 234, Miraflores", departamento: "Lima", provincia: "Lima", distrito: "Miraflores", telefono: "956789012", email: "anacecilia.diaz@gmail.com" },
  "44556677": { dni: "44556677", nombre: "Miguel Angel", apellido_paterno: "Vargas", apellido_materno: "Ramos", fecha_nacimiento: "1975-04-10", sexo: "M", estado_civil: "Divorciado", direccion: "Av. Brasil 1567, Pueblo Libre", departamento: "Lima", provincia: "Lima", distrito: "Pueblo Libre", telefono: "967890123", email: "mvargas75@hotmail.com" },
  "44556678": { dni: "44556678", nombre: "Lucia Fernanda", apellido_paterno: "Torres", apellido_materno: "Silva", fecha_nacimiento: "1999-08-14", sexo: "F", estado_civil: "Soltera", direccion: "Av. Salaverry 2345, Jesus Maria", departamento: "Lima", provincia: "Lima", distrito: "Jesus Maria", telefono: "978901234", email: "lucia.torres99@gmail.com" },
  "44556679": { dni: "44556679", nombre: "Fernando Jose", apellido_paterno: "Lopez", apellido_materno: "Chavez", fecha_nacimiento: "1970-02-28", sexo: "M", estado_civil: "Casado", direccion: "Calle Las Begonias 456, San Isidro", departamento: "Lima", provincia: "Lima", distrito: "San Isidro", telefono: "989012345", email: "flopez70@gmail.com" },
  "44556680": { dni: "44556680", nombre: "Carmen Rosa", apellido_paterno: "Espinoza", apellido_materno: "Huamani", fecha_nacimiento: "1987-05-20", sexo: "F", estado_civil: "Casada", direccion: "Jr. Union 678, Cercado de Lima", departamento: "Lima", provincia: "Lima", distrito: "Cercado de Lima", telefono: "990123456", email: "carmen.espinoza@outlook.com" },
  // Arequipa
  "44556681": { dni: "44556681", nombre: "Eduardo", apellido_paterno: "Caceres", apellido_materno: "Delgado", fecha_nacimiento: "1983-08-12", sexo: "M", estado_civil: "Casado", direccion: "Calle Mercaderes 312, Cercado", departamento: "Arequipa", provincia: "Arequipa", distrito: "Cercado", telefono: "954112233", email: "e.caceres83@gmail.com" },
  "44556682": { dni: "44556682", nombre: "Yolanda", apellido_paterno: "Apaza", apellido_materno: "Chura", fecha_nacimiento: "1991-02-17", sexo: "F", estado_civil: "Soltera", direccion: "Av. Ejercito 1450, Cayma", departamento: "Arequipa", provincia: "Arequipa", distrito: "Cayma", telefono: "954223344", email: "yolanda.apaza91@hotmail.com" },
  "44556683": { dni: "44556683", nombre: "Raul Ernesto", apellido_paterno: "Zegarra", apellido_materno: "Bustamante", fecha_nacimiento: "1968-11-30", sexo: "M", estado_civil: "Viudo", direccion: "Calle Bolivar 567, Yanahuara", departamento: "Arequipa", provincia: "Arequipa", distrito: "Yanahuara", telefono: "954334455", email: "raulz68@yahoo.com" },
  // Cusco
  "44556684": { dni: "44556684", nombre: "Sonia Beatriz", apellido_paterno: "Ccopa", apellido_materno: "Huallpa", fecha_nacimiento: "1996-04-05", sexo: "F", estado_civil: "Soltera", direccion: "Calle Plateros 234, Centro Historico", departamento: "Cusco", provincia: "Cusco", distrito: "Cusco", telefono: "974112233", email: "sonia.ccopa96@gmail.com" },
  "44556685": { dni: "44556685", nombre: "Julio Cesar", apellido_paterno: "Ticona", apellido_materno: "Paucar", fecha_nacimiento: "1980-09-18", sexo: "M", estado_civil: "Casado", direccion: "Av. El Sol 890, Wanchaq", departamento: "Cusco", provincia: "Cusco", distrito: "Wanchaq", telefono: "974223344", email: "julio.ticona80@outlook.com" },
  "44556686": { dni: "44556686", nombre: "Gladys Marlene", apellido_paterno: "Condemayta", apellido_materno: "Sutta", fecha_nacimiento: "1974-01-22", sexo: "F", estado_civil: "Casada", direccion: "Jr. Ayacucho 456, Santiago", departamento: "Cusco", provincia: "Cusco", distrito: "Santiago", telefono: "974334455", email: "gladys.conde74@gmail.com" },
  // Trujillo
  "44556687": { dni: "44556687", nombre: "Segundo Manuel", apellido_paterno: "Avalos", apellido_materno: "Castillo", fecha_nacimiento: "1986-06-14", sexo: "M", estado_civil: "Soltero", direccion: "Jr. Pizarro 789, Centro", departamento: "La Libertad", provincia: "Trujillo", distrito: "Trujillo", telefono: "944112233", email: "s.avalos86@gmail.com" },
  "44556688": { dni: "44556688", nombre: "Milagros del Pilar", apellido_paterno: "Reyes", apellido_materno: "Zavaleta", fecha_nacimiento: "1994-12-08", sexo: "F", estado_civil: "Soltera", direccion: "Av. Espana 1234, Centro", departamento: "La Libertad", provincia: "Trujillo", distrito: "Trujillo", telefono: "944223344", email: "milagros.reyes94@hotmail.com" },
  "44556689": { dni: "44556689", nombre: "Oscar Wilfredo", apellido_paterno: "Crispin", apellido_materno: "Benites", fecha_nacimiento: "1971-03-25", sexo: "M", estado_civil: "Divorciado", direccion: "Calle Colon 567, La Esperanza", departamento: "La Libertad", provincia: "Trujillo", distrito: "La Esperanza", telefono: "944334455", email: "oscar.crispin71@yahoo.com" },
  // Piura
  "44556690": { dni: "44556690", nombre: "Flor de Maria", apellido_paterno: "Seminario", apellido_materno: "Talledo", fecha_nacimiento: "1989-07-19", sexo: "F", estado_civil: "Casada", direccion: "Av. Grau 890, Piura Centro", departamento: "Piura", provincia: "Piura", distrito: "Piura", telefono: "969112233", email: "flor.seminario89@gmail.com" },
  "44556691": { dni: "44556691", nombre: "Luis Fernando", apellido_paterno: "Chunga", apellido_materno: "More", fecha_nacimiento: "1977-10-02", sexo: "M", estado_civil: "Casado", direccion: "Calle Lima 345, Castilla", departamento: "Piura", provincia: "Piura", distrito: "Castilla", telefono: "969223344", email: "luis.chunga77@hotmail.com" },
  "44556692": { dni: "44556692", nombre: "Karina Isabel", apellido_paterno: "Palacios", apellido_materno: "Feria", fecha_nacimiento: "2001-05-11", sexo: "F", estado_civil: "Soltera", direccion: "Jr. Tacna 678, 26 de Octubre", departamento: "Piura", provincia: "Piura", distrito: "26 de Octubre", telefono: "969334455", email: "karina.palacios01@gmail.com" },
  // Chiclayo
  "44556693": { dni: "44556693", nombre: "Pedro Pablo", apellido_paterno: "Chaname", apellido_materno: "Effio", fecha_nacimiento: "1965-08-30", sexo: "M", estado_civil: "Casado", direccion: "Av. Balta 1234, Chiclayo Centro", departamento: "Lambayeque", provincia: "Chiclayo", distrito: "Chiclayo", telefono: "979112233", email: "pedro.chaname65@yahoo.com" },
  "44556694": { dni: "44556694", nombre: "Delia Esperanza", apellido_paterno: "Santisteban", apellido_materno: "Vidaurre", fecha_nacimiento: "1992-01-15", sexo: "F", estado_civil: "Soltera", direccion: "Calle San Jose 567, La Victoria", departamento: "Lambayeque", provincia: "Chiclayo", distrito: "La Victoria", telefono: "979223344", email: "delia.santi92@gmail.com" },
  // Huancayo
  "44556695": { dni: "44556695", nombre: "Maximo", apellido_paterno: "Canchanya", apellido_materno: "Orellana", fecha_nacimiento: "1973-04-28", sexo: "M", estado_civil: "Viudo", direccion: "Jr. Real 345, Centro", departamento: "Junin", provincia: "Huancayo", distrito: "Huancayo", telefono: "964112233", email: "maximo.canch73@hotmail.com" },
  "44556696": { dni: "44556696", nombre: "Nelly Rosario", apellido_paterno: "Poma", apellido_materno: "Yauri", fecha_nacimiento: "1998-09-06", sexo: "F", estado_civil: "Soltera", direccion: "Av. Ferrocarril 890, El Tambo", departamento: "Junin", provincia: "Huancayo", distrito: "El Tambo", telefono: "964223344", email: "nelly.poma98@gmail.com" },
  // Iquitos
  "44556697": { dni: "44556697", nombre: "Humberto", apellido_paterno: "Saavedra", apellido_materno: "Pinedo", fecha_nacimiento: "1981-12-03", sexo: "M", estado_civil: "Casado", direccion: "Jr. Prospero 456, Iquitos Centro", departamento: "Loreto", provincia: "Maynas", distrito: "Iquitos", telefono: "965112233", email: "humberto.saavedra81@gmail.com" },
  "44556698": { dni: "44556698", nombre: "Anita Luz", apellido_paterno: "Chota", apellido_materno: "Rengifo", fecha_nacimiento: "2000-03-21", sexo: "F", estado_civil: "Soltera", direccion: "Calle Putumayo 789, Punchana", departamento: "Loreto", provincia: "Maynas", distrito: "Punchana", telefono: "965223344", email: "anita.chota00@hotmail.com" },
  // Puno
  "44556699": { dni: "44556699", nombre: "Feliciano", apellido_paterno: "Mamani", apellido_materno: "Calsina", fecha_nacimiento: "1963-06-17", sexo: "M", estado_civil: "Casado", direccion: "Jr. Lima 234, Puno Centro", departamento: "Puno", provincia: "Puno", distrito: "Puno", telefono: "951112233", email: "feliciano.mamani63@yahoo.com" },
  "44556700": { dni: "44556700", nombre: "Domitila", apellido_paterno: "Cari", apellido_materno: "Coaquira", fecha_nacimiento: "1979-11-08", sexo: "F", estado_civil: "Casada", direccion: "Av. El Sol 567, Juliaca", departamento: "Puno", provincia: "San Roman", distrito: "Juliaca", telefono: "951223344", email: "domitila.cari79@gmail.com" },
  // Tacna
  "44556701": { dni: "44556701", nombre: "Wilber", apellido_paterno: "Llanos", apellido_materno: "Ale", fecha_nacimiento: "1987-02-14", sexo: "M", estado_civil: "Soltero", direccion: "Av. Bolognesi 890, Tacna Centro", departamento: "Tacna", provincia: "Tacna", distrito: "Tacna", telefono: "952112233", email: "wilber.llanos87@gmail.com" },
  // Ayacucho
  "44556702": { dni: "44556702", nombre: "Teodora", apellido_paterno: "Palomino", apellido_materno: "Galindo", fecha_nacimiento: "1976-07-31", sexo: "F", estado_civil: "Viuda", direccion: "Jr. 28 de Julio 345, Ayacucho Centro", departamento: "Ayacucho", provincia: "Huamanga", distrito: "Ayacucho", telefono: "966112233", email: "teodora.palomino76@hotmail.com" },
  // Cajamarca
  "44556703": { dni: "44556703", nombre: "Santos Edilberto", apellido_paterno: "Chuquilin", apellido_materno: "Vasquez", fecha_nacimiento: "1969-05-09", sexo: "M", estado_civil: "Casado", direccion: "Jr. Del Comercio 678, Cajamarca Centro", departamento: "Cajamarca", provincia: "Cajamarca", distrito: "Cajamarca", telefono: "976112233", email: "santos.chuquilin69@yahoo.com" },
  // Ica
  "44556704": { dni: "44556704", nombre: "Jackeline", apellido_paterno: "Hernandez", apellido_materno: "Rosas", fecha_nacimiento: "1997-10-25", sexo: "F", estado_civil: "Soltera", direccion: "Av. San Martin 1234, Ica Centro", departamento: "Ica", provincia: "Ica", distrito: "Ica", telefono: "956112233", email: "jackeline.hr97@gmail.com" },
  // Huaraz
  "44556705": { dni: "44556705", nombre: "Elmer Augusto", apellido_paterno: "Mejia", apellido_materno: "Figueroa", fecha_nacimiento: "1984-01-18", sexo: "M", estado_civil: "Casado", direccion: "Jr. Simon Bolivar 456, Huaraz Centro", departamento: "Ancash", provincia: "Huaraz", distrito: "Huaraz", telefono: "943112233", email: "elmer.mejia84@outlook.com" },
  // Chimbote
  "44556706": { dni: "44556706", nombre: "Blanca Estela", apellido_paterno: "Carranza", apellido_materno: "Morillo", fecha_nacimiento: "1990-08-07", sexo: "F", estado_civil: "Casada", direccion: "Av. Pardo 789, Chimbote Centro", departamento: "Ancash", provincia: "Santa", distrito: "Chimbote", telefono: "943223344", email: "blanca.carranza90@gmail.com" },
  // Tarapoto
  "44556707": { dni: "44556707", nombre: "Renzo Paolo", apellido_paterno: "Del Aguila", apellido_materno: "Vasquez", fecha_nacimiento: "1995-06-12", sexo: "M", estado_civil: "Soltero", direccion: "Jr. San Martin 234, Tarapoto Centro", departamento: "San Martin", provincia: "San Martin", distrito: "Tarapoto", telefono: "942112233", email: "renzo.delaguila95@gmail.com" },
  // Callao
  "44556708": { dni: "44556708", nombre: "Juana Rosa", apellido_paterno: "Villanueva", apellido_materno: "Ore", fecha_nacimiento: "1972-12-19", sexo: "F", estado_civil: "Divorciada", direccion: "Av. Saenz Pena 567, Callao Centro", departamento: "Callao", provincia: "Callao", distrito: "Callao", telefono: "991112233", email: "juana.villanueva72@hotmail.com" },
  "44556709": { dni: "44556709", nombre: "Alfredo", apellido_paterno: "Montalvo", apellido_materno: "Prado", fecha_nacimiento: "1966-03-08", sexo: "M", estado_civil: "Casado", direccion: "Jr. Galvez 890, Bellavista", departamento: "Callao", provincia: "Callao", distrito: "Bellavista", telefono: "991223344", email: "alfredo.montalvo66@yahoo.com" },
};

// Fake payment transactions for Act 3 (MercadoPago clone)
const comercios = {
  "8870": {
    id: "8870",
    nombre: "Restaurante El Buen Sabor EIRL",
    ruc: "20501234567",
    rubro: "Gastronomia"
  },
  "8871": {
    id: "8871",
    nombre: "Clinica Dental Sonrisa SAC",
    ruc: "20509876543",
    rubro: "Salud"
  },
  "8872": {
    id: "8872",
    nombre: "ElectroMax Peru SAC",
    ruc: "20512345678",
    rubro: "Electronica y Tecnologia"
  },
  "8873": {
    id: "8873",
    nombre: "Farmacia SaludTotal",
    ruc: "20598765432",
    rubro: "Farmaceutica"
  },
  "8874": {
    id: "8874",
    nombre: "Viajes Aventura Peru SRL",
    ruc: "20534567890",
    rubro: "Turismo"
  },
  "8875": {
    id: "8875",
    nombre: "Supermercados FreshMarket SAC",
    ruc: "20545678901",
    rubro: "Retail / Supermercados"
  }
};

const transacciones = [
  {
    id: "TXN-20250301-001",
    comercio_id: "8872",
    fecha: "2025-03-01T14:23:00Z",
    monto: 2499.90,
    moneda: "PEN",
    estado: "approved",
    metodo_pago: "credit_card",
    tarjeta_parcial: "****-****-****-4532",
    tarjeta_marca: "Visa",
    tarjeta_expiracion: "08/27",
    cliente: {
      nombre: "Maria Elena Gutierrez Flores",
      dni: "44556670",
      email: "m.gutierrez85@gmail.com",
      telefono: "987654321"
    },
    descripcion: "Laptop ASUS VivoBook 15"
  },
  {
    id: "TXN-20250301-002",
    comercio_id: "8872",
    fecha: "2025-03-01T15:45:00Z",
    monto: 349.90,
    moneda: "PEN",
    estado: "approved",
    metodo_pago: "credit_card",
    tarjeta_parcial: "****-****-****-8901",
    tarjeta_marca: "Mastercard",
    tarjeta_expiracion: "12/26",
    cliente: {
      nombre: "Carlos Alberto Quispe Mamani",
      dni: "44556671",
      email: "carlos.quispe90@hotmail.com",
      telefono: "912345678"
    },
    descripcion: "Audifonos Sony WH-1000XM5"
  },
  {
    id: "TXN-20250302-003",
    comercio_id: "8872",
    fecha: "2025-03-02T09:12:00Z",
    monto: 1899.00,
    moneda: "PEN",
    estado: "approved",
    metodo_pago: "debit_card",
    tarjeta_parcial: "****-****-****-2345",
    tarjeta_marca: "Visa",
    tarjeta_expiracion: "03/28",
    cliente: {
      nombre: "Jorge Luis Fernandez Torres",
      dni: "44556673",
      email: "jfernandez95@gmail.com",
      telefono: "976543210"
    },
    descripcion: "Smart TV Samsung 55 pulgadas"
  },
  {
    id: "TXN-20250302-004",
    comercio_id: "8872",
    fecha: "2025-03-02T11:30:00Z",
    monto: 599.90,
    moneda: "PEN",
    estado: "approved",
    metodo_pago: "credit_card",
    tarjeta_parcial: "****-****-****-6789",
    tarjeta_marca: "Diners",
    tarjeta_expiracion: "06/27",
    cliente: {
      nombre: "Ana Cecilia Diaz Paredes",
      dni: "44556676",
      email: "anacecilia.diaz@gmail.com",
      telefono: "956789012"
    },
    descripcion: "Tablet iPad 10th Gen"
  },
  {
    id: "TXN-20250303-005",
    comercio_id: "8872",
    fecha: "2025-03-03T16:05:00Z",
    monto: 129.90,
    moneda: "PEN",
    estado: "approved",
    metodo_pago: "credit_card",
    tarjeta_parcial: "****-****-****-1122",
    tarjeta_marca: "Visa",
    tarjeta_expiracion: "11/26",
    cliente: {
      nombre: "Fernando Jose Lopez Chavez",
      dni: "44556679",
      email: "flopez70@gmail.com",
      telefono: "989012345"
    },
    descripcion: "Mouse Logitech MX Master 3S"
  },
  {
    id: "TXN-20250303-006",
    comercio_id: "8872",
    fecha: "2025-03-03T17:22:00Z",
    monto: 4299.00,
    moneda: "PEN",
    estado: "approved",
    metodo_pago: "credit_card",
    tarjeta_parcial: "****-****-****-3344",
    tarjeta_marca: "Mastercard",
    tarjeta_expiracion: "09/27",
    cliente: {
      nombre: "Ricardo Javier Mendoza Castillo",
      dni: "44556675",
      email: "ricardo.mendoza@gmail.com",
      telefono: "934567890"
    },
    descripcion: "iPhone 15 Pro 256GB"
  },
  {
    id: "TXN-20250304-007",
    comercio_id: "8872",
    fecha: "2025-03-04T10:45:00Z",
    monto: 89.90,
    moneda: "PEN",
    estado: "declined",
    metodo_pago: "credit_card",
    tarjeta_parcial: "****-****-****-5566",
    tarjeta_marca: "Visa",
    tarjeta_expiracion: "01/25",
    cliente: {
      nombre: "Miguel Angel Vargas Ramos",
      dni: "44556677",
      email: "mvargas75@hotmail.com",
      telefono: "967890123"
    },
    descripcion: "Cable HDMI 2.1 3m"
  },
  // Restaurante El Buen Sabor (8870)
  {
    id: "TXN-20250228-008", comercio_id: "8870", fecha: "2025-02-28T20:15:00Z", monto: 189.90, moneda: "PEN", estado: "approved", metodo_pago: "credit_card", tarjeta_parcial: "****-****-****-7788", tarjeta_marca: "Visa", tarjeta_expiracion: "04/27",
    cliente: { nombre: "Patricia Carmen Rojas Vargas", dni: "44556674", email: "patricia.rojas82@outlook.com", telefono: "923456789" },
    descripcion: "Cena para 4 personas - Menu degustacion"
  },
  {
    id: "TXN-20250301-009", comercio_id: "8870", fecha: "2025-03-01T13:30:00Z", monto: 45.50, moneda: "PEN", estado: "approved", metodo_pago: "debit_card", tarjeta_parcial: "****-****-****-9900", tarjeta_marca: "Visa", tarjeta_expiracion: "11/26",
    cliente: { nombre: "Lucia Fernanda Torres Silva", dni: "44556678", email: "lucia.torres99@gmail.com", telefono: "978901234" },
    descripcion: "Almuerzo ejecutivo x2"
  },
  // Clinica Dental Sonrisa (8871)
  {
    id: "TXN-20250225-010", comercio_id: "8871", fecha: "2025-02-25T10:00:00Z", monto: 850.00, moneda: "PEN", estado: "approved", metodo_pago: "credit_card", tarjeta_parcial: "****-****-****-1199", tarjeta_marca: "Mastercard", tarjeta_expiracion: "09/28",
    cliente: { nombre: "Eduardo Caceres Delgado", dni: "44556681", email: "e.caceres83@gmail.com", telefono: "954112233" },
    descripcion: "Tratamiento de conducto - pieza 16"
  },
  {
    id: "TXN-20250227-011", comercio_id: "8871", fecha: "2025-02-27T16:45:00Z", monto: 320.00, moneda: "PEN", estado: "approved", metodo_pago: "credit_card", tarjeta_parcial: "****-****-****-2233", tarjeta_marca: "Visa", tarjeta_expiracion: "02/27",
    cliente: { nombre: "Carmen Rosa Espinoza Huamani", dni: "44556680", email: "carmen.espinoza@outlook.com", telefono: "990123456" },
    descripcion: "Limpieza dental + radiografia panoramica"
  },
  // Farmacia SaludTotal (8873)
  {
    id: "TXN-20250303-012", comercio_id: "8873", fecha: "2025-03-03T08:20:00Z", monto: 127.60, moneda: "PEN", estado: "approved", metodo_pago: "credit_card", tarjeta_parcial: "****-****-****-4455", tarjeta_marca: "Visa", tarjeta_expiracion: "07/26",
    cliente: { nombre: "Rosa Luz Huaman Condori", dni: "44556672", email: "rosa.huaman78@yahoo.com", telefono: "945678123" },
    descripcion: "Losartan 50mg x30, Metformina 850mg x60, Atorvastatina 20mg x30"
  },
  {
    id: "TXN-20250304-013", comercio_id: "8873", fecha: "2025-03-04T19:10:00Z", monto: 234.80, moneda: "PEN", estado: "approved", metodo_pago: "debit_card", tarjeta_parcial: "****-****-****-6677", tarjeta_marca: "Mastercard", tarjeta_expiracion: "10/27",
    cliente: { nombre: "Feliciano Mamani Calsina", dni: "44556699", email: "feliciano.mamani63@yahoo.com", telefono: "951112233" },
    descripcion: "Insulina Lantus, jeringas, glucometro Accu-Chek"
  },
  // Viajes Aventura Peru (8874)
  {
    id: "TXN-20250220-014", comercio_id: "8874", fecha: "2025-02-20T11:30:00Z", monto: 4500.00, moneda: "PEN", estado: "approved", metodo_pago: "credit_card", tarjeta_parcial: "****-****-****-8899", tarjeta_marca: "Visa", tarjeta_expiracion: "05/28",
    cliente: { nombre: "Jorge Luis Fernandez Torres", dni: "44556673", email: "jfernandez95@gmail.com", telefono: "976543210" },
    descripcion: "Paquete Cusco-Machu Picchu 5D/4N para 2 personas"
  },
  {
    id: "TXN-20250222-015", comercio_id: "8874", fecha: "2025-02-22T15:00:00Z", monto: 2800.00, moneda: "PEN", estado: "approved", metodo_pago: "credit_card", tarjeta_parcial: "****-****-****-0011", tarjeta_marca: "Diners", tarjeta_expiracion: "12/27",
    cliente: { nombre: "Flor de Maria Seminario Talledo", dni: "44556690", email: "flor.seminario89@gmail.com", telefono: "969112233" },
    descripcion: "Tour Iquitos - Pacaya Samiria 4D/3N"
  },
  // Supermercados FreshMarket (8875)
  {
    id: "TXN-20250305-016", comercio_id: "8875", fecha: "2025-03-05T18:45:00Z", monto: 387.20, moneda: "PEN", estado: "approved", metodo_pago: "debit_card", tarjeta_parcial: "****-****-****-3344", tarjeta_marca: "Visa", tarjeta_expiracion: "08/26",
    cliente: { nombre: "Fernando Jose Lopez Chavez", dni: "44556679", email: "flopez70@gmail.com", telefono: "989012345" },
    descripcion: "Compra semanal - viveres y limpieza"
  },
  {
    id: "TXN-20250305-017", comercio_id: "8875", fecha: "2025-03-05T20:10:00Z", monto: 156.90, moneda: "PEN", estado: "approved", metodo_pago: "credit_card", tarjeta_parcial: "****-****-****-5566", tarjeta_marca: "Mastercard", tarjeta_expiracion: "03/27",
    cliente: { nombre: "Karina Isabel Palacios Feria", dni: "44556692", email: "karina.palacios01@gmail.com", telefono: "969334455" },
    descripcion: "Carnes, lacteos, frutas y verduras"
  }
];

module.exports = { ciudadanos, comercios, transacciones };
