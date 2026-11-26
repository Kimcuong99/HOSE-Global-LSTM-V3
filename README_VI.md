# HOSE Global LSTM V3 — Hướng dẫn cài đặt và chạy

## 1. Yêu cầu máy tính

- Windows 10/11 64-bit.
- Python 3.12 64-bit và Python Launcher (`py`).
- Kết nối Internet trong lần cài thư viện đầu tiên.
- Khuyến nghị tối thiểu 8 GB RAM; huấn luyện LSTM có thể cần nhiều thời gian và tài nguyên hơn.

## 2. Cấu trúc thư mục

Đặt các file đúng vị trí trong `C:\HOSE_GLOBAL_LSTM_V3`:

```text
HOSE_GLOBAL_LSTM_V3/
├── app.py
├── INSTALL.bat
├── RUN_APP.bat
├── requirements.txt
├── README_VI.md
├── config/
│   └── settings.py
├── scripts/
│   ├── generate_hose_simulation.py
│   ├── prepare_data.py
│   ├── benchmark_models.py
│   └── train_global_lstm.py
├── data/
│   ├── simulation/
│   │   ├── raw/
│   │   └── processed/
│   └── real/
│       ├── raw/
│       └── processed/
├── models/
│   ├── simulation/
│   └── real/
├── outputs/
│   ├── simulation/
│   └── real/
└── tests/
```

`settings.py` nằm trong `config/`; bốn script `.py` nằm trong `scripts/`. Không đổi tên file nếu chưa cập nhật các lệnh tương ứng.

## 3. Cài đặt môi trường

1. Đóng các cửa sổ Streamlit đang chạy.
2. Mở thư mục `C:\HOSE_GLOBAL_LSTM_V3`.
3. Nhấp đúp `INSTALL.bat`.
4. Chờ cài thư viện và tạo dữ liệu mô phỏng hoàn tất. Không tắt cửa sổ giữa chừng.

Nếu Windows báo không tìm thấy Python 3.12, cài Python 3.12 64-bit, bật tùy chọn thêm Python vào PATH và thử lại.

## 4. Xử lý dữ liệu và huấn luyện mô hình

Mở PowerShell tại thư mục dự án và chạy lần lượt:

```powershell
.\.venv\Scripts\Activate.ps1
python scripts\prepare_data.py
python scripts\benchmark_models.py
python scripts\train_global_lstm.py
```

Nếu PowerShell chặn kích hoạt môi trường, có thể không cần kích hoạt; gọi trực tiếp Python trong môi trường ảo:

```powershell
.\.venv\Scripts\python.exe scripts\prepare_data.py
.\.venv\Scripts\python.exe scripts\benchmark_models.py
.\.venv\Scripts\python.exe scripts\train_global_lstm.py
```

Chỉ chạy lệnh tiếp theo khi lệnh trước kết thúc không có lỗi. Quá trình huấn luyện TensorFlow có thể mất thời gian.

## 5. Mở dashboard

Sau khi dữ liệu và các bước xử lý đã hoàn tất, nhấp đúp `RUN_APP.bat`. Streamlit sẽ mở dashboard trong trình duyệt. Nếu trình duyệt không tự mở, xem địa chỉ Local URL trong cửa sổ dòng lệnh (thường là `http://localhost:8501`). Giữ cửa sổ dòng lệnh mở trong lúc sử dụng ứng dụng.

Để tắt ứng dụng, quay lại cửa sổ dòng lệnh và nhấn `Ctrl+C`.

## 6. Dữ liệu và giới hạn diễn giải

- Bộ dữ liệu được tạo cho prototype gồm 160 mã cổ phiếu, giai đoạn 2020–2025; giá và khối lượng là dữ liệu **mô phỏng**.
- Dữ liệu mô phỏng không phải dữ liệu giao dịch thực tế của HOSE. Các biểu đồ, dự báo và chỉ số đánh giá từ bộ dữ liệu này chỉ phục vụ kiểm thử quy trình và minh họa.
- Không sử dụng kết quả mô phỏng làm bằng chứng về khả năng dự báo trên thị trường thực hoặc làm khuyến nghị đầu tư.
- Thư mục `data/real/` được dành cho dữ liệu thực được thu thập và kiểm tra riêng. Không chép dữ liệu thực vào thư mục mô phỏng.

## 7. Khi gặp lỗi

Hãy gửi ảnh chụp toàn bộ cửa sổ lỗi, đồng thời cho biết bạn đang chạy file nào (`INSTALL.bat`, lệnh xử lý dữ liệu hay `RUN_APP.bat`). Không xóa `.venv`, dữ liệu hoặc các file đầu ra trước khi lưu lại thông báo lỗi.

## 8. Trạng thái phát triển

Đây là bộ prototype đang được hoàn thiện theo từng file. Cần kiểm tra chạy thực tế trên máy Windows của người dùng trước khi xác nhận toàn bộ hệ thống hoạt động ổn định. Một số chức năng dashboard có thể chưa tích hợp đầy đủ việc nạp mô hình và dự báo trực tiếp; không mặc định rằng có file mô hình là dashboard đã dùng mô hình đó.
