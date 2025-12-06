/**
 * Sistema Simple de Detección de Cambios de Peso - Movimientos Grises
 * Lee directamente de lecturas_peso y registra movimientos cuando diferencia_anterior > 15g
 */

class DetectorPesoSimple {
  constructor() {
    this.UMBRAL = 15; // gramos
    this.lecturasYaProcesadas = new Set(); // IDs de lecturas ya procesadas
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

      // 2. Si ya procesamos esta lectura, skip
      if (this.lecturasYaProcesadas.has(idLectura)) {
        return;
      }

      // 3. Verificar si supera el umbral (positivo o negativo)
      if (Math.abs(diferencia) < this.UMBRAL) {
        return; // Cambio muy pequeño
      }

      console.log(`🔔 [Detección] Estante ${idEstante}: ${diferencia > 0 ? 'ADICIÓN' : 'RETIRO'} de ${Math.abs(diferencia).toFixed(1)}g`);

      // 4. Marcar como procesada
      this.lecturasYaProcesadas.add(idLectura);

      // 5. Registrar movimiento gris
      await this.registrarMovimientoGris(idEstante, lectura);

    } catch (error) {
      console.error(`❌ [Verificar] Error verificando estante ${idEstante}:`, error);
      console.error(`   Stack:`, error.stack);
    }
  }

  async registrarMovimientoGris(idEstante, lectura) {
    const diferencia = parseFloat(lectura.diferencia_anterior);
    const pesoActual = parseFloat(lectura.peso_leido);
    const tipoCambio = diferencia > 0 ? 'ADICIÓN' : 'RETIRO';

    const movimiento = {
      id_estante: idEstante,
      idproducto: null,
      // rut_usuario se toma automáticamente de la sesión en el backend
      cantidad: diferencia > 0 ? 1 : -1,
      tipo_evento: 'gris',
      peso_total: pesoActual / 1000, // kg
      peso_por_unidad: Math.abs(diferencia) / 1000, // kg
      observacion: `${tipoCambio}: ${Math.abs(diferencia).toFixed(0)}g`
    };

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
        return;
      }

      const resultado = await response.json();
      
      if (resultado.success) {
        console.log(`✅ Movimiento gris registrado - Estante ${idEstante}: ${tipoCambio} ${Math.abs(diferencia).toFixed(0)}g`);
        
        if (window.mostrarToast) {
          window.mostrarToast(
            `${diferencia > 0 ? '📥' : '📤'} ${tipoCambio} en estante ${idEstante}: ${Math.abs(diferencia).toFixed(0)}g`,
            diferencia > 0 ? 'warning' : 'info'
          );
        }
      } else {
        console.error(`❌ Error al registrar movimiento:`, resultado.error);
      }
    } catch (error) {
      console.error('❌ Error registrando movimiento:', error);
    }
  }

  iniciarMonitoreo(estantes, intervalo = 15000) {
    console.log(`🚀 Iniciando monitoreo de estantes: ${estantes.join(', ')} cada ${intervalo/1000}s`);
    
    setInterval(() => {
      estantes.forEach(estante => this.verificarEstante(estante));
    }, intervalo);

    // Verificación inicial
    estantes.forEach(estante => this.verificarEstante(estante));
  }
}

// Instancia global
window.detectorPeso = new DetectorPesoSimple();

console.log('✅ Detector de peso cargado - Umbral: 15g');
