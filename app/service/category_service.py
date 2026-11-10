from typing import Any

from ..repository.category_repo import CategoryRepository
from ..model.product_model import Category

from app.custom_exceptions import EntityAlreadyExistsError, EntityNotFoundError


class CategoryService:
    def __init__(self, repo: CategoryRepository) -> None:
        self.repo = repo


    async def create_category(self, req_dict: dict[str, Any]) -> None:
        db_category_by_slug = await self.repo.get_category_by_slug(req_dict.get("slug"))
        if db_category_by_slug:
            raise EntityAlreadyExistsError("slug 값이 이미 사용 중입니다.")

        await self.repo.create_category(req_dict)


    async def update_category(self, category_id, req_dict: dict[str, Any]) -> None:
        db_category = await self.repo.get_category_by_id(category_id)
        if not db_category:
            raise EntityNotFoundError("Category Not Found")

        in_slug = req_dict.get("slug")
        if db_category.slug != in_slug:
            db_category_by_slug = await self.repo.get_category_by_slug(in_slug)
            if db_category_by_slug:
                raise EntityAlreadyExistsError("slug 값이 이미 사용 중입니다.")

        await self.repo.update_category(db_category, req_dict)


    async def delete_category(self, category_id: int) -> None:
        db_category = await self.repo.get_category_by_id(category_id)
        if not db_category:
            # raise EntityNotFoundError("Category Not Found")
            return None

        await self.repo.delete_category(db_category)


    async def get_category_by_id(self, category_id: int) -> Category:
        return await self.repo.get_category_by_id(category_id)


    async def get_all_categories(self, active_only: bool = False) -> list[Category]:
        result = await self.repo.get_all_categories(active_only=False)
        return result
