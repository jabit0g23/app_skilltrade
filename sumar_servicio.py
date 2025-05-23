import socket
import time

# --- Configuración ---
MY_SERVICE_NAME = "sumar"  # Nombre de este servicio (5 caracteres)
SERVICE_ID_LEN = 5         # Longitud del ID de servicio (ej: "resta", "sinit")
LENGTH_PREFIX_LEN = 5    # Longitud del prefijo de longitud (ej: "00010")

HOST = 'localhost'
BUS_PORT = 5000          # Puerto del Bus central para anuncios
MY_LISTEN_PORT = 5001    # Puerto donde ESTE servicio "resta" escuchará

# --- Función auxiliar para recibir datos (sin cambios) ---
def recv_all(sock, n):
    data = bytearray()
    while len(data) < n:
        try:
            packet = sock.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        except socket.error:
            return None
        except Exception:
            return None
    return bytes(data)

# --- Parte 1: Anuncio del servicio (anuncia al BUS_PORT) ---
def announce_service_to_bus(bus_host, bus_port_to_announce, service_to_register):
    init_command = "sinit"
    # En una implementación más avanzada, aquí podrías incluir MY_LISTEN_PORT en el mensaje de anuncio
    # ej: payload_data = f"{service_to_register}:{MY_LISTEN_PORT}"
    # Pero por ahora, mantenemos el anuncio simple como antes.
    payload_data = service_to_register
    service_id_for_init_msg = init_command

    payload_total_len = len(service_id_for_init_msg) + len(payload_data)
    largo_str = str(payload_total_len).zfill(LENGTH_PREFIX_LEN)
    mensaje = largo_str + service_id_for_init_msg + payload_data
    
    print(f"Anunciando servicio '{service_to_register}' al bus en {bus_host}:{bus_port_to_announce} con mensaje: '{mensaje}'")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((bus_host, bus_port_to_announce))
            s.sendall(mensaje.encode('utf-8'))
            print(f"Anuncio para '{service_to_register}' enviado.")
            # El bus actual podría responder "00012sinitOKresta"
            # respuesta_bus = recv_all(s, LENGTH_PREFIX_LEN + 12) # Leer la respuesta del bus si se desea
            # if respuesta_bus:
            # print(f"Respuesta del bus al anuncio: {respuesta_bus.decode('utf-8')}")
            return True
    except Exception as e:
        print(f"Fallo el anuncio del servicio '{service_to_register}': {e}")
        return False

# --- Parte 2: Manejo de solicitudes con conexión persistente ---
def handle_client_connection(conn, addr):
    print(f"Cliente conectado a '{MY_SERVICE_NAME}': {addr} - Iniciando sesión persistente.")
    try:
        while True:
            largo_str_bytes = recv_all(conn, LENGTH_PREFIX_LEN)
            if not largo_str_bytes:
                print(f"Cliente {addr} desconectado (leyendo longitud). Terminando sesión para '{MY_SERVICE_NAME}'.")
                break
            
            try:
                largo_str = largo_str_bytes.decode('utf-8')
                largo_int = int(largo_str)
                if largo_int <= 0:
                    print(f"Longitud inválida ({largo_int}) de {addr}. Sesión para '{MY_SERVICE_NAME}' terminada.")
                    break
            except (UnicodeDecodeError, ValueError) as e:
                print(f"Error en prefijo de longitud de {addr}: {e}. Sesión para '{MY_SERVICE_NAME}' terminada.")
                break

            message_body_bytes = recv_all(conn, largo_int)
            if not message_body_bytes:
                print(f"Cliente {addr} desconectado (leyendo cuerpo). Terminando sesión para '{MY_SERVICE_NAME}'.")
                break
            
            try:
                message_body = message_body_bytes.decode('utf-8')
            except UnicodeDecodeError as e:
                print(f"Error decodificando cuerpo de {addr}: {e}. Sesión para '{MY_SERVICE_NAME}' terminada.")
                break
            
            if len(message_body) < SERVICE_ID_LEN:
                print(f"Cuerpo de mensaje muy corto de {addr}. Sesión para '{MY_SERVICE_NAME}' terminada.")
                break

            req_service_id = message_body[:SERVICE_ID_LEN]
            req_payload_data = message_body[SERVICE_ID_LEN:]
            print(f"Recibido para '{MY_SERVICE_NAME}' de {addr}: ID='{req_service_id}', Datos='{req_payload_data}'")

            if req_service_id == MY_SERVICE_NAME:
                response_message_str = ""
                # Si el mensaje es "restaHOLAS1", largo_str sería "00011" (5 de resta + 6 de HOLAS1)
                if largo_str == "00011" and req_service_id == "sumar" and req_payload_data == "HOLAS1":
                    response_message_str = "00012sumarPRUEBA1SUMAR" # Respuesta específica para resta
                    print(f"Enviando respuesta específica de '{MY_SERVICE_NAME}' a {addr}: '{response_message_str}'")
                else:
                    # Lógica de resta (ejemplo: "10-3")
                    if "-" in req_payload_data and len(req_payload_data.split('-')) == 2 :
                        try:
                            parts = req_payload_data.split('-')
                            num1 = int(parts[0].strip())
                            num2 = int(parts[1].strip())
                            result = num1 - num2
                            resp_datos = str(result)
                            print(f"Servicio '{MY_SERVICE_NAME}': {num1} - {num2} = {result}")
                        except ValueError:
                            resp_datos = "Error: operandos invalidos para resta"
                    else: # Respuesta genérica ACK
                        resp_datos = f"ACK-{MY_SERVICE_NAME}-{req_payload_data}"
                    
                    resp_largo_val = len(MY_SERVICE_NAME) + len(resp_datos)
                    resp_largo_str = str(resp_largo_val).zfill(LENGTH_PREFIX_LEN)
                    response_message_str = resp_largo_str + MY_SERVICE_NAME + resp_datos
                    print(f"Enviando respuesta de '{MY_SERVICE_NAME}' a {addr}: '{response_message_str}'")
                
                try:
                    conn.sendall(response_message_str.encode('utf-8'))
                except socket.error as e:
                    print(f"Error al enviar respuesta desde '{MY_SERVICE_NAME}' a {addr}: {e}. Cerrando sesión.")
                    break
            else:
                print(f"Servicio '{req_service_id}' no es '{MY_SERVICE_NAME}'. Ignorando.")

    except Exception as e:
        print(f"Error inesperado en sesión con {addr} para '{MY_SERVICE_NAME}': {e}")
    finally:
        print(f"Cerrando conexión final con {addr} para '{MY_SERVICE_NAME}'.")
        conn.close()

# --- Parte 3: Iniciar el servidor RESTA ---
def start_resta_server(host, listen_port): # Cambiado nombre de función
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((host, listen_port))
        server_socket.listen(1)
        print(f"Servicio '{MY_SERVICE_NAME}' escuchando en {host}:{listen_port}...")

        while True:
            try:
                conn, addr = server_socket.accept()
                handle_client_connection(conn, addr) 
            except KeyboardInterrupt:
                print(f"Cerrando servidor '{MY_SERVICE_NAME}' por interrupción.")
                break
            except Exception as e:
                print(f"Error en bucle de aceptación de '{MY_SERVICE_NAME}': {e}")
                time.sleep(0.1) 

    except Exception as e:
        print(f"No se pudo iniciar el servidor '{MY_SERVICE_NAME}' en {host}:{listen_port}. Error: {e}")
    finally:
        print(f"Cerrando socket principal del servidor '{MY_SERVICE_NAME}'.")
        server_socket.close()

# --- Ejecución Principal ---
if __name__ == "__main__":
    print(f"Iniciando servicio '{MY_SERVICE_NAME}' (escuchará en el puerto {MY_LISTEN_PORT})...")
    
    # Intenta anunciar el servicio al BUS_PORT (ej: 5000)
    announce_service_to_bus(HOST, BUS_PORT, MY_SERVICE_NAME)
    
    print(f"El servicio '{MY_SERVICE_NAME}' intentará escuchar en {HOST}:{MY_LISTEN_PORT}.")
    print(f"Asegúrese de que el puerto {BUS_PORT} (del bus) y {MY_LISTEN_PORT} (de este servicio) no causen conflictos no deseados.")

    # Inicia el servidor para escuchar solicitudes EN SU PROPIO PUERTO (MY_LISTEN_PORT)
    start_resta_server(HOST, MY_LISTEN_PORT) # Usa MY_LISTEN_PORT y función renombrada

    print(f"Servicio '{MY_SERVICE_NAME}' terminado.")