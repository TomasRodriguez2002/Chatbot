from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from swiplserver import PrologMQI
import requests
from pyswip import Prolog
#from unidecode import unidecode
from rasa_sdk.events import SlotSet, SessionStarted, ActionExecuted, EventType, UserUtteranceReverted
import json
#from prolog_mqi import PrologMQI
import random
import datetime
import string
import pandas as pd
import csv
import os
from sklearn.preprocessing import LabelEncoder
from sklearn import tree
from sklearn.tree import DecisionTreeClassifier
import graphviz 
import numpy as np



class ActionPredictProduct(Action):
    def name(self):
        return "action_predict_product"

    def run(self, dispatcher, tracker, domain):

        documento = tracker.get_slot("documento")
        csv_filename = f"{documento}.csv"
        archivo_csv = f"C:/Users/s7/Desktop/Facultad/3°/Segundo Cuatrimestre/Programación Exploratoria/Arbol de Decision/{csv_filename}"

        # Obtenemos el dataset a entrenar
        df = pd.read_csv(archivo_csv)
        
        # Preprocesamos los datos
        label_encoder_nombre = LabelEncoder()
        label_encoder_marca = LabelEncoder()
        df['nombre'] = label_encoder_nombre.fit_transform(df['nombre'])
        df['marca'] = label_encoder_marca.fit_transform(df['marca'])
        
        # Seleccionamos las variables
        X = df.drop(columns='gusta')  # Features
        y = df['gusta']  # Target

        # Creamos el modelo
        model = DecisionTreeClassifier(max_depth=3)

        # Entrenamos el modelo
        model.fit(X, y)
        #print(model.score(X, y))

        # Para visualizar el árbol
        dot_data = tree.export_graphviz(model, out_file=None,
                                         feature_names=X.columns.tolist(),
                                         class_names=df['gusta'].astype(str).unique().tolist(),
                                         filled=True, rounded=True,
                                         special_characters=True)
        graph = graphviz.Source(dot_data)
        graph.render("C:/Users/s7/Desktop/Facultad/3°/Segundo Cuatrimestre/Programación Exploratoria/Arbol de Decision/arbolPreview")

        producto = next(tracker.get_latest_entity_values("producto"), None)
        marca = marca = next(tracker.get_latest_entity_values("marca"), None)

        if producto in label_encoder_nombre.classes_:
            producto_encoded = label_encoder_nombre.transform([producto])[0]
        else:
            # Asignar un valor numérico nuevo para el producto
            producto_encoded = df['nombre'].max() + 1
            label_encoder_nombre.classes_ = np.append(label_encoder_nombre.classes_, producto)

        if marca in label_encoder_marca.classes_:
            marca_encoded = label_encoder_marca.transform([marca])[0]
        else:
            # Asignar un valor numérico nuevo para la marca
            marca_encoded = df['marca'].max() + 1
            label_encoder_marca.classes_ = np.append(label_encoder_marca.classes_, marca)

        # Preprocesa los datos para realizar la predicción
        data = pd.DataFrame({'nombre': [producto_encoded], 'marca': [marca_encoded]})

        # Realiza la predicción
        prediction = model.predict(data)

        if prediction[0] == 1:
            dispatcher.utter_message(f"Parece que el producto {producto} de la marca {marca} es de tu agrado")
        else:
            dispatcher.utter_message(f"Parece que el producto {producto} de la marca {marca} no es de tu agrado")

        return []


class ActionReportProduct(Action):
    def name(self) -> Text:
        return "action_report_product"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        producto = next(tracker.get_latest_entity_values("producto"), None)
        marca = next(tracker.get_latest_entity_values("marca"), None)

        if producto and marca:
            documento = tracker.get_slot("documento")

            csv_filename = f"{documento}.csv"

            archivo_csv = f"C:/Users/s7/Desktop/Facultad/3°/Segundo Cuatrimestre/Programación Exploratoria/Arbol de Decision/{csv_filename}"

            # Verifica si el archivo CSV existe en la ruta
            if os.path.exists(archivo_csv):
                # Abre el archivo CSV en modo lectura
                with open(archivo_csv, 'r', newline='') as csv_file:
                    reader = csv.reader(csv_file)

                    # Convierte el contenido del archivo CSV en una lista de listas
                    existing_data = [row for row in reader]

                # Verifica si una fila con los mismos valores ya existe
                new_row = [producto, marca, '0']
                if new_row not in existing_data:
                    # Abre el archivo CSV en modo adición y agrega la nueva fila
                    with open(archivo_csv, 'a', newline='') as csv_file:
                        writer = csv.writer(csv_file)
                        writer.writerow(new_row)

                    dispatcher.utter_message("Genial, gracias por informarlo!")

                else:
                    print("La fila ya existe en el archivo CSV.")
            else:
                print("El archivo CSV no existe en la ruta especificada.")
        else:
            dispatcher.utter_message("No se proporcionaron los valores de 'producto' y 'marca'.")
        
        return []



class ActionBirthdayDiscount(Action):
    def name(self):
        return "action_birthday_discount"

    def is_birthday(self, fecha_nacimiento):

        fecha_actual = datetime.datetime.now()
        dia_actual = fecha_actual.day
        mes_actual = fecha_actual.month

        # Divide la fecha de nacimiento en día y mes
        dia_nacimiento, mes_nacimiento, _ = fecha_nacimiento.split('/')

        return int(dia_nacimiento) == dia_actual and int(mes_nacimiento) == mes_actual

    def generate_discount_code(self):
        # Genera un código de descuento aleatorio de 6 caracteres alfanuméricos
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):

        fecha_nacimiento = tracker.get_slot("fecha_nacimiento")

        if not fecha_nacimiento:
            dispatcher.utter_message("No se proporcionó una fecha de nacimiento válida.")
            return []

        if self.is_birthday(fecha_nacimiento):
            # Genera un código de descuento aleatorio
            codigo_descuento = self.generate_discount_code()

            response_message = (
                "¡Feliz cumpleaños! Como regalo especial, "
                f"tienes un 10% de descuento en tus compras de hoy. "
                f"Usa el código '{codigo_descuento}' al finalizar tu compra. "
                "¡Disfruta de tu día!"
            )
            dispatcher.utter_message(response_message)

        return []



class ActionSearchPromotions(Action):
    def name(self):
        return "action_search_promotions"  

    def get_category_with_highest_count(self, cliente):

        categorias_consultadas = cliente.get("categorias_consultadas", {})
        if not categorias_consultadas:
            return None
        categoria_mas_consultada = max(categorias_consultadas, key=categorias_consultadas.get)
        return categoria_mas_consultada

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):

        documento = tracker.get_slot("documento")

        if not documento:
            dispatcher.utter_message("No se proporcionó un número de documento.")
            return []

        try:
            with open('clientes.json', 'r') as json_file:
                clientes = json.load(json_file)
        except FileNotFoundError:
            dispatcher.utter_message("No se encontró el archivo de clientes.")
            return []

        matching_clients = [cliente for cliente in clientes if cliente.get('documento') == documento]

        if not matching_clients:
            dispatcher.utter_message(f"No se encontró ningún cliente con el documento {documento}.")
            return []

        if len(matching_clients) > 1:
            dispatcher.utter_message("Se encontraron múltiples clientes con el mismo documento. Por favor, proporcione más información para identificar al cliente.")
            return []

        cliente = matching_clients[0]

        categoria = self.get_category_with_highest_count(cliente)

        if categoria:
            url = f"https://api.mercadolibre.com/sites/MLA/search?q={categoria}"

            # Realizar la solicitud HTTP para obtener las ofertas
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])

                if results:
                    # Seleccionar un producto aleatorio de la lista
                    random_product = random.choice(results)

                    title = random_product.get("title", "")
                    price = random_product.get("price", 0.0)
                    permalink = random_product.get("permalink", "")

                    response_message = f"Tenemos una oferta para ti!\n\n\n"
                    response_message += f"{title} a {price}\n"
                    response_message += f"Encuentra mas detalles y compra a traves del siguiente link: {permalink}"

                    dispatcher.utter_message(response_message)
                else:
                    dispatcher.utter_message(f"No se encontraron ofertas para la categoría de {categoria}.")
            else:
                dispatcher.utter_message("No se pudo obtener información de la API de MercadoLibre.")
        else:
            dispatcher.utter_message("El cliente no ha consultado ninguna categoría.")

        return []


class ActionSearchProduct(Action):
    def name(self) -> Text:
        return "action_search_product"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        producto = tracker.get_slot("producto")
        marca_entity = next(tracker.get_latest_entity_values("marca"), None)

        if producto and marca_entity:

            producto_con_marca = f"{producto} {marca_entity}"

            api_url = "https://api.mercadolibre.com/sites/MLA/search"
            params = {"q": producto_con_marca}

            try:

                response = requests.get(api_url, params=params)

                if response.status_code == 200:

                    data = response.json()
                    results = data.get("results", [])

                    if results:

                        product_info = []
                        max_results = 10

                        for idx, result in enumerate(results, start=1):
                            if idx > max_results:
                                break  

                            title = result.get("title")
                            price = result.get("price")
                            permalink = result.get("permalink")

                            if title and price and permalink:
                                product_info.append((title, price, permalink))

                        if product_info:

                            response_message = f"Aquí tienes {producto_con_marca} que hay en stock:\n\n\n"

                            for title, price, permalink in product_info:
                                response_message += f"{title} a ${price}\n"
                                response_message += f"Enlace de compra: {permalink}\n\n\n"

                            # Agrego el nombre y la marca del producto con gusta=1 al csv del cliente
                            
                            documento = tracker.get_slot('documento')

                            csv_filename = f"{documento}.csv"

                            archivo_csv = f"C:/Users/s7/Desktop/Facultad/3°/Segundo Cuatrimestre/Programación Exploratoria/Arbol de Decision/{csv_filename}"

                            # Verifica si el archivo CSV existe en la ruta
                            if os.path.exists(archivo_csv):
                                # Abre el archivo CSV en modo lectura
                                with open(archivo_csv, 'r', newline='') as csv_file:
                                    reader = csv.reader(csv_file)

                                    # Convierte el contenido del archivo CSV en una lista de listas
                                    existing_data = [row for row in reader]

                                # Verifica si una fila con los mismos valores ya existe
                                new_row = [producto, marca_entity, '1']
                                if new_row not in existing_data:
                                    # Abre el archivo CSV en modo adición y agrega la nueva fila
                                    with open(archivo_csv, 'a', newline='') as csv_file:
                                        writer = csv.writer(csv_file)
                                        writer.writerow(new_row)
                                else:
                                    print("La fila ya existe en el archivo CSV.")
                            else:
                                print("El archivo CSV no existe en la ruta especificada.")


                            dispatcher.utter_message(response_message)
                        else:
                            dispatcher.utter_message(f"No se encontraron resultados para {producto_con_marca}.")
                    else:
                        dispatcher.utter_message(f"No se encontraron resultados para {producto_con_marca}.")
                else:
                    dispatcher.utter_message(f"Error en la solicitud: {response.status_code}")
            except requests.exceptions.RequestException as e:
                dispatcher.utter_message(f"Error en la solicitud: {e}")
        else:
            dispatcher.utter_message("No se proporcionó un producto o una marca para buscar.")

        return []


class ActionShowPromotionsWithPrice(Action):
    def name(self) -> Text:
        return "action_show_promotions_with_price"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        price_entity = next(tracker.get_latest_entity_values("precio"), None)

        if price_entity:
            try:
                price = float(price_entity)

                with PrologMQI(port=8000) as mqi:
                    with mqi.create_thread() as prolog_thread:
                        prolog_thread.query("consult('C:/Users/s7/Desktop/Facultad/3°/Segundo Cuatrimestre/Programación Exploratoria/Prolog/DB_Supermarket.pl')")
                        promotions_data = list(prolog_thread.query(f'get_promotions_below_price({price}, Promotions)'))

                if promotions_data:
                    response_message = f"Promociones con precio menor o igual a ${price}:\n"
                    response_message += "\n"

                    for promotion_data in promotions_data:
                        if 'Promotions' in promotion_data:
                            promotions = promotion_data['Promotions']
                            for promotion in promotions:
                                product_name = promotion['args'][0]
                                brand = promotion['args'][1]['args'][0]
                                category = promotion['args'][1]['args'][1]['args'][0]
                                price = promotion['args'][1]['args'][1]['args'][1]['args'][0]
                                quantity = promotion['args'][1]['args'][1]['args'][1]['args'][1]['args'][0]
                                units = promotion['args'][1]['args'][1]['args'][1]['args'][1]['args'][1]

                                response_message += "\n"
                                response_message += f"{product_name} {brand} {quantity} de la categoria {category} a ${price}, llevando {units} unidad/es\n"
                                response_message += "\n"

                        else:
                            response_message += "Promoción sin detalles disponibles\n"
                else:
                    response_message = f"No se encontraron promociones con precio menor o igual a ${price}"

                dispatcher.utter_message(response_message)
            except ValueError:
                dispatcher.utter_message("El valor de precio proporcionado no es valido.")
        else:
            dispatcher.utter_message("No se proporcionó un precio válido.")

        return []


class ActionShowPromotions(Action):
    def name(self) -> Text:
        return "action_show_promotions"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        category = tracker.get_slot("categoria")
        documento = tracker.get_slot("documento")

        if category:
            if documento:

                try:
                    with open('clientes.json', 'r') as json_file:
                        clientes = json.load(json_file)
                except FileNotFoundError:
                    dispatcher.utter_message("No se encontró el archivo de clientes.")
                    return []

                matching_clients = [cliente for cliente in clientes if cliente.get('documento') == documento]

                if not matching_clients:
                    dispatcher.utter_message(f"No se encontró ningún cliente con el documento {documento}.")
                    return []

                if len(matching_clients) > 1:
                    dispatcher.utter_message("Se encontraron múltiples clientes con el mismo documento. Por favor, proporcione más información para identificar al cliente.")
                    return []

                cliente = matching_clients[0]

                # Incrementar en 1 la categoría consultada en 'categorias_consultadas'
                if 'categorias_consultadas' in cliente:
                    categorias_consultadas = cliente['categorias_consultadas']
                    if category in categorias_consultadas:
                        categorias_consultadas[category] = categorias_consultadas.get(category, 0) + 1

                with open('clientes.json', 'w') as json_file:
                    json.dump(clientes, json_file, indent=2)
               
            # Si no hay valor en 'documento', muestra las promociones normalmente
            with PrologMQI(port=8000) as mqi:
                with mqi.create_thread() as prolog_thread:
                    prolog_thread.query("consult('C:/Users/s7/Desktop/Facultad/3°/Segundo Cuatrimestre/Programación Exploratoria/Prolog/DB_Supermarket.pl')")
                    promotions = list(prolog_thread.query(f'get_promotions_by_category({category}, Promotions)'))

            response_message = f"¡Aquí tienes las promociones de la categoría {category}:\n"
            response_message += "\n"

            for promotion_data in promotions[0]['Promotions']:
                product_name = promotion_data['args'][0]
                brand = promotion_data['args'][1]['args'][0]
                price = promotion_data['args'][1]['args'][1]['args'][0]
                quantity = promotion_data['args'][1]['args'][1]['args'][1]['args'][0]
                units = promotion_data['args'][1]['args'][1]['args'][1]['args'][1]

                response_message += "\n"
                response_message += f"{product_name} {brand} {quantity} a ${price} llevando {units} unidad/es\n"
                response_message += "\n"

            dispatcher.utter_message(response_message)
        else:
            dispatcher.utter_message("No se encontró la categoría.")

        return []


class NormalizeCategoryAction(Action):
    def name(self):
        return "normalize_category_action"

    def run(self, dispatcher, tracker, domain):

        slot_value = tracker.get_slot("categoria")

        if slot_value:

            categoria_normalizada = slot_value.lower()
            return [SlotSet("categoria", categoria_normalizada)]

        else:
            return []



class ActionGetClientData(Action):
    def name(self):
        return "action_get_client_data"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):

        documento = next(tracker.get_latest_entity_values("documento"), None)

        if not documento:
            dispatcher.utter_message("No se proporcionó un número de documento.")
            return []

        try:
            with open('clientes.json', 'r') as json_file:
                clientes = json.load(json_file)
        except FileNotFoundError:
            dispatcher.utter_message("No se encontró el archivo de clientes.")
            return []

        matching_clients = [cliente for cliente in clientes if cliente.get('documento') == documento]

        if not matching_clients:
            dispatcher.utter_message(f"No se encontró ningún cliente con el documento {documento}.")
            return []

        if len(matching_clients) > 1:
            dispatcher.utter_message("Se encontraron múltiples clientes con el mismo documento. Por favor, proporcione más información para identificar al cliente.")
            return []

        cliente = matching_clients[0]
        
        nombre = cliente.get('nombre')
        apellido = cliente.get('apellido')
        saludo = f"Hola {nombre} {apellido}!"
        dispatcher.utter_message(saludo)

        return [
            SlotSet("documento", cliente.get('documento')),
            SlotSet("nombre", nombre),
            SlotSet("apellido", apellido),
            SlotSet("fecha_nacimiento", cliente.get('fecha_nacimiento')),
            SlotSet("email", cliente.get('email'))
        ]


class ActionAddClient(Action):
    def name(self):
        return "action_add_client"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain):
        nombre = tracker.get_slot('nombre')
        apellido = tracker.get_slot('apellido')
        fecha_nacimiento = tracker.get_slot('fecha_nacimiento')
        documento = tracker.get_slot('documento')
        email = tracker.get_slot('email')

        if not (nombre and apellido and fecha_nacimiento and documento and email):
            dispatcher.utter_message("Faltan datos para agregar el cliente.")
            return []

        categorias_consultadas = {
            'lacteos': 0,
            'carniceria': 0,
            'limpieza': 0,
            'verduleria': 0,
            'galletitas': 0,
            'bebidas': 0,
            'panaderia': 0,
            'reposteria': 0
        }

        nuevo_cliente = {
            'nombre': nombre,
            'apellido': apellido,
            'fecha_nacimiento': fecha_nacimiento,
            'documento': documento,
            'email': email,
            'categorias_consultadas': categorias_consultadas
        }

        clientes = []
        try:
            with open('clientes.json', 'r') as json_file:
                clientes = json.load(json_file)
        except FileNotFoundError:
            pass  # El archivo aún no existe

        clientes.append(nuevo_cliente)

        with open('clientes.json', 'w') as json_file:
            json.dump(clientes, json_file, indent=2)

        data = {
            'nombre': [],
            'marca': [],
            'gusta': []
        }
        df = pd.DataFrame(data)

        csv_filename = f"{documento}.csv"

        ruta_csv = f"C:/Users/s7/Desktop/Facultad/3°/Segundo Cuatrimestre/Programación Exploratoria/Arbol de Decision/{csv_filename}"

        # Guarda el DataFrame en el archivo CSV
        df.to_csv(ruta_csv, index=False)

        dispatcher.utter_message("Cliente agregado exitosamente.")

        return []


class ActionExtractNameAndLastname(Action):

    def name(self) -> Text:
        return "action_extract_name_and_lastname"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        name_entity = next(tracker.get_latest_entity_values("nombre"), None)
        lastname_entity = next(tracker.get_latest_entity_values("apellido"), None)

        return [
            SlotSet("nombre", name_entity),
            SlotSet("apellido", lastname_entity)
        ]


class ActionDisplayNameAndLastname(Action):

    def name(self) -> Text:
        return "action_display_name_and_lastname"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        name = tracker.get_slot("nombre")
        lastname = tracker.get_slot("apellido")

        if name and lastname:
            dispatcher.utter_message(f"Tu nombre es {name} y tu apellido es {lastname}.")
        else:
            dispatcher.utter_message("Por favor, proporciona tanto tu nombre como tu apellido.")

        return []


class ActionExtractDocument(Action):

    def name(self) -> Text:
        return "action_extract_document"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        document_entity = next(tracker.get_latest_entity_values("documento"), None)

        return [
            SlotSet("documento", document_entity)
        ]


class ActionDisplayDocument(Action):

    def name(self) -> Text:
        return "action_display_document"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        document = tracker.get_slot("documento")

        if document:
            dispatcher.utter_message(f"Tu numero de documento es {document}.")
        else:
            dispatcher.utter_message("Por favor, proporciona tu numero de documento.")

        return []


class ActionExtractBirthdate(Action):

    def name(self) -> Text:
        return "action_extract_birthdate"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        birthday_entity = next(tracker.get_latest_entity_values("fecha_nacimiento"), None)

        return [
            SlotSet("fecha_nacimiento", birthday_entity)
        ]


class ActionDisplayBirthday(Action):

    def name(self) -> Text:
        return "action_display_birthday"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        birthday = tracker.get_slot("fecha_nacimiento")

        if birthday:
            dispatcher.utter_message(f"Tu fecha de nacimiento es {birthday}.")
        else:
            dispatcher.utter_message("Por favor, proporciona tu fecha de nacimiento.")

        return []   

class ActionExtractEmail(Action):

    def name(self) -> Text:
        return "action_extract_email"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        email_entity = next(tracker.get_latest_entity_values("email"), None)

        return [
            SlotSet("email", email_entity)
        ]


class ActionDisplayEmail(Action):

    def name(self) -> Text:
        return "action_display_email"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        email = tracker.get_slot("email")

        if email:
            dispatcher.utter_message(f"Tu email es {email}.")
        else:
            dispatcher.utter_message("Por favor, proporciona tu email.")

        return []         


class ActionSessionStart(Action):
    def name(self) -> Text:
        return "action_session_start"

    async def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        dispatcher.utter_message("¡Hola! Soy un bot de ejemplo. ¿En qué puedo ayudarte hoy?")

        events = [SessionStarted()]

        events.append(ActionExecuted("action_listen"))

        events.append(UserUtteranceReverted())

        return events
