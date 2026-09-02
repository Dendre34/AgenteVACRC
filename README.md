# AgenteVACRC
Agente para hacerle preguntas

## API de contacto (FastAPI)

API simple con un único endpoint para enviar el formulario de contacto por correo a `vacrcproyectos@gmail.com`.

### Instalación

```bash
pip install -r requirements.txt
cp .env.example .env  # y completar con tus credenciales
```

### Ejecutar en desarrollo

```bash
uvicorn app.main:app --reload
```

### Endpoint

`POST /api/v1/contact/send-email`

Header requerido:

```
X-API-Token: <valor de API_TOKEN en .env>
```

Body:

```json
{
  "nombre": "Juan Pérez",
  "telefono": "555-123-4567",
  "servicio": "Consultoría",
  "mensaje": "Quiero más información."
}
```

