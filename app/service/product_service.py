from typing import Any

from app.repository.product_repo import ProductRepository
from app.model.product_model import Product, ProductImage
from app.schema.product_schema import ProductResponse, ProductWithOneThumbImage

from app.custom_exceptions import EntityNotFoundError


class ProductService:
    def __init__(self, repo: ProductRepository) -> None:
        self.repo = repo


    async def create_product(self, product_dict: dict[str, Any]) -> Product:
        return await self.repo.create_product(product_dict)


    async def update_product(self, product_id: int, product_dict: dict[str, Any]) -> None:
        db_product = await self.repo.get_product_only_by_id(product_id)
        if not db_product:
            raise EntityNotFoundError("Product not found")

        await self.repo.update_product(db_product, product_dict)


    async def create_multiple_product_file_info(self, product: Product, final_saved_paths: list[tuple[str, str]]) -> None:
        product_files_dict = []
        for saved_path in final_saved_paths:
            product_file_dict = {
                "url": saved_path[0], "thumb_url": saved_path[1], "alt": f"{product.name} Image", "product_id": product.id, "sort_order": 0
            }
            product_files_dict.append(product_file_dict)

        await self.repo.create_multiple_product_file_info(product_files_dict)


    async def create_product_with_files(
        self, 
        product_dict: dict[str, Any], 
        final_saved_paths: list[tuple[str, str]] | None
    ) -> None:
        product_files_dict = []
        if final_saved_paths and (len(final_saved_paths) > 0):
            for saved_path in final_saved_paths:
                product_file_dict = { 
                    "url": saved_path[0], "thumb_url": saved_path[1], "alt": f"{product_dict["name"]} Image", "sort_order": 0
                }
                product_files_dict.append(product_file_dict)

        await self.repo.create_product_with_files(product_dict, product_files_dict)


    async def update_product_with_files(
        self, 
        product: Product, 
        product_dict: dict[str, Any], 
        final_saved_paths: list[tuple[str, str]] | None
    ) -> None:
        product_files_dict = []
        if final_saved_paths and (len(final_saved_paths) > 0):
            for saved_path in final_saved_paths:
                product_file_dict = { 
                    "url": saved_path[0], "thumb_url": saved_path[1], "alt": f"{product.name} Image", "product_id": product.id, "sort_order": 0
                }
                product_files_dict.append(product_file_dict)

        await self.repo.update_product_with_files(product, product_dict, product_files_dict)


    async def delete_product_file(self, product_id: int, image_id: int) -> tuple[str,str]:
        db_product = await self.repo.get_product_only_by_id(product_id)
        if not db_product:
            raise EntityNotFoundError("Product not found")

        return await self.repo.delete_product_file_info(image_id)


    async def delete_product(self, product_id: int) -> None:
        db_product = await self.repo.get_product_only_by_id(product_id)
        if not db_product:
            raise EntityNotFoundError("Product not found")

        await self.repo.delete_product(db_product)


    async def get_product_category_images_by_product_id(self, product_id: int) -> ProductResponse:
        return await self.repo.get_product_category_images_by_product_id(product_id)


    async def get_product_only_by_id(self, product_id: int) -> Product:
        product = await self.repo.get_product_only_by_id(product_id)
        if not product:
            raise EntityNotFoundError("Product not found")
        return product

    
    async def get_product_images_by_product_id(self, product_id: int) -> list[ProductImage]:
        return await self.repo.get_product_images_by_product_id(product_id)

    async def get_count_for_all_products(
        self, 
        category_id: int | None = None,
        featured_only: bool | None = None,
        query: str | None = None, 
    ) -> int:
        return await self.repo.get_count_for_all_products(category_id, featured_only, query)


    async def get_all_products(
        self, 
        category_id: int | None = None,
        featured_only: bool | None = None,
        query: str | None = None, 
        skip: int | None = None,
        limit: int | None = None
    ) -> list[ProductResponse]:
        products = await self.repo.get_all_products(category_id, featured_only, query, skip, limit)
        return products


    async def get_products_by_category_id(
        self, 
        category_id: int, 
        product_id: int | None = None, 
        limit: int | None = None
    ) -> list[ProductWithOneThumbImage]:

        products = await self.repo.get_products_by_category_id(category_id, product_id, limit)
        return products
