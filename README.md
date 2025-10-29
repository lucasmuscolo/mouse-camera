# 🖱️ Mouse Virtual por Gestos (v7.0)

Este es un script de Python que te permite controlar el cursor de tu computadora usando gestos de la mano a través de tu cámara web. Utiliza **OpenCV** para la captura de video y **MediaPipe** para el reconocimiento de la mano en tiempo real.

El proyecto está diseñado para ser robusto y altamente configurable, permitiendo una interacción fluida con tu PC sin necesidad de un mouse físico.


*(Recomendación: ¡Graba un GIF corto de la app funcionando y ponelo acá!)*

---

## 🚀 Características Principales

* **Activación por Gesto:** El control no está siempre activo. Debes mostrar la palma de tu mano ✋ durante 5 segundos para "invocar" el mouse.
* **Desactivación por Timeout:** Si la mano desaparece de la cámara por 10 segundos, el control se desactiva automáticamente.
* **Dos Modos de Control:**
    1.  **Modo Palma (Absoluto):** El cursor sigue el centro de tu palma. Ideal para navegar.
    2.  **Modo Pick (Relativo):** "Agarras" el cursor juntando 3 dedos y lo mueves como un mouse físico.
* **Atajo de Teclado:** Cambia entre "Modo Palma" y "Modo Pick" en cualquier momento presionando **`Shift + A`**.
* **Gestos de Clic Avanzados:**
    * Soporte para **Clic Corto**, **Arrastre (Drag)** y **Doble Clic**.
    * Lógica de timer para diferenciar un clic de un arrastre.
* **Panel de Configuración:** Todas las variables (tiempos, sensibilidad, suavizado) están centralizadas al inicio del script para un "tuneo" fácil.

---

## 🛠️ Tecnologías Utilizadas

* **Python 3.11+**
* **OpenCV (`opencv-python`):** Para la captura de video y la interfaz visual.
* **MediaPipe (`mediapipe`):** Para la detección de landmarks de la mano.
* **PyAutoGUI (`pyautogui`):** Para controlar el cursor y los clics.
* **Keyboard (`keyboard`):** Para detectar el atajo de teclado global.

---

## 📦 Instalación

1.  Asegúrate de tener Python 3.11 instalado.
2.  Instala las dependencias usando `pip`:

    ```bash
    pip install opencv-python mediapipe pyautogui keyboard
    ```
    *Nota: Si tenés problemas de certificados SSL (como nos pasó), usá este comando:*
    ```bash
    pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org opencv-python mediapipe pyautogui keyboard
    ```
3.  (Opcional: Solo si `keyboard` falla) En Windows, quizás necesites ejecutar el script como Administrador para que el atajo `Shift+A` funcione.

---

## ⌨️ ¿Cómo Usarlo?

1.  Ejecuta el script desde tu terminal:
    ```bash
    python mouse_virtual_v7.py
    ```

2.  **Activación:** El programa iniciará en modo **Inactivo**. Muestra tu mano abierta (palma ✋) a la cámara. Un contador de 5 segundos aparecerá. Mantenla quieta hasta que se active.

3.  **¡Controla el Mouse!** El programa iniciará en **Modo Palma** (puedes cambiar esto en la configuración).

### Modo 2: "Modo Palma" (Default)

* **Movimiento:** (Absoluto) El cursor saltará a la posición de la palma de tu mano 🟣.
* **Clic Izquierdo:** Junta el **Pulgar (4)** y el **Índice (8)** 🔵.
* **Clic Derecho:** Junta el **Pulgar (4)** y el **Dedo Medio (12)** 🟡.
* **Arrastrar (Drag):** Mantén el gesto de clic por más de 0.5 segundos (configurable).
* **Doble Clic:** Haz el gesto de clic (pellizco corto) dos veces rápido.

### Modo 1: "Modo Pick"

* *Presiona `Shift + A` para cambiar a este modo.*
* **Movimiento:** (Relativo) Junta los 3 dedos: **Pulgar (4) + Índice (8) + Medio (12)** 🟢. El mouse ahora está "agarrado" y se moverá *relativamente* a cómo muevas la mano.
* **Clic Izquierdo:** Mientras "agarras", levanta el **Índice (8)** 🔵.
* **Clic Derecho:** Mientras "agarras", levanta el **Dedo Medio (12)** 🟡.

### Desactivación

* **Automática:** Simplemente saca la mano del cuadro. Después de 10 segundos, el control se desactivará.
* **Manual:** Presiona **`q`** en la ventana de OpenCV para cerrar el programa.

---

## 🔧 Configuración y Ajustes

Para cambiar la sensibilidad, los tiempos o los umbrales, no toques el código principal. Simplemente abre el archivo `.py` y edita los valores en el bloque `### --- PANEL DE CONFIGURACION (v7.0) --- ###` que se encuentra al inicio de todo.
