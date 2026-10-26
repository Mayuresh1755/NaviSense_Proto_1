
"""NaviSense laptop test. Press Q or Esc to exit."""

import time
import cv2
import config

from detector import NaviDetector
from speech import Speech


def main():
    cap = None
    speech = None

    try:
        # --------------------------------------------------
        # 1. Initialize webcam
        # --------------------------------------------------
        cap = cv2.VideoCapture(
            config.CAMERA_INDEX,
            cv2.CAP_DSHOW if hasattr(cv2, "CAP_DSHOW") else 0,
        )

        if not cap.isOpened():
            cap.release()
            cap = cv2.VideoCapture(config.CAMERA_INDEX)

        if not cap.isOpened():
            raise RuntimeError(
                "Could not open camera. Check Windows camera "
                "permissions or CAMERA_INDEX in config.py."
            )

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)

        # --------------------------------------------------
        # 2. Initialize detector and speech
        # --------------------------------------------------
        detector = NaviDetector("ultralytics")
        speech = Speech()

        print(
            "NaviSense started. Q/Esc exits. "
            "Distance estimates are approximate."
        )

        speech.say(
            "NaviSense started. Audio alerts enabled.",
            key="startup",
            interval=0,
        )

        # --------------------------------------------------
        # 3. Tracking and display state
        # --------------------------------------------------
        start = time.monotonic()
        frame_count = 0
        fps = 0.0
        last_debug = 0.0

        last_announced_object = None
        last_announced_distance = None
        last_announcement_time = 0.0

        # Announce again if distance changes by this amount.
        DISTANCE_CHANGE_THRESHOLD = 0.75

        # Minimum time between routine announcements.
        ANNOUNCEMENT_INTERVAL = 2.5

        # --------------------------------------------------
        # 4. Main detection loop
        # --------------------------------------------------
        while True:
            ok, frame = cap.read()

            if not ok or frame is None:
                print("[Camera] Frame unavailable; stopping.")
                break

            detections = detector.detect(frame)

            # Select detected objects within warning range.
            nearby = sorted(
                [
                    d for d in detections
                    if d.distance is not None
                    and 0 < d.distance <= config.WARNING_DISTANCE
                ],
                key=lambda d: d.distance,
            )

            now = time.monotonic()

            # --------------------------------------------------
            # 5. Debug output once per second
            # --------------------------------------------------
            if now - last_debug >= 1.0:
                if detections:
                    for d in detections:
                        distance_text = (
                            f"{d.distance:.2f} m"
                            if d.distance is not None
                            else "unknown"
                        )

                        print(
                            f"[DETECTION] {d.name} | "
                            f"confidence={d.confidence:.2f} | "
                            f"distance={distance_text} | "
                            f"direction={d.direction}"
                        )
                else:
                    print("[DETECTION] No objects detected.")

                if nearby:
                    closest = nearby[0]
                    print(
                        f"[ALERT] {closest.name} within "
                        f"{config.WARNING_DISTANCE} metres."
                    )
                else:
                    print("[ALERT] No object within warning range.")

                last_debug = now

            # --------------------------------------------------
            # 6. Speech announcements
            # --------------------------------------------------
            if nearby:
                d = nearby[0]
                current_distance = float(d.distance)

                # Track object name and direction as an alert identity.
                current_object = (d.name, d.direction)

                object_changed = (
                    current_object != last_announced_object
                )

                distance_changed = (
                    last_announced_distance is None
                    or abs(
                        current_distance - last_announced_distance
                    ) >= DISTANCE_CHANGE_THRESHOLD
                )

                elapsed = now - last_announcement_time

                # Announce a new nearest object immediately, or
                # announce a meaningful distance change after cooldown.
                should_announce = (
                    object_changed
                    or (
                        distance_changed
                        and elapsed >= ANNOUNCEMENT_INTERVAL
                    )
                )

                # Give newly critical detections priority.
                is_critical = (
                    getattr(d, "category", "") == "critical"
                )

                if is_critical and elapsed >= 0.5:
                    should_announce = True

                if should_announce:
                    message = (
                        f"{d.name}, approximately "
                        f"{current_distance:.1f} metres, "
                        f"{d.direction}"
                    )

                    speech.say(
                        message,
                        key=f"{d.name}:{d.direction}",
                        interval=0,
                    )

                    last_announced_object = current_object
                    last_announced_distance = current_distance
                    last_announcement_time = now

            else:
                # Allow the next detected object to be announced
                # as a new alert after the warning area clears.
                last_announced_object = None
                last_announced_distance = None

            # --------------------------------------------------
            # 7. Draw detection boxes and labels
            # --------------------------------------------------
            for d in detections:
                x1, y1, x2, y2 = map(int, d.bbox)

                level = (
                    d.category
                    if d.distance is not None
                    else "unknown"
                )

                color = {
                    "critical": (0, 0, 255),
                    "warning": (0, 220, 255),
                    "safe": (0, 200, 0),
                    "near": (0, 220, 255),
                    "medium": (0, 200, 0),
                    "far": (0, 200, 0),
                    "unknown": (180, 180, 180),
                }.get(level, (180, 180, 180))

                if d.distance is not None:
                    label = (
                        f"{d.name} {d.confidence:.2f} | "
                        f"{d.distance:.1f}m | {d.direction}"
                    )
                else:
                    label = (
                        f"{d.name} | distance unknown | "
                        f"{d.direction}"
                    )

                cv2.rectangle(
                    frame, (x1, y1), (x2, y2), color, 2
                )

                cv2.putText(
                    frame,
                    label,
                    (max(2, x1), max(18, y1 - 6)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.48,
                    color,
                    2,
                    cv2.LINE_AA,
                )

            # --------------------------------------------------
            # 8. Calculate approximate FPS
            # --------------------------------------------------
            frame_count += 1

            if frame_count >= 10:
                now = time.monotonic()
                fps = frame_count / max(now - start, 1e-6)
                frame_count = 0
                start = now

            cv2.putText(
                frame,
                f"NaviSense | {fps:.1f} FPS | Q to quit",
                (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2,
            )

            cv2.imshow("NaviSense - Laptop Test", frame)

            # Exit on Q or Escape.
            if cv2.waitKey(1) & 0xFF in (ord("q"), 27):
                print("[MAIN] Exit requested.")
                break

    except KeyboardInterrupt:
        print("\n[MAIN] Interrupted by user.")

    finally:
        # Stop speech first so queued announcements cannot continue
        # while the camera and windows are being released.
        if speech is not None:
            speech.close()

        if cap is not None:
            cap.release()

        cv2.destroyAllWindows()
        print("[MAIN] NaviSense stopped.")


if __name__ == "__main__":
    main()
