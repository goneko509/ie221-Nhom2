import os
import requests
from fastapi import FastAPI
from contextlib import asynccontextmanager

# Cấu hình nguồn từ điển: Sử dụng bộ 10,000 từ phổ biến của Google
# DICTIONARY_URL = "https://raw.githubusercontent.com/first20hours/google-10000-english/master/google-10000-english.txt"
# DICTIONARY_FILE = "backend/google-10000-english.txt"
DICTIONARY_URL = "https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt"
DICTIONARY_FILE = "backend/words_alpha.txt"


# Cấu trúc dữ liệu Set() cho phép tra cứu (lookup) với tốc độ siêu tốc độ O(1)
english_words = set()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Server lifecycle (Startup and Shutdown)
    """
    # ================= STARTUP =================
    print("\n[+] Starting Local Backend: Loading dictionary (Dictionary API)...")
    
    # 1. Download from GitHub if not cached locally (first run)
    if not os.path.exists(DICTIONARY_FILE):
        print("[+] Downloading dictionary from GitHub (first time)...")
        os.makedirs("backend", exist_ok=True)
        try:
            response = requests.get(DICTIONARY_URL)
            if response.status_code == 200:
                with open(DICTIONARY_FILE, "w", encoding="utf-8") as f:
                    f.write(response.text)
                print("[+] Download successful!")
            else:
                print("[-] Failed to download dictionary. Check network.")
        except Exception as e:
            print(f"[-] Internet connection error: {str(e)}")
    
    # 2. Load dictionary from disk into RAM
    if os.path.exists(DICTIONARY_FILE):
        with open(DICTIONARY_FILE, "r", encoding="utf-8") as f:
            for line in f:
                word = line.strip().lower()
                if len(word) >= 4: 
                    english_words.add(word)
        print(f"[+] Loaded {len(english_words)} words into RAM (Set).\n")
    
    yield # Allow Server to run
    
    # ================= SHUTDOWN =================
    print("\n[-] Shutting down Backend. Freeing RAM...")
    english_words.clear()

# Khởi tạo Web Framework FastAPI
app = FastAPI(lifespan=lifespan)

@app.get("/api/check_pattern")
def check_pattern(word: str):
    """
    Endpoint nhận chuỗi chữ cái (vd: Vienanimals) và tự động dùng Sliding Window
    trên RAM để tìm ra TẤT CẢ các từ tiếng Anh (>= 5 ký tự) nằm ẩn bên trong nó.
    """
    word_lower = word.lower()
    found = []
    
    length = len(word_lower)
    # Trượt cửa sổ tìm từ dài nhất trước (ưu tiên các từ có nghĩa dài)
    for window_size in range(length, 4, -1):
        for i in range(length - window_size + 1):
            sub = word_lower[i:i+window_size]
            if sub in english_words:
                found.append(sub)
                
    if found:
        # Lọc trùng lặp bằng set()
        return {"is_dictionary_word": True, "words": list(set(found))}
    
    return {"is_dictionary_word": False, "words": []}

@app.get("/api/status")
def status():
    """
    API Ping để kiểm tra trạng thái hoạt động của Backend
    """
    return {
        "status": "running",
        "words_loaded": len(english_words)
    }
