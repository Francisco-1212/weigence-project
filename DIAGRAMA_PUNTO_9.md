# Diagramas Punto 9 - Detalle de Arquitectura a Implementar

## 1. BPMN - Proceso de Gestión de Inventario

```mermaid
graph TB
    A([Inicio]) --> B[Sensor detecta<br/>cambio peso]
    B --> C[Pico W<br/>digitaliza señal]
    
    A --> D{Filtrar<br/>ruido?}
    D -->|Ruido| A
    D -->|Válido| E[Flask procesa<br/>y calcula diferencia]
    
    C --> E
    E --> F[Actualizar<br/>Base Datos]
    
    F --> G[Registrar<br/>auditoría]
    G --> H{Stock<br/>crítico?}
    
    H -->|Sí| I[Generar<br/>alerta]
    H -->|No| J([Fin])
    I --> J
    
    style A fill:#90EE90
    style B fill:#87CEEB
    style C fill:#87CEEB
    style E fill:#DDA0DD
    style F fill:#FFB6C1
    style G fill:#FFD700
    style I fill:#FF6347
    style J fill:#90EE90
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
