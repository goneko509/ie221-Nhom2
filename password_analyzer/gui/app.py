import tkinter as tk
from tkinter import messagebox
import requests
import threading
import re
import os
from ..core.evaluator import PasswordEvaluator

class PasswordCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Checker")
        self.root.geometry("450x550")
        self.root.resizable(False, False)
        
        self.setup_ui()

    def setup_ui(self):
        # Tiêu đề
        title_label = tk.Label(self.root, text="KIỂM TRA MẬT KHẨU", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Trạng thái Backend API
        self.api_status_label = tk.Label(self.root, text="🟡 Đang khởi động Backend và nạp Từ điển...", font=("Arial", 10, "italic"), fg="#ff9800")
        self.api_status_label.pack(pady=2)
        
        # Ô nhập liệu
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=5)
        
        tk.Label(input_frame, text="Nhập mật khẩu:").pack(side=tk.LEFT, padx=5)
        self.password_entry = tk.Entry(input_frame, width=30, show="*", font=("Arial", 11))
        self.password_entry.pack(side=tk.LEFT, padx=5)
        
        # Checkbox ẩn hiện mật khẩu
        self.show_pwd_var = tk.BooleanVar()
        self.show_pwd_cb = tk.Checkbutton(
            self.root, text="Hiển thị mật khẩu", variable=self.show_pwd_var, command=self.toggle_password
        )
        self.show_pwd_cb.pack(pady=2)
        
        # Nút kiểm tra
        self.check_btn = tk.Button(
            self.root, text="Kiểm Tra", command=self.check_password, 
            bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), width=15,
            state=tk.DISABLED # Khóa nút cho đến khi Backend sẵn sàng
        )
        self.check_btn.pack(pady=10)
        
        # Nhãn hiển thị kết quả
        self.result_label = tk.Label(self.root, text="Kết quả: Chưa đánh giá", font=("Arial", 12))
        self.result_label.pack(pady=5)
        
        # Thanh biểu thị trực quan (Strength Bar)
        self.strength_canvas = tk.Canvas(self.root, width=300, height=20, bg="lightgrey", highlightthickness=0)
        self.strength_canvas.pack(pady=5)
        self.strength_bar = self.strength_canvas.create_rectangle(0, 0, 0, 20, fill="lightgrey", outline="")
        
        # Khu vực thông báo chi tiết dùng Text widget để hỗ trợ rich text (màu + bold)
        tk.Label(self.root, text="Thông báo chi tiết (Bảng điểm):").pack(anchor=tk.W, padx=25)
        
        text_frame = tk.Frame(self.root)
        text_frame.pack(pady=5, padx=25, fill=tk.X)
        
        self.suggestions_text = tk.Text(
            text_frame, width=68, height=13, font=("Arial", 10),
            state=tk.DISABLED, wrap=tk.WORD, cursor="arrow",
            relief=tk.SUNKEN, bd=1
        )
        scrollbar = tk.Scrollbar(text_frame, command=self.suggestions_text.yview)
        self.suggestions_text.config(yscrollcommand=scrollbar.set)
        self.suggestions_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Định nghĩa các tags cho rich text
        self.suggestions_text.tag_config("fail", foreground="#d32f2f")             # dòng ❌ màu đỏ
        self.suggestions_text.tag_config("bold_word", font=("Arial", 10, "bold")) # từ tiếng Anh in đậm
        self.suggestions_text.tag_config("fail_bold", foreground="#d32f2f",        # từ in đậm + đỏ
                                          font=("Arial", 10, "bold"))
        
        # Nút About - hiển thị thông tin nhóm phát triển
        self.about_btn = tk.Button(
            self.root, text="ℹ️ About", command=self.show_about,
            bg="#607d8b", fg="white", font=("Arial", 9), width=10, relief=tk.FLAT
        )
        self.about_btn.pack(pady=(2, 8))
        
        # Bắt đầu vòng lặp kiểm tra trạng thái Backend API sau khi khởi tạo xong UI
        self.check_backend_status()

    def toggle_password(self):
        if self.show_pwd_var.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")
    
    def show_about(self):
        """
        Đọc file about.txt và hiển thị nội dung trong popup.
        """
        # Tìm file about.txt tương đối từ thư mục gốc của dự án (2 cấp lên so với file này)
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        about_path = os.path.join(base_dir, "about.txt")
        try:
            with open(about_path, "r", encoding="utf-8") as f:
                content = f.read()
            # Hiển thị trong cửa sổ popup tùy chỉnh để giữ định dạng (không dùng messagebox)
            popup = tk.Toplevel(self.root)
            popup.title("Giới thiệu")
            popup.resizable(False, False)
            popup.grab_set()  # Modal
            tk.Label(popup, text="ℹ️ Giới thiệu ứng dụng", font=("Arial", 12, "bold"), pady=8).pack()
            text_area = tk.Text(popup, width=52, height=14, font=("Courier New", 10),
                                state=tk.NORMAL, wrap=tk.WORD, relief=tk.FLAT, bg="#f5f5f5")
            text_area.insert(tk.END, content)
            text_area.config(state=tk.DISABLED)
            text_area.pack(padx=20, pady=(0, 10))
            tk.Button(popup, text="Đóng", command=popup.destroy,
                      bg="#607d8b", fg="white", font=("Arial", 10), width=10).pack(pady=(0, 12))
        except FileNotFoundError:
            messagebox.showerror("Lỗi", f"Không tìm thấy file about.txt\n({about_path})")
            
    def check_password(self):
        pwd = self.password_entry.get()
        
        # Cập nhật trạng thái đang xử lý
        self.api_status_label.config(text="🔵 Đang gửi dữ liệu và tra cứu từ điển trên Backend...", fg="#2196F3")
        self.root.update_idletasks()
        
        # Liên kết (binding) với lớp xử lý logic OOP
        evaluator = PasswordEvaluator(pwd)
        evaluator.evaluate()
        feedback = evaluator.get_password_feedback()
        
        # Xóa nội dung cũ trong Text widget
        self.suggestions_text.config(state=tk.NORMAL)
        self.suggestions_text.delete("1.0", tk.END)
        
        if not feedback["is_valid"]:
            self.result_label.config(text="Kết quả: Lỗi dữ liệu", fg="red")
            self.strength_canvas.coords(self.strength_bar, 0, 0, 300, 20)
            self.strength_canvas.itemconfig(self.strength_bar, fill="red")
            for sug in feedback["suggestions"]:
                self._insert_suggestion(f"❌ {sug}")
            self.suggestions_text.config(state=tk.DISABLED)
            return
            
        score = feedback["score"]
        level = feedback["level"]
        
        # Cập nhật Label
        self.result_label.config(text=f"Kết quả: {level} (Điểm: {score}/100)")
        
        # Cập nhật màu sắc và độ dài thanh sức mạnh
        bar_width = (score / 100) * 300
        self.strength_canvas.coords(self.strength_bar, 0, 0, bar_width, 20)
        
        if level == "Yếu":
            color = "#f44336"
        elif level == "Trung bình":
            color = "#ff9800"
        else:
            color = "#4CAF50"
            
        self.result_label.config(fg=color)
        self.strength_canvas.itemconfig(self.strength_bar, fill=color)
        
        # Sắp xếp danh sách gợi ý (✅ đúng ở trên, ❌ sai gạch chéo ở dưới)
        def sort_suggestion_key(text):
            if text.startswith("✅"): return 0
            if text.startswith("🔍") or text.startswith("🧮"): return 1
            if text.startswith("💡"): return 2
            if text.startswith("❌"): return 3
            return 4
            
        sorted_suggestions = sorted(feedback["suggestions"], key=sort_suggestion_key)
        
        # Render từng dòng gợi ý với định dạng phong phú
        for sug in sorted_suggestions:
            self._insert_suggestion(sug)
            
        if score == 100 and not feedback.get("has_penalty", False):
            self._insert_suggestion("🏆 Tuyệt vời! Mật khẩu của bạn đạt điểm tối đa.")
        else:
            has_errors = any(sug.startswith("❌") for sug in feedback["suggestions"])
            if has_errors:
                self._insert_suggestion("💡 Lời khuyên: Hãy khắc phục các lỗi ❌ để đạt 100 điểm.")
            else:
                self._insert_suggestion("💡 Lời khuyên: Hãy tăng độ dài hoặc độ phức tạp của mật khẩu để đạt 100 điểm.")
        
        self.suggestions_text.config(state=tk.DISABLED)

    def _insert_suggestion(self, text: str):
        """
        Chèn một dòng gợi ý vào Text widget với định dạng rich text:
        - Dòng ❌: tô toàn bộ màu đỏ
        - Từ tiếng Anh được phát hiện (nằm trong dấu nháy đơn '...'): in đậm thêm
        """
        is_fail = text.startswith("❌")
        
        # Tìm từ tiếng Anh trong dấu nháy đơn, ví dụ: 'animals', 'private'
        # Pattern: dấu ' ... ' chứa chữ cái
        pattern = re.compile(r"'([a-zA-Z]+)'")
        matches = list(pattern.finditer(text))
        
        if not matches:
            # Không có từ đặc biệt: chèn cả dòng một lần
            tag = "fail" if is_fail else ""
            self.suggestions_text.insert(tk.END, text + "\n", tag if tag else ())
        else:
            # Chèn từng phần: trước từ / từ in đậm / sau từ
            prev_end = 0
            base_tag = "fail" if is_fail else ""
            bold_tag = "fail_bold" if is_fail else "bold_word"
            
            for m in matches:
                # Phần văn bản trước từ được tìm thấy
                if m.start() > prev_end:
                    self.suggestions_text.insert(tk.END, text[prev_end:m.start()], base_tag if base_tag else ())
                # Chèn cả dấu nháy đơn + từ + dấu nháy đơn nhưng in đậm
                self.suggestions_text.insert(tk.END, text[m.start():m.end()], bold_tag)
                prev_end = m.end()
            
            # Phần còn lại sau match cuối
            if prev_end < len(text):
                self.suggestions_text.insert(tk.END, text[prev_end:], base_tag if base_tag else ())
            self.suggestions_text.insert(tk.END, "\n")

    def check_backend_status(self):
        """
        Gửi request liên tục mỗi giây để thăm dò xem Local Backend đã nạp xong từ điển chưa.
        Chạy trực tiếp trên Main Thread của Tkinter. Do kết nối localhost và timeout 0.5s nên
        sẽ không gây giật lag đáng kể, đồng thời đảm bảo an toàn Thread-safe cho Tkinter.
        """
        try:
            res = requests.get("http://127.0.0.1:8000/api/status", timeout=0.5)
            if res.status_code == 200:
                data = res.json()
                words_count = data.get("words_loaded", 0)
                if words_count > 0:
                    # Thêm một chút biểu tượng để cho thấy nó đang chạy thực (Real-time polling)
                    current_text = self.api_status_label.cget("text")
                    indicator = "⚡" if "🟢" in current_text else "🟢"
                    self.api_status_label.config(text=f"{indicator} Backend OK: Đã nạp {words_count:,} từ tiếng Anh.", fg="#4CAF50")
                    self.check_btn.config(state=tk.NORMAL) # Kích hoạt nút
                    # Tiếp tục polling định kỳ 1 giây
                    self.root.after(1000, self.check_backend_status)
                else:
                    self.api_status_label.config(text="🟡 Backend đang khởi động, chờ nạp từ...", fg="#ff9800")
                    self.check_btn.config(state=tk.DISABLED) # Khóa nút
                    self.root.after(1000, self.check_backend_status)
            else:
                self.api_status_label.config(text="🔴 Backend lỗi phản hồi.", fg="#f44336")
                self.check_btn.config(state=tk.DISABLED)
                self.root.after(2000, self.check_backend_status)
        except requests.exceptions.RequestException:
            # Nếu không gọi được, có thể backend chưa bật xong
            self.api_status_label.config(text="🟡 Đang chờ Local Backend khởi động...", fg="#ff9800")
            self.check_btn.config(state=tk.DISABLED)
            self.root.after(1000, self.check_backend_status)

def run_app():
    root = tk.Tk()
    app = PasswordCheckerApp(root)
    root.mainloop()
