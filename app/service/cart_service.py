from loguru import logger
from typing import Any
from app.repository.cart_repo import CartRepository

from app.model.cart_model import Cart, CartItem

from app.custom_exceptions import CustomBadRequestError
from .cart_validation_error import CartValidationError


class CartService:
    def __init__(self, repo: CartRepository) -> None:
        self.repo = repo


    async def clear_cart(self, user_id: int) -> None:
        await self.repo.clear_cart(user_id)


    async def validate_cart_items(self, cart: Cart) -> None:
        errors = []

        for item in cart.items:
            product = await self.repo.get_product_only_by_product_id(item.product_id)
            if not product:
                errors.append({
                    "item_id": item.id, "message": f"'{item.product.name}' 상품이 존재하지 않습니다"
                })
                continue

            if not product.is_active:
                errors.append({
                    "item_id": item.id, "message": f"'{product.name}' 상품이 판매 중지되었습니다"
                })
                continue

            if product.stock < item.quantity:
                errors.append({
                    "item_id": item.id, "message": f"'{product.name}' 재고가 부족합니다 (재고: {product.stock}개)"
                })

        if errors:
            raise CartValidationError(errors)


    async def update_cart_item_qty(self,  cartitem_id: int, quantity: int) -> None:
        prev_cartitem = await self.repo.get_cartitem_by_cartitem_id(cartitem_id)
        if not prev_cartitem:
            raise CustomBadRequestError("CartItem Not Found")

        if quantity <= 0:
            return await self.repo.delete_cart_item(prev_cartitem)

        await self.repo.update_cart_item_qty(prev_cartitem, quantity)


    async def get_current_cart(self, user_id: int | None, cart_session_id: str | None) -> Cart | None:
        logger.info("\n\n\t시작: get_current_cart in CartService\n")
        cart = None
        if user_id:
            cart = await self.repo.get_cart_by_user_id(user_id)
        elif cart_session_id:
            cart = await self.repo.get_cart_by_cart_session_id(user_id)

        logger.info("\n\n\t끝: get_current_cart in CartService\n\n\n")

        return cart
    
    
    async def get_or_update_or_create_cart(
        self, 
        user_id_in_session: int | None, 
        session_id_hashed: str,
        cart_req_dict: dict[str, Any]   # {"product_id": 1234, "quantity": 2}
    ) -> Cart:
        """장바구니 조회 또는 생성"""
        product_id = cart_req_dict.get("product_id", None)

        db_cart = None
        db_cart_item = None
        if user_id_in_session:
            cart_by_user_id = await self.repo.get_cart_only_by_user_id(user_id_in_session)
            if cart_by_user_id:
                db_cart = cart_by_user_id


        if db_cart:
            if db_cart.session_id != session_id_hashed:
                raise CustomBadRequestError("check session_id for cart")
        else:
            cart_by_session_id = await self.repo.get_cart_only_by_session_id(session_id_hashed)
            if cart_by_session_id:
                db_cart = cart_by_session_id

        if db_cart:
            db_cart_item = await self.repo.get_cart_item_only(db_cart.id, product_id)

        db_cart_new = await self.repo.create_or_update_cart(db_cart, db_cart_item, user_id_in_session, session_id_hashed, cart_req_dict)
        return db_cart_new


    # -----------------------------------------------------------------------------------------#
    # non login 상태의 cart ==> login 상태의 cart 로 변환
    # 로그인 직후에 호출된다. from auth_router: login
    async def process_non_login_cart(self, user_id: int, session_id_hashed: str) -> None:
        await self.repo.process_non_login_cart(user_id, session_id_hashed)


    # async def def add_to_cart(
    #     session: Session,
    #     cart: Cart,
    #     product_id: int,
    #     quantity: int = 1
    # ) -> CartItem:
    #     """장바구니에 상품 추가"""
    #     # 이미 담긴 상품인지 확인
    #     statement = select(CartItem).where(
    #         CartItem.cart_id == cart.id,
    #         CartItem.product_id == product_id
    #     )
    #     item = session.exec(statement).first()
    #     if item:
    #         # 수량 추가
    #         item.quantity += quantity
    #     else:
    #         # 새로 추가
    #         item = CartItem(
    #             cart_id=cart.id,
    #             product_id=product_id,
    #             quantity=quantity
    #         )
    #         session.add(item)
    #     # 장바구니 업데이트 시간
    #     cart.updated_at = datetime.now()
    #     session.add(cart)
    #     session.commit()
    #     session.refresh(item)
    #     return item
