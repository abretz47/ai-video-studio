#!/usr/bin/env python3
"""
OpenAIimage generate Dan Yuan Ce Shi - Du Li Ban Ben

Zhi Jie Ce ShiOpenAI APIcall, Bu Yi Lai complete DeFastAPIYing Yong
"""

import asyncio
import os

import httpx
import pytest
from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):
 OPENAI_API_KEY: str = None

 class Config:
 env_file = ".env"
 case_sensitive = True


if os.getenv("RUN_OPENAI_DIRECT_TEST")!= "1":
 pytest.skip(
 "OpenAI Zhi Lian API Mao Yan Ce Shi(Mo Ren Tiao Guo); set RUN_OPENAI_DIRECT_TEST=1 Cai Yun Xing",
 allow_module_level=True,
)


@pytest.mark.openai
@pytest.mark.external
@pytest.mark.asyncio
async def test_openai_dalle_direct(skip_if_no_openai):
 """Zhi Jie Ce ShiOpenAI DALL-E APIcall"""

 print("🧪 startOpenAI DALL-EDan Yuan Ce Shi(Zhi JieAPIcall)")
 print("=" * 60)

 # Jia Zai Pei Zhi
 settings = TestSettings()

 if not settings.OPENAI_API_KEY:
 pytest.skip("OPENAI_API_KEY Wei Pei Zhi")

 # Ce Shi Can Shu
 prompt = "A simple test image of a cat"
 style = "realistic"

 print("🔍 Ce Shi Can Shu:")
 print(f" Ti Shi Ci: {prompt}")
 print(f" style: {style}")
 print(f" APIMi Yao: sk-...{settings.OPENAI_API_KEY[-10:]}")

 try:
 print("\n⏳ Zhi Jie Diao YongOpenAI API...")
 start_time = asyncio.get_event_loop().time()

 async with httpx.AsyncClient() as client:
 response = await client.post(
 "https://api.openai.com/v1/images/generations",
 headers={
 "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
 "Content-Type": "application/json",
 },
 json={
 "model": "dall-e-3",
 "prompt": prompt[:1000],
 "n": 1,
 "size": "1024x1024",
 "quality": "hd",
 "style": "vivid" if style!= "realistic" else "natural",
 "response_format": "b64_json",
 },
 timeout=60.0,
)

 end_time = asyncio.get_event_loop().time()
 duration = end_time - start_time

 print(f"⏱️ APIDiao Yong Hao Shi: {duration:.2f}seconds")
 print(f"📡 HTTPZhuang Tai Ma: {response.status_code}")

 if response.status_code!= 200:
 print("❌ APIFan Hui Cuo Wu")
 print(f" Cuo Wu Nei Rong: {response.text[:300]}")
 return False

 response.raise_for_status()
 result = response.json()

 print("✅ APIDiao Yong Cheng Gong")
 print(f" response Shu Ju Jie Gou: {list(result.keys())}")

 if "data" in result and len(result["data"]) > 0:
 data = result["data"][0]
 print(f" image Shu Ju Zi Duan: {list(data.keys())}")

 if "b64_json" in data:
 base64_data = data["b64_json"]
 print(f" base64Shu Ju Chang Du: {len(base64_data)}")

 # validatebase64data
 import base64

 png_header = b"\x89PNG"
 try:
 decoded = base64.b64decode(base64_data)
 print(f" Jie Ma Hou image Da Xiao: {len(decoded)} bytes")
 print(
 f" Tu Xiang Ge Shi check: {'PNG' if decoded.startswith(png_header) else 'Wei Zhi'}"
)
 assert decoded.startswith(png_header)
 return
 except Exception as decode_error:
 print(f" ❌ base64Jie Ma Shi Bai: {decode_error}")
 raise
 else:
 print(" ❌ response Zhong Mei Youb64_jsonZi Duan")
 raise AssertionError("missing b64_json")
 else:
 print(" ❌ response Zhong Mei YoudataZi Duan")
 raise AssertionError("missing data")

 except httpx.TimeoutException as e:
 print(f"❌ Qing Qiu Chao Shi: {e}")
 raise
 except httpx.HTTPStatusError as e:
 print(f"❌ HTTPerror: {e.response.status_code}")
 print(f" Cuo Wu Xiang Qing: {e.response.text[:300]}")
 raise
 except Exception as e:
 print(f"❌ Diao Yong Yi Chang: {e}")
 print(f" Yi Chang Lei Xing: {type(e).__name__}")
 raise


async def main():
 """main test function"""
 success = await test_openai_dalle_direct()

 print("\n" + "=" * 60)
 print(f"🎯 Dan Yuan Ce Shi Jie Guo: {'✅ pass' if success else '❌ failed'}")

 return success


if __name__ == "__main__":
 try:
 result = asyncio.run(main())
 exit(0 if result else 1)
 except KeyboardInterrupt:
 print("\n⏹️ test Bei user Zhong Duan")
 exit(130)
 except Exception as e:
 print(f"\n💥 Ce Shi Yi Chang: {e}")
 exit(1)
