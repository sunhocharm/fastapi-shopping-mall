from loguru import logger

from app.config import settings
from fastapi import UploadFile
from pathlib import Path

import anyio
import asyncio
import aiofiles
from PIL import Image, ImageOps
from io import BytesIO
from uuid import uuid4

# from PIL import UnidentifiedImageError

from app.custom_exceptions import CustomBadRequestError


class FileUploadService:
    def __init__(self) -> None:
        self.saved_file_list = []

    def _add_saved_file(self, file_path_saved: str) -> None:
        self.saved_file_list.append(file_path_saved)


    # private func
    async def _create_thumb_image(self, original_file_path: Path, thumb_file_path_to_save: Path, size: tuple[int, int]) -> None:
        """이미지 최적화 (리사이즈, 압축) - 비동기 처리 버전"""
        try:
            # 1. aiofiles를 사용하여 원본 파일을 비동기로 읽어옵니다.
            async with aiofiles.open(original_file_path, mode='rb') as f:
                contents = await f.read()


            # private func (이미지 변환 연산(CPU Bound Task)은 이벤트 루프를 막지 않도록 별도 스레드에서 실행합니다)
            def _process_image_in_thread() -> bytes:
                with Image.open(BytesIO(contents)) as original:
                    # 휴대폰 촬영 이미지 방향 수정 및 고품질 다운샘플링 리사이즈
                    img = ImageOps.exif_transpose(image=original)
                    img = ImageOps.fit(image=img, size=size, method=Image.Resampling.LANCZOS)
                    
                    if img.mode in ("RGBA", "LA", "P"):
                        img = img.convert("RGB")
                    
                    # 결과물을 바이트 스트림으로 먼저 임시 저장
                    output = BytesIO()
                    img.save(output, "JPEG", quality=85, optimize=True)
                    return output.getvalue()


            # asyncio.to_thread를 통해 내부 헬퍼 함수를 비동기 스레드 풀에서 구동시킵니다.
            thumb_data = await asyncio.to_thread(_process_image_in_thread)

            # 3. 완성된 썸네일 바이너리 데이터를 aiofiles로 비동기 디스크 쓰기 처리합니다.
            async with aiofiles.open(thumb_file_path_to_save, mode='wb') as f:
                await f.write(thumb_data)

        except Exception as err:
            logger.error(str(err))
            raise Exception from err


    # private func
    async def _save_original_image(self, image_file: UploadFile, file_path_to_save: str) -> None:
       # 핵심: aiofiles를 사용하여 파일 기록 과정을 완전한 Async 논블로킹으로 처리
        async with aiofiles.open(file_path_to_save, "wb") as out_file:
            while content := await image_file.read(1024 * 1024):  # 1MB 씩 분할 청크 비동기 읽기
                await out_file.write(content)  # 비동기 쓰기
        await image_file.close()


    # public func
    async def save_image_files(self, image_files: list[UploadFile], folder: str = "products") -> list[tuple[str,str]]:

        # 먼저 파일 확인한다.
        for image_file in image_files:
            content_type = image_file.content_type
            if not content_type.startswith("image"):
                msg = "Invalid image file. Please upload a valid image (JPEG, PNG, GIF, WebP)."
                raise CustomBadRequestError(msg)

            if image_file.size > settings.max_upload_size_bytes:
                max_mb = settings.max_upload_size_bytes / (1024*1024)
                msg = f"File too large. Maximum: {max_mb} MB | Current: {image_file.size:,} bytes"
                raise CustomBadRequestError(msg)

        thumbnail_size = settings.product_image_thumbnail_size
        file_final_path = Path(settings.upload_dir) / folder
        file_final_path.mkdir(parents=True, exist_ok=True)
        result_file_paths = []

        # 하나씩 파일을 저장한다.
        for image_file in image_files:
            ext = Path(image_file.filename).suffix

            unique_id = uuid4().hex
            file_name_to_save = f"{unique_id}{ext}"
            file_path_to_save = file_final_path / file_name_to_save

            await self._save_original_image(image_file, file_path_to_save)

            thumbnail_file_name_to_save = f"{unique_id}-thumbnail.jpeg"
            thumbnail_file_path_to_save = file_final_path / thumbnail_file_name_to_save

            if settings.do_create_product_thumbnail:
                await self._create_thumb_image(file_path_to_save, thumbnail_file_path_to_save, size=thumbnail_size)

            origin_file_path = f"/{str(file_path_to_save)}"
            thumbnail_file_path = f"/{str(thumbnail_file_path_to_save)}"
            if not settings.do_create_product_thumbnail:
                thumbnail_file_path = origin_file_path

            self._add_saved_file(origin_file_path)
            self._add_saved_file(thumbnail_file_path)

            result_file_paths.append((origin_file_path, thumbnail_file_path))

        return result_file_paths


    async def remove_uploaded_files(self):
        # 1. 모든 파일 삭제 작업에 대한 비동기 태스크(코루틴 객체) 리스트 생성
        tasks = [self._delete_uploaded_file(file_path) for file_path in self.saved_file_list]
        
        # 2. gather를 사용해 병렬로 일괄 실행 (return_exceptions=True로 두면 하나가 실패해도 전체가 터지지 않음)
        await asyncio.gather(*tasks, return_exceptions=True)


    # private func
    async def _delete_uploaded_file(self, file_full_path: str | None = None) -> bool:
        """Upload File 비동기 삭제 (aiofiles & anyio 가속)"""

        if not file_full_path:
            return False

        # if not file_full_path.startswith("/upload/"):
        if not file_full_path.startswith("/upload"):  # Windows 경로 구분자 유연성 확보
            return False

        dir_name = settings.upload_dir
        # file_path = Path(file_full_path.replace("/upload/", f"{dir_name}"))
        file_path = Path(file_full_path.replace("/upload", f"{dir_name}"))

        async_uploaded_path = anyio.Path(file_path)
        exists = await async_uploaded_path.exists()
        if exists:
            await async_uploaded_path.unlink()

        return True


    # public func
    async def delete_uploaded_file(self, file_full_path: str | None = None, thumbnail_file_full_path: str | None = None) -> bool:
        """Upload File 삭제"""
        await self._delete_uploaded_file(file_full_path)
        await self._delete_uploaded_file(thumbnail_file_full_path)
