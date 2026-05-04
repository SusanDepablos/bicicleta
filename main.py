import flet as ft
import json
import os

ARCHIVO_DATOS = "config_tasas.json"

def cargar_datos():
    if os.path.exists(ARCHIVO_DATOS):
        try:
            with open(ARCHIVO_DATOS, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def guardar_datos(pv, pc, com_salida, com_plat, aplica_compra):
    with open(ARCHIVO_DATOS, "w") as f:
        json.dump({
            "tasa_venta": pv, 
            "tasa_compra": pc,
            "comision_salida": com_salida,
            "comision_plataforma": com_plat,
            "aplica_compra": aplica_compra
        }, f)

def main(page: ft.Page):
    page.title = "Calculadora Arbitraje"
    page.window_width = 400
    page.window_height = 850
    page.scroll = "adaptive"
    page.theme_mode = "dark" 

    # --- CAMPOS DE ENTRADA PRINCIPALES ---
    capital_input = ft.TextField(label="Capital a invertir (USD)", keyboard_type="number")
    pv_input = ft.TextField(label="Tasa de Venta (Pv)", keyboard_type="number")
    pc_input = ft.TextField(label="Tasa de Compra (Pc)", keyboard_type="number")

    # --- CAMPOS DE COMISIONES (NUEVOS) ---
    aplica_compra_check = ft.Checkbox(label="Cobrar comisión de compra (0.5%)", value=True)
    com_salida_input = ft.TextField(label="Comisión salida banco (%)", value="2.5", keyboard_type="number")
    com_plataforma_input = ft.TextField(label="Recarga plataforma (%)", value="3.6", keyboard_type="number")

    # --- CARGAR DATOS GUARDADOS ---
    datos_guardados = cargar_datos()
    if "tasa_venta" in datos_guardados:
        pv_input.value = datos_guardados["tasa_venta"]
    if "tasa_compra" in datos_guardados:
        pc_input.value = datos_guardados["tasa_compra"]
    if "comision_salida" in datos_guardados:
        com_salida_input.value = datos_guardados["comision_salida"]
    if "comision_plataforma" in datos_guardados:
        com_plataforma_input.value = datos_guardados["comision_plataforma"]
    if "aplica_compra" in datos_guardados:
        aplica_compra_check.value = datos_guardados["aplica_compra"]

    resultado_texto = ft.Text(size=16, selectable=True)

    # --- LÓGICA DE CÁLCULO ---
    def calcular(e):
        try:
            capital = float(capital_input.value)
            pv = float(pv_input.value)
            pc = float(pc_input.value)
            
            # Leer las comisiones dinámicas
            val_salida = float(com_salida_input.value)
            val_plataforma = float(com_plataforma_input.value)

            # Guardar automáticamente la configuración para la próxima vez
            guardar_datos(
                pv_input.value, 
                pc_input.value, 
                com_salida_input.value, 
                com_plataforma_input.value, 
                aplica_compra_check.value
            )

            # Lógica matemática adaptada
            factor_compra = 1.005 if aplica_compra_check.value else 1.0
            factor_salida = 1 + (val_salida / 100) # Ej: 1 + 0.025 = 1.025
            factor_plataforma = 1 - (val_plataforma / 100) # Ej: 1 - 0.036 = 0.964

            bs_totales = capital * pv
            bs_netos = bs_totales / factor_compra
            cantidad_usd = int(bs_netos / pc) 
            
            monto_plataforma = cantidad_usd / factor_salida
            recibes = monto_plataforma * factor_plataforma 

            ganancia = recibes - capital
            rendimiento = ((recibes / capital) - 1) * 100

            resultado_texto.value = (
                f"📊 Desglose de Operación Susan\n\n"
                f"1. Fase de Compra (Efectivo/Banco):\n"
                f"• Bolívares Totales por venta: {bs_totales:,.2f} Bs.\n"
                f"• Dólares que puedes comprar: {cantidad_usd} USD\n"
                f"• Bolívares necesarios: {(cantidad_usd * pc * factor_compra):,.2f} Bs.\n"
                f"• Cambio (Sobrante): {bs_totales - (cantidad_usd * pc * factor_compra):,.2f} Bs.\n\n"
                f"2. Fase de Movimiento (Transferencia):\n"
                f"• Monto a colocar en la plataforma: {monto_plataforma:,.2f} USD\n"
                f"• Comisión de salida ({val_salida}%): {cantidad_usd - monto_plataforma:,.2f} USD\n"
                f"• Total en cuenta bancaria: {cantidad_usd} USD\n\n"
                f"3. Resultado Final:\n"
                f"• Monto neto que cae en plataforma: {recibes:,.2f} USD\n"
                f"• Ganancia Neta: {ganancia:,.2f} USD\n"
                f"• Rendimiento Real: {rendimiento:,.2f}%\n"
            )
        except ValueError:
            resultado_texto.value = "⚠️ Error: Asegúrate de llenar todos los campos y usar el punto (.) para los decimales."
        
        page.update()

    # --- INTERFAZ VISUAL ---
    boton_calcular = ft.ElevatedButton(
        "Calcular Operación", 
        on_click=calcular
    )

    page.add(
        ft.Text("Arbitraje Pro", size=32, weight="bold"),
        ft.Text("Calculadora Dinámica", size=14, color="grey"),
        ft.Divider(height=10, color="transparent"),
        capital_input,
        pv_input,
        pc_input,
        ft.Divider(height=5, color="grey"), # Un divisor visual
        ft.Text("Configuración de Comisiones:", weight="bold"),
        aplica_compra_check,
        com_salida_input,
        com_plataforma_input,
        ft.Divider(height=10, color="transparent"),
        boton_calcular,
        ft.Divider(height=20),
        resultado_texto
    )

ft.app(target=main)