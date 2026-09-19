from .rules import analyze_password_complexity
from ..utils.validators import validate_not_empty, validate_length_bounds
from ..utils.exceptions import PasswordValidationError

class PasswordEvaluator:
    """
    Lớp đối tượng đánh giá độ mạnh mật khẩu (OOP).
    Áp dụng tính Đóng gói (Encapsulation) để bảo vệ dữ liệu đầu vào.
    """
    def __init__(self, raw_password: str):
        self.__password = raw_password  # Thuộc tính ẩn
        self.score = 0
        self.strength_level = "Chưa đánh giá"
        self.suggestions = []
        self.is_valid = True

    def evaluate(self, *args, **kwargs):
        """
        Thực thi quy trình đánh giá mật khẩu:
        1. Gọi hàm Validator kiểm tra ngoại lệ.
        2. Gọi hàm phân tích Rules lấy các cờ hiệu (flags).
        3. Tính toán điểm số và cấp độ.
        Hỗ trợ *args và **kwargs để tăng tính linh hoạt:
        - *args: Danh sách các hàm kiểm tra lỗi bổ sung (Custom rules - Dependency Injection).
        - **kwargs: Cấu hình ngưỡng điểm (threshold_weak, threshold_medium).
        """
        # Trích xuất cấu hình từ kwargs (tham số động)
        t_weak = kwargs.get("threshold_weak", 40)
        t_medium = kwargs.get("threshold_medium", 70)

        # Reset trạng thái mỗi khi đánh giá lại
        self.score = 0
        self.suggestions.clear()
        self.is_valid = True
        
        try:
            # 1. Kiểm tra ngoại lệ đầu vào
            validate_not_empty(self.__password)
            validate_length_bounds(self.__password)
        except PasswordValidationError as e:
            self.is_valid = False
            self.strength_level = "Không hợp lệ"
            self.suggestions.append(str(e))
            return
            
        # 2. Phân tích độ phức tạp (O(N) thuật toán cờ hiệu)
        flags = analyze_password_complexity(self.__password)
        
        # 3. Tính toán kích thước không gian mẫu (N)
        pool_size = 0
        if flags["has_lower"]: 
            pool_size += 26
            self.suggestions.append("✅ Có chữ cái viết thường (N + 26)")
        else: 
            self.suggestions.append("❌ Thiếu chữ cái viết thường (Giảm không gian mẫu)")
        
        if flags["has_upper"]: 
            pool_size += 26
            self.suggestions.append("✅ Có chữ cái viết hoa (N + 26)")
        else: 
            self.suggestions.append("❌ Thiếu chữ cái viết hoa (Giảm không gian mẫu)")
        
        if flags["has_digit"]: 
            pool_size += 10
            self.suggestions.append("✅ Có chứa chữ số (N + 10)")
        else: 
            self.suggestions.append("❌ Thiếu chữ số (Giảm không gian mẫu)")
        
        if flags["has_special"]: 
            pool_size += 32
            self.suggestions.append("✅ Có ký tự đặc biệt (N + 32)")
        else: 
            self.suggestions.append("❌ Thiếu ký tự đặc biệt (Giảm không gian mẫu)")
        
        if pool_size == 0:
            pool_size = 1  # Tránh lỗi log2(0)
            
        # 4. Áp dụng Công thức Entropy (H = L * log2(N))
        import math
        L = flags["length"]
        entropy = L * math.log2(pool_size)
        
        self.suggestions.append(f"🔍 Phân tích toán học cơ sở: L={L}, N={pool_size}, H_gốc={round(entropy, 2)} bits")
        
        # 5. Kiểm tra các lỗ hổng bảo mật (Penalty) từ Backend và Regex
        from .rules import check_repetition, check_dictionary_words
        
        penalty = 0
        repetition_issues = check_repetition(self.__password)
        if repetition_issues:
            for issue in repetition_issues:
                self.suggestions.append(f"❌ Lỗ hổng: {issue} (-15 bits)")
                penalty += 15
                
        dictionary_words = check_dictionary_words(self.__password)
        if dictionary_words:
            words_str = ", ".join(dictionary_words)
            self.suggestions.append(f"❌ Lỗ hổng: Chứa từ tiếng Anh dễ đoán '{words_str}' (-15 bits)")
            penalty += 15
            
        # 5.5. Thực thi các rule tùy chỉnh (Dependency Injection) từ *args
        if args:
            for custom_rule in args:
                if callable(custom_rule):
                    custom_issues = custom_rule(self.__password)
                    if custom_issues:
                        for issue in custom_issues:
                            self.suggestions.append(f"❌ Lỗ hổng (Custom): {issue} (-10 bits)")
                            penalty += 10
            
        final_entropy = entropy - penalty
        if final_entropy < 0:
            final_entropy = 0
            
        self.suggestions.append(f"🧮 Độ khó thực tế (Final Entropy): {round(final_entropy, 2)} bits")
        
        # Quy đổi Entropy ra thang điểm 100:
        # Tính base_score từ entropy GỐC (trước penalty), sau đó trừ điểm phạt
        # → đảm bảo penalty luôn làm giảm điểm, ngay cả khi entropy gốc > 100
        base_score = min(100, int(entropy))
        self.score = max(0, base_score - penalty)  # Mỗi penalty = 15 điểm bị trừ
        
        self.penalty = penalty  # Lưu lại để GUI biết có phạt hay không
        
        # 6. Phân loại mức độ bảo mật chuẩn quốc tế (Sử dụng ngưỡng điểm linh hoạt từ kwargs)
        if self.score < t_weak:
            self.strength_level = "Yếu"
            self.suggestions.append(f"💡 Mật khẩu dưới {t_weak} điểm rất dễ bị bẻ khóa. Hãy tăng cả chiều dài L và độ phức tạp N.")
        elif t_weak <= self.score < t_medium:
            self.strength_level = "Trung bình"
            self.suggestions.append(f"💡 Mức độ an toàn tạm ổn (từ {t_weak} đến dưới {t_medium} điểm), nhưng vẫn có thể bị tấn công Brute-force.")
        else:
            self.strength_level = "Mạnh"
            
    def get_password_feedback(self) -> dict:
        """
        Trả về kết quả đánh giá dưới dạng Dictionary để giao diện GUI dễ dàng xử lý.
        """
        return {
            "is_valid": self.is_valid,
            "score": self.score,
            "level": self.strength_level,
            "suggestions": self.suggestions,
            "has_penalty": hasattr(self, "penalty") and self.penalty > 0
        }
