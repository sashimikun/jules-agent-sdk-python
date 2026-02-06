[English](README.md) | [日本語](README.ja.md)

# Jules Agent SDK para Python

> **Descargo de responsabilidad**: Esta es una implementación de código abierto del wrapper del SDK de la API de Jules en Python y no tiene ninguna asociación con Google. Para la API oficial, por favor visite: https://developers.google.com/jules/api/

Un SDK de Python para la API de Jules. Interfaz sencilla para trabajar con sesiones, actividades y fuentes de Jules.

![Jules](jules.png)

## Inicio rápido

### Instalación

```bash
pip install jules-agent-sdk
```

### Uso básico

```python
from jules_agent_sdk import JulesClient

# Inicializar con tu clave de API
client = JulesClient(api_key="tu-clave-de-api")

# Listar fuentes
sources = client.sources.list_all()
print(f"Se encontraron {len(sources)} fuentes")

# Crear una sesión
session = client.sessions.create(
    prompt="Agregar manejo de errores al módulo de autenticación",
    source=sources[0].name,
    starting_branch="main"
)

print(f"Sesión creada: {session.id}")
print(f"Ver en: {session.url}")

client.close()
```

## Configuración

Establece tu clave de API como una variable de entorno:

```bash
export JULES_API_KEY="tu-clave-de-api-aqui"
```

Obtén tu clave de API desde el [panel de Jules](https://jules.google.com).

## Características

### Cobertura de la API
- **Sesiones**: crear, obtener, listar, aprobar planes, enviar mensajes, esperar a que se complete
- **Actividades**: obtener, listar con paginación automática
- **Fuentes**: obtener, listar con paginación automática


## Documentación

- **[Inicio rápido](docs/QUICKSTART.md)** - Guía para empezar
- **[Documentación completa](docs/README.md)** - Referencia completa de la API
- **[Guía de desarrollo](docs/DEVELOPMENT.md)** - Para colaboradores

## Ejemplos de uso

### Gestor de contexto (Recomendado)

```python
from jules_agent_sdk import JulesClient

with JulesClient(api_key="tu-clave-de-api") as client:
    sources = client.sources.list_all()

    session = client.sessions.create(
        prompt="Corregir error de autenticación",
        source=sources[0].name,
        starting_branch="main"
    )

    print(f"Creado: {session.id}")
```

### Soporte para Async/Await

```python
import asyncio
from jules_agent_sdk import AsyncJulesClient

async def main():
    async with AsyncJulesClient(api_key="tu-clave-de-api") as client:
        sources = await client.sources.list_all()

        session = await client.sessions.create(
            prompt="Agregar pruebas unitarias",
            source=sources[0].name,
            starting_branch="main"
        )

        # Esperar a que se complete
        completed = await client.sessions.wait_for_completion(session.id)
        print(f"Listo: {completed.state}")

asyncio.run(main())
```

### Manejo de errores

```python
from jules_agent_sdk import JulesClient
from jules_agent_sdk.exceptions import (
    JulesAuthenticationError,
    JulesNotFoundError,
    JulesValidationError,
    JulesRateLimitError
)

try:
    client = JulesClient(api_key="tu-clave-de-api")
    session = client.sessions.create(
        prompt="Mi tarea",
        source="sources/invalid-id"
    )
except JulesAuthenticationError:
    print("Clave de API inválida")
except JulesNotFoundError:
    print("Fuente no encontrada")
except JulesValidationError as e:
    print(f"Error de validación: {e.message}")
except JulesRateLimitError as e:
    retry_after = e.response.get("retry_after_seconds", 60)
    print(f"Límite de velocidad alcanzado. Reintentar después de {retry_after} segundos")
finally:
    client.close()
```

### Configuración personalizada

```python
client = JulesClient(
    api_key="tu-clave-de-api",
    timeout=60,              # Tiempo de espera de la solicitud en segundos (predeterminado: 30)
    max_retries=5,           # Intentos máximos de reintento (predeterminado: 3)
    retry_backoff_factor=2.0 # Multiplicador de backoff (predeterminado: 1.0)
)
```

Los reintentos ocurren automáticamente para:
- Errores de red (problemas de conexión, tiempos de espera)
- Errores del servidor (códigos de estado 5xx)

No hay reintentos para:
- Errores del cliente (códigos de estado 4xx)
- Errores de autenticación

## Referencia de la API

### Sesiones

```python
# Crear sesión
session = client.sessions.create(
    prompt="Descripción de la tarea",
    source="sources/source-id",
    starting_branch="main",
    title="Título opcional",
    require_plan_approval=False
)

# Obtener sesión
session = client.sessions.get("session-id")

# Listar sesiones
result = client.sessions.list(page_size=10)
sessions = result["sessions"]

# Aprobar plan
client.sessions.approve_plan("session-id")

# Enviar mensaje
client.sessions.send_message("session-id", "Instrucciones adicionales")

# Esperar a que se complete
completed = client.sessions.wait_for_completion(
    "session-id",
    poll_interval=5,
    timeout=600
)
```

### Actividades

```python
# Obtener actividad
activity = client.activities.get("session-id", "activity-id")

# Listar actividades (paginado)
result = client.activities.list("session-id", page_size=20)

# Listar todas las actividades (paginación automática)
all_activities = client.activities.list_all("session-id")
```

### Fuentes

```python
# Obtener fuente
source = client.sources.get("source-id")

# Listar fuentes (paginado)
result = client.sources.list(page_size=10)

# Listar todas las fuentes (paginación automática)
all_sources = client.sources.list_all()
```

## Registro

Habilita el registro para ver los detalles de la solicitud:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("jules_agent_sdk")
```

## Pruebas

```bash
# Ejecutar todas las pruebas
pytest

# Ejecutar con cobertura
pytest --cov=jules_agent_sdk

# Ejecutar prueba específica
pytest tests/test_client.py -v
```

## Estructura del proyecto

```
jules-api-python-sdk/
├── src/jules_agent_sdk/
│   ├── client.py              # Cliente principal
│   ├── async_client.py        # Cliente asíncrono
│   ├── base.py                # Cliente HTTP con reintentos
│   ├── models.py              # Modelos de datos
│   ├── sessions.py            # API de sesiones
│   ├── activities.py          # API de actividades
│   ├── sources.py             # API de fuentes
│   └── exceptions.py          # Excepciones personalizadas
├── tests/                     # Suite de pruebas
├── examples/                  # Ejemplos de uso
│   ├── simple_test.py         # Inicio rápido
│   ├── interactive_demo.py    # Demostración completa
│   ├── async_example.py       # Uso asíncrono
│   └── plan_approval_example.py
├── docs/                      # Documentación
└── README.md
```

## Contribuir

Consulta [DEVELOPMENT.md](docs/DEVELOPMENT.md) para la configuración de desarrollo y las directrices.

## Licencia

Licencia MIT - consulta el archivo [LICENSE](LICENSE) para más detalles.

## Soporte

- **Documentación**: Consulta la carpeta [docs/](docs/)
- **Ejemplos**: Consulta la carpeta [examples/](examples/)
- **Problemas**: Abre un issue en GitHub

## Próximos pasos

1. Ejecuta `python examples/simple_test.py` para probarlo
2. Lee [docs/QUICKSTART.md](docs/QUICKSTART.md) para más detalles
3. Revisa la carpeta [examples/](examples/) para más casos de uso