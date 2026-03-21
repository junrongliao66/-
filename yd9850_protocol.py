"""YD9850 协议层：负责组帧、拆帧、CRC 校验。"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List


class ProtocolError(Exception):
    """协议解析异常。"""


@dataclass(slots=True)
class YD9850Frame:
    """一帧业务数据（不包含帧头、长度、CRC）。"""

    command: int
    payload: bytes


class YD9850Protocol:
    """协议说明（示例，可按设备文档调整）:

    frame = [0xAA, 0x55] + length(1B) + command(1B) + payload(NB) + crc16(2B, little)
    length = command + payload 的总长度。
    crc16 覆盖范围: length + command + payload。
    """

    HEADER = b"\xAA\x55"
    HEADER_SIZE = 2
    LENGTH_SIZE = 1
    CRC_SIZE = 2
    MIN_FRAME_BYTES = HEADER_SIZE + LENGTH_SIZE + 1 + CRC_SIZE

    def __init__(self) -> None:
        self._buffer = bytearray()

    @staticmethod
    def crc16_modbus(data: bytes) -> int:
        """MODBUS CRC16，多数工业设备常用。"""
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc >>= 1
        return crc & 0xFFFF

    def build_frame(self, command: int, payload: bytes = b"") -> bytes:
        """将业务命令打包为设备帧。"""
        if not 0 <= command <= 0xFF:
            raise ValueError("command 必须在 0~255")

        body = bytes([1 + len(payload), command]) + payload
        crc = self.crc16_modbus(body)
        return self.HEADER + body + crc.to_bytes(2, "little")

    def feed(self, chunk: bytes) -> List[YD9850Frame]:
        """流式喂入串口字节，支持粘包/半包处理。"""
        if not chunk:
            return []

        self._buffer.extend(chunk)
        frames: List[YD9850Frame] = []

        while True:
            # 1) 对齐帧头
            header_index = self._buffer.find(self.HEADER)
            if header_index < 0:
                # 没有帧头，最多保留 1 字节用于和下一包拼头
                if len(self._buffer) > 1:
                    del self._buffer[:-1]
                break

            if header_index > 0:
                del self._buffer[:header_index]

            # 2) 长度不足，等待下一包
            if len(self._buffer) < self.MIN_FRAME_BYTES:
                break

            length = self._buffer[self.HEADER_SIZE]
            frame_total_len = self.HEADER_SIZE + self.LENGTH_SIZE + length + self.CRC_SIZE

            if len(self._buffer) < frame_total_len:
                break

            frame_bytes = bytes(self._buffer[:frame_total_len])
            del self._buffer[:frame_total_len]

            body = frame_bytes[self.HEADER_SIZE : self.HEADER_SIZE + self.LENGTH_SIZE + length]
            recv_crc = int.from_bytes(frame_bytes[-2:], "little")
            calc_crc = self.crc16_modbus(body)

            if recv_crc != calc_crc:
                # CRC 不匹配，忽略该帧继续解析
                continue

            command = body[1]
            payload = body[2:]
            frames.append(YD9850Frame(command=command, payload=payload))

        return frames
