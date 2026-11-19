"""Ejercicio 3 - Auditoría con tests unitarios e integración web (EcoTech Solutions).

Todo en un solo archivo:
  - calcular_emisiones_carbono + obtener_metricas_consumo
  - Punto A: TestCalculoEmisiones (unittest)
  - Punto B: vista_panel_sustentabilidad (Django) y la plantilla sustentabilidad/panel.html

Ejecutar los tests:  python ejercicio3.py
Uso en Django: copiar las funciones y la vista a sustentabilidad/views.py y guardar
PLANTILLA_PANEL_HTML en sustentabilidad/templates/sustentabilidad/panel.html
"""
import unittest

try:
    from django.shortcuts import render
except ImportError:          
    render = None


# ------------------------------------------------------------ Lógica de negocio
def calcular_emisiones_carbono(consumo_kwh, factor_emision=0.4):
    """Emisiones (kg CO2) = consumo en kWh * factor de emisión."""
    if consumo_kwh < 0:
        raise ValueError("El consumo no puede ser negativo")
    return consumo_kwh * factor_emision


# ---------------------------------------------------------------- Punto A
class TestCalculoEmisiones(unittest.TestCase):
    
    def test_consumo_nominal_factor_por_defecto(self):
        self.assertAlmostEqual(calcular_emisiones_carbono(100), 40.0)

    def test_consumo_nominal_factor_personalizado(self):
        self.assertAlmostEqual(calcular_emisiones_carbono(250, factor_emision=0.5), 125.0)

    def test_consumo_decimal(self):
        self.assertAlmostEqual(calcular_emisiones_carbono(12.5), 5.0)
    
    def test_consumo_cero(self):
        self.assertEqual(calcular_emisiones_carbono(0), 0)

    def test_consumo_negativo_lanza_value_error(self):
        with self.assertRaises(ValueError):
            calcular_emisiones_carbono(-1)

    def test_consumo_negativo_con_factor_lanza_value_error(self):
        with self.assertRaises(ValueError):
            calcular_emisiones_carbono(-50.5, factor_emision=0.3)


# ---------------------------------------------------------------- Punto B
def obtener_metricas_consumo(registros):
    """Procesa el historial de consumos por planta.

    registros: lista de dicts, p. ej. {"planta": "Norte", "consumo_kwh": 1200.0}
    Devuelve consumo y emisiones por planta, total global de emisiones y
    la planta de mayor consumo.
    """
    consumo_por_planta = {}
    for registro in registros:
        planta = registro["planta"]
        consumo_por_planta[planta] = consumo_por_planta.get(planta, 0) + registro["consumo_kwh"]

    emisiones_por_planta = {
        planta: calcular_emisiones_carbono(consumo)
        for planta, consumo in consumo_por_planta.items()
    }

    planta_mayor_consumo = (
        max(consumo_por_planta, key=consumo_por_planta.get) if consumo_por_planta else None
    )

    return {
        "consumo_por_planta": consumo_por_planta,
        "emisiones_por_planta": emisiones_por_planta,
        "total_emisiones": sum(emisiones_por_planta.values()),
        "planta_mayor_consumo": planta_mayor_consumo,
    }


def _obtener_registros():
    """Historial de consumos. En producción vendría de la base de datos."""
    return [
        {"planta": "Planta Norte", "consumo_kwh": 1200.0},
        {"planta": "Planta Sur", "consumo_kwh": 950.5},
        {"planta": "Planta Norte", "consumo_kwh": 800.0},
        {"planta": "Planta Este", "consumo_kwh": 1500.0},
    ]


def construir_contexto_panel(registros):
    """Arma el diccionario de contexto listo para la plantilla."""
    metricas = obtener_metricas_consumo(registros)
    return {
        "titulo": "Panel de Sustentabilidad - EcoTech Solutions",
        "total_emisiones": round(metricas["total_emisiones"], 2),
        "planta_mayor_consumo": metricas["planta_mayor_consumo"],
        "plantas": [
            {
                "nombre": planta,
                "consumo_kwh": metricas["consumo_por_planta"][planta],
                "emisiones_kg": round(metricas["emisiones_por_planta"][planta], 2),
            }
            for planta in metricas["consumo_por_planta"]
        ],
    }


def vista_panel_sustentabilidad(request):
    contexto = construir_contexto_panel(_obtener_registros())
    return render(request, "sustentabilidad/panel.html", contexto)


# urls.py de la app:
#   urlpatterns = [path("panel/", vista_panel_sustentabilidad, name="panel_sustentabilidad")]

# Contenido de sustentabilidad/templates/sustentabilidad/panel.html
PLANTILLA_PANEL_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>{{ titulo }}</title>
</head>
<body>
    <h1>{{ titulo }}</h1>
    <p><strong>Total global de emisiones:</strong> {{ total_emisiones }} kg CO₂</p>
    <p><strong>Planta de mayor consumo:</strong> {{ planta_mayor_consumo|default:"Sin datos" }}</p>
    <table border="1" cellpadding="6">
        <thead>
            <tr><th>Planta</th><th>Consumo (kWh)</th><th>Emisiones (kg CO₂)</th></tr>
        </thead>
        <tbody>
        {% for planta in plantas %}
            <tr>
                <td>{{ planta.nombre }}</td>
                <td>{{ planta.consumo_kwh }}</td>
                <td>{{ planta.emisiones_kg }}</td>
            </tr>
        {% empty %}
            <tr><td colspan="3">No hay registros de consumo.</td></tr>
        {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""


class TestMetricasConsumo(unittest.TestCase):
    def test_total_y_planta_mayor_consumo(self):
        registros = [
            {"planta": "Norte", "consumo_kwh": 100},
            {"planta": "Sur", "consumo_kwh": 300},
            {"planta": "Norte", "consumo_kwh": 150},
        ]
        m = obtener_metricas_consumo(registros)
        self.assertEqual(m["planta_mayor_consumo"], "Sur")
        self.assertAlmostEqual(m["total_emisiones"], 220.0)
        self.assertAlmostEqual(m["emisiones_por_planta"]["Norte"], 100.0)

    def test_historial_vacio(self):
        m = obtener_metricas_consumo([])
        self.assertIsNone(m["planta_mayor_consumo"])
        self.assertEqual(m["total_emisiones"], 0)

    def test_contexto_para_plantilla(self):
        ctx = construir_contexto_panel(_obtener_registros())
        self.assertEqual(ctx["planta_mayor_consumo"], "Planta Norte")
        self.assertEqual(len(ctx["plantas"]), 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
