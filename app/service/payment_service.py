from typing import Any
import httpx
import base64
from app.config import settings

from app.repository.payment_repo import PaymentRepository
from app.schema.payment_schema import PaymentCreate
from app.model.order_model import OrderStatus


class PaymentService:
    def __init__(self, repo: PaymentRepository) -> None:
        self.repo = repo
        self.toss_api_url = "https://api.tosspayments.com/v1"


    def get_auth_header(self) -> dict[str, Any]:
        """인증 헤더 생성"""
        credentials = f"{settings.toss_secret_key.get_secret_value()}:"
        encoded = base64.b64encode(credentials.encode()).decode()
        return {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/json"
        }


    async def confirm_payment(self, payment_key: str, order_id: str, amount: int) -> dict[str, Any]:
        """
        결제 승인
        https://docs.tosspayments.com/reference#결제-승인
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=f"{self.toss_api_url}/payments/confirm",
                headers=self.get_auth_header(),
                json={ "paymentKey": payment_key, "orderId": order_id, "amount": amount }
            )

            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": response.json()}


    async def cancel_payment(self, payment_key: str, cancel_reason: str) -> dict[str, Any]:
        """
        결제 취소
        https://docs.tosspayments.com/reference#결제-취소
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=f"{self.toss_api_url}/payments/{payment_key}/cancel",
                headers=self.get_auth_header(),
                json={"cancelReason": cancel_reason}
            )

            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": response.json()}


    async def partial_cancel_payment(self, payment_key: str, cancel_reason: str, cancel_amount: int) -> dict[str, Any]:
        """부분 취소"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=f"{self.toss_api_url}/payments/{payment_key}/cancel",
                headers=self.get_auth_header(),
                json={ "cancelReason": cancel_reason, "cancelAmount": cancel_amount }
            )

            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": response.json()}


    async def get_payment(self, payment_key: str) -> dict[str, Any]:
        """결제 조회"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url=f"{self.toss_api_url}/payments/{payment_key}",
                headers=self.get_auth_header()
            )

            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": response.json()}


    async def update_order_status(self, order_id: int, status: OrderStatus) -> None:
        return await self.repo.update_order_status(order_id, status=status)


    async def process_payment_ok(self, order_id: int, payment: PaymentCreate) -> None:
        payment_dict = payment.model_dump()
        await self.repo.process_payment_ok(order_id, payment_dict)
