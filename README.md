# Ứng dụng Kiểm tra Độ mạnh Mật khẩu

> **Đồ án môn IE221 - Kỹ thuật lập trình Python**
> Trường Đại học Công nghệ Thông tin (UIT) - ĐHQG TP.HCM

---

## Nhóm phát triển

| Họ và tên | MSSV |
|---|---|
| Nguyễn Tấn Viễn | 25410333 |
| Nguyễn Mai Xuân | 25410342 |

**Nhóm:** Nhóm 2 | **Môn học:** IE221 - Kỹ thuật lập trình Python | **GVHD:** Nghi Hoàng Khoa

---

## Giới thiệu

Ứng dụng **Password Checker** là một công cụ phân tích và đánh giá độ mạnh mật khẩu, được xây dựng theo kiến trúc **Client-Server (Local)** gồm 2 tầng:

- **Frontend (GUI):** Tkinter — Giao diện đồ họa người dùng
- **Backend (API):** FastAPI — Máy chủ cục bộ xử lý từ điển và kiểm tra mẫu (pattern)

Nguyên tắc bảo mật cốt lõi được tuân thủ: **TUYỆT ĐỐI KHÔNG gửi mật khẩu nguyên bản qua mạng**. Mọi phân tích đều được thực hiện hoàn toàn trên máy tính cục bộ (`localhost`).

---

## Tính năng chính

### Phân tích mật khẩu
- **Kiểm tra thành phần ký tự:** Chữ thường (a-z), chữ hoa (A-Z), chữ số (0-9), ký tự đặc biệt (!@#$...)
- **Tính toán Entropy thông tin:** Áp dụng công thức `H = L × log₂(N)` (Shannon Entropy)
  - `L` = độ dài mật khẩu
  - `N` = kích thước không gian ký tự (Character Pool)
- **Chấm điểm 0–100:** Dựa trên entropy thực tế sau khi trừ điểm phạt

### Phát hiện lỗ hổng bảo mật
| Lỗ hổng | Mô tả | Hình phạt |
|---|---|---|
| **Từ tiếng Anh** | Phát hiện từ có nghĩa (≥ 5 ký tự) nhúng trong mật khẩu, ví dụ `Vienanimals@1` → phát hiện `animals` | -15 điểm |
| **Ký tự lặp liền kề** | Chuỗi ký tự lặp ≥ 3 lần, ví dụ `aaa`, `111` | -15 điểm |
| **Chuỗi tuần hoàn** | Cụm 2–4 ký tự lặp lại liên tiếp, ví dụ `abcabc`, `1212` | -15 điểm |

### Phân loại mức độ bảo mật
| Điểm | Mức độ | Màu sắc hiển thị |
|---|---|---|
| 0 – 39 | Yếu | Đỏ |
| 40 – 69 | Trung bình | Cam |
| 70 – 100 | Mạnh | Xanh lá |

### Giao diện người dùng
- **Thanh trực quan** thay đổi chiều dài và màu sắc theo điểm số
- **Bảng điểm chi tiết** với định dạng rich text:
  - Dòng cảnh báo lỗi → tô toàn bộ **màu đỏ**
  - Từ/chuỗi phát hiện (trong dấu `'...'`) → **in đậm** nổi bật
- **Trạng thái Backend** cập nhật liên tục (real-time polling định kỳ)
- **Nút Kiểm tra** tự động khóa khi Backend chưa sẵn sàng
- **Ẩn/hiện mật khẩu** bằng chức năng hộp kiểm (checkbox)
- **Cửa sổ Giới thiệu (About)** hiển thị thông tin nhóm phát triển

---

## Kiến trúc hệ thống

```text
PasswordCheckerProject/
│
├── main.py                          # Điểm khởi động: khởi tạo Backend và GUI
├── about.txt                        # Thông tin nhóm phát triển
├── requirements.txt                 # Thư viện phụ thuộc
│
├── backend/
│   ├── server.py                    # FastAPI server: xử lý từ điển và kiểm tra pattern
│   └── words_alpha.txt              # Từ điển từ tiếng Anh
│
└── password_analyzer/
    ├── core/
    │   ├── evaluator.py             # Lớp PasswordEvaluator (OOP - Encapsulation)
    │   └── rules.py                 # Hàm phân tích: độ phức tạp, chuỗi lặp, từ điển
    ├── gui/
    │   └── app.py                   # Giao diện Tkinter (PasswordCheckerApp)
    └── utils/
        ├── validators.py            # Kiểm tra đầu vào hợp lệ
        └── exceptions.py           # Custom Exception xử lý lỗi
```

### Luồng dữ liệu

```text
Người dùng nhập mật khẩu
        ↓
  [GUI - Tkinter]
        ↓ Gọi
  [PasswordEvaluator]
     ├── analyze_password_complexity()  → Trích xuất cờ hiệu (flags)
     ├── check_repetition()             → Quét Regex pattern
     └── check_dictionary_words()
               ↓ HTTP GET localhost:8000
         [FastAPI Backend]
           └── Sliding Window search trên không gian từ vựng
               ↓ Trả về JSON
  ← Kết quả: Điểm, Cấp độ, Danh sách lỗi
        ↓
  [GUI] Hiển thị kết quả đánh giá chi tiết
```

---

## Công nghệ sử dụng

| Công nghệ | Phiên bản | Vai trò |
|---|---|---|
| **Python** | ≥ 3.10 | Ngôn ngữ lập trình chính |
| **Tkinter** | Built-in | Giao diện đồ họa (GUI) |
| **FastAPI** | ≥ 0.100 | Web framework cho Backend API |
| **Uvicorn** | ≥ 0.23 | ASGI server chạy FastAPI |
| **Requests** | ≥ 2.31 | HTTP client gọi API từ GUI |
| **Regex (re)** | Built-in | Phát hiện pattern lặp và trích xuất từ |

---

## Hướng dẫn cài đặt và sử dụng

### Yêu cầu
- Python ≥ 3.10
- Khuyến nghị sử dụng môi trường ảo (Virtual Environment)

### Cài đặt và khởi chạy

1. **Kích hoạt môi trường ảo (tùy chọn)**
   ```powershell
   .venv\Scripts\Activate
   ```

2. **Cài đặt thư viện phụ thuộc**
   ```bash
   pip install -r requirements.txt
   ```

3. **Chạy ứng dụng**
   ```bash
   python main.py
   ```

> **Lưu ý:** Khi khởi chạy `main.py`, hệ thống tự động:
> 1. Khởi động Backend FastAPI ở nền (port 8000)
> 2. Nạp dữ liệu từ điển vào bộ nhớ
> 3. Khởi tạo giao diện Tkinter
> 4. Tự động giải phóng tài nguyên Backend khi đóng giao diện

---

## Phương pháp tính điểm

### Công thức cơ sở

```text
H_gốc   = L × log₂(N)         (Shannon Entropy)
Penalty = số_lỗ_hổng × 15     (mỗi lỗ hổng trừ 15 điểm)
Score   = min(100, H_gốc) − Penalty
Score   = max(0, Score)        (Giới hạn điểm tối thiểu là 0)
```

**Ví dụ minh họa:**
- Mật khẩu `@MyPrivate2024!` (15 ký tự, bao gồm đủ 4 thành phần):
  - `H_gốc = 15 × log₂(94) ≈ 98.4 bits`
  - Phát hiện từ `private` → `Penalty = 15`
  - `Score = min(100, 98) − 15 = 83/100`

### Phát hiện từ tiếng Anh (Sliding Window)

Backend áp dụng thuật toán **Sliding Window** trên tập dữ liệu để tìm kiếm từ có nghĩa được nhúng bên trong mật khẩu:

```text
Mật khẩu đầu vào: "Vienanimals@1"
Chuỗi ký tự trích xuất: "Vienanimals"
Quá trình trượt cửa sổ (ưu tiên từ dài):
  - "vienanimals" → Không tìm thấy
  - "ienanimals"  → Không tìm thấy
  - "animals"     → Phát hiện có ý nghĩa → Áp dụng điểm phạt (-15)
```

---

## Nguyên tắc bảo mật ứng dụng

1. **Bảo mật mạng:** Toàn bộ quá trình xử lý diễn ra trên môi trường cục bộ (`127.0.0.1`), không truyền tải dữ liệu mật khẩu ra bên ngoài.
2. **Encapsulation:** Thuộc tính mật khẩu được đóng gói dưới dạng private (sử dụng cơ chế name mangling của Python).
3. **Graceful Degradation:** Đảm bảo ứng dụng tiếp tục hoạt động và cung cấp đánh giá cơ bản ngay cả khi quá trình khởi động Backend gặp sự cố.
4. **Quản lý tài nguyên:** Tự động thu hồi tài nguyên Backend khi quá trình sử dụng kết thúc thông qua thư viện `atexit`.

---

## Áp dụng các nguyên lý Lập trình Hướng đối tượng (OOP)

| Nguyên lý / Khái niệm | Vị trí áp dụng |
|---|---|
| **Encapsulation (Đóng gói)** | Thuộc tính ẩn `PasswordEvaluator.__password` |
| **Abstraction (Trừu tượng)** | Phân tách logic xử lý tại `rules.py`, `validators.py`, `exceptions.py` |
| **Custom Exception** | Xây dựng ngoại lệ `PasswordValidationError` kế thừa từ lớp `Exception` |
| **Thiết kế Thuật toán** | Tối ưu hóa kiểm tra độ phức tạp với `analyze_password_complexity()` (độ phức tạp O(N)) |

---
*Tài liệu thuộc Đồ án môn học IE221 — Nhóm 2 — UIT 2026*
