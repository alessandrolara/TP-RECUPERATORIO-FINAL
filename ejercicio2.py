import json


class StockInvalidoError(Exception):
    """Se lanza cuando se intenta asignar un stock inválido (negativo o no entero)."""


# ---------------------------------------------------------------- Punto A
class DispositivoEcológico:
    def __init__(self, nombre, precio, stock):
        self.nombre = nombre
        self.precio = precio
        self.stock = stock          

    @property
    def stock(self):
        return self._stock

    @stock.setter
    def stock(self, valor):
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise StockInvalidoError(f"El stock debe ser un entero, se recibió: {valor!r}")
        if valor < 0:
            raise StockInvalidoError(f"El stock no puede ser negativo: {valor}")
        self._stock = valor

    def ficha_tecnica(self):
        """Ficha comercial genérica. Las subclases la redefinen (polimorfismo)."""
        return (f"Dispositivo: {self.nombre}\n"
                f"Precio: ${self.precio:,.2f}\n"
                f"Stock: {self.stock} unidades")

    def to_dict(self):
        return {
            "tipo": type(self).__name__,
            "nombre": self.nombre,
            "precio": self.precio,
            "stock": self.stock,
        }


class PanelSolar(DispositivoEcológico):
    def __init__(self, nombre, precio, stock, potencia_w):
        super().__init__(nombre, precio, stock)
        self.potencia_w = potencia_w

    def ficha_tecnica(self):
        return (f"Panel solar: {self.nombre}\n"
                f"Potencia: {self.potencia_w} W\n"
                f"Precio: ${self.precio:,.2f}\n"
                f"Stock: {self.stock} unidades")

    def to_dict(self):
        datos = super().to_dict()
        datos["potencia_w"] = self.potencia_w
        return datos


# ---------------------------------------------------------------- Punto B
class GestorInventario:
    def guardar_catalogo_json(self, lista_dispositivos, ruta_archivo="catalogo_ecotech.json"):
        datos = [d.to_dict() for d in lista_dispositivos]
        with open(ruta_archivo, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, indent=4, ensure_ascii=False)
        return ruta_archivo


# ------------------------------------------------- Bloque de prueba
if __name__ == "__main__":
    catalogo = []
    
    catalogo.append(DispositivoEcológico("Cargador solar portátil", 15999.90, 25))
    catalogo.append(PanelSolar("Panel Monocristalino 450W", 289500.00, 10, 450))
    catalogo.append(PanelSolar("Panel Policristalino 330W", 198000.00, 15, 330))

    for dispositivo in catalogo:
        print(dispositivo.ficha_tecnica())
        print("-" * 35)

    try:
        catalogo[1].stock = -5
    except StockInvalidoError as error:
        print(f"[Capturado] StockInvalidoError: {error}")
    print(f"Stock se mantiene en: {catalogo[1].stock}")

    try:
        catalogo.append(PanelSolar("Panel defectuoso", 100000.00, -3, 200))
    except StockInvalidoError as error:
        print(f"[Capturado] StockInvalidoError al crear: {error}")

    gestor = GestorInventario()
    ruta = gestor.guardar_catalogo_json(catalogo, "catalogo_ecotech.json")
    print(f"Catálogo exportado: {ruta} ({len(catalogo)} productos)")
