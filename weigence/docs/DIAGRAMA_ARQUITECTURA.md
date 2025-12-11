# Diagramas de Arquitectura - Sistema Weigence

## 1. Arquitectura en Capas

```mermaid
graph TB
    A[Presentación: HTML + Tailwind CSS] --> B[Controladores Flask]
    B --> C[Lógica de Negocio: IA + ML]
    C --> D[Acceso a Datos: Repositorios]
    D --> E[(Supabase PostgreSQL)]

    style A fill:#e3f2fd
    style B fill:#f3e5f5
    style C fill:#fff3e0
    style D fill:#e8f5e9
    style E fill:#fce4ec
```

---

## 2. Flujo de Recomendaciones IA

```mermaid
sequenceDiagram
    participant Usuario
    participant Flask
    participant IAService
    participant Supabase

    Usuario->>Flask: Accede a pantalla
    Flask->>IAService: Generar recomendación
    IAService->>Supabase: Consultar datos
    Supabase-->>IAService: Ventas y Alertas
    IAService->>IAService: Análisis ML
    IAService-->>Flask: Recomendación
    Flask-->>Usuario: Header actualizado
```

---

## 3. Stack Tecnológico

```mermaid
graph LR
    A[Jinja2 + Tailwind] --> B[Flask Python]
    B --> C[IA + Socket.IO]
    C --> D[Supabase PostgreSQL]
    
    style A fill:#bbdefb
    style B fill:#ce93d8
    style C fill:#ffcc80
    style D fill:#a5d6a7
```

---

## 4. Modelo de Datos Principal

```mermaid
erDiagram
    USUARIOS ||--o{ VENTAS : realiza
    VENTAS ||--o{ DETALLE_VENTAS : tiene
    PRODUCTOS ||--o{ DETALLE_VENTAS : contiene
    PRODUCTOS ||--o{ MOVIMIENTOS_INVENTARIO : afecta
    PRODUCTOS }o--|| ESTANTES : ubicado
    USUARIOS ||--o{ MOVIMIENTOS_INVENTARIO : registra
    
    USUARIOS {
        string rut_usuario PK
        string nombre
        string rol
    }
    
    VENTAS {
        int idventa PK
        string rut_usuario FK
        date fecha
        decimal total
    }
    
    PRODUCTOS {
        int idproducto PK
        string nombre
        int stock
        decimal precio
    }
    
    DETALLE_VENTAS {
        int id PK
        int idventa FK
        int idproducto FK
        int cantidad
    }
    
    ESTANTES {
        int id PK
        string nombre
        decimal peso_actual
    }
    
    MOVIMIENTOS_INVENTARIO {
        int id PK
        int idproducto FK
        string rut_usuario FK
        string tipo
        int cantidad
    }
```

---

## 5. Flujo de Autenticación

```mermaid
flowchart TD
    A([Login]) --> B{Credenciales válidas?}
    B -->|No| C[Error]
    B -->|Sí| D[Crear sesión]
    D --> E{Tiene permisos?}
    E -->|No| F[Denegado]
    E -->|Sí| G[Dashboard]
    
    style A fill:#4caf50
    style G fill:#2196f3
    style C fill:#f44336
    style F fill:#ff9800
```

---

## 6. Arquitectura de Despliegue

```mermaid
graph LR
    A[Usuarios] -->|HTTPS| B[Servidor Flask]
    B --> C[Supabase Cloud]
    
    style A fill:#64b5f6
    style B fill:#4caf50
    style C fill:#9c27b0
```

---

## 7. Chat en Tiempo Real

```mermaid
sequenceDiagram
    participant U1 as Usuario 1
    participant S as Socket.IO
    participant DB as Supabase
    participant U2 as Usuario 2

    U1->>S: Envía mensaje
    S->>DB: Guarda mensaje
    S->>U1: Confirmación
    S->>U2: Notificación
```

---

## Instrucciones

### Para insertar en Word:
1. Ir a https://mermaid.live
2. Copiar código del diagrama
3. Exportar como PNG o SVG
4. Insertar en Word como imagen
5. Numerar: "Figura 6.1: Arquitectura del Sistema Weigence"
