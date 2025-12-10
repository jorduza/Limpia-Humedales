import argparse
import time
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO


def parse_args():
    p = argparse.ArgumentParser(description="YOLOv8 sobre stream MJPEG de ESP32-CAM")
    p.add_argument("--url", required=True, help="URL del stream (p.ej. http://http://172.20.10.7:81/stream)")
    p.add_argument("--model", default="yolov8n.pt", help="Ruta o nombre del modelo YOLO")
    p.add_argument("--conf", type=float, default=0.35, help="Umbral de confianza")
    p.add_argument("--save", action="store_true", help="Guardar video con anotaciones (output.mp4)")
    p.add_argument("--show", action="store_true", help="Mostrar ventana con video")
    p.add_argument("--max-w", type=int, default=640, help="Redimensionar ancho máximo (0 = no escalar)")
    p.add_argument("--reconnect", type=int, default=3, help="Intentos de reconexión si el stream cae")
    return p.parse_args()


def open_capture(url: str):
    cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    return cap


def main():
    args = parse_args()

    print("[INFO] Cargando modelo...")
    model = YOLO(args.model)

    print("[INFO] Conectando a la cámara...")
    cap = open_capture(args.url)

    if not cap.isOpened():
        print(f"[ERROR] No se puede abrir el stream: {args.url}")
        return

    writer = None
    prev_time = time.time()
    fps = 0.0
    reconnects_left = args.reconnect

    while True:
        ok, frame = cap.read()

        if not ok or frame is None:
            print("[WARN] Frame nulo. Intentando reconectar...")
            cap.release()
            time.sleep(0.7)

            cap = open_capture(args.url)
            if not cap.isOpened():
                reconnects_left -= 1
                print(f"[WARN] Reconexiones restantes: {reconnects_left}")
                if reconnects_left < 0:
                    print("[ERROR] No hay stream, saliendo.")
                    break
                continue

            reconnects_left = args.reconnect
            continue

        
        if args.max_w > 0 and frame.shape[1] > args.max_w:
            h = int(frame.shape[0] * (args.max_w / frame.shape[1]))
            frame = cv2.resize(frame, (args.max_w, h), interpolation=cv2.INTER_AREA)

        results = model.predict(source=frame, conf=args.conf, verbose=False)
        annotated = frame.copy()


        for r in results:
            if not hasattr(r, "boxes") or r.boxes is None:
                continue

            for box in r.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int).tolist()

                label = f"{model.names.get(cls_id, cls_id)} {conf:.2f}"

                cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
                (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                cv2.rectangle(annotated, (x1, y1 - th - 6), (x1 + tw + 4, y1), (0, 255, 0), -1)
                cv2.putText(annotated, label, (x1 + 2, y1 - 4),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

        now = time.time()
        fps = fps * 0.9 + (1.0 / max(1e-6, now - prev_time)) * 0.1
        prev_time = now
        cv2.putText(annotated, f"FPS: {fps:.1f}", (8, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        if args.save:
            if writer is None:
                h, w = annotated.shape[:2]
                writer = cv2.VideoWriter(
                    "output.mp4",
                    cv2.VideoWriter_fourcc(*"mp4v"),
                    20.0,
                    (w, h)
                )
            writer.write(annotated)
        if args.show:
            cv2.imshow("Camara wetlandcare", annotated)
            cv2.resizeWindow("Camara wetlandcare", 480, 320)
            key = cv2.waitKey(1) & 0xFF
            if key in (27, ord("q")):  
                break

    if writer is not None:
        writer.release()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()