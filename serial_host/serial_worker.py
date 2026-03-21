"""Service 层：串口收发与自动重连。"""
from __future__ import annotations

import threading
import time
from datetime import datetime
from typing import Callable, Optional

import serial
from serial import SerialException

from .protocol_events import DeviceLogEvent, DeviceStatusEvent

StatusCallback = Callable[[DeviceStatusEvent], None]
RawDataCallback = Callable[[bytes], None]
LogCallback = Callable[[DeviceLogEvent], None]


class SerialWorker:
    """后台串口工作线程。

    功能：
    - 非阻塞读取
    - 断线自动重连
    - 写入线程安全
    """

    def __init__(
        self,
        port: str,
        baudrate: int,
        status_callback: StatusCallback,
        data_callback: RawDataCallback,
        log_callback: Optional[LogCallback] = None,
        reconnect_interval: float = 2.0,
    ) -> None:
        self._port = port
        self._baudrate = baudrate
        self._status_callback = status_callback
        self._data_callback = data_callback
        self._log_callback = log_callback
        self._reconnect_interval = reconnect_interval

        self._serial: Optional[serial.Serial] = None
        self._stop_event = threading.Event()
        self._write_lock = threading.Lock()
        self._thread: Optional[threading.Thread] = None
        self._connected = False

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, name="SerialWorker", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        self._close_serial()

    def send(self, data: bytes) -> None:
        if not data:
            return
        with self._write_lock:
            if not self._serial or not self._serial.is_open:
                raise RuntimeError("串口未连接")
            self._serial.write(data)
            self._serial.flush()

    def _run(self) -> None:
        while not self._stop_event.is_set():
            if not self._ensure_connected():
                time.sleep(self._reconnect_interval)
                continue

            try:
                chunk = self._serial.read(256) if self._serial else b""
                if chunk:
                    self._data_callback(chunk)
            except SerialException as exc:
                self._log(f"串口异常，准备重连: {exc}")
                self._set_connected(False, reason=str(exc))
                self._close_serial()
                time.sleep(self._reconnect_interval)
            except Exception as exc:  # noqa: BLE001
                self._log(f"未知读取异常: {exc}")
                time.sleep(0.2)

    def _ensure_connected(self) -> bool:
        if self._serial and self._serial.is_open:
            return True

        try:
            self._serial = serial.Serial(
                port=self._port,
                baudrate=self._baudrate,
                timeout=0.2,
                write_timeout=1.0,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
            )
            self._set_connected(True, reason=f"已连接 {self._port}@{self._baudrate}")
            self._log("串口连接成功")
            return True
        except SerialException as exc:
            self._set_connected(False, reason=f"连接失败: {exc}")
            self._log(f"连接失败，{self._reconnect_interval}s 后重试")
            return False

    def _close_serial(self) -> None:
        if self._serial:
            try:
                self._serial.close()
            except Exception:  # noqa: BLE001
                pass
            self._serial = None

    def _set_connected(self, connected: bool, reason: str) -> None:
        if self._connected == connected:
            return
        self._connected = connected
        self._status_callback(
            DeviceStatusEvent(timestamp=datetime.now(), connected=connected, reason=reason)
        )

    def _log(self, message: str) -> None:
        if self._log_callback:
            self._log_callback(DeviceLogEvent(timestamp=datetime.now(), message=message))
