"""UI 层：仅负责展示与用户交互，不包含串口/协议逻辑。"""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from protocol_events import DeviceFrameEvent, DeviceLogEvent, DeviceStatusEvent


class MainWindow:
    """主界面。通过回调调用 Controller，不直接操作串口。"""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("YD9850 上位机示例")
        self.root.geometry("760x520")

        self.on_start = None
        self.on_stop = None
        self.on_send = None

        self._build_layout()

    def _build_layout(self) -> None:
        top = ttk.Frame(self.root, padding=8)
        top.pack(fill=tk.X)

        ttk.Label(top, text="命令(HEX):").pack(side=tk.LEFT)
        self.command_var = tk.StringVar(value="01")
        ttk.Entry(top, textvariable=self.command_var, width=8).pack(side=tk.LEFT, padx=4)

        ttk.Label(top, text="负载(HEX):").pack(side=tk.LEFT)
        self.payload_var = tk.StringVar(value="")
        ttk.Entry(top, textvariable=self.payload_var, width=40).pack(side=tk.LEFT, padx=4)

        ttk.Button(top, text="连接", command=self._start_clicked).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="断开", command=self._stop_clicked).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="发送", command=self._send_clicked).pack(side=tk.LEFT, padx=4)

        status_frame = ttk.Frame(self.root, padding=(8, 0))
        status_frame.pack(fill=tk.X)
        ttk.Label(status_frame, text="连接状态:").pack(side=tk.LEFT)
        self.status_var = tk.StringVar(value="未连接")
        ttk.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT)

        self.log_text = tk.Text(self.root, height=26)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self.log_text.configure(state=tk.DISABLED)

    def bind_actions(self, on_start, on_stop, on_send) -> None:
        self.on_start = on_start
        self.on_stop = on_stop
        self.on_send = on_send

    def push_status(self, event: DeviceStatusEvent) -> None:
        text = "已连接" if event.connected else "未连接"
        self.status_var.set(f"{text} ({event.reason})")
        self.push_log(DeviceLogEvent(timestamp=event.timestamp, message=f"状态变化: {event.reason}"))

    def push_frame(self, event: DeviceFrameEvent) -> None:
        self.push_log(
            DeviceLogEvent(
                timestamp=event.timestamp,
                message=f"收到帧: cmd=0x{event.command:02X}, payload={event.payload.hex(' ')}",
            )
        )

    def push_log(self, event: DeviceLogEvent) -> None:
        line = f"[{event.timestamp.strftime('%H:%M:%S')}] {event.message}\n"
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, line)
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def _start_clicked(self) -> None:
        if self.on_start:
            self.on_start()

    def _stop_clicked(self) -> None:
        if self.on_stop:
            self.on_stop()

    def _send_clicked(self) -> None:
        if not self.on_send:
            return

        try:
            command = int(self.command_var.get().strip(), 16)
            payload_str = self.payload_var.get().replace(" ", "")
            payload = bytes.fromhex(payload_str) if payload_str else b""
            self.on_send(command, payload)
        except ValueError as exc:
            messagebox.showerror("输入错误", f"请检查 HEX 格式: {exc}")
