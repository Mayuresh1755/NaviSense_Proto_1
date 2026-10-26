
"""Latest-message-wins Windows speech for NaviSense."""

import os
import queue
import subprocess
import sys
import threading
import time


class Speech:
    def __init__(self, enabled=True):
        self.enabled = enabled and sys.platform == "win32"
        self.messages = queue.Queue(maxsize=1)
        self.last = {}
        self.lock = threading.Lock()
        self.process = None
        self.worker = None
        self.closing = threading.Event()

        if not enabled:
            return

        if sys.platform != "win32":
            print("[Speech] This implementation requires Windows.")
            self.enabled = False
            return

        script = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "speech_worker.ps1",
        )

        if not os.path.isfile(script):
            print(f"[Speech] Script not found: {script}")
            self.enabled = False
            return

        try:
            self.process = subprocess.Popen(
                [
                    "powershell.exe",
                    "-NoProfile",
                    "-ExecutionPolicy", "Bypass",
                    "-File", script,
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=None,
                text=True,
                encoding="utf-8",
                bufsize=1,
            )

            self.worker = threading.Thread(
                target=self._worker,
                daemon=True,
                name="NaviSenseSpeech",
            )
            self.worker.start()
            print("[Speech] Latest-message speech ready.")

        except Exception as exc:
            self.enabled = False
            print(f"[Speech] Startup error: {exc}")

    def _send(self, command):
        if not self.process or self.process.poll() is not None:
            return False

        self.process.stdin.write(command + "\n")
        self.process.stdin.flush()
        return True

    def _worker(self):
        try:
            while True:
                message = self.messages.get()

                try:
                    if message is None:
                        break

                    if self.closing.is_set():
                        break

                    if self.closing.is_set():
                        break

                    text = str(message).replace("\r", " ").replace("\n", " ")

                    if not self._send(text):
                        self.enabled = False
                        break

                except (BrokenPipeError, OSError, ValueError) as exc:
                    print(f"[Speech] Send error: {exc}")
                    self.enabled = False
                    break

                finally:
                    self.messages.task_done()

        finally:
            # This worker is the only thread that writes to stdin.
            try:
                if self.process and self.process.poll() is None:
                    self._send("__QUIT__")
                    self.process.stdin.close()
                    self.process.wait(timeout=3)
            except Exception:
                if self.process and self.process.poll() is None:
                    self.process.terminate()

    def say(self, text, key=None, interval=1.0):
        if not self.enabled or self.closing.is_set() or not text:
            return

        now = time.monotonic()
        key = key or text

        with self.lock:
            previous = self.last.get(key, float("-inf"))
            if now - previous < interval:
                return

            self.last[key] = now

            # Replace an outdated pending announcement.
            while True:
                try:
                    self.messages.get_nowait()
                    self.messages.task_done()
                except queue.Empty:
                    break

            try:
                self.messages.put_nowait(str(text))
            except queue.Full:
                return

        print(f"[Speech] Latest alert: {text}")

    def close(self):
        if self.closing.is_set():
            return

        self.closing.set()
        self.enabled = False

        # Discard every pending announcement.
        while True:
            try:
                self.messages.get_nowait()
                self.messages.task_done()
            except queue.Empty:
                break

        if self.worker and self.worker.is_alive():
            self.messages.put(None)
            self.worker.join(timeout=2)

        # Force-stop PowerShell if graceful shutdown fails.
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                self.process.kill()
