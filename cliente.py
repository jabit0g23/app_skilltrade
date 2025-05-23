# cliente.py (modificado)
import socket
import sys # Asegúrate de tener sys si lo usas para argumentos, sino no es necesario


HOST = 'localhost'

SERVICE_ID_EXPECTED_LEN = 5

def enviar_transaccion(target_port: int, service_id: str, payload_data: str):
    if len(service_id) != SERVICE_ID_EXPECTED_LEN:
        print(f"Error: El ID de servicio '{service_id}' debe tener {SERVICE_ID_EXPECTED_LEN} caracteres.")

    largo_payload_completo = len(service_id) + len(payload_data)
    largo_str = str(largo_payload_completo).zfill(5) # LENGTH_PREFIX_LEN es 5

    mensaje = largo_str + service_id + payload_data
    
    print(f"Preparando mensaje: '{mensaje}' para el puerto {target_port}")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            print(f"Conectando a {HOST}:{target_port}...")
            sock.connect((HOST, target_port))
            print(f"Enviando mensaje: '{mensaje}'")
            sock.sendall(mensaje.encode('utf-8'))
            print("Mensaje enviado. Esperando respuesta...")
            resp_largo_str_bytes = sock.recv(5) # LENGTH_PREFIX_LEN es 5
            if not resp_largo_str_bytes:
                print("No se recibió prefijo de longitud de respuesta o conexión cerrada.")
                return
            
            resp_largo_str = resp_largo_str_bytes.decode('utf-8')
            try:
                resp_largo_int = int(resp_largo_str)
            except ValueError:
                print(f"Respuesta con prefijo de longitud inválido: {resp_largo_str}")
                return

            # Leer cuerpo de la respuesta
            if resp_largo_int > 0:
                respuesta_body_bytes = sock.recv(resp_largo_int)
                if respuesta_body_bytes:
                    print(f"Respuesta recibida (cuerpo): '{respuesta_body_bytes.decode('utf-8')}' (Full: '{resp_largo_str}{respuesta_body_bytes.decode('utf-8')}')")
                else:
                    print("No se recibió cuerpo de respuesta completo.")
            elif resp_largo_int == 0:
                 print("Respuesta recibida con cuerpo vacío (longitud 0).")
            else:
                print(f"Respuesta con longitud negativa o inválida: {resp_largo_int}")


    except socket.error as e:
        print(f"Error de socket: {e}")
    except Exception as e:
        print(f"Ocurrió un error: {e}")

if __name__ == "__main__":
    # --- Para probar el servicio SUMAR (en puerto 5001) ---
    print("--- Probando servicio SUMAR ---")
    PORT_SUMAR = 5001
    id_servicio_sumar = "sumar" # 5 caracteres
    datos_sumar = "HOLAS1"      # 6 caracteres -> largo total 11 -> prefijo "00011"
    enviar_transaccion(PORT_SUMAR, id_servicio_sumar, datos_sumar)
    
    # --- Para probar el servicio RESTA (en puerto 5002) ---
    print("\n--- Probando servicio RESTA ---")
    PORT_RESTA = 5002
    id_servicio_resta = "resta" # 5 caracteres
    datos_resta = "HOLAS1"      # 6 caracteres -> largo total 11 -> prefijo "00011"
    enviar_transaccion(PORT_RESTA, id_servicio_resta, datos_resta)
