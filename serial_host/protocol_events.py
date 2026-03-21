"""跨层事件定义，避免 UI 直接依赖通信细节。"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class DeviceFrameEvent:
    """收到一帧设备业务数据。"""

    timestamp: datetime
    command: int
    payload: bytes


@dataclass(slots=True)
class DeviceStatusEvent:
    """设备连接状态变化。"""

    timestamp: datetime
    connected: bool
    reason: str


@dataclass(slots=True)
class DeviceLogEvent:
    """通用日志事件。"""

    timestamp: datetime
    message: str
