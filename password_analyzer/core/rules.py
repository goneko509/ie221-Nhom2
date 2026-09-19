def analyze_password_complexity(password: str, special_chars_set: str = "!@#$%^&*()-=+./") -> dict:
    """
    Phân tích độ phức tạp của mật khẩu chỉ với một lần duyệt (One-pass algorithm - O(N)).
    Sử dụng kỹ thuật Cờ hiệu (Flags Pattern) để ghi nhận trạng thái.
    
    Trả về một từ điển chứa các thông tin:
    - has_lower: Có chứa chữ cái thường (a-z)
    - has_upper: Có chứa chữ cái hoa (A-Z)
    - has_digit: Có chứa chữ số (0-9)
    - has_special: Có chứa ký tự đặc biệt
    - length: Chiều dài của mật khẩu
    """
    flags = {
        "has_lower": False,
        "has_upper": False,
        "has_digit": False,
        "has_special": False,
        "length": len(password)
    }
    
    for char in password:
        if 'a' <= char <= 'z':
            flags["has_lower"] = True
        elif 'A' <= char <= 'Z':
            flags["has_upper"] = True
        elif '0' <= char <= '9':
            flags["has_digit"] = True
        elif char in special_chars_set:
            flags["has_special"] = True
            
    return flags

import re
import requests

def check_repetition(password: str) -> list:
    """
    Quét và tìm các chuỗi lặp (Pattern Repetition).
    Ví dụ: 'aaa', '111', 'abcabc'
    Trả về danh sách mô tả lỗi, bao gồm chuỗi lặp thực tế tìm thấy.
    """
    issues = []
    
    # Regex 1: Ký tự lặp liền kề 3 lần trở lên (vd: aaa, 111)
    m1 = re.search(r'(.)\1{2,}', password)
    if m1:
        repeated_seq = m1.group(0)  # Ví dụ: 'aaa', '1111'
        issues.append(f"Phát hiện ký tự lặp liền kề '{repeated_seq}'")
        
    # Regex 2: Cụm 2-4 ký tự lặp lại liên tiếp (vd: abcabc)
    m2 = re.search(r'(.{2,4})\1{1,}', password)
    if m2:
        repeated_seq = m2.group(0)  # Ví dụ: 'abcabc', '1212'
        issues.append(f"Phát hiện chuỗi tuần hoàn '{repeated_seq}'")
        
    return issues

def check_dictionary_words(password: str) -> list:
    """
    Trích xuất tất cả các chuỗi chứa từ 5 chữ cái (a-z, A-Z) liên tiếp trở lên trong mật khẩu.
    Gọi Backend API (Localhost) để tra cứu từ điển O(1).
    Ví dụ: 'myanimals123' -> trích xuất 'myanimals', gọi API kiểm tra.
    """
    found_words = set()
    
    # Dùng regex để tìm tất cả các cụm từ chỉ toàn chữ cái, độ dài >= 5
    potential_words = re.findall(r'[a-zA-Z]{5,}', password)
    
    if not potential_words:
        return list(found_words)
        
    try:
        for word in potential_words:
            # Gọi API nội bộ, timeout 0.5s để tránh freeze GUI nếu lag
            response = requests.get(f"http://127.0.0.1:8000/api/check_pattern?word={word}", timeout=0.5)
            if response.status_code == 200:
                data = response.json()
                if data.get("is_dictionary_word"):
                    for w in data.get("words", []):
                        found_words.add(w)
    except requests.exceptions.RequestException:
        # Bỏ qua âm thầm nếu Backend chưa được bật (Graceful Degradation)
        pass
        
    return list(found_words)
