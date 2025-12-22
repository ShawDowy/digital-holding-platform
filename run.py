import uvicorn

if __name__ == "__main__":
    print("🚀 Запуск цифровой платформы холдинга...")
    print("🌐 Откройте в браузере: http://localhost:8000")
    print("🔑 Тестовые аккаунты:")
    print("   - Admin: admin / admin")
    print("   - Manager: manager / manager")
    print("   - Operator: operator / operator")
    
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

