from loguru import logger
from typing import Any

from sqlalchemy.orm import joinedload, selectinload, contains_eager, noload
from sqlalchemy.exc import DatabaseError
from sqlmodel import select, delete
from sqlmodel.ext.asyncio.session import AsyncSession
from app.model.cart_model import Cart, CartItem
from app.model.product_model import Product
from app.schema.cart_schema import CartItemResponse, CartOnlyResponse, CartResponse

from app.custom_exceptions import CustomDatabaseError, EntityNotFoundError


class CartRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session


    async def clear_cart(self, user_id: int) -> None:
        db_cart = await self.session.exec(select(Cart).where(Cart.user_id == user_id))
        db_cart = db_cart.first()
        if db_cart:
            await self.session.exec(delete(CartItem).where(CartItem.cart_id == db_cart.id))
            await self.session.delete(db_cart)
            await self.session.commit()


    async def get_product_only_by_product_id(self, product_id: int) -> Product | None:
        return await self.session.get(Product, product_id)


    async def update_cart_item_qty(self,  prev_cartitem: CartItem, quantity: int) -> None:
        prev_cartitem.quantity = quantity
        self.session.add(prev_cartitem)
        await self.session.commit()


    async def delete_cart_item(self, prev_cartitem: CartItem) -> None:
        await self.session.delete(prev_cartitem)
        await self.session.commit()
    
    
    async def get_cartitem_by_cartitem_id(self, cartitem_id: int) -> CartItem | None:
        return await self.session.get(CartItem, cartitem_id)


    async def get_cart_by_user_id(self, user_id: int) -> Cart | None:
        logger.info("\n\n\t시작: get_cart_by_user_id in CartRepository\n")

        result = await self.session.exec(
            select(Cart)
            .options(
                selectinload(Cart.items)
                .joinedload(CartItem.product, innerjoin=True)
                .selectinload(Product.images),
                # 2. Cart의 user 정보도 함께 비동기로 미리 로드
                # 위에 콤마를 넣어서 연쇄를 막는다(핵심)
                # joinedload(Cart.user, innerjoin=True)                 
            )
            .where(Cart.user_id == user_id)
        )
        logger.info("\n\n\t끝: get_cart_by_user_id in CartRepository\n\n\n")
        return result.first()


    async def get_cart_by_cart_session_id(self, cart_session_id: str) -> Cart | None:
        result = await self.session.exec(
            select(Cart)
            .options(selectinload(Cart.items))
            .where(Cart.session_id == cart_session_id)
        )
        return result.first()


    async def _create_cart(self, user_id_in_session: int, session_id: str) -> Cart:
        # cart = {"user_id": user_id_in_session, "session_id": session_id}
        # db_cart = Cart.model_validate(cart)
        db_cart = Cart(user_id=user_id_in_session, session_id=session_id)
        self.session.add(db_cart)
        await self.session.flush()
        return db_cart


    async def _update_cart_user_id(self, prev_cart: Cart, user_id_in_session: str) -> None:
        prev_cart.user_id = user_id_in_session
        self.session.add(prev_cart)


    async def _update_cart_item(self, prev_cart_item: CartItem, quantity: int) -> None:
        prev_cart_item.quantity += quantity
        self.session.add(prev_cart_item)


    async def _create_cart_item(self, cart_id: int, product_id: int, quantity: int) -> None:
        cart_item = {"cart_id": cart_id, "product_id": product_id, "quantity": quantity}
        db_cart_item = CartItem.model_validate(cart_item)
        self.session.add(db_cart_item)


    async def create_or_update_cart(
        self, 
        prev_cart: Cart | None, 
        prev_cart_item: CartItem | None, 
        user_id_in_session: int | None, 
        session_id_hashed: str,
        cart_req_dict: dict[str, Any]   # {"product_id": 1234, "quantity": 2}
    ) -> Cart:
        product_id = cart_req_dict.get("product_id", None)
        quantity = cart_req_dict.get("quantity", None)
        if prev_cart:
            if (not prev_cart.user_id) and (user_id_in_session):
                await self._update_cart_user_id(prev_cart, user_id_in_session)

        if not prev_cart:
            prev_cart = await self._create_cart(user_id_in_session, session_id_hashed)

        if prev_cart_item:
            await self._update_cart_item(prev_cart_item, quantity)
        else:
            await self._create_cart_item(prev_cart.id, product_id, quantity)

        try:
            await self.session.commit()
        except (DatabaseError) as err:
            await self.session.rollback()
            logger.error(err)
            raise CustomDatabaseError

        await self.session.refresh(prev_cart, attribute_names=["items"])
        return prev_cart


    # -----------------------------------------------------------------------------------------#
    # non login 상태의 cart ==> login 상태의 cart 로 변환
    # 로그인 직후에 호출된다. from auth_router: login
    async def process_non_login_cart(self, user_id: int, session_id_hashed: str) -> None:
        result = await self.session.exec(select(Cart).where(Cart.session_id == session_id_hashed))
        prev_cart = result.first()
        if not prev_cart:
            logger.error("\n\nERROR: non login cart 전환 실패 (session_id not found)\n\n")

        prev_cart.user_id = user_id
        self.session.add(prev_cart)
        await self.session.commit()


    async def get_cart_only_by_user_id(self, user_id: int) -> Cart | None:
        result = await self.session.exec(select(Cart).where(Cart.user_id == user_id))
        return result.first()


    async def get_cart_only_by_session_id(self, session_id: str) -> Cart | None:
        result = await self.session.exec(select(Cart).where(Cart.session_id == session_id))
        return result.first()


    async def get_cart_item_only(self, cart_id: int, product_id: int) -> CartItem | None:
        result = await self.session.exec(
            select(CartItem)
            .where(CartItem.cart_id == cart_id, CartItem.product_id == product_id)
        )
        return result.first()
