#!/usr/bin/env python3
"""
Xiang XiOSStest，mock Wo Men Dai Ma Que Qie call Fang Shi
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import asyncio
from datetime import datetime

import oss2
from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):
    ALIYUN_ACCESS_KEY_ID: str = None
    ALIYUN_ACCESS_KEY_SECRET: str = None
    ALIYUN_OSS_ENDPOINT: str = None
    ALIYUN_OSS_BUCKET: str = None

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


async def test_exact_oss_call():
    """test and Wo Men Dai Ma Wan Quan Xiang TongOSScall"""
    print("🔍 test and Dai Ma Wan Quan Xiang TongOSScall...")

    settings = TestSettings()

    try:
        # createOSSconnection（and Wo Men Dai Ma Xiang Tong）
        auth = oss2.Auth(
            settings.ALIYUN_ACCESS_KEY_ID, settings.ALIYUN_ACCESS_KEY_SECRET
        )
        bucket = oss2.Bucket(
            auth, settings.ALIYUN_OSS_ENDPOINT, settings.ALIYUN_OSS_BUCKET
        )

        # mock Wo Men file content
        test_content = b"fake image content for testing"

        # generate object Jian（mock Wo Men generate Fang Shi）
        timestamp = datetime.now().strftime("%Y%m%d/%H%M%S")
        import uuid

        random_str = str(uuid.uuid4())[:8]
        object_key = f"ai-generated/virtual-ip/image/{timestamp}/{random_str}.png"

        print(f"Object key: {object_key}")

        # Zhun Beiheaders（and Wo Men Dai Ma Wan Quan Xiang Tong）
        headers = {"Content-Type": "image/png", "Cache-Control": "max-age=31536000"}

        # Tian Jiametadata（and Wo Men Dai Ma Xiang Tong）
        metadata = {
            "ip_name": "Mia",  # Zhe Ge Bao Han Zhong Wen，Hui be Tiao Guo
            "style": "realistic",
            "category": "portrait",
            "provider": "openai",
            "model": "dall-e-3",
            "generation_time": datetime.now().isoformat(),
        }

        print(f"Yuan Shimetadata: {metadata}")

        # handlemetadata（and Wo Men Dai Ma Xiang Tong logic）
        processed_metadata = {}
        for key, value in metadata.items():
            value_str = str(value)
            try:
                value_str.encode("ascii")
                headers[f"x-oss-meta-{key}"] = value_str
                processed_metadata[key] = value_str
            except UnicodeEncodeError:
                print(f"Tiao Guo Bao Han FeiASCIIZi Fumetadata: {key}={value_str}")
                continue

        print(f"handle aftermetadata: {processed_metadata}")
        print(f"Zui Zhongheaders: {headers}")

        # useasyncio executorcall（and Wo Men Dai Ma Xiang Tong）
        await asyncio.get_event_loop().run_in_executor(
            None, lambda: bucket.put_object(object_key, test_content, headers=headers)
        )

        print(f"✅ Cheng Gong upload: {object_key}")

        # clean up
        bucket.delete_object(object_key)
        print("✅ already clean up test file")

        return True

    except Exception as e:
        print(f"❌ upload failed: {str(e)}")

        # Ru Guo isoss2exception，Da Yin Geng Duo Xiang Xi Xin Xi
        if hasattr(e, "details"):
            print(f"error details: {e.details}")

        return False


async def test_without_content_type():
    """test not setContent-TypeQing Kuang"""
    print("\n🔍 test not setContent-Type...")

    settings = TestSettings()

    try:
        auth = oss2.Auth(
            settings.ALIYUN_ACCESS_KEY_ID, settings.ALIYUN_ACCESS_KEY_SECRET
        )
        bucket = oss2.Bucket(
            auth, settings.ALIYUN_OSS_ENDPOINT, settings.ALIYUN_OSS_BUCKET
        )

        test_content = b"fake image content for testing"

        timestamp = datetime.now().strftime("%Y%m%d/%H%M%S")
        import uuid

        random_str = str(uuid.uuid4())[:8]
        object_key = f"ai-generated/test2/image/{timestamp}/{random_str}.png"

        # only setmetadata，not setContent-Type
        headers = {
            "x-oss-meta-category": "portrait",
            "x-oss-meta-style": "realistic",
            "x-oss-meta-provider": "openai",
            "x-oss-meta-model": "dall-e-3",
        }

        print(f"Headers: {headers}")

        await asyncio.get_event_loop().run_in_executor(
            None, lambda: bucket.put_object(object_key, test_content, headers=headers)
        )

        print(f"✅ Cheng Gong upload（noneContent-Type）: {object_key}")

        bucket.delete_object(object_key)
        print("✅ already clean up test file")

        return True

    except Exception as e:
        print(f"❌ upload failed（noneContent-Type）: {str(e)}")
        return False


async def main():
    print(f"🕒 Dang Qian time: {datetime.now()}")

    # test1: Wan Quan mock Wo Men Dai Ma
    success1 = await test_exact_oss_call()

    # test2: not setContent-Type
    success2 = await test_without_content_type()

    if success1 and success2:
        print("\n✅ Suo You Ce Shi Tong Guo，OSSservice normal")
    else:
        print("\n❌ exists issue，Xu Yao Jin Yi Bu Tiao Shi")


if __name__ == "__main__":
    asyncio.run(main())
