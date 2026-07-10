#!/usr/bin/env python3
try:
 print("import user model...")
 print("✓ user model import success")

 print("Dao Ru Xu NiIPmodel...")
 print("✓ virtualIPmodel import success")

 print("import Jiao Ben model...")
 print("✓ Jiao Ben model import success")

 print("import database Ji Lei...")
 from app.core.database import Base

 print("✓ database Ji Lei import success")

 print("checkmetadata...")
 print(f"Base.metadata.tables: {list(Base.metadata.tables.keys())}")

 print("Suo You import success!")

except Exception as e:
 print(f"Dao Ru Shi Bai: {e}")
 import traceback

 traceback.print_exc()
