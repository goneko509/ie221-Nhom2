from .exceptions import EmptyPasswordError, LengthError

def validate_not_empty(password: str) -> bool:
    """
    Kiểm tra chuỗi đầu vào không được rỗng hoặc chỉ chứa khoảng trắng.
    """
    if not password or not password.strip():
        raise EmptyPasswordError("Mật khẩu không được để trống hoặc chỉ chứa khoảng trắng.")
    return True

def validate_length_bounds(password: str, min_len: int = 6, max_len: int = 24) -> bool:
    """
    Kiểm tra độ dài mật khẩu có nằm trong giới hạn cho phép hay không.
    Mặc định theo chuẩn của nhóm: 6-24 ký tự.
    """
    if not (min_len <= len(password) <= max_len):
        raise LengthError(f"Độ dài mật khẩu phải từ {min_len} đến {max_len} ký tự.")
    return True
