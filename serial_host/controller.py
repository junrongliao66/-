"""Controller 层：协调 UI、Service 与 Protocol。"""
from __future__ import annotations

from datetime import datetime
from typing import Callable, Optional

from .protocol_events import DeviceFrameEvent, DeviceLogEvent, DeviceStatusEvent
from .serial_worker import SerialWorker
from .yd9850_protocol import YD9850Protocol

FrameCallback = Callable[[DeviceFrameEvent], None]
StatusCallback = Callable[[DeviceStatusEvent], None]
LogCallback = Callable[[DeviceLogEvent], None]


class DeviceController:
    """业务控制器，UI 只和它交互，实现解耦。"""

    def __init__(self, port: str, baudrate: int) -> None:
        self._protocol = YD9850Protocol()
        self._ui_frame_callback: Optional[FrameCallback] = None
        self._ui_status_callback: Optional[StatusCallback] = None
        self._ui_log_callback: Optional[LogCallback] = None

        self._serial_worker = SerialWorker(
            port=port,
            baudrate=baudrate,
            status_callback=self._handle_status,
            data_callback=self._handle_raw_data,
            log_callback=self._handle_log,
        )

    def bind_callbacks(
        self,
        frame_callback: FrameCallback,
        status_callback: StatusCallback,
        log_callback: LogCallback,
    ) -> None:
        self._ui_frame_callback = frame_callback
        self._ui_status_callback = status_callback
        self._ui_log_callback = log_callback

    def start(self) -> None:
        self._serial_worker.start()

    def stop(self) -> None:
        self._serial_worker.stop()

    def send_command(self, command: int, payload: bytes = b"") -> None:
        frame = self._protocol.build_frame(command=command, payload=payload)
        self._serial_worker.send(frame)
        self._handle_log(DeviceLogEvent(timestamp=datetime.now(), message=f"发送: {frame.hex(' ')}"))

    def _handle_raw_data(self, chunk: bytes) -> None:
        self._handle_log(DeviceLogEvent(timestamp=datetime.now(), message=f"接收原始: {chunk.hex(' ')}"))
        for frame in self._protocol.feed(chunk):
            if self._ui_frame_callback:
                self._ui_frame_callback(
                    DeviceFrameEvent(
                        timestamp=datetime.now(),
                        command=frame.command,
                        payload=frame.payload,
                    )
                )

    def _handle_status(self, event: DeviceStatusEvent) -> None:
        if self._ui_status_callback:
            self._ui_status_callback(event)

    def _handle_log(self, event: DeviceLogEvent) -> None:
        if self._ui_log_callback:
            self._ui_log_callback(event)
