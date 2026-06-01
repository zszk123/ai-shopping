"""OSS 客户端 —— 阿里云对象存储图片上传"""
import oss2

from app.config import settings


class OSSClient:
    def __init__(self):
        if not all([settings.OSS_ACCESS_KEY, settings.OSS_SECRET_KEY,
                     settings.OSS_ENDPOINT, settings.OSS_BUCKET]):
            raise RuntimeError("OSS 配置不完整，请检查 .env 中的 OSS_ACCESS_KEY / OSS_SECRET_KEY / OSS_ENDPOINT / OSS_BUCKET")
        self._auth = oss2.Auth(settings.OSS_ACCESS_KEY, settings.OSS_SECRET_KEY)
        self._bucket = oss2.Bucket(self._auth, settings.OSS_ENDPOINT, settings.OSS_BUCKET)

    def upload_image(self, file_bytes: bytes, object_key: str) -> str:
        """上传图片到 OSS 并返回带签名的临时访问 URL（有效期 1 小时）"""
        try:
            result = self._bucket.put_object(object_key, file_bytes)
            if result.status != 200:
                raise RuntimeError(f"OSS 上传返回非 200 状态码: {result.status}")
        except oss2.exceptions.OssError as e:
            raise RuntimeError(f"OSS 上传失败: {str(e)}") from e
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"OSS 上传异常: {str(e)}") from e

        # 生成带签名的临时 URL，确保 DashScope 数据审查服务能访问图片
        return self._bucket.sign_url("GET", object_key, 3600)


oss_client = OSSClient()
