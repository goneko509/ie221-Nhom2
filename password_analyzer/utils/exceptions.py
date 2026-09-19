class PasswordValidationError(Exception):
    """Lớp ngoại lệ cơ bản cho các lỗi xác thực mật khẩu."""
    pass

class LengthError(PasswordValidationError):
    """Ngoại lệ khi mật khẩu vi phạm quy tắc về độ dài."""
    pass

class ComplexityError(PasswordValidationError):
    """Ngoại lệ khi mật khẩu không đáp ứng đủ các quy tắc về độ phức tạp (thiếu chữ hoa, số, ký tự đặc biệt...)."""
    pass

class EmptyPasswordError(PasswordValidationError):
    """Ngoại lệ khi mật khẩu bị bỏ trống."""
    pass
