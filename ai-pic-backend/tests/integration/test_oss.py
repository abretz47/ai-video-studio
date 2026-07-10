#!/usr/bin/env python3
"""
Jian Dan DeOSSLian Jie Ce Shi
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

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


def test_oss_connection():
 """testOSSJi Chu Lian Jie"""
 print("🔍 testOSSconnection...")

 # Jia Zai Pei Zhi
 settings = TestSettings()
 print(f"Access Key ID: {settings.ALIYUN_ACCESS_KEY_ID}")
 print(f"Endpoint: {settings.ALIYUN_OSS_ENDPOINT}")
 print(f"Bucket: {settings.ALIYUN_OSS_BUCKET}")

 if not all(
 [
 settings.ALIYUN_ACCESS_KEY_ID,
 settings.ALIYUN_ACCESS_KEY_SECRET,
 settings.ALIYUN_OSS_ENDPOINT,
 settings.ALIYUN_OSS_BUCKET,
 ]
):
 print("❌ OSSconfiguration Bu complete")
 return False

 try:
 # createOSSRen Zheng Hebucketobject
 auth = oss2.Auth(
 settings.ALIYUN_ACCESS_KEY_ID, settings.ALIYUN_ACCESS_KEY_SECRET
)
 bucket = oss2.Bucket(
 auth, settings.ALIYUN_OSS_ENDPOINT, settings.ALIYUN_OSS_BUCKET
)

 # test1: Lie ChubucketZhong De Wen Jian(Zhi Qu Qian5Ge)
 print("\n🔍 test Lie Chu file...")
 result = bucket.list_objects(max_keys=5)
 print(f"✅ Cheng Gong Lian Jie, Zhao Dao {len(result.object_list)} Ge Dui Xiang")

 # test2: upload Yi Ge Jian Dan De Wen Ben Wen Jian
 print("\n🔍 test upload file...")
 test_content = f"OSSCe Shi Wen Jian - {datetime.now().isoformat()}"
 test_key = f"test/oss_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

 bucket.put_object(test_key, test_content)
 print(f"✅ success upload test file: {test_key}")

 # test3: Xia Zai file validate
 print("\n🔍 test Xia Zai file...")
 downloaded = bucket.get_object(test_key)
 content = downloaded.read().decode("utf-8")
 print(f"✅ Cheng Gong Xia Zai, Nei Rong Pi Pei: {content == test_content}")

 # clean up test file
 bucket.delete_object(test_key)
 print("✅ Yi clean up test file")

 return True

 except Exception as e:
 print(f"❌ OSSLian Jie Shi Bai: {str(e)}")
 return False


def test_oss_with_metadata():
 """Ce Shi DaimetadataDe Shang Chuan"""
 print("\n🔍 Ce Shi DaimetadataDe Shang Chuan...")

 settings = TestSettings()

 try:
 auth = oss2.Auth(
 settings.ALIYUN_ACCESS_KEY_ID, settings.ALIYUN_ACCESS_KEY_SECRET
)
 bucket = oss2.Bucket(
 auth, settings.ALIYUN_OSS_ENDPOINT, settings.ALIYUN_OSS_BUCKET
)

 # Ce Shi Bu DaimetadataDe Shang Chuan
 test_content = "Ce Shi Bu Daimetadata"
 test_key = f"test/no_metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
 bucket.put_object(test_key, test_content)
 print(f"✅ nonemetadataShang Chuan Cheng Gong: {test_key}")
 bucket.delete_object(test_key)

 # Ce Shi DaiASCII metadataDe Shang Chuan
 test_content = "testASCII metadata"
 test_key = f"test/ascii_metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
 headers = {
 "x-oss-meta-category": "portrait",
 "x-oss-meta-style": "realistic",
 "x-oss-meta-provider": "openai",
 }
 bucket.put_object(test_key, test_content, headers=headers)
 print(f"✅ ASCII metadataShang Chuan Cheng Gong: {test_key}")
 bucket.delete_object(test_key)

 return True

 except Exception as e:
 print(f"❌ metadatatest failed: {str(e)}")
 return False


if __name__ == "__main__":
 print(f"🕒 Dang Qian Shi Jian: {datetime.now()}")

 if test_oss_connection():
 test_oss_with_metadata()
 else:
 print("\n💡 possible De Jie Jue Fang An:")
 print("1. checkOSS Access KeyHeSecret KeyShi Fou Zheng Que")
 print("2. checkendpointconfiguration Shi Fou correct")
 print("3. checkbucketname Shi Fou correct")
 print("4. check Wang Luo Lian Jie")
 print("5. check system time Shi Fou correct(Zhong Yao!)")
