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