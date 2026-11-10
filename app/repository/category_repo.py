from typing import Any

from sqlmodel import select
from sqlalchemy.exc import DatabaseError, IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession
from ..model.product_model import Category

from app.custom_exceptions import CustomDatabaseError, EntityAlreadyExistsError


class CategoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session


    async def create_category(self, category_dict: dict[str, Any]) -> None:
        db_category = Category.model_validate(category_dict)
        self.session.add(db_category)
        try:
            await self.session.commit()
        except (IntegrityError, DatabaseError) as err:
            await self.session.rollback()

            if isinstance(err, IntegrityError):
                raise EntityAlreadyExistsError("Database 참조 무결성 오류") from err

            raise CustomDatabaseError from err


    async def update_category(self, db_category: Category, category_dict: dict[str, Any]) -> None:
        updated_category = db_category.sqlmodel_update(category_dict)
        self.session.add(updated_category)
        try:
            await self.session.commit()
        except (IntegrityError, DatabaseError) as err:
            await self.session.rollback()

            if isinstance(err, IntegrityError):
                raise EntityAlreadyExistsError("Database 참조 무결성 오류") from err

            raise CustomDatabaseError from err


    async def delete_category(self, prev_category: Category) -> None:
        await self.session.delete(prev_category)
        await self.session.commit()


    async def get_category_by_slug(self, slug_value: str) -> Category:
        result = await self.session.exec(select(Category).where(Category.slug == slug_value))
        return result.first()


    async def get_category_by_id(self, category_id: int) -> Category:
        return await self.session.get(Category, category_id)


    async def get_all_categories(self, active_only: bool = False) -> list[Category]:
        stmt = (select(Category).order_by(Category.sort_order))
        if active_only:
            stmt = stmt.where(Category.is_active == True)
        result = await self.session.exec(stmt)
        return result.all()
