# Diagramas Punto 9 - Detalle de Arquitectura a Implementar

## 1. BPMN - Proceso de Gestión de Inventario

El siguiente diagrama modela el proceso de negocio principal: la detección y registro de variaciones de inventario. A diferencia de un flujo manual tradicional, aquí se destaca la automatización del ingreso de datos mediante el sensor IoT y el filtrado inteligente de ruido.

```mermaid
---
config:
  layout: elk
---
flowchart TB
    A(["Inicio"]) -- Lectura --> B(["Sensor IoT<br>detecta peso"])
    B -- Digitaliza --> C{{"Filtrar<br>ruido?"}}
    C -- Válido --> D(["Flask procesa<br>y actualiza BD"])
    D -- Audita --> E{{"Stock<br>crítico?"}}
    E -- No --> F(["Fin"])
    E -- Sí --> G(["Generar<br>alerta"])
    G -- Alerta --> F
    C -. Ruido .-> A

     A:::start
     B:::sens
     C:::decision
     D:::proc
     E:::decision
     G:::alerta
     F:::start
    classDef start fill:#90EE90,stroke:#15803d,stroke-width:2px,color:#17420f,font-weight:bold
    classDef sens fill:#87CEEB,stroke:#1e3a8a,stroke-width:2px,color:#152747
    classDef decision fill:#FFE4B5,stroke:#b45309,stroke-width:3px,color:#7c470a,font-weight:bold
    classDef proc fill:#DDA0DD,stroke:#7e22ce,stroke-width:2px,color:#3c0066
    classDef alerta fill:#FF6347,stroke:#b91c1c,stroke-width:2px,color:#fff
    linkStyle 0 stroke:#3b82f6,stroke-width:2.5px,fill:none
    linkStyle 1 stroke:#3b82f6,stroke-width:2.5px,fill:none
    linkStyle 2 stroke:#3b82f6,stroke-width:2.5px,fill:none
    linkStyle 3 stroke:#3b82f6,stroke-width:2.5px,fill:none
    linkStyle 4 stroke:#f97316,stroke-width:2.5px,fill:none
    linkStyle 5 stroke:#dc2626,stroke-width:2.5px,fill:none
    linkStyle 6 stroke:#dc2626,stroke-width:2.5px,fill:none
    linkStyle 7 stroke:#ef4444,stroke-width:2px,stroke-dasharray:4,2,fill:none
```

---

## 2. Casos de Uso - Roles del Sistema

```mermaid
graph TB
    subgraph Actores
        Admin((Administrador))
        Super((Supervisor))
        Oper((Operador))
    end
    
    subgraph CasosAdmin[Casos Administrador]
        GU[Gestionar Usuarios]
        CR[Configurar Roles]
        VA[Ver Auditoría]
    end
    
    subgraph CasosSuper[Casos Supervisor]
        RV[Registrar Ventas]
        VM[Consultar Movimientos]
        RI[Revisar Recomendaciones IA]
        Alert[Gestionar Alertas]
    end
    
    subgraph CasosOper[Casos Operador]
        RI2[Registrar Movimiento Manual]
        CS[Consultar Stock]
        CV[Consultar Ventas]
    end
    
    Admin --> GU
    Admin --> CR
    Admin --> VA
    
    Super --> RV
    Super --> VM
    Super --> RI
    Super --> Alert
    Super --> VA
    
    Oper --> RI2
    Oper --> CS
    Oper --> CV
    
    style Admin fill:#e91e63
    style Super fill:#ff9800
    style Oper fill:#4caf50
```

---

## 3. Flujo de Interacción Usuario-Sistema

```mermaid
sequenceDiagram
    participant U as Usuario
    participant Auth as Autenticación
    participant App as Aplicación
    participant IA as Motor IA
    participant DB as Base Datos

    U->>Auth: Login (rut + contraseña)
    Auth->>DB: Validar credenciales
    DB-->>Auth: Usuario válido + rol
    Auth->>App: Crear sesión
    App->>U: Redirigir a inicio
    
    U->>App: Navega a pantalla (ventas/movimientos/etc)
    App->>IA: Generar recomendación contextualizada
    IA->>DB: Consultar datos del módulo actual
    DB-->>IA: Datos operacionales
    IA->>IA: Detectar anomalías contextualizadas
    IA-->>App: Mensaje IA
    App-->>U: Renderizar vista + header IA
    
    Note over U,DB: El header muestra anomalías según módulo:<br/>Ventas → anomalías de ventas<br/>Movimientos → anomalías de stock<br/>Auditoría → análisis detallado con plan
```

---

## 4. Flujo Asistente IA - Auditoría

```mermaid
sequenceDiagram
    participant S as Supervisor
    participant Web as Navegador
    participant API as Flask
    participant DB as Supabase
    participant IA as Motor IA

    S->>Web: Accede a /auditoria
    Web->>API: GET /auditoria
    
    API->>DB: Consultar eventos últimas 6h<br/>(movimientos, ventas, alertas, usuarios)
    DB-->>API: 30 eventos + metadatos
    
    API->>IA: Generar recomendación contextual
    IA->>DB: Analizar datos operacionales
    IA->>IA: Detectar anomalías (ML)
    IA-->>API: Mensaje para header
    
    API-->>Web: Renderizar vista + header IA
    Web-->>S: Auditoría cargada
```

---

## 5. Diagrama de Componentes

```mermaid
graph LR
    subgraph Frontend["FRONTEND"]
        HTML[Jinja2]
        CSS[Tailwind]
    end
    
    subgraph Backend["BACKEND"]
        Routes[Routes]
        Auth[Auth]
    end
    
    subgraph IA["IA"]
        ML[ML Detector]
    end
    
    subgraph External["EXTERNOS"]
        DB[(Supabase)]
        Socket[Socket.IO]
    end
    
    Frontend --> Backend
    Backend --> IA
    Backend --> External
    IA --> External
    
    style Frontend fill:#e3f2fd
    style Backend fill:#f3e5f5
    style IA fill:#fff3e0
    style External fill:#fce4ec
```

---

## 6. Topología de Componentes

```mermaid
graph LR
    subgraph Cliente["NAVEGADOR"]
        Browser[HTML + JS]
        WS[Socket.IO]
    end
    
    subgraph Servidor["SERVIDOR"]
        Flask[Flask 3.0]
        SocketIO[WebSocket]
        ML[Motor IA]
    end
    
    subgraph Cloud["SUPABASE"]
        DB[(PostgreSQL)]
    end
    
    subgraph IoT["IoT"]
        Pico[Pico W]
    end
    
    Browser -->|HTTP| Flask
    WS -.->|WSS| SocketIO
    Flask --> ML
    Flask --> DB
    SocketIO --> DB
    Pico -->|POST| Flask
    
    style Cliente fill:#bbdefb
    style Servidor fill:#c8e6c9
    style Cloud fill:#f8bbd0
    style IoT fill:#c5e1a5
```

---

## 7. Flujo de Datos - Pipeline IA

```mermaid
graph TB
    D[Ventas] --> E[ventas]
    
    A[Sensor IoT] -->|Peso| B[pesajes]
    B --> C[movimientos]
    E --> C
    
    F[Usuarios] --> G[auditoria_eventos]
    
    C --> H[Snapshot]
    G --> H
    E --> H
    
    H --> I[ML Detector]
    I --> J[ia_auditoria_logs]
    
    style A fill:#4caf50
    style I fill:#9c27b0
    style J fill:#ff9800
```

---

## 8. Seguridad Implementada

```mermaid
graph LR
    User[Usuario] --> Auth[Autenticación]
    Auth --> Flask[Flask App]
    
    subgraph Security["SEGURIDAD"]
        CSRF[CSRF Tokens]
        RBAC[RBAC Roles]
        Hash[bcrypt Hash]
    end
    
    Flask --> Security
    Security --> DB[(Supabase)]
    
    style User fill:#2196f3
    style Security fill:#ff9800
    style DB fill:#4caf50
```

---

## Instrucciones de Uso

### Para Word:
1. Copiar cada código Mermaid a https://mermaid.live
2. Exportar como PNG (alta resolución)
3. Insertar en documento numerando:
   - Figura 9.1: BPMN Proceso de Venta
   - Figura 9.2: Diagrama de Casos de Uso
   - Figura 9.3: Flujo de Interacción Usuario-Sistema
   - Figura 9.4: Flujo Asistente IA - Auditoría
   - Figura 9.5: Diagrama de Componentes
   - Figura 9.6: Topología de Componentes
   - Figura 9.7: Arquitectura de Datos ETL
   - Figura 9.8: Infraestructura y Seguridad
