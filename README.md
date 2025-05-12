
# 🧠 Backend Calendarios – Arquitectura Hexagonal

Este repositorio implementa un sistema backend para la gestión de calendarios empresariales, procesos y hitos asociados a clientes, respetando los principios de la **arquitectura hexagonal (puertos y adaptadores)** y **principios SOLID**.

---

## 📦 Estructura de Carpetas

```plaintext
calendarios_back_hexagonal/
│
├── app/
│   ├── domain/                       
│   │   ├── entities/                 
│   │   └── repositories/            
│   │
│   ├── application/                 
│   │   └── use_cases/
│   │       ├── procesos/
│   │       ├── hitos/
│   │       ├── clientes/
│   │       ├── plantilla/
│   │       ├── plantilla_proceso/
│   │       ├── cliente_proceso/
│   │       └── cliente_proceso_hito/
│   │
│   ├── infrastructure/              
│   │   ├── db/
│   │   │   ├── database.py          
│   │   │   ├── models/              
│   │   │   └── repositories/        
│   │   └── api/
│   │       └── v1/
│   │           └── endpoints/       
│   │
│   └── main.py                      
│
├── tests/                           
├── scripts/                         
│   ├── mock_data.py
│   └── test_endpoints.py
│
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## ⚙️ Flujo de una Petición

1. El cliente lanza una petición a un endpoint de FastAPI (`/v1/...`)
2. El endpoint recibe la solicitud, extrae los datos y llama a un **caso de uso**
3. El caso de uso invoca a un repositorio **abstracto**
4. Este es inyectado por su implementación concreta (`*_repository_sql.py`)
5. El repositorio ejecuta operaciones con la BBDD a través del ORM SQLAlchemy
6. El resultado se devuelve hacia el cliente

---

## 🧠 Entidades Disponibles

| Entidad                  | Descripción                                      |
|--------------------------|--------------------------------------------------|
| **Proceso**              | Flujo empresarial recurrente                     |
| **Hito**                 | Evento o tarea específica de un proceso          |
| **Plantilla**            | Configuración base con procesos predefinidos     |
| **Cliente**              | Entidad externa consumida desde otra plataforma |
| **ProcesoHitoMaestro**   | Relación entre procesos e hitos base             |
| **PlantillaProceso**     | Asociación entre plantilla y procesos            |
| **ClienteProceso**       | Asignación de procesos a clientes                |
| **ClienteProcesoHito**   | Hitos derivados del cliente_proceso             |

---

## 🔗 Relaciones entre Tablas

```plaintext
Plantilla ⟷ PlantillaProceso ⟶ Proceso
Proceso ⟷ ProcesoHitoMaestro ⟶ Hito

Cliente ⟶ ClienteProceso ⟶ Proceso
ClienteProceso ⟶ ClienteProcesoHito ⟶ Hito (vía ProcesoHitoMaestro)
```

---

## ✍️ Proceso para Agregar Nuevas Entidades

1. **Dominio**
   - Crear clase en `entities/`
   - Crear interfaz abstracta en `repositories/`

2. **Casos de Uso**
   - Crear funciones específicas en `use_cases/<entidad>/`

3. **Infraestructura**
   - Crear modelo en `models/`
   - Crear repositorio en `repositories/`

4. **API**
   - Crear endpoint en `endpoints/`

5. **Mocks y Test**
   - Agregar mocks en `scripts/mock_data.py`
   - Agregar pruebas en `scripts/test_endpoints.py`

---

## 🛠️ Cambio de Motor de Base de Datos

1. Crear una nueva clase repositorio implementando la interfaz
2. Sustituir la inyección en los endpoints
3. ¡El dominio y casos de uso no se tocan! ✅

---

## 🧪 Scripts Disponibles

| Script                | Descripción                            |
|-----------------------|----------------------------------------|
| `mock_data.py`        | Inserta datos simulados en la BBDD     |
| `test_endpoints.py`   | Ejecuta tests para todos los endpoints |

---

## ✅ Buenas Prácticas Aplicadas

- Arquitectura hexagonal limpia
- Responsabilidad única y principios SOLID
- Separación entre lógica de negocio, aplicación y persistencia
- Fácil testeo, mantenimiento y escalabilidad

---
