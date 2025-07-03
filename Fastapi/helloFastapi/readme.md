# Hướng dẫn tạo dự án FastAPI đầu tiên

FastAPI là một framework web Python hiện đại, hiệu suất cao, giúp bạn xây dựng các API một cách nhanh chóng và dễ dàng. Dưới đây là các bước để tạo dự án đầu tiên của bạn.

### **Bước 1: Cài đặt các công cụ cần thiết**

Trước tiên, bạn cần đảm bảo đã cài đặt Python và trình quản lý gói `pip`.

1.  **Cài đặt Python:** Nếu chưa có, hãy tải và cài đặt phiên bản Python mới nhất (từ 3.7 trở lên) từ trang chủ [python.org](https://www.python.org/downloads/).
    *Lưu ý: Khi cài đặt trên Windows, hãy nhớ tick vào ô "Add Python to PATH".*

2.  **Kiểm tra Python và pip:** Mở Terminal (trên macOS/Linux) hoặc Command Prompt/PowerShell (trên Windows) và chạy các lệnh sau để kiểm tra:
    ```bash
    python --version
    pip --version
    ```
    Nếu các lệnh này trả về phiên bản tương ứng, bạn đã sẵn sàng.

### **Bước 2: Tạo môi trường ảo (Virtual Environment)**

Đây là một bước rất quan trọng và được khuyến khích để mỗi dự án có một môi trường riêng, tránh xung đột thư viện.

1.  Tạo một thư mục mới cho dự án của bạn và di chuyển vào đó:
    ```bash
    mkdir du-an-fastapi
    cd du-an-fastapi
    ```

2.  Tạo một môi trường ảo bên trong thư mục dự án:
    ```bash
    python -m venv venv
    ```
    Lệnh này sẽ tạo một thư mục con tên là `venv`.

3.  Kích hoạt môi trường ảo:
    * **Trên Windows:**
        ```bash
        .\venv\Scripts\activate
        ```
    * **Trên macOS và Linux:**
        ```bash
        source venv/bin/activate
        ```
    Sau khi kích hoạt, bạn sẽ thấy tên môi trường ảo `(venv)` xuất hiện ở đầu dòng lệnh.

### **Bước 3: Cài đặt FastAPI và Uvicorn**

Bên trong môi trường ảo đã được kích hoạt, hãy cài đặt FastAPI và Uvicorn (một máy chủ ASGI để chạy ứng dụng của bạn).

```bash
pip install fastapi "uvicorn[standard]"
```
* `fastapi`: Là chính framework FastAPI.
* `uvicorn[standard]`: Là máy chủ web (server) để chạy ứng dụng của bạn. Gói `standard` cung cấp hiệu suất tốt hơn và các tính năng hữu ích.

### **Bước 4: Viết mã FastAPI đầu tiên**

Bây giờ, hãy tạo một tệp tin Python, ví dụ là `main.py`, trong thư mục dự án của bạn và thêm đoạn mã sau:

**`main.py`**
```python
from fastapi import FastAPI

# 1. Tạo một đối tượng FastAPI
app = FastAPI()

# 2. Định nghĩa một "path operation" (đường dẫn và phương thức)
@app.get("/")
def read_root():
    # 3. Trả về một JSON response
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
```

**Giải thích mã:**
* **`from fastapi import FastAPI`**: Import lớp FastAPI.
* **`app = FastAPI()`**: Tạo một instance (thể hiện) của lớp FastAPI. Đây sẽ là điểm tương tác chính để tạo tất cả các API của bạn.
* **`@app.get("/")`**: Đây được gọi là "decorator". Nó nói với FastAPI rằng hàm `read_root()` bên dưới sẽ xử lý các yêu cầu gửi đến đường dẫn (`path`) là `/` bằng phương thức (`method`) `GET`.
* **`def read_root(): ...`**: Hàm xử lý yêu cầu. Nội dung bạn trả về (ở đây là một dictionary) sẽ được FastAPI tự động chuyển đổi thành định dạng JSON.
* **`@app.get("/items/{item_id}")`**: Một ví dụ khác về path operation với tham số đường dẫn (`item_id`) và tham số truy vấn (`q`). FastAPI sẽ tự động xác thực kiểu dữ liệu cho bạn.

### **Bước 5: Chạy ứng dụng**

Quay lại cửa sổ dòng lệnh (với môi trường ảo vẫn đang được kích hoạt), hãy chạy máy chủ Uvicorn:

```bash
uvicorn main:app --reload
```

**Giải thích lệnh:**
* `main`: Tên tệp tin Python của bạn (`main.py`).
* `app`: Đối tượng FastAPI bạn đã tạo bên trong tệp `main.py` (`app = FastAPI()`).
* `--reload`: Tùy chọn này giúp máy chủ tự động khởi động lại mỗi khi bạn thay đổi mã nguồn, rất hữu ích trong quá trình phát triển.

Sau khi chạy lệnh, bạn sẽ thấy output tương tự như sau:
```
INFO:     Uvicorn running on [http://127.0.0.1:8000](http://127.0.0.1:8000) (Press CTRL+C to quit)
INFO:     Started reloader process [28720]
INFO:     Started server process [28722]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### **Bước 6: Kiểm tra API**

Bây giờ, ứng dụng của bạn đã hoạt động! Hãy mở trình duyệt và truy cập các địa chỉ sau:

1.  **Truy cập API gốc:**
    * Mở: `http://127.0.0.1:8000`
    * Bạn sẽ thấy response JSON: `{"Hello":"World"}`

2.  **Truy cập API với tham số:**
    * Mở: `http://127.0.0.1:8000/items/5?q=somequery`
    * Bạn sẽ thấy: `{"item_id":5,"q":"somequery"}`

### **Bước 7: Khám phá tài liệu API tự động**

FastAPI tự động tạo tài liệu API tương tác cho bạn. Đây là một trong những tính năng mạnh mẽ nhất.

> #### **Swagger UI**
> Mở: `http://127.0.0.1:8000/docs`
>
> Bạn sẽ thấy một giao diện người dùng tương tác, nơi bạn có thể xem tất cả các endpoint, tham số và thậm chí là gửi yêu cầu để kiểm thử trực tiếp trên trình duyệt.

> #### **ReDoc**
> Mở: `http://127.0.0.1:8000/redoc`
>
> Một giao diện tài liệu thay thế, tập trung vào việc hiển thị.

---
Chúc mừng! Bạn đã tạo và chạy thành công dự án FastAPI đầu tiên của mình.
