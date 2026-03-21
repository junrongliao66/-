# 项目拆分说明

本仓库已拆分为两个互不干扰的项目：

- `serial_host/`：工业设备上位机（Python + pyserial + tkinter）
- `meal_ordering/`：报餐项目（原有前端文件）

## 运行上位机项目

```bash
pip install -r serial_host/requirements.txt
python -m serial_host.main
```

> 串口参数可在 `serial_host/main.py` 中修改。
