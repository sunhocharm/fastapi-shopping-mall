import asyncio
from sqlmodel import delete
# from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import engine, AsyncSessionLocal
from app.model.user_model import User, UserRole
from app.model.product_model import Category
from app.util.auth_util import hash_password

# 시드 데이터
categories = [
    {"name": "의류", "slug": "clothing", "description": "의류", "sort_order": 1},
    {"name": "전자제품", "slug": "electronics", "description": "전자제품", "sort_order": 2},
    {"name": "도서", "slug": "books", "description": "도서", "sort_order": 3},
    {"name": "식품", "slug": "food", "description": "식품", "sort_order": 4},
]

admins = [
    {
        "email": "sunho.park@gmail.com",
        "name": "sunho",
        "phone": "01052118935,",
        "role": UserRole.ADMIN, 
        "password": "11111"
    },
    {
        "email": "funnyworld9.park@gmail.com",
        "name": "Sunho Park",
        "phone": "01052118935,",
        "role": UserRole.ADMIN, 
        "password": "22222"
    }

]
async def clear_admin_user():
    async with AsyncSessionLocal() as session:
        await session.exec(delete(User).where(User.role == UserRole.ADMIN))
        await session.exec(delete(Category))
        await session.commit()
    print("\n\nDone: cleared Database data\n\n")

async def create_admin_user():
    async with AsyncSessionLocal() as session:
        for user in admins:
            user["hashed_password"] = hash_password(user["password"])
            session.add(User.model_validate(user))
        await session.commit()
        print("\n\nDone: created Database data (User)\n\n")

        for category in categories:
            session.add(Category.model_validate(category))
        await session.commit()
        print("\n\nDone: created Database data (Category)\n\n")


async def populate_admin_data():
    await clear_admin_user()
    await create_admin_user()


if __name__ == "__main__":
    asyncio.run(populate_admin_data())
