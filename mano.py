import cv2
import mediapipe as mp
import serial
import time
import os

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

arduino = serial.Serial("COM14", 9600, timeout=1)

time.sleep(2)

COLOR_PRIMARIO = (255, 0, 0)
COLOR_SECUNDARIO = (255, 255, 255)

COLOR_ABIERTO = (0, 255, 0)
COLOR_CERRADO = (0, 0, 255)

COLOR_TEXTO = (255, 255, 255)
COLOR_PANEL = (180, 40, 0)

GROSOR_LINEA = 3
RADIO_PUNTO = 8

estado_anterior = {
    "pulgar": None,
    "indice": None,
    "medio": None,
    "anular": None,
    "menique": None
}

def cargar_logo(ruta, ancho, alto):

    logo = cv2.imread(
        ruta,
        cv2.IMREAD_UNCHANGED
    )

    if logo is None:
        return None

    logo = cv2.resize(
        logo,
        (ancho, alto),
        interpolation=cv2.INTER_AREA
    )

    return logo

def colocar_logo(imagen, logo, x, y):

    if logo is None:
        return imagen

    h, w = logo.shape[:2]

    if logo.shape[2] == 4:

        logo_rgb = logo[:, :, :3]

        alpha = logo[:, :, 3] / 255.0

        roi = imagen[
            y:y+h,
            x:x+w
        ]

        for c in range(3):

            roi[:, :, c] = (
                alpha * logo_rgb[:, :, c]
                +
                (1 - alpha) * roi[:, :, c]
            )

        imagen[
            y:y+h,
            x:x+w
        ] = roi

    else:

        imagen[
            y:y+h,
            x:x+w
        ] = logo

    return imagen

def enviar_comando(
    dedo,
    estado,
    comando
):

    if estado_anterior[dedo] != estado:

        arduino.write(
            comando.encode()
        )

        estado_anterior[dedo] = estado

def dedo_arriba(
    landmarks,
    punta,
    pip
):

    return landmarks[punta].y < landmarks[pip].y

def dibujar_logo_dedo(
    imagen,
    x,
    y,
    nombre,
    estado
):

    if estado == "ABIERTO":

        color = COLOR_ABIERTO

    elif estado == "CERRADO":

        color = COLOR_CERRADO

    else:

        color = (180, 180, 180)

    cv2.circle(
        imagen,
        (x, y),
        18,
        (255, 255, 255),
        2
    )

    cv2.circle(
        imagen,
        (x, y),
        11,
        color,
        -1
    )

    cv2.putText(
        imagen,
        nombre,
        (x + 35, y - 5),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        COLOR_TEXTO,
        2
    )

    cv2.putText(
        imagen,
        estado,
        (x + 35, y + 18),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.50,
        color,
        2
    )

def texto_centrado(
    imagen,
    texto,
    y,
    escala,
    grosor,
    color,
    centro_x
):

    (ancho_texto, alto_texto), _ = cv2.getTextSize(
        texto,
        cv2.FONT_HERSHEY_SIMPLEX,
        escala,
        grosor
    )

    x = centro_x - (ancho_texto // 2)

    cv2.putText(
        imagen,
        texto,
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        escala,
        color,
        grosor,
        cv2.LINE_AA
    )

def main():

    base_path = os.path.dirname(
        os.path.abspath(__file__)
    )

    logo1 = cargar_logo(
        os.path.join(
            base_path,
            "logored.jpg"
        ),
        70,
        70
    )

    logo2 = cargar_logo(
        os.path.join(
            base_path,
            "escudo-isi.jpg"
        ),
        70,
        70
    )

    cv2.namedWindow(
        "Control de Mano Robotica",
        cv2.WINDOW_NORMAL
    )

    while cap.isOpened():

        ret, frame = cap.read()

        if not ret:
            break

        frame = cv2.flip(
            frame,
            1
        )

        alto, ancho = frame.shape[:2]

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        result = hands.process(
            rgb
        )

        output = frame.copy()

        estados = {
            "pulgar": "SIN DETECTAR",
            "indice": "SIN DETECTAR",
            "medio": "SIN DETECTAR",
            "anular": "SIN DETECTAR",
            "menique": "SIN DETECTAR"
        }

        if result.multi_hand_landmarks:

            hand_landmarks = (
                result.multi_hand_landmarks[0]
            )

            mp_drawing.draw_landmarks(
                output,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,

                mp_drawing.DrawingSpec(
                    color=COLOR_PRIMARIO,
                    thickness=GROSOR_LINEA,
                    circle_radius=RADIO_PUNTO
                ),

                mp_drawing.DrawingSpec(
                    color=COLOR_SECUNDARIO,
                    thickness=GROSOR_LINEA
                )
            )

            landmarks = (
                hand_landmarks.landmark
            )

            if landmarks[4].x > landmarks[3].x:

                enviar_comando(
                    "pulgar",
                    "abierto",
                    "E"
                )

                estados["pulgar"] = "ABIERTO"

            else:

                enviar_comando(
                    "pulgar",
                    "cerrado",
                    "5"
                )

                estados["pulgar"] = "CERRADO"

            indice_abierto = dedo_arriba(
                landmarks,
                8,
                6
            )

            if indice_abierto:

                enviar_comando(
                    "indice",
                    "abierto",
                    "1"
                )

                estados["indice"] = "ABIERTO"

            else:

                enviar_comando(
                    "indice",
                    "cerrado",
                    "A"
                )

                estados["indice"] = "CERRADO"

            medio_abierto = dedo_arriba(
                landmarks,
                12,
                10
            )

            if medio_abierto:

                enviar_comando(
                    "medio",
                    "abierto",
                    "2"
                )

                estados["medio"] = "ABIERTO"

            else:

                enviar_comando(
                    "medio",
                    "cerrado",
                    "B"
                )

                estados["medio"] = "CERRADO"

            anular_abierto = dedo_arriba(
                landmarks,
                16,
                14
            )

            if anular_abierto:

                enviar_comando(
                    "anular",
                    "abierto",
                    "C"
                )

                estados["anular"] = "ABIERTO"

            else:

                enviar_comando(
                    "anular",
                    "cerrado",
                    "3"
                )

                estados["anular"] = "CERRADO"

            menique_abierto = dedo_arriba(
                landmarks,
                20,
                18
            )

            if menique_abierto:

                enviar_comando(
                    "menique",
                    "abierto",
                    "D"
                )

                estados["menique"] = "ABIERTO"

            else:

                enviar_comando(
                    "menique",
                    "cerrado",
                    "4"
                )

                estados["menique"] = "CERRADO"

        cv2.rectangle(
            output,
            (0, 0),
            (390, alto),
            COLOR_PANEL,
            -1
        )

        colocar_logo(
            output,
            logo1,
            15,
            15
        )

        colocar_logo(
            output,
            logo2,
            305,
            15
        )

        texto_centrado(
            output,
            "CONTROL",
            38,
            0.60,
            2,
            COLOR_TEXTO,
            195
        )

        texto_centrado(
            output,
            "MANO ROBOTICA",
            63,
            0.50,
            2,
            COLOR_TEXTO,
            195
        )

        cv2.line(
            output,
            (20, 95),
            (370, 95),
            COLOR_TEXTO,
            2
        )

        dibujar_logo_dedo(
            output,
            35,
            145,
            "PULGAR",
            estados["pulgar"]
        )

        dibujar_logo_dedo(
            output,
            35,
            215,
            "INDICE",
            estados["indice"]
        )

        dibujar_logo_dedo(
            output,
            35,
            285,
            "MEDIO",
            estados["medio"]
        )

        dibujar_logo_dedo(
            output,
            35,
            355,
            "ANULAR",
            estados["anular"]
        )

        dibujar_logo_dedo(
            output,
            35,
            425,
            "MENIQUE",
            estados["menique"]
        )

        cv2.putText(
            output,
            "ESC = SALIR",
            (20, alto - 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            COLOR_TEXTO,
            1
        )

        cv2.imshow(
            "Control de Mano Robotica",
            output
        )

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()

    arduino.close()

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()