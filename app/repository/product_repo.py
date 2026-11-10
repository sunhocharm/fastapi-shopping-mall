from typing import Any
from sqlmodel import select, delete, func, text
from sqlalchemy.orm import contains_eager, selectinload, joinedload
from sqlalchemy.exc import IntegrityError, DatabaseError
from sqlmodel.ext.asyncio.session import AsyncSession

from app.model.product_model import Product, Category, ProductImage
from app.schema.product_schema import ProductResponse, ProductWithOneThumbImage

from app.custom_exceptions import EntityAlreadyExistsError, EntityNotFoundError, CustomDatabaseError


class ProductRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session


    async def create_product(self, product_dict: dict[str, Any]) -> Product:
        db_product = Product.model_validate(product_dict)
        self.session.add(db_product)
        try:
            await self.session.commit()
        except (IntegrityError, DatabaseError) as err:
            await self.session.rollback()

            if isinstance(err, IntegrityError):
                raise EntityAlreadyExistsError("Database 참조 무결성 오류") from err

            raise CustomDatabaseError from err

        await self.session.refresh(db_product)
        return db_product


    async def create_product_with_files(
        self, 
        product_dict: dict[str, Any], 
        product_files_dict: list[dict[str, Any]] | None
    ) -> None:
        db_product = Product.model_validate(product_dict)
        self.session.add(db_product)
        await self.session.flush()

        new_product_id = db_product.id
        if product_files_dict and (len(product_files_dict) > 0):
            for product_file_dict in product_files_dict:
                product_file_dict["product_id"] = new_product_id
                db_product_file = ProductImage.model_validate(product_file_dict)
                self.session.add(db_product_file)

        try:
            await self.session.commit()
        except (IntegrityError, DatabaseError) as err:
            await self.session.rollback()

            if isinstance(err, IntegrityError):
                raise EntityAlreadyExistsError("Database 참조 무결성 오류") from err

            raise CustomDatabaseError from err


    async def update_product_with_files(
            self, 
            prev_product: Product, 
            product_dict: dict[str, Any], 
            product_files_dict: list[dict[str, Any]] | None
    ) -> None:
        db_product = prev_product.sqlmodel_update(product_dict)
        self.session.add(db_product)

        if product_files_dict and (len(product_files_dict) > 0):
            for product_file_dict in product_files_dict:
                db_product_file = ProductImage.model_validate(product_file_dict)
                self.session.add(db_product_file)

        try:
            await self.session.commit()
        except (IntegrityError, DatabaseError) as err:
            await self.session.rollback()

            if isinstance(err, IntegrityError):
                raise EntityAlreadyExistsError("Database 참조 무결성 오류") from err

            raise CustomDatabaseError from err


    async def update_product(self, prev_product: Product, product_dict: dict[str, Any]) -> None:
        db_product = prev_product.sqlmodel_update(product_dict)
        self.session.add(db_product)
        try:
            await self.session.commit()
        except (IntegrityError, DatabaseError) as err:
            await self.session.rollback()

            if isinstance(err, IntegrityError):
                raise EntityAlreadyExistsError("Database 참조 무결성 오류") from err

            raise CustomDatabaseError from err


    async def create_multiple_product_file_info(self, product_files_dict: list[dict[str, Any]]) -> None:
        for product_file_dict in product_files_dict:
            db_product_file = ProductImage.model_validate(product_file_dict)
            self.session.add(db_product_file)

        try:
            await self.session.commit()
        except (IntegrityError, DatabaseError) as err:
            await self.session.rollback()

            if isinstance(err, IntegrityError):
                raise EntityAlreadyExistsError("Database 참조 무결성 오류") from err

            raise CustomDatabaseError from err


    async def delete_product(self, prev_product: Product) -> None:
        await self.session.exec(delete(ProductImage).where(ProductImage.product_id == prev_product.id))

        await self.session.delete(prev_product)
        await self.session.commit()


    async def delete_product_file_info(self, image_id: int) -> tuple[str, str]:
        db_image_file = await self.session.get(ProductImage, image_id)
        if not db_image_file:
            raise EntityNotFoundError("Image file not found in DB")

        file_full_path = db_image_file.url
        thumbnail_file_full_path = db_image_file.thumb_url
        await self.session.delete(db_image_file)
        await self.session.commit()

        return (file_full_path, thumbnail_file_full_path)


    # ------------------------------------------------------- #
    # --- get all products ---------------------------------- #
    async def get_product_category_images_by_product_id(self, product_id: int) -> ProductResponse:
        statement = (
            select(Product)
            .where(Product.id == product_id)
            .options(
                joinedload(Product.category),  # 다대일 관계 -> 로우 증가 없음 (JOIN)
                selectinload(Product.images)   # 일대다 관계 -> 로우 증가 방지 (별도 SELECT)
            )
        )
        
        result = await self.session.exec(statement)
        # joinedload와 selectinload 조합은 결과 Row 중복을 만들지 않으므로 scalar_one_or_none() 바로 가능
        return  result.first() # result.scalar_one_or_none()        


    async def get_product_only_by_id(self, product_id: int) -> Product:
        return await self.session.get(Product, product_id)

    
    async def get_product_images_by_product_id(self, product_id: int) -> list[ProductImage]:
        return await self.session.exec(select(ProductImage).where(ProductImage.product_id == product_id))

    
    # async def get_product_by_id(self, product_id: int) -> ProductResponse:
    #     # return await self.session.get(Product, product_id)
    #     stmt = (
    #         select(Product)
    #         .join(Category, Product.category_id == Category.id)
    #         .join(ProductImage, ProductImage.product_id == Product.id, isouter=True)
    #         .where(Product.id == product_id)
    #         .options(contains_eager(Product.category), contains_eager(Product.images))
    #     )
    #     result = await self.session.exec(stmt)
    #     return result.unique().first()


    # async def get_count_for_all_products(
    #     self, 
    #     category_id: int | None = None,
    #     featured_only: bool | None = None,
    #     query: str | None = None, 
    # ) -> int:
    #     stmt = (
    #         select(Product)
    #     )

    #     if category_id:
    #         stmt = stmt.where(Product.category_id == category_id)

    #     if featured_only:
    #         stmt = stmt.where(Product.is_featured == True)

    #     if query:
    #         stmt = stmt.where(Product.name.contains(query) | Product.description.contains(query))

    #     count_statement = select(func.count()).select_from(stmt.subquery())
            
    #     # 3. 핵심 수정: session.exec() 결과 자체를 await하여 Result 객체를 먼저 얻은 후 .one()을 호출합니다.
    #     result = await self.session.exec(count_statement)
    #     return result.one()


    async def get_count_for_all_products(
        self, 
        category_id: int | None = None,
        featured_only: bool | None = None,
        query: str | None = None, 
    ) -> int:
        # 1. 기본 SELECT COUNT 쿼리 및 파라미터 딕셔너리 초기화
        # 서브쿼리 방식을 사용할 수도 있지만, 성능상 메인 쿼리에 직접 COUNT를 적용하는 것이 더 효율적입니다.
        base_sql = "SELECT COUNT(*) FROM products WHERE 1=1"
        conditions = []
        params = {}

        # 2. 조건별 Raw SQL 조각 및 파라미터 동적 추가
        if category_id:
            conditions.append("category_id = :category_id")
            params["category_id"] = category_id

        if featured_only:
            conditions.append("is_featured = TRUE")

        if query:
            # PostgreSQL의 ILIKE(대소문자 구분 없음)나 LIKE를 사용하며, % 와일드카드를 결합합니다.
            conditions.append("(name LIKE :query OR description LIKE :query)")
            params["query"] = f"%{query}%"

        # 3. 전체 SQL 문자열 결합
        if conditions:
            final_sql = f"{base_sql} AND " + " AND ".join(conditions)
        else:
            final_sql = base_sql

        # 4. text() 객체에 파라미터를 미리 묶어서 생성
        statement = text(final_sql).bindparams(**params)

        # 이제 인자가 1개(statement)만 넘어가므로 TypeError가 발생하지 않습니다.
        result = await self.session.exec(statement)
            
        # 5. 단일 카운트 값 반환
        return result.scalar_one()


    async def get_all_products(
        self, 
        category_id: int | None = None,
        featured_only: bool | None = None,
        query: str | None = None, 
        skip: int | None = None,
        limit: int | None = None
    ) -> list[ProductResponse]:
        """여러 상품 목록 조회 최적화 (2-Query 패턴)
        - Category: joinedload로 1번째 쿼리에 INNER JOIN으로 결합
        - Images: selectinload로 2번째 쿼리에 IN (...) 조건으로 분리 조회
        """

        stmt = (
            select(Product)
            .options(
                joinedload(Product.category, innerjoin=True),  # Category는 1:1이므로 JOIN (필수 카테고리라면 innerjoin=True 가능)
                selectinload(Product.images)   # Images는 1:N이므로 별도 배치를 통해 2번째 쿼리로 처리
            )
        )

        if category_id:
            stmt = stmt.where(Product.category_id == category_id)

        if featured_only:
            stmt = stmt.where(Product.is_featured == True)

        if query:
            stmt = stmt.where(Product.name.contains(query) | Product.description.contains(query))

        if skip:
            stmt = stmt.offset(skip)

        if limit:
            stmt = stmt.limit(limit)

        result = await self.session.exec(stmt)
        
        # joinedload+selectinload는 결과 집합 자체의 로우 중복을 발생시키지 않으므로 
        # 무거운 .unique() 연산 부담을 크게 줄이거나 생략할 수 있습니다.
        return result.all()
        # return result.unique().all()


    async def get_products_by_category_id(
        self, 
        category_id: int, 
        product_id: int | None = None, 
        limit: int | None = None
    ) -> list[ProductWithOneThumbImage]:
    
        # 1. 각 상품별로 첫 번째(가장 작은 ID) 이미지의 thumb_url을 가져오는 서브쿼리 생성
        thumb_subquery = (
            select(ProductImage.thumb_url)
            .where(ProductImage.product_id == Product.id)
            .order_by(ProductImage.sort_order.asc(), ProductImage.id.asc())
            .limit(1)
            .scalar_subquery()
        )

        # 2. 메인 쿼리: 상품 정보와 함께 위 서브쿼리 결과(thumb_url)를 한 번에 조회
        statement = (
            select(Product, thumb_subquery.label("thumb_url"))
            .where(Product.category_id == category_id, Product.id != 20)
        )
        if product_id:
            statement = statement.where(Product.id != product_id)

        if limit:
            statement = statement.limit(limit)
        
        result = await self.session.exec(statement)
        return result.all()
