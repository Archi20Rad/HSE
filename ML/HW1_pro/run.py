import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app:app",  # Указываем путь к приложению: "имя_файла:имя_экземпляра_FastAPI"
        host="127.0.0.1",  
        port=8001,     
        reload=True      # Перезагрузка при изменении кода
    )
