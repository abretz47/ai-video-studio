import logging
from urllib.parse import urlparse

import oss2
from app.core.config import settings

from .oss_admin_mixin import OSSAdminMixin
from .oss_backup_mixin import OSSBackupMixin
from .oss_upload_mixin import OSSUploadMixin


class OSSService(OSSUploadMixin, OSSAdminMixin, OSSBackupMixin):
    """A Li YunOSSCun Chu service"""

    def __init__(self):
        # Ji Ben configuration, unified ZuostripQu Diao Ke Neng Kong Bai Zi Fu, avoid Qian Ming failed
        raw_access_key_id = getattr(settings, "ALIYUN_ACCESS_KEY_ID", None)
        raw_access_key_secret = getattr(settings, "ALIYUN_ACCESS_KEY_SECRET", None)
        raw_endpoint = getattr(settings, "ALIYUN_OSS_ENDPOINT", None)
        raw_bucket = getattr(settings, "ALIYUN_OSS_BUCKET", None)
        raw_domain = getattr(settings, "ALIYUN_OSS_DOMAIN", None)

        self.access_key_id = (
            raw_access_key_id.strip()
            if isinstance(raw_access_key_id, str)
            else raw_access_key_id
        )
        self.access_key_secret = (
            raw_access_key_secret.strip()
            if isinstance(raw_access_key_secret, str)
            else raw_access_key_secret
        )
        self.endpoint = (
            raw_endpoint.strip() if isinstance(raw_endpoint, str) else raw_endpoint
        )
        self.bucket_name = (
            raw_bucket.strip() if isinstance(raw_bucket, str) else raw_bucket
        )
        self.domain = raw_domain.strip() if isinstance(raw_domain, str) else raw_domain
        self.logger = logging.getLogger(__name__)

        if not all(
            [
                self.access_key_id,
                self.access_key_secret,
                self.endpoint,
                self.bucket_name,
            ]
        ):
            raise ValueError("A Li YunOSSconfiguration not complete, Qing check Huan Jing Bian Liang")

        # Gui Fan Hua endpoint, Bao Zheng subsequent SDK Shi Yong Yi Zhi
        parsed = urlparse(self.endpoint)
        if parsed.scheme:
            endpoint_host = parsed.netloc or parsed.path
        else:
            endpoint_host = parsed.path or parsed.netloc
        self._endpoint_host = endpoint_host

        # Shi Yong Guan Fang SDK responsible for Qian Ming, avoid Shou Xie Qian Ming Chu Cuo Dao Zhi 403
        auth = oss2.Auth(self.access_key_id, self.access_key_secret)
        self.bucket = oss2.Bucket(
            auth, f"https://{self._endpoint_host}", self.bucket_name
        )

        # She Zhi default access Yu Ming
        if not self.domain:
            self.domain = f"https://{self.bucket_name}.{self._endpoint_host}"


# create Quan JuOSS serviceinstance
try:
    oss_service = OSSService()
except ValueError as e:
    print(f"OSS服务初始化失败: {e}")
    oss_service = None
