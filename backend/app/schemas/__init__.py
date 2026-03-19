"""
📋 PYDANTIC SCHEMAS (валидация данных)
==================================================
Разделение: Create (вход) → Public (выход ORM→JSON)

🎯 ЦЕЛЬ: Валидация JSON → Python objects
✅ Backend A: UserCreate/Public
⏳ Backend B: ThemeCreate/Public  
⏳ Backend C: RequestCreate/Public

🔧 ИСПОЛЬЗОВАНИЕ:
class ThemeCreate(BaseModel):
    title: str
    datetime: datetime

theme_data = ThemeCreate(**request.json())  # Авто валидация!
theme = Theme(**theme_data.dict())

🚀 ORM → JSON:
class ThemePublic(BaseModel):
    class Config:
        from_attributes = True  # SQLAlchemy → Pydantic

ThemePublic.from_orm(theme)  # → JSON response
"""
