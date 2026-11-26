from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs
from html import escape


# PRODUCTOS Y PRECIOS
PRODUCTOS = {
    "mochila": {
        "nombre": "Mochila tejida",
        "precio": 120000
    },
    "perlado": {
        "nombre": "Bolso perlado",
        "precio": 150000
    },
    "mini": {
        "nombre": "Mini bolso combinado",
        "precio": 95000
    }
}


# CODIGOS DE DESCUENTO
CODIGOS_DESCUENTO = {
    "MIA10": 10,
    "PERLAS15": 15
}


def formatear_pesos(valor):
    """Convierte un número a pesos colombianos."""
    return "$" + f"{valor:,.0f}".replace(",", ".")


def calcular_pedido(clave_producto, cantidad, codigo=""):
    """Calcula el valor del pedido y sus descuentos."""

    if clave_producto not in PRODUCTOS:
        raise ValueError("Selecciona un producto válido.")

    try:
        cantidad = int(cantidad)
    except (TypeError, ValueError):
        raise ValueError("Ingresa una cantidad válida.")

    if cantidad < 1 or cantidad > 99:
        raise ValueError("La cantidad debe estar entre 1 y 99.")

    producto = PRODUCTOS[clave_producto]

    subtotal = producto["precio"] * cantidad

    codigo = (codigo or "").strip().upper()

    porcentaje = 0
    mensaje = "Sin código de descuento."

    # PROMOCION AUTOMATICA PARA DOS BOLSOS PERLADOS
    if clave_producto == "perlado" and cantidad >= 2:
        porcentaje = 15
        mensaje = "¡Promoción aplicada! 15% de descuento por comprar dos o más bolsos perlados."

    # CODIGOS DE DESCUENTO
    elif codigo:
        if codigo in CODIGOS_DESCUENTO:
            porcentaje = CODIGOS_DESCUENTO[codigo]
            mensaje = (
                f"Código {codigo} aplicado: "
                f"{porcentaje}% de descuento."
            )
        else:
            mensaje = "El código no es válido. No se aplicó descuento."

    descuento = round(subtotal * porcentaje / 100)

    total = subtotal - descuento

    return {
        "producto": producto["nombre"],
        "cantidad": cantidad,
        "subtotal": subtotal,
        "porcentaje": porcentaje,
        "descuento": descuento,
        "total": total,
        "mensaje": mensaje
    }


def mostrar_resultado(resultado):
    """Construye la página con el resumen del pedido."""

    return f"""
    <section class="resultado-calculadora">
        <h2>Resumen de tu pedido</h2>

        <p>Producto seleccionado:</p>
        <strong>{escape(resultado["producto"])}</strong>

        <p>Cantidad:</p>
        <strong>{resultado["cantidad"]}</strong>

        <hr>

        <p>Subtotal:</p>
        <strong>{formatear_pesos(resultado["subtotal"])}</strong>

        <p>Descuento ({resultado["porcentaje"]}%):</p>
        <strong>-{formatear_pesos(resultado["descuento"])}</strong>

        <hr>

        <p>Valor total:</p>
        <span class="valor-total">
            {formatear_pesos(resultado["total"])}
        </span>

        <p class="mensaje-calculadora">
            {escape(resultado["mensaje"])}
        </p>

        <a href="/#calculadora" class="boton-calcular">
            Volver a la calculadora
        </a>
    </section>
    """


def mostrar_error(mensaje):
    """Muestra un mensaje cuando los datos no son válidos."""

    return f"""
    <section class="resultado-calculadora">
        <h2>No pudimos calcular tu pedido</h2>
        <p>{escape(mensaje)}</p>
        <a href="/#calculadora" class="boton-calcular">
            Volver a intentarlo
        </a>
    </section>
    """


class handler(BaseHTTPRequestHandler):

    def do_POST(self):

        try:
            longitud = int(
                self.headers.get("Content-Length", 0)
            )

            datos = self.rfile.read(longitud).decode("utf-8")

            formulario = parse_qs(datos)

            producto = formulario.get(
                "producto", [""]
            )[0]

            cantidad = formulario.get(
                "cantidad", [""]
            )[0]

            codigo = formulario.get(
                "codigo", [""]
            )[0]

            resultado = calcular_pedido(
                producto,
                cantidad,
                codigo
            )

            contenido = mostrar_resultado(resultado)

        except ValueError as error:
            contenido = mostrar_error(str(error))

        except Exception:
            contenido = mostrar_error(
                "Ocurrió un inconveniente. Revisa los datos e inténtalo nuevamente."
            )

        self.responder(contenido)

    def responder(self, contenido):

        pagina = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Resultado del pedido | MiaAmorBag</title>
            <link rel="stylesheet" href="/css/styles.css">
        </head>
        <body>
            <main>
                {contenido}
            </main>
        </body>
        </html>
        """

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "text/html; charset=utf-8"
        )
        self.end_headers()

        self.wfile.write(
            pagina.encode("utf-8")
        )