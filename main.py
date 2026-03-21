"""应用入口。"""
from __future__ import annotations

import tkinter as tk

from controller import DeviceController
from ui_main import MainWindow


def main() -> None:
    # 根据现场设备修改默认参数。
    port = "COM3"  # Linux 示例: /dev/ttyUSB0
    baudrate = 115200

    controller = DeviceController(port=port, baudrate=baudrate)

    root = tk.Tk()
    ui = MainWindow(root)

    ui.bind_actions(
        on_start=controller.start,
        on_stop=controller.stop,
        on_send=controller.send_command,
    )
    controller.bind_callbacks(
        frame_callback=ui.push_frame,
        status_callback=ui.push_status,
        log_callback=ui.push_log,
    )

    def on_close() -> None:
        controller.stop()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
