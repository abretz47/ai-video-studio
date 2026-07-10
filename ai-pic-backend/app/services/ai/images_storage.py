from __future__ import annotations

import asyncio
import hashlib
import os
from typing import Any, Dict, Optional

import httpx
from app.core.config import settings
from app.services.media import build_generation_metadata
from app.services.media import upload_bytes as upload_media_bytes
from app.services.storage.oss_service import oss_service


class ImageStorageMixin:
    async def _download_image(
        self, image_data: Any, ip_name: str, category: str
    ) -> str:
        """process image data(URLorbase64)and save to local, failed Pao exception and Bao Liu Yuan Yin."""
        import base64
        import uuid
        from urllib.parse import unquote

        import aiofiles
        from app.utils.url_utils import normalize_presigned_url

        # Sheng Cheng Wei Yi Wen Jian Ming
        file_extension = ".png"  # OpenAI DALL-Edefault returnPNG
        unique_filename = f"{uuid.uuid4().hex}{file_extension}"

        # Que Bao Mu Lu Cun Zai
        upload_dir = settings.UPLOAD_DIR
        os.makedirs(upload_dir, exist_ok=True)

        local_file_path = os.path.join(upload_dir, unique_filename)

        if not isinstance(image_data, str):
            resolved: str | None = None
            if isinstance(image_data, dict):
                for key in ("url", "image_url", "image", "src"):
                    value = image_data.get(key)
                    if isinstance(value, str) and value:
                        resolved = value
                        break
            if resolved is None:
                raise TypeError(
                    f"image_data must be a string URL or data URL, got {type(image_data).__name__}"
                )
            image_data = resolved

        # determine Shibase64data Hai ShiURL
        if image_data.startswith("data:image"):
            # processbase64data
            self.logger.info("processbase64image data")
            base64_data = image_data.split(",")[1]  # Yi Chudata:image/png;base64,Qian Zhui
            image_bytes = base64.b64decode(base64_data)

            # directly savebase64data
            async with aiofiles.open(local_file_path, "wb") as f:
                await f.write(image_bytes)
            self.logger.info("base64 image save to: %s", local_file_path)
            return local_file_path

        # processURL, increase retry and output specific error
        normalized_url = unquote(image_data) if "%25" in image_data else image_data
        normalized_url = normalize_presigned_url(normalized_url)
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                self.logger.info(
                    "Xia Zai imageURL (attempt %s): %s...",
                    attempt + 1,
                    normalized_url[:100],
                )
                async with httpx.AsyncClient(follow_redirects=True) as client:
                    response = await client.get(normalized_url, timeout=60.0)
                    response.raise_for_status()

                async with aiofiles.open(local_file_path, "wb") as f:
                    await f.write(response.content)

                self.logger.info("image save to: %s", local_file_path)
                return local_file_path
            except Exception as exc:  # pragma: no cover - network failures
                last_error = exc
                self.logger.warning(
                    "image Xia Zai failed attempt=%s url=%s err=%s",
                    attempt + 1,
                    normalized_url,
                    exc,
                )
                if attempt < 2:
                    await asyncio.sleep(1.5 * (attempt + 1))

        raise RuntimeError(f"image Chu Li failed: {last_error}")

    async def _upload_local_image_to_oss(
        self,
        local_file_path: str,
        *,
        prefix: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """local Xia Zai image Shang Chuan Zhi OSS, failed then Pao Chu exception."""
        service = oss_service
        if not service:
            raise RuntimeError("OSS service not configuration, unable to Shang Chuan image")

        try:
            with open(local_file_path, "rb") as f:
                file_content = f.read()
        except Exception as exc:  # pragma: no cover - IO guard
            raise RuntimeError(f"Du Qu Ben Di image failed: {exc}") from exc

        filename = os.path.basename(local_file_path)

        sha256 = hashlib.sha256(file_content).hexdigest()
        extra = dict(metadata or {})
        provider = str(extra.get("provider") or "unknown")
        model_val = extra.get("model")
        model = str(model_val) if model_val is not None else None
        oss_result = await upload_media_bytes(
            content=file_content,
            filename=filename,
            media_type="image",
            prefix=prefix,
            metadata=build_generation_metadata(
                provider=provider,
                model=model,
                media_type="image",
                sha256=sha256,
                extra=extra,
            ),
            oss_service_override=service,
        )
        if not oss_result or not oss_result.get("success"):
            raise RuntimeError(f"OSS Shang Chuan failed: {oss_result}")
        return oss_result

    async def _persist_local_image(
        self,
        local_file_path: str,
        *,
        prefix: str,
        metadata: Optional[Dict[str, Any]] = None,
        require_upload: bool = False,
    ) -> Dict[str, Any]:
        """
 Cun Zai local Tu Xiang Wen Jian Chi Jiu Hua(Ji Suan Xiang Dui Lu Jing, can Xuan Shang Chuan OSS).

 Gong Bu Tong Lai Yuan image Fu Yong: Bao Kuo AI Sheng Cheng after Xia Zai to local file, Yi Ji user directly Shang Chuan Luo Pan file.
        """
        file_size = os.path.getsize(local_file_path)
        filename = os.path.basename(local_file_path)
        relative_path = f"/uploads/{filename}"

        oss_result = None
        oss_url = None
        if oss_service:
            try:
                oss_result = await self._upload_local_image_to_oss(
                    local_file_path,
                    prefix=prefix,
                    metadata=metadata or {},
                )
                # Dang require_upload as True when, any Fei successful Jie Guo all Shi Wei failed and Pao Chu exception; 
                # Fou Ze Ji Lu Gao Jing and fallback to local path.
                success = bool(oss_result.get("success"))
                file_url = oss_result.get("file_url")
                if success and file_url:
                    oss_url = file_url
                    self.logger.info(
                        "CDN Shang Chuan successful | filename=%s object_key=%s url=%s prefix=%s",
                        filename,
                        oss_result.get("object_key"),
                        file_url,
                        prefix,
                    )
                elif require_upload:
                    raise RuntimeError(f"OSS Shang Chuan failed: {oss_result}")
                else:
                    self.logger.warning(
                        "OSS Shang Chuan not return availableURL, Shi Yong local path | filename=%s result=%s",
                        filename,
                        oss_result,
                    )
            except Exception as exc:
                if require_upload:
                    raise
                self.logger.warning("OSS Shang Chuan exception, Shi Yong local path: %s", exc)
        elif require_upload:
            raise RuntimeError("OSS not configuration, unable to Shang Chuan image")
        else:
            self.logger.info(
                "OSS/CDN not configuration, Shi Yong local path | filename=%s path=%s",
                filename,
                relative_path,
            )

        return {
            "local_file_path": local_file_path,
            "relative_path": relative_path,
            "file_size": file_size,
            "filename": filename,
            "oss_url": oss_url,
            "oss_upload": oss_result,
        }

    async def _persist_generated_image(
        self,
        image_data: str,
        *,
        ip_name: str,
        category: str,
        prefix: str,
        metadata: Optional[Dict[str, Any]] = None,
        require_upload: bool = False,
    ) -> Dict[str, Any]:
        """Xia Zai/save Sheng Cheng image, and in configuration OSS when Shang Chuan, return path and Yuan data."""
        local_file_path = await self._download_image(image_data, ip_name, category)

        return await self._persist_local_image(
            local_file_path,
            prefix=prefix,
            metadata=metadata,
            require_upload=require_upload,
        )

    async def persist_uploaded_image(
        self,
        file_bytes: bytes,
        original_filename: str,
        *,
        prefix: str,
        metadata: Optional[Dict[str, Any]] = None,
        require_upload: bool = False,
    ) -> Dict[str, Any]:
        """
 Chi Jiu Hua user Shang Chuan Tu Xiang Wen Jian: first write local uploads, then Gen Ju configuration on Chuan Dao OSS.

 return structure and _persist_generated_image Bao Chi Yi Zhi, Bian Yu Shang Ceng unified process.
        """
        import uuid
        from pathlib import Path

        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        ext = Path(original_filename).suffix or ".png"
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        local_file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

        with open(local_file_path, "wb") as f:
            f.write(file_bytes)

        return await self._persist_local_image(
            local_file_path,
            prefix=prefix,
            metadata=metadata,
            require_upload=require_upload,
        )
