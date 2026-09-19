# 🔐 Ứng dụng kiểm tra độ mạnh mật khẩu

> **Đồ án môn IE221 - Kỹ thuật lập trình Python**
> Trường Đại học Công nghệ Thông tin (UIT) - ĐHQG TP.HCM

---

## 👥 Nhóm phát triển

| Họ và tên       | MSSV     |
| ------------------ | -------- |
| Nguyễn Tấn Viễn | 25410333 |
| Nguyễn Mai Xuân  | 25410342 |

**Nhóm:** Nhóm 2 | **Môn học:** IE221 - Kỹ thuật lập trình Python | **GVHD:** Nghi Hoàng Khoa

---

## 📖 Giới thiệu

Ứng dụng **Password Checker** là một công cụ phân tích và đánh giá độ mạnh mật khẩu, được xây dựng theo kiến trúc **Client-Server (Local)** gồm 2 tầng:

- **Frontend (GUI):** Tkinter — Giao diện đồ họa người dùng
- **Backend (API):** FastAPI — Máy chủ cục bộ xử lý từ điển và kiểm tra pattern

Nguyên tắc bảo mật cốt lõi được tuân thủ: **TUYỆT ĐỐI KHÔNG gửi mật khẩu nguyên bản qua mạng**. Mọi phân tích đều được thực hiện hoàn toàn trên máy tính cục bộ (`localhost`).

---

## ✨ Tính năng chính

### 🎯 Phân tích mật khẩu

- **Kiểm tra thành phần ký tự:** Chữ thường (a-z), chữ hoa (A-Z), chữ số (0-9), ký tự đặc biệt (!@#$...)
- **Tính toán Entropy thông tin:** Áp dụng công thức `H = L × log₂(N)` (Shannon Entropy)
  - `L` = độ dài mật khẩu
  - `N` = kích thước không gian ký tự (Character Pool)
- **Chấm điểm 0–100:** Dựa trên entropy thực tế sau khi trừ điểm phạt

### 🔍 Phát hiện lỗ hổng bảo mật

| Lỗ hổng                        | Mô tả                                                                                                                | Hình phạt |
| -------------------------------- | ---------------------------------------------------------------------------------------------------------------------- | ----------- |
| **Từ tiếng Anh**         | Phát hiện từ có nghĩa (≥ 5 ký tự) nhúng trong mật khẩu, ví dụ`Vienanimals@1` → phát hiện `animals` | -15 điểm  |
| **Ký tự lặp liền kề** | Chuỗi ký tự lặp ≥ 3 lần, ví dụ`aaa`, `111`                                                                 | -15 điểm  |
| **Chuỗi tuần hoàn**     | Cụm 2–4 ký tự lặp lại liên tiếp, ví dụ`abcabc`, `1212`                                                   | -15 điểm  |

### 🏆 Phân loại mức độ bảo mật

| Điểm    | Mức độ      | Màu     |
| --------- | -------------- | -------- |
| 0 – 39   | 🔴 Yếu        | Đỏ     |
| 40 – 69  | 🟡 Trung bình | Cam      |
| 70 – 100 | 🟢 Mạnh       | Xanh lá |

### 🖥️ Giao diện người dùng

- **Thanh sức mạnh** trực quan thay đổi màu sắc theo điểm số
- **Bảng điểm chi tiết** với định dạng rich text:
  - Dòng ❌ → tô toàn bộ **màu đỏ**
  - Từ/chuỗi phát hiện (trong dấu `'...'`) → **in đậm** nổi bật
- **Trạng thái Backend** cập nhật liên tục (real-time polling mỗi 1 giây)
- **Nút Kiểm tra** tự động khóa khi Backend chưa sẵn sàng
- **Ẩn/hiện mật khẩu** bằng checkbox
- **Popup About** hiển thị thông tin nhóm từ file `about.txt`

---

## 🏗️ Kiến trúc hệ thống

```
PasswordCheckerProject/
│
├── main.py                          # Điểm khởi động: tự động bật Backend + GUI
├── about.txt                        # Thông tin nhóm phát triển
├── requirements.txt                 # Thư viện phụ thuộc
│
├── backend/
│   ├── server.py                    # FastAPI server: từ điển & kiểm tra pattern
│   └── google-10000-english.txt     # Từ điển 10,000 từ tiếng Anh phổ biến (Google)
│
└── password_analyzer/
    ├── core/
    │   ├── evaluator.py             # Lớp PasswordEvaluator (OOP - Encapsulation)
    │   └── rules.py                 # Hàm phân tích: complexity, repetition, dictionary
    ├── gui/
    │   └── app.py                   # Giao diện Tkinter (PasswordCheckerApp)
    └── utils/
        ├── validators.py            # Validator: kiểm tra đầu vào hợp lệ
        └── exceptions.py           # Custom Exception: PasswordValidationError
```

### Luồng dữ liệu

```
Người dùng nhập mật khẩu
        ↓
  [GUI - Tkinter]
        ↓ Gọi
  [PasswordEvaluator]
     ├── analyze_password_complexity()  → Cờ hiệu (flags)
     ├── check_repetition()             → Regex pattern
     └── check_dictionary_words()
               ↓ HTTP GET localhost:8000
         [FastAPI Backend]
           └── Sliding Window search trên RAM Set{10,000 từ}
               ↓ Trả về JSON
  ← Kết quả: Điểm, Cấp độ, Danh sách lỗi
        ↓
  [GUI] Hiển thị rich text với màu sắc
```

---

## 🔧 Công nghệ sử dụng

| Công nghệ          | Phiên bản | Vai trò                                      |
| -------------------- | ----------- | --------------------------------------------- |
| **Python**     | ≥ 3.10     | Ngôn ngữ lập trình chính                 |
| **Tkinter**    | Built-in    | Giao diện đồ họa (GUI)                    |
| **FastAPI**    | ≥ 0.100    | Web framework cho Backend API                 |
| **Uvicorn**    | ≥ 0.23     | ASGI server chạy FastAPI                     |
| **Requests**   | ≥ 2.31     | HTTP client gọi API từ GUI                  |
| **Regex (re)** | Built-in    | Phát hiện pattern lặp và trích xuất từ |

---

## 🚀 Hướng dẫn cài đặt và chạy

### Yêu cầu

- Python ≥ 3.10
- Môi trường ảo (khuyến nghị)

### Bước 1: Kích hoạt môi trường ảo

```powershell
# Windows (PowerShell)
.venv\Scripts\Activate
```

### Bước 2: Cài đặt thư viện

```bash
pip install -r requirements.txt
```

### Bước 3: Chạy ứng dụng

```bash
python main.py
```

> ✅ Khi chạy `main.py`, hệ thống sẽ **tự động**:
>
> 1. Khởi động Backend FastAPI ở nền (port 8000)
> 2. Nạp từ điển 10,000 từ vào RAM
> 3. Mở giao diện Tkinter
> 4. Khi đóng cửa sổ → Backend tự động tắt, giải phóng RAM

---

## 🧮 Phương pháp tính điểm

### Công thức cơ bản

```
H_gốc   = L × log₂(N)         (Shannon Entropy)
Penalty = số_lỗ_hổng × 15     (mỗi lỗ hổng trừ 15 điểm)
Score   = min(100, H_gốc) − Penalty
Score   = max(0, Score)        (sàn tại 0)
```

**Ví dụ thực tế:**

- Mật khẩu `@MyPrivate2024!` (15 ký tự, đủ 4 thành phần):
  - `H_gốc = 15 × log₂(94) ≈ 98.4 bits`
  - Phát hiện từ `private` → `Penalty = 15`
  - `Score = min(100, 98) − 15 = 83/100`

### Phát hiện từ tiếng Anh (Sliding Window)

Backend sử dụng thuật toán **Sliding Window** trên tập `Set` để tìm từ có nghĩa nhúng bên trong mật khẩu:

```
Mật khẩu: "Vienanimals@1"
Trích xuất chuỗi chữ: "Vienanimals"
Cửa sổ trượt từ dài → ngắn:
  - "vienanimals" → không có
  - "ienanimals"  → không có
  - "animals"     → ✅ TÌM THẤY → Phạt -15 điểm
```

---

## 🛡️ Nguyên tắc bảo mật

1. **Không gửi mật khẩu qua Internet:** Toàn bộ xử lý diễn ra trên `127.0.0.1`
2. **Encapsulation:** Thuộc tính `__password` được đặt là private (name mangling Python)
3. **Graceful Degradation:** Nếu Backend chưa khởi động, ứng dụng tiếp tục hoạt động (bỏ qua kiểm tra từ điển)
4. **Auto cleanup:** Backend tự tắt khi GUI đóng thông qua `atexit`

---

## 📚 Các khái niệm OOP được áp dụng

| Khái niệm                           | Nơi áp dụng                                          |
| ------------------------------------- | ------------------------------------------------------- |
| **Encapsulation (Đóng gói)** | `PasswordEvaluator.__password` — thuộc tính ẩn    |
| **Abstraction (Trừu tượng)** | Tách`rules.py`, `validators.py`, `exceptions.py` |
| **Custom Exception**            | `PasswordValidationError` kế thừa `Exception`     |
| **One-pass Algorithm**          | `analyze_password_complexity()` duyệt O(N) một lần |

---

*Đồ án IE221 — Nhóm 2 — UIT 2024*
