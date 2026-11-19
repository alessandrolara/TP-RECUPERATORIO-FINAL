import re

UBICACION_POR_DEFECTO = "Sin ubicación"


_PATRON_NUMERO = re.compile(r"-?\d+(?:[.,]\d+)?")


# ---------------------------------------------------------------- Punto A
def limpiar_registro_sensor(registro_raw):
    """Devuelve un NUEVO diccionario estandarizado (no modifica registro_raw)."""
    sensor_id = str(registro_raw.get("sensor_id", "")).strip()

    temperatura = None
    texto_temp = str(registro_raw.get("temperatura", "")).strip()
    coincidencia = _PATRON_NUMERO.search(texto_temp)
    if coincidencia:
        temperatura = float(coincidencia.group().replace(",", "."))

    ubicacion = registro_raw.get("ubicacion")
    ubicacion = str(ubicacion).strip() if ubicacion is not None else ""
    if not ubicacion:
        ubicacion = UBICACION_POR_DEFECTO

    return {
        "sensor_id": sensor_id,
        "temperatura": temperatura,
        "ubicacion": ubicacion,
    }


# ---------------------------------------------------------------- Punto B
def generar_resumen_sensores(lista_sensores_limpios, umbral_temperatura):
    """Devuelve (lista_ids_en_alerta, promedio_temperatura).

    - Alerta: temperatura estrictamente mayor al umbral.
    - Se ignoran los registros sin temperatura válida (None).
    - Con lista vacía (o sin lecturas válidas) el promedio es 0.0: no hay división por cero.
    """
    validos = [s for s in lista_sensores_limpios if s.get("temperatura") is not None]

    sensores_alerta = [s["sensor_id"] for s in validos if s["temperatura"] > umbral_temperatura]

    if not validos:
        return sensores_alerta, 0.0
    promedio = sum(s["temperatura"] for s in validos) / len(validos)
    return sensores_alerta, promedio


# ------------------------------------------------- Bloque de ejecución
if __name__ == "__main__":
    registros_crudos = [
        {"sensor_id": " SENSOR-001 ", "temperatura": "24.5C", "ubicacion": "Planta Norte"},
        {"sensor_id": "SENSOR-002", "temperatura": "35,5°C", "ubicacion": "Planta Sur"},
        {"sensor_id": " SENSOR-003", "temperatura": " 41.0 C "},                    
        {"sensor_id": "SENSOR-004 ", "temperatura": "28C", "ubicacion": "   "},      
    ]
    UMBRAL = 30.0

    limpios = [limpiar_registro_sensor(r) for r in registros_crudos]
    alertas, promedio = generar_resumen_sensores(limpios, UMBRAL)

    print("=" * 46)
    print("      REPORTE DE SENSORES - EcoTech Solutions")
    print("=" * 46)
    for s in limpios:
        print(f"{s['sensor_id']:<12} {s['temperatura']:>6.1f} °C   {s['ubicacion']}")
    print("-" * 46)
    print(f"Umbral de temperatura : {UMBRAL:.1f} °C")
    print(f"Promedio global       : {promedio:.2f} °C")
    print(f"Sensores en alerta    : {', '.join(alertas) if alertas else 'ninguno'}")

    # Caso borde: lista vacía
    print("Lista vacía ->", generar_resumen_sensores([], UMBRAL))
