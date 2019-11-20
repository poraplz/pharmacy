__author__ = "Kevin Samuel Rodrigues Toledo"
__license__ = "Public Domain"
__version__ = "1.0.0"
__email__ = "kevin.rodrigues@fpuna.edu.py"
__status__ = "Prototype"

'''
    Sistema de Pedidos en Farmacias

'''

from controlador import *
import os
import sys
import logging
import utiles


class Vista:
    @staticmethod
    def realizar_pedido():
        try:
            articulos = []
            articulos = Vista.seleccionar_articulos(articulos)
            if articulos:
                orden = Controlador.crear_orden(articulos)
                Vista.limpiar_pantalla()
                Vista.imprimir('Detalle de la orden creada: ')
                Vista.imprimir(str(orden))
            else:
                raise Exception('Debe introducir por lo menos un articulo.')
        except Exception as e:
            Vista.imprimir(str(e))
            Vista.imprimir('No se pudo generar la orden...')

        Vista.pausa()

    @staticmethod
    def cobrar_pedido():
        Vista.imprimir('Introduzca numero de orden: ')
        try:
            entrada = Vista.leer_numero()
            orden = Controlador.buscar_orden(
                entrada, utiles.ESTADO_PENDIENTE)
            Vista.imprimir('Introduzca numero de cedula: ')
            entrada_cedula = Vista.leer_numero()
            cliente = Controlador.buscar_cliente(entrada_cedula)
            if cliente is None:
                Vista.imprimir(
                    'Desea crear el cliente de cedula: ' + str(entrada_cedula) + '?')
                Vista.imprimir('Y: Si, N: No')
                desea_registrar = Vista.leer_cadena()
                if desea_registrar[0] == 'Y':
                    cliente = Vista.registrar_cliente(entrada_cedula)
                elif desea_registrar[0] == 'N':
                    cliente = Controlador.obtener_cliente_por_defecto()
                else:
                    raise Exception('Opcion invalida')
            Vista.pausa()
            medio_pago = Vista.seleccionar_metodo_pago()
            comprobante = Controlador.crear_comprobante(
                orden, medio_pago, cliente)
            cliente.facturas.append(comprobante)
            orden.estado = utiles.ESTADO_PAGADO
            Controlador.guardar_comprobante(comprobante)
            Vista.imprimir('Cobro realizado con exito: ')
            Vista.imprimir(str(comprobante))
            Vista.pausa()
        except Exception as e:
            Vista.imprimir('No se pudo realizar el cobro: ' + str(e))
            Vista.pausa()

    @staticmethod
    def seleccionar_metodo_pago():
        ''' 
            Metodo que permite ingresar el tipo de medio de pago a utilizar
        '''
        Vista.limpiar_pantalla()
        Vista.imprimir('----------- Seleccion Metodo de Pago ------------')
        Vista.imprimir('Seleccione metodo de pago: 1: Efectivo, 2: Tarjeta')
        metodo_pago = {1: Controlador.obtener_metodo_pago_efectivo(
        ), 2: Controlador.obtener_metodo_pago_tarjeta()}
        entrada = Vista.leer_numero()
        return metodo_pago[entrada]

    @staticmethod
    def desplegar_articulos():
        Vista.limpiar_pantalla()
        Vista.imprimir(
            '---------- Listado de Articulos en categoria ----------')
        # DICCIONARIO que posee los articulos disponibles en categoria
        articulos_categorizados = Controlador.filtrar_articulos()
        articulos_higiene = articulos_categorizados[utiles.KEY_HIGIENE]
        articulos_medicamento = articulos_categorizados[utiles.KEY_MEDICAMENTO]
        articulos_belleza = articulos_categorizados[utiles.KEY_BELLEZA]
        if not Controlador.farmacia_existen_articulos():
            Vista.farmacia_sin_articulos()
        else:
            mensaje = ('\n--- LISTA DE ARTICULOS DISPONIBLES: ---\n')
            mensaje = mensaje + ('\t--- MEDICAMENTOS: --- \n')
            for medicamento in articulos_medicamento:
                mensaje = (mensaje + '\t\t' + medicamento.descripcion + '\n')

            mensaje = mensaje + ('\t--- ARTICULOS DE HIGIENE PERSONAL: --- \n')
            for higiene in articulos_higiene:
                mensaje = (mensaje + '\t\t' + higiene.descripcion + '\n')

            mensaje = mensaje + ('\t--- ARTICULOS DE BELLEZA: --- \n')
            for belleza in articulos_belleza:
                mensaje = (mensaje + '\t\t' + belleza.descripcion + '\n')
            Vista.imprimir(mensaje)
        Vista.pausa()

    @staticmethod
    def gestionar_informe():
        try:
            acciones = {'DD': lambda: Vista.obtener_informe_diario(),
                        'MM': lambda: Vista.obtener_informe_mensual(),
                        'YY': lambda: Vista.obtener_informe_anual(),
                        'WW': lambda: Vista.obtener_informe_semanal()}
            Vista.imprimir('Seleccione periodo de tiempo')
            Vista.imprimir('Diario: DD, Semana: WW, Mensual: MM, Anual: YY')
            entrada = Vista.leer_cadena()
            utiles.realizar(acciones[entrada[0]])
        except Exception as e:
            Vista.imprimir("Error al intentar obtener informe: " + str(e))
        Vista.pausa()

    @staticmethod
    def obtener_informe_diario():
        Vista.imprimir('Introduzca anio: ')
        anio = Vista.leer_numero()
        Vista.imprimir('Introduzca mes: ')
        mes = Vista.leer_numero()
        Vista.imprimir('Introduzca dia')
        dia = Vista.leer_numero()
        condicion = Controlador.definicion_filtro_comprobante_diario(
            anio, mes, dia)
        reporte = Controlador.filtrar_comprobantes(condicion)
        Vista.imprimir(reporte)

    @staticmethod
    def obtener_informe_semanal():
        Vista.imprimir('Introduzca anio: ')
        anio = Vista.leer_numero()
        Vista.imprimir('Introduzca mes: ')
        mes = Vista.leer_numero()
        Vista.imprimir('Introduzca semana')
        semana = Vista.leer_numero()
        condicion = Controlador.definicion_filtro_comprobante_semanal(
            semana, mes, anio)
        reporte = Controlador.filtrar_comprobantes(condicion)
        Vista.imprimir(reporte)

    @staticmethod
    def obtener_informe_mensual():
        Vista.imprimir('Introduzca anio: ')
        anio = Vista.leer_numero()
        Vista.imprimir('Introduzca mes: ')
        mes = Vista.leer_numero()
        condicion = Controlador.definicion_filtro_comprobante_mensual(
            anio, mes)
        reporte = Controlador.filtrar_comprobantes(condicion)
        Vista.imprimir(reporte)

    @staticmethod
    def obtener_informe_anual():
        Vista.imprimir('Introduzca anio: ')
        entrada = Vista.leer_numero()
        condicion = Controlador.definicion_filtro_comprobante_anual(entrada)
        reporte = Controlador.filtrar_comprobantes(condicion)
        Vista.imprimir(reporte)

    @staticmethod
    def registrar_cliente(numero_cedula):
        ''' 
            Metodo para registrar un cliente en el sistema
        '''
        Vista.imprimir('Introduzca nombre: ')
        nombre = Vista.leer_cadena()[0]
        Vista.imprimir('Introduzca apellido')
        apellido = Vista.leer_cadena()[0]
        Vista.imprimir('Introduzca direccion: ')
        direccion = Vista.leer_cadena()[0]
        Vista.imprimir('Introduzca RUC')
        ruc = Vista.leer_cadena()[0]
        contactos = Vista.seleccionar_contactos()
        cliente = Controlador.registrar_cliente(numero_cedula,
                                                nombre, apellido, ruc, direccion, contactos)
        Vista.imprimir('Cliente registrado exitosamente: ' + str(cliente))
        return cliente

    @staticmethod
    def seleccionar_contactos():
        Vista.imprimir('--------- Seleccion de contactos ----------')
        contactos = []
        while(True):
            opcion = {1: lambda: Vista.seleccionar_contacto_telefono(),
                      2: lambda: Vista.seleccionar_contacto_email(),
                      3: lambda: Vista.seleccionar_contacto_red_social()}
            Vista.imprimir('Seleccione tipo de contacto: {}, {}, {}, {}'
                           .format('1. Telefono', '2: Email', '3: Red Social', '-1: Finalizar'))
            entrada = Vista.leer_numero()
            if (entrada == -1):
                return contactos
            contactos.append(utiles.realizar(opcion[entrada]))

    @staticmethod
    def seleccionar_contacto_telefono():
        ''' Metodo para selecciona un contacto de tipo telefonico '''
        Vista.imprimir('Introduzca prefijo: ')
        prefijo = Vista.leer_numero()
        Vista.imprimir('Introduzca valor: ')
        valor = Vista.leer_numero()
        return Telefono(prefijo, valor)

    @staticmethod
    def seleccionar_contacto_email():
        ''' Metodo para selecciona un contacto de tipo correo electronico '''
        Vista.imprimir('Introduzca valor')
        valor = Vista.leer_cadena()
        return Email(valor)

    @staticmethod
    def seleccionar_contacto_red_social():
        ''' Metodo para selecciona un contacto de tipo red social '''
        Vista.imprimir('Introduzca valor: ')
        valor = Vista.leer_cadena()
        return RedSocial(valor)

    # Metodo para limpiar la pantalla
    @staticmethod
    def limpiar_pantalla():
        '''Limpia la pantalla de la sesion utilizada'''
        os.system('cls' if os.name == 'nt' else 'clear')

    # Metodo para la lectura de numeros con manejo de excepciones
    @staticmethod
    def leer_numero(mensaje='', valor_minimo=-1, valor_maximo=None, default=None):
        ''' Se valida para establecer un rango de validez
         :param str mensaje: El mensaje a mostrar al usuario
         :param int valor_minimo: Valor minimo aceptable
         :param int valor_maximo: Valor maximo aceptable
         :param int default: Valor por defecto
        '''
        activo = True
        valor = input(mensaje)
        valor = valor or default
        try:
            valor_numerico = int(valor)
            if ((valor_maximo != None) and (valor_numerico < valor_minimo or
                                            valor_numerico > valor_maximo)) or ((valor_maximo == None)
                                                                                and (valor_numerico < valor_minimo)):
                raise Exception("Introduzca argumentos validos")
            else:
                activo = False
                return valor_numerico
        except ValueError as e:
            raise ValueError("Debe ingresar un número")
        except TypeError as e:
            raise Exception("Debe ingresar un número")
        except Exception as e:
            raise (e)

    @staticmethod
    def leer_cadena(mensaje='', default=None):
        ''' Funcion que obtiene una cadena
         :param str mensaje: El mensaje a mostrar al usuario
         :param str default: Valor por defecto
         '''
        if default:
            mensaje = mensaje + default + chr(8) * len(default)
        entrada = input(mensaje)
        entrada = entrada or default
        try:
            if entrada == None:
                raise Exception("Debe ingresar el dato!")
            # Se retorna una lista con el valor válido ingresado por el usuario
            # Y el boolean True indicando que se pudo concretar la lectura
            return [entrada, True]

            # En caso de algun error, se retorna una lista con el error
            # Y un boolean False que indica el error
        except ValueError as e:
            return ["Vuelva a ingresar el dato", False]
        except TypeError as e:
            return ["Vuelva a ingresar el dato", False]
        except Exception as e:
            return [e, False]

    @staticmethod
    def pausa():
        '''Confirmación para continuar'''
        entrada = input("Continuar... ")
        return

    @staticmethod
    def error_menu():
        '''Error en la seleccion del menú'''
        mensaje = "Error: Opción seleccionada no existe. Vuelva a intentarlo"
        Vista.imprimir(mensaje)

    @staticmethod
    def menu_principal():
        ''' Vista del menú principal'''
        Vista.limpiar_pantalla()
        mensaje = ("---------------- Bienvenido al Sistema de Pedidos para Farmacias ---------------\n" +
                   "------------------- Menú Principal ----------------- \n" +
                   "Ingrese el número correspondiente a la opción deseada: \n"
                   + "1. Realizar pedido \n"
                   + "2. Cobrar pedido \n"
                   + "3. Listar Articulos \n"
                   + "4. Obtener informe \n"
                   + "0. Salir")
        Vista.imprimir(mensaje)

        while(True):
            Vista.imprimir("Accion: ")
            opcion_menu = Vista.leer_numero()
            if isinstance(opcion_menu, str):
                Vista.imprimir(opcion_menu)
            else:
                break

        return opcion_menu

    @staticmethod
    def cerrar_aplicacion():
        '''Confirmación para cerrar la aplicación'''
        mensaje = ("--------------- Cerrar aplicación ----------------\n" +
                   "\n Está Seguro? \t\tSí = 1 \t\tNo = 0 ")
        Vista.imprimir(mensaje)
        entrada = Vista.leer_numero('Confirme: ', 0, 1, 0)
        if (entrada == 1):
            sys.exit()

    @staticmethod
    def farmacia_sin_articulos():
        '''Mensaje de Farmacia sin articulos'''
        mensaje = ("---------------- FARMACIA FUERA DE STOCK ---------------\n" +
                   "Por favor, regrese mas tarde.")
        Vista.imprimir(mensaje)

    @staticmethod
    def seleccionar_categoria():
        return Vista.leer_numero("Ingrese categoria: ")

    @staticmethod
    def imprimir_opciones_categorias():
        mensaje = (
            '------------------- Categorias Disponibles ----------------------------')
        categorias = Controlador.obtener_categorias_articulos()
        for id in categorias:
            mensaje += '\n'
            mensaje += str(id) + '- ' + \
                Controlador.obtener_nombre_categoria(id)
        mensaje += '\n'
        mensaje += '-----------------------------------------------------------------------'
        Vista.imprimir(mensaje)

    @staticmethod
    def seleccionar_articulos(articulos_seleccionados):
        '''
            Metodo para seleccionar articulos
        '''
        Vista.limpiar_pantalla()
        mensaje = ("--------- Seleccione categoria del articulo ---------")
        Vista.imprimir(mensaje)
        Vista.imprimir_opciones_categorias()
        categoria_seleccionada = Vista.seleccionar_categoria()
        try:
            articulos_en_categoria = Controlador.obtener_articulos_por_categoria(
                categoria_seleccionada)
            Vista.limpiar_pantalla()
            Vista.imprimir('Articulos de la categoria: ' +
                           str(categoria_seleccionada))
            for articulo in articulos_en_categoria:
                Vista.imprimir(articulo)
            Vista.imprimir(
                'Ingrese identificadores de los articulos, enter para confirmar.')
            Vista.imprimir(
                'Ingrese numero de articulo: -1 para confirmar; -2 volver atras')
            articulos_parciales = Vista.seleccionar_articulos_desde(
                articulos_en_categoria)
            articulos_seleccionados.extend(articulos_parciales)
            return articulos_seleccionados

        except Exception as e:
            Vista.imprimir(e)
            raise e

    @staticmethod
    def seleccionar_articulos_desde(articulo_en_categoria):
        '''
            Metodo para seleccionar articulos en base al listado de categorias
        '''
        articulos = []
        entrada = Vista.leer_cadena()
        while(not entrada[0] == '-1'):
            if entrada[0] == '-2':
                Vista.seleccionar_articulos(articulos)
                break
            if entrada[0] == '-3':
                return []
            articulo = Controlador.filtrar_articulo_desde(
                articulo_en_categoria, entrada[0])
            if articulo is not None:
                articulos.append(articulo)
            else:
                Vista.imprimir('No se pudo agregar el articulo ingresado.')
            entrada = Vista.leer_cadena()
        return articulos

    @staticmethod
    def imprimir(mensaje):
        ''' Mediante este metodo se imprime en la consola '''
        print(mensaje)

    @staticmethod
    def salir():
        '''Confirmación para salir'''
        op = input("Presione enter para salir. ")
        return

    @staticmethod
    def final():
        '''Indica el final de la aplicacion'''
        mensaje = "----------------------- FIN ----------------------------"
        Vista.imprimir(mensaje)
        op = input()
