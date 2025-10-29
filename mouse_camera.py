import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import math
import time
import keyboard

# --- ¡¡NUEVO: Variables de Estado de Tracking!! ---
tracking_activo = False
estado_texto = "Inactivo"
segundos_para_activar = 5.0
segundos_para_desactivar = 10.0
tiempo_mano_abierta_inicio = 0
tiempo_sin_mano_inicio = 0
# ---

# --- Variables Globales de Modo ---
modo_actual = 2 # Inicia en Modo Palma
button_rect = [10, 10, 240, 50] 
window_name = 'Mouse Virtual - v6.5 (Activacion)'
hotkey_presionado = False 

def cambiar_modo():
    global modo_actual
    if modo_actual == 1:
        modo_actual = 2
        print("Cambiado a MODO 2 (Palma)")
    else:
        modo_actual = 1
        print("Cambiado a MODO 1 (Pick)")

def gestionar_clic(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        if (button_rect[0] < x < button_rect[2] and 
            button_rect[1] < y < button_rect[3]):
            cambiar_modo() 

# --- ¡¡NUEVO: Función para detectar Mano Abierta!! ---
def es_mano_abierta(mano_landmarks, mp_manos):
    try:
        # Comparamos la punta de los 4 dedos con su nudillo (MCP)
        # Si la punta 'y' es menor (más arriba), el dedo está extendido.
        idx_extendido = mano_landmarks.landmark[mp_manos.HandLandmark.INDEX_FINGER_TIP].y < mano_landmarks.landmark[mp_manos.HandLandmark.INDEX_FINGER_MCP].y
        mid_extendido = mano_landmarks.landmark[mp_manos.HandLandmark.MIDDLE_FINGER_TIP].y < mano_landmarks.landmark[mp_manos.HandLandmark.MIDDLE_FINGER_MCP].y
        ring_extendido = mano_landmarks.landmark[mp_manos.HandLandmark.RING_FINGER_TIP].y < mano_landmarks.landmark[mp_manos.HandLandmark.RING_FINGER_MCP].y
        pinky_extendido = mano_landmarks.landmark[mp_manos.HandLandmark.PINKY_TIP].y < mano_landmarks.landmark[mp_manos.HandLandmark.PINKY_MCP].y
        
        # El pulgar es más complejo, lo simplificamos:
        # Comprobamos que esté "abierto" (lejos) del nudillo del índice
        thumb_abierto = abs(mano_landmarks.landmark[mp_manos.HandLandmark.THUMB_TIP].x - mano_landmarks.landmark[mp_manos.HandLandmark.INDEX_FINGER_MCP].x) > 0.05
        
        return idx_extendido and mid_extendido and ring_extendido and pinky_extendido and thumb_abierto
    except Exception as e:
        print(f"Error al chequear mano abierta: {e}")
        return False
# ---

# --- Configuración Inicial ---
mp_manos = mp.solutions.hands
manos = mp_manos.Hands(
    static_image_mode=False, max_num_hands=1,
    min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_dibujo = mp.solutions.drawing_utils

ancho_pantalla, alto_pantalla = pyautogui.size()
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error fatal: No se puede abrir la cámara.")
    exit()

cv2.namedWindow(window_name) 
cv2.setMouseCallback(window_name, gestionar_clic) 

# --- Variables de Estado (Modo 1: Pick) ---
modo_arrastre = False
x_mano_anterior, y_mano_anterior = 0, 0
factor_suavizado = 3  
umbral_movimiento = 1.5 

# --- Variables de Timer (Modo 2: Palma) ---
tiempo_clic_izq = 0     
tiempo_clic_der = 0
drag_izq_activo = False 
drag_der_activo = False
tiempo_para_drag = 0.5
tiempo_ventana_dobleclic = 0.5 
ultimo_clic_izq = 0
ultimo_clic_der = 0

clic_izq_hecho = False
clic_der_hecho = False 

# --- Umbrales de Gestos ---
umbral_corto = 40
umbral_largo = 65

print(f"Iniciando (v6.5)... MODO INACTIVO. Muestra la mano abierta ✋ por {segundos_para_activar}s para activar.")

# --- Bucle Principal ---
while True:
    try:
        # Lógica de Hotkey
        if keyboard.is_pressed('shift+a'):
            if not hotkey_presionado:
                cambiar_modo()
                hotkey_presionado = True
        else:
            hotkey_presionado = False
            
        exito, frame = cap.read()
        if not exito or frame is None:
            print("Advertencia: Frame malo. Reintentando...")
            continue

        frame = cv2.flip(frame, 1)
        alto_frame, ancho_frame, _ = frame.shape
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        resultados = manos.process(frame_rgb)

        # --- ¡¡NUEVA LÓGICA DE ESTADO PRINCIPAL!! ---
        if tracking_activo:
            # --- ESTADO ACTIVO ---
            # Mostramos el botón de modo
            color_boton = (255, 100, 0) # Azul
            texto_modo = f"Modo {modo_actual}: {'Pick' if modo_actual == 1 else 'Palma'}"
            cv2.rectangle(frame, (button_rect[0], button_rect[1]), (button_rect[2], button_rect[3]), color_boton, -1)
            cv2.putText(frame, texto_modo, (button_rect[0] + 10, button_rect[1] + 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            estado_texto = f"Activo (Modo {modo_actual})"
            
            if resultados.multi_hand_landmarks:
                # --- MANO DETECTADA (en modo activo) ---
                tiempo_sin_mano_inicio = 0 # Resetea el timer de desactivación
                
                mano_landmarks = resultados.multi_hand_landmarks[0]
                
                # ... (Aquí va TODA la lógica de v6.4, sin cambios) ...
                
                # Copia y pega de v6.4
                indice_punta = mano_landmarks.landmark[mp_manos.HandLandmark.INDEX_FINGER_TIP] # 8
                pulgar_punta = mano_landmarks.landmark[mp_manos.HandLandmark.THUMB_TIP]      # 4
                medio_punta = mano_landmarks.landmark[mp_manos.HandLandmark.MIDDLE_FINGER_TIP] # 12
                palma_centro = mano_landmarks.landmark[mp_manos.HandLandmark.MIDDLE_FINGER_MCP] # 9
                
                x_idx_frame = int(indice_punta.x * ancho_frame)
                y_idx_frame = int(indice_punta.y * alto_frame)
                x_pulgar_frame = int(pulgar_punta.x * ancho_frame)
                y_pulgar_frame = int(pulgar_punta.y * alto_frame)
                x_medio_frame = int(medio_punta.x * ancho_frame)
                y_medio_frame = int(medio_punta.y * alto_frame)
                x_palma_frame = int(palma_centro.x * ancho_frame)
                y_palma_frame = int(palma_centro.y * alto_frame)

                dist_pulgar_indice = math.hypot(x_idx_frame - x_pulgar_frame, y_idx_frame - y_pulgar_frame)
                dist_pulgar_medio = math.hypot(x_medio_frame - x_pulgar_frame, y_medio_frame - y_pulgar_frame)
                color_gesto = (0, 0, 255) # Rojo (default)

                if modo_actual == 1:
                    # --- MODO 1: PICK ---
                    x_pantalla = np.interp(indice_punta.x, [0.1, 0.9], [0, ancho_pantalla])
                    y_pantalla = np.interp(indice_punta.y, [0.1, 0.9], [0, alto_pantalla])
                    if (dist_pulgar_indice < umbral_corto and dist_pulgar_medio < umbral_corto):
                        color_gesto = (0, 255, 0)
                        if not modo_arrastre:
                            modo_arrastre = True
                            x_mano_anterior, y_mano_anterior = x_pantalla, y_pantalla
                        else:
                            x_suavizado = x_mano_anterior + (x_pantalla - x_mano_anterior) / factor_suavizado
                            y_suavizado = y_mano_anterior + (y_pantalla - y_mano_anterior) / factor_suavizado
                            delta_x = x_suavizado - x_mano_anterior
                            delta_y = y_suavizado - y_mano_anterior
                            if abs(delta_x) > umbral_movimiento or abs(delta_y) > umbral_movimiento:
                                pyautogui.move(delta_x, delta_y)
                                x_mano_anterior, y_mano_anterior = x_suavizado, y_suavizado
                        clic_izq_hecho = False; clic_der_hecho = False; drag_izq_activo = False; drag_der_activo = False; tiempo_clic_izq = 0; tiempo_clic_der = 0
                    elif (dist_pulgar_indice > umbral_largo and dist_pulgar_medio < umbral_corto):
                        color_gesto = (255, 0, 0)
                        modo_arrastre = False
                        if not clic_izq_hecho:
                            pyautogui.click(button='left'); print("¡CLIC IZQUIERDO (Modo 1)!"); clic_izq_hecho = True
                        clic_der_hecho = False
                    elif (dist_pulgar_indice < umbral_corto and dist_pulgar_medio > umbral_largo):
                        color_gesto = (255, 255, 0)
                        modo_arrastre = False
                        if not clic_der_hecho:
                            pyautogui.click(button='right'); print("¡CLIC DERECHO (Modo 1)!"); clic_der_hecho = True
                        clic_izq_hecho = False
                    else:
                        color_gesto = (0, 0, 255); modo_arrastre = False; clic_izq_hecho = False; clic_der_hecho = False
                
                elif modo_actual == 2:
                    # --- MODO 2: PALMA ---
                    x_pantalla = np.interp(palma_centro.x, [0.1, 0.9], [0, ancho_pantalla])
                    y_pantalla = np.interp(palma_centro.y, [0.1, 0.9], [0, alto_pantalla])
                    pyautogui.moveTo(x_pantalla, y_pantalla)
                    
                    if (dist_pulgar_medio < umbral_corto):
                        color_gesto = (255, 255, 0) # Cian
                        if tiempo_clic_der == 0: tiempo_clic_der = time.time()
                        tiempo_transcurrido = time.time() - tiempo_clic_der
                        if tiempo_transcurrido > tiempo_para_drag and not drag_der_activo:
                            pyautogui.mouseDown(button='right'); print("INICIO DRAG DERECHO"); drag_der_activo = True
                    elif (dist_pulgar_indice < umbral_corto):
                        color_gesto = (255, 0, 0) # Azul
                        if tiempo_clic_izq == 0: tiempo_clic_izq = time.time()
                        tiempo_transcurrido = time.time() - tiempo_clic_izq
                        if tiempo_transcurrido > tiempo_para_drag and not drag_izq_activo:
                            pyautogui.mouseDown(button='left'); print("INICIO DRAG IZQUIERDO"); drag_izq_activo = True
                    else:
                        color_gesto = (0, 255, 0) # Verde
                        ahora = time.time()
                        if tiempo_clic_izq > 0:
                            if not drag_izq_activo:
                                if (ahora - ultimo_clic_izq) < tiempo_ventana_dobleclic:
                                    pyautogui.doubleClick(button='left'); print("¡¡DOBLE CLIC IZQUIERDO!!"); ultimo_clic_izq = 0
                                else:
                                    pyautogui.click(button='left'); print("CLIC IZQUIERDO (Corto)"); ultimo_clic_izq = ahora
                            else:
                                pyautogui.mouseUp(button='left'); print("FIN DRAG IZQUIERDO"); ultimo_clic_izq = 0
                        if tiempo_clic_der > 0:
                            if not drag_der_activo:
                                if (ahora - ultimo_clic_der) < tiempo_ventana_dobleclic:
                                    pyautogui.doubleClick(button='right'); print("¡¡DOBLE CLIC DERECHO!!"); ultimo_clic_der = 0
                                else:
                                    pyautogui.click(button='right'); print("CLIC DERECHO (Corto)"); ultimo_clic_der = ahora
                            else:
                                pyautogui.mouseUp(button='right'); print("FIN DRAG DERECHO"); ultimo_clic_der = 0
                        tiempo_clic_izq = 0; drag_izq_activo = False
                        tiempo_clic_der = 0; drag_der_activo = False

                # --- Fin de la lógica v6.4 ---
                
                # Feedback visual (común a ambos modos)
                cv2.circle(frame, (x_idx_frame, y_idx_frame), 10, color_gesto, cv2.FILLED)
                cv2.circle(frame, (x_pulgar_frame, y_pulgar_frame), 10, color_gesto, cv2.FILLED)
                cv2.circle(frame, (x_medio_frame, y_medio_frame), 10, color_gesto, cv2.FILLED)
                cv2.circle(frame, (x_palma_frame, y_palma_frame), 15, (255, 0, 255), cv2.FILLED) # Fucsia
                mp_dibujo.draw_landmarks(frame, mano_landmarks, mp_manos.HAND_CONNECTIONS)
            
            else:
                # --- NO HAY MANO (en modo activo) ---
                # Inicia el timer de desactivación
                if tiempo_sin_mano_inicio == 0:
                    print("Mano perdida... iniciando timer de desactivacion.")
                    tiempo_sin_mano_inicio = time.time()
                
                duracion_sin_mano = time.time() - tiempo_sin_mano_inicio
                estado_texto = f"Sin mano... Apagando en {int(segundos_para_desactivar - duracion_sin_mano)}s"
                
                if duracion_sin_mano > segundos_para_desactivar:
                    tracking_activo = False
                    tiempo_sin_mano_inicio = 0
                    print(f"¡TRACKING DESACTIVADO! (Timeout de {segundos_para_desactivar}s)")
                
                # Soltamos los drags por si acaso
                if drag_izq_activo: pyautogui.mouseUp(button='left'); print("FIN DRAG (mano perdida)")
                if drag_der_activo: pyautogui.mouseUp(button='right'); print("FIN DRAG (mano perdida)")
                modo_arrastre = False; drag_izq_activo = False; drag_der_activo = False
                tiempo_clic_izq = 0; tiempo_clic_der = 0

        else:
            # --- ESTADO INACTIVO ---
            # Buscando el gesto de activación
            if resultados.multi_hand_landmarks:
                mano_landmarks = resultados.multi_hand_landmarks[0]
                if es_mano_abierta(mano_landmarks, mp_manos):
                    # --- MANO ABIERTA DETECTADA ---
                    if tiempo_mano_abierta_inicio == 0:
                        tiempo_mano_abierta_inicio = time.time()
                    
                    duracion_mano_abierta = time.time() - tiempo_mano_abierta_inicio
                    estado_texto = f"Mano Abierta OK. Activando en {int(segundos_para_activar - duracion_mano_abierta)}s"
                    
                    if duracion_mano_abierta > segundos_para_activar:
                        tracking_activo = True
                        tiempo_mano_abierta_inicio = 0
                        print(f"¡TRACKING ACTIVADO! (Gesto de {segundos_para_activar}s)")
                else:
                    # La mano está, pero no es el gesto
                    tiempo_mano_abierta_inicio = 0
                    estado_texto = "Inactivo (Muestra ✋ para activar)"
                
                # Dibujamos la mano para feedback
                mp_dibujo.draw_landmarks(frame, mano_landmarks, mp_manos.HAND_CONNECTIONS)
            else:
                # No hay mano, resetea el timer de activación
                tiempo_mano_abierta_inicio = 0
                estado_texto = "Inactivo (Muestra ✋ para activar)"
        
        # --- Mostrar Estado (siempre) ---
        if not tracking_activo:
            cv2.putText(frame, estado_texto, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        cv2.imshow(window_name, frame) 

        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

    except Exception as e:
        print(f"Error atrapado: {e}. Saltando fotograma.")
        continue

# --- Limpieza ---
print("Cerrando programa...")
cap.release()
cv2.destroyAllWindows()