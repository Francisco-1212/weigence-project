/**
 * Sistema Simple de Detección de Cambios de Peso - Movimientos Grises
 * Lee directamente de lecturas_peso y registra movimientos cuando diferencia_anterior > 15g
 */

class DetectorPesoSimple {
  constructor() {
    this.UMBRAL = 15; // gramos
    this.lecturasYaProcesadas = new Set(); // IDs de lecturas ya procesadas
    this.ultimoMovimientoPorEstante = {}; // Rastrear último peso por estante
    this.UMBRAL_CAMBIO_REAL = 50; // gramos - cambio mínimo para considerar movimiento real
  }

  async verificarEstante(idEstante) {
    try {
      console.log(`🔍 [Verificar] Consultando estante ${idEstante}...`);
      
      // 1. Obtener última lectura del estante (sin CSRF - es petición interna)
      const response = await fetch('/api/lecturas_peso_recientes', {
        method: 'POST',
        credentials: 'include',
        headers: { 
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ id_estante: idEstante })
      });

      console.log(`📡 [Verificar] Respuesta HTTP ${response.status} para estante ${idEstante}`);

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`❌ [Verificar] Error HTTP ${response.status} para estante ${idEstante}:`, errorText);
        return;
      }

      const resultado = await response.json();
      console.log(`📊 [Verificar] Datos recibidos para estante ${idEstante}:`, resultado);
      
      if (!resultado.success || !resultado.data || resultado.data.length === 0) {
        console.log(`⚠️ [Verificar] Sin lecturas para estante ${idEstante}`);
        return;
      }

      const lectura = resultado.data[0]; // La más reciente
      const idLectura = lectura.id_lectura;
      const diferencia = parseFloat(lectura.diferencia_anterior) || 0;
      const timestampLectura = new Date(lectura.timestamp);
      const ahora = new Date();
      const edadSegundos = (ahora - timestampLectura) / 1000;

      // 2. Si la lectura es muy antigua (>1 min), omitir (ya se recuperó al cargar)
      if (edadSegundos > 60) {
        return; // Silenciosamente omitir
      }
      
      // Si es antigua pero relevante (30s - 1min), solo para debug
      if (edadSegundos > 30) {
        console.log(`⏱️ [Verificar] Procesando lectura reciente ${idLectura} (${edadSegundos.toFixed(1)}s)`);
      }

      // 3. Si ya procesamos esta lectura, skip
      if (this.lecturasYaProcesadas.has(idLectura)) {
        return;
      }

      // 4. Verificar si supera el umbral (positivo o negativo)
      if (Math.abs(diferencia) < this.UMBRAL) {
        return; // Cambio muy pequeño
      }

      // 5. Verificar cambio real vs último peso registrado
      const pesoActual = parseFloat(lectura.peso_leido);
      const ultimoPeso = this.ultimoMovimientoPorEstante[idEstante];
      
      if (ultimoPeso !== undefined) {
        const cambioReal = Math.abs(pesoActual - ultimoPeso);
        
        if (cambioReal < this.UMBRAL_CAMBIO_REAL) {
          console.log(`⚪ [Verificar] Estante ${idEstante}: Cambio insignificante desde último registro (${cambioReal.toFixed(1)}g), omitiendo`);
          this.lecturasYaProcesadas.add(idLectura);
          return;
        }
      }

      console.log(`🔔 [Detección] Estante ${idEstante}: ${diferencia > 0 ? 'ADICIÓN' : 'RETIRO'} de ${Math.abs(diferencia).toFixed(1)}g (Lectura: ${edadSegundos.toFixed(1)}s)`);

      // 6. Marcar como procesada
      this.lecturasYaProcesadas.add(idLectura);
      
      // 7. Actualizar último peso registrado
      this.ultimoMovimientoPorEstante[idEstante] = pesoActual;

      // 8. Registrar el movimiento gris
      await this.registrarMovimientoGris(idEstante, lectura);

    } catch (error) {
      console.error(`❌ [Verificar] Error verificando estante ${idEstante}:`, error);
      console.error(`   Stack:`, error.stack);
    }
  }

  async registrarMovimientoGris(idEstante, lectura, desdeRecuperacion = false) {
    const diferencia = parseFloat(lectura.diferencia_anterior);
    const pesoActual = parseFloat(lectura.peso_leido);
    const tipoCambio = diferencia > 0 ? 'ADICIÓN' : 'RETIRO';
    const idLectura = lectura.id_lectura;

    // VERIFICACIÓN DOBLE: Si ya está procesada, no enviar (excepto si viene de recuperación que ya verificó)
    if (!desdeRecuperacion && this.lecturasYaProcesadas.has(idLectura)) {
      console.log(`⏭️ [Registrar] Lectura ${idLectura} ya procesada anteriormente, omitiendo envío`);
      return false;
    }

    const movimiento = {
      id_estante: idEstante,
      idproducto: null,
      // rut_usuario se toma automáticamente de la sesión en el backend
      cantidad: diferencia > 0 ? 1 : -1,
      tipo_evento: 'gris',
      peso_total: Math.abs(diferencia) / 1000, // kg - siempre positivo para buscar coincidencias
      peso_por_unidad: Math.abs(diferencia) / 1000, // kg
      observacion: `${tipoCambio}: ${Math.abs(diferencia).toFixed(0)}g [Lectura: ${idLectura}]`
    };

    // Marcar ANTES de enviar para evitar duplicados por race condition (solo si no es recuperación)
    if (!desdeRecuperacion) {
      this.lecturasYaProcesadas.add(idLectura);
    }

    try {
      const response = await fetch('/api/movimientos/gris', {
        method: 'POST',
        credentials: 'include',
        headers: { 
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(movimiento)
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`❌ Error HTTP ${response.status} al registrar movimiento:`, errorText);
        if (!desdeRecuperacion) this.lecturasYaProcesadas.delete(idLectura);
        return false;
      }

      const resultado = await response.json();
      
      if (resultado.success) {
        // Verificar si fue rechazado por duplicado
        if (resultado.data === null && resultado.mensaje) {
          console.log(`⏭️ [Registrar] ${resultado.mensaje}`);
          return false; // Ya estaba procesado
        }
        
        console.log(`✅ Movimiento gris registrado - Estante ${idEstante}: ${tipoCambio} ${Math.abs(diferencia).toFixed(0)}g`);
        
        // Marcar como procesada DESPUÉS del registro exitoso (si es recuperación)
        if (desdeRecuperacion) {
          this.lecturasYaProcesadas.add(idLectura);
        }
        
        if (window.mostrarToast) {
          window.mostrarToast(
            `${diferencia > 0 ? '📥' : '📤'} ${tipoCambio} en estante ${idEstante}: ${Math.abs(diferencia).toFixed(0)}g`,
            diferencia > 0 ? 'warning' : 'info'
          );
        }
        
        return true;
      } else {
        console.error(`❌ Error al registrar movimiento:`, resultado.error);
        // Si falló, quitar de procesadas para reintentar
        if (!desdeRecuperacion) this.lecturasYaProcesadas.delete(idLectura);
        return false;
      }
    } catch (error) {
      console.error('❌ Error registrando movimiento:', error);
      if (!desdeRecuperacion) this.lecturasYaProcesadas.delete(idLectura);
      return false;
    }
  }

  async recuperarMovimientosPerdidos(estantes) {
    console.log(`🔄 [Recuperar] Buscando movimientos perdidos en estantes: ${estantes.join(', ')}`);
    
    try {
      // Obtener lecturas pendientes del último minuto (para evitar consolidar ciclos antiguos)
      const response = await fetch('/api/lecturas_peso_pendientes', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ estantes: estantes, minutos: 1 })
      });
      
      if (!response.ok) {
        console.error(`❌ [Recuperar] Error HTTP ${response.status}`);
        return;
      }
      
      const resultado = await response.json();
      
      if (!resultado.success || !resultado.lecturas || resultado.lecturas.length === 0) {
        console.log(`✅ [Recuperar] No hay movimientos pendientes`);
        return;
      }
      
      console.log(`📋 [Recuperar] ${resultado.lecturas.length} lecturas pendientes encontradas`);
      
      // CONSOLIDAR lecturas por estante - calcular cambio neto
      const cambiosPorEstante = {};
      
      for (const lectura of resultado.lecturas) {
        const idLectura = lectura.id_lectura;
        const idEstante = lectura.id_estante;
        const diferencia = parseFloat(lectura.diferencia_anterior) || 0;
        
        // Verificar si ya fue procesada
        if (this.lecturasYaProcesadas.has(idLectura)) {
          console.log(`⏭️ [Recuperar] Lectura ${idLectura} ya procesada, omitiendo`);
          continue;
        }
        
        if (!cambiosPorEstante[idEstante]) {
          cambiosPorEstante[idEstante] = {
            cambioNeto: 0,
            lecturas: [],
            pesoInicial: parseFloat(lectura.peso_leido) - diferencia,
            pesoFinal: parseFloat(lectura.peso_leido)
          };
        }
        
        cambiosPorEstante[idEstante].cambioNeto += diferencia;
        cambiosPorEstante[idEstante].lecturas.push(lectura);
        cambiosPorEstante[idEstante].pesoFinal = parseFloat(lectura.peso_leido);
        
        // NO marcar como procesadas aquí - se marcará después del registro exitoso
      }
      
      // Registrar solo cambios netos significativos (usando umbral mayor)
      for (const [idEstante, datos] of Object.entries(cambiosPorEstante)) {
        const cambioNeto = datos.cambioNeto;
        
        // Usar umbral más alto para recuperación (50g)
        if (Math.abs(cambioNeto) >= this.UMBRAL_CAMBIO_REAL) {
          console.log(`📦 [Recuperar] Estante ${idEstante}: Cambio neto ${cambioNeto > 0 ? '+' : ''}${cambioNeto.toFixed(1)}g (de ${datos.lecturas.length} lecturas)`);
          
          // Usar la lectura MÁS RECIENTE como referencia
          const lecturaReciente = datos.lecturas[datos.lecturas.length - 1];
          
          // Crear lectura consolidada con ID único combinado
          const idsConsolidados = datos.lecturas.map(l => l.id_lectura).join(',');
          const lecturaConsolidada = {
            id_lectura: lecturaReciente.id_lectura, // Usar el más reciente
            id_estante: parseInt(idEstante),
            peso_leido: datos.pesoFinal,
            diferencia_anterior: cambioNeto,
            timestamp: lecturaReciente.timestamp
          };
          
          console.log(`   📋 Consolidando lecturas: [${idsConsolidados}]`);
          
          // Actualizar peso base ANTES de registrar
          this.ultimoMovimientoPorEstante[idEstante] = datos.pesoFinal;
          
          // Registrar con flag de recuperación para manejo especial de lecturas procesadas
          const registrado = await this.registrarMovimientoGris(parseInt(idEstante), lecturaConsolidada, true);
          
          if (registrado) {
            console.log(`   ✅ Movimiento recuperado registrado correctamente`);
          } else {
            console.log(`   ⚠️ Movimiento no se pudo registrar (posible duplicado)`);
          }
        } else {
          console.log(`⚪ [Recuperar] Estante ${idEstante}: Cambio neto insignificante (±${Math.abs(cambioNeto).toFixed(1)}g), omitiendo`);
          
          // Aunque no se registre, actualizar peso base para evitar re-detecciones
          this.ultimoMovimientoPorEstante[idEstante] = datos.pesoFinal;
        }
      }
      
      console.log(`✅ [Recuperar] Recuperación completada`);
      
    } catch (error) {
      console.error(`❌ [Recuperar] Error:`, error);
    }
  }

  async iniciarMonitoreo(estantes, intervalo = 15000) {
    console.log(`🚀 Iniciando monitoreo de estantes: ${estantes.join(', ')} cada ${intervalo/1000}s`);
    
    // 1. Primero recuperar movimientos perdidos
    await this.recuperarMovimientosPerdidos(estantes);
    
    // 2. Luego verificación inicial
    estantes.forEach(estante => this.verificarEstante(estante));
    
    // 3. Iniciar monitoreo continuo
    setInterval(() => {
      estantes.forEach(estante => this.verificarEstante(estante));
    }, intervalo);
  }
}

// Instancia global
window.detectorPeso = new DetectorPesoSimple();

console.log('✅ Detector de peso cargado');
console.log('   📊 Umbral detección: 15g');
console.log('   📦 Umbral movimiento real: 50g');
console.log('   ⏱️  Recuperación: último minuto');
