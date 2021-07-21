import os
import logging
from hashlib import md5

from fdfs_client.client import Fdfs_client, get_tracker_conf
from fdfs_client.exceptions import FDFSError

from app.utils.security import aes_encrypt, aes_decrypt
from app.configs import CONFIG
from app.utils import errors


logger = logging.getLogger(__name__)


class FastDFSStorage:
    conf_path = get_tracker_conf(CONFIG.FASTDFS_CONF_PATH)

    def upload(self, content, ext_name=None):
        cli = Fdfs_client(self.conf_path)
        if ext_name is not None:
            ext_name = ext_name.lstrip('.')
        fbuffer = aes_encrypt(content.read(), key=CONFIG.FILE_SECRET)
        result = cli.upload_by_buffer(fbuffer, file_ext_name=ext_name)
        logger.debug(f'FastDFS Upload: {result}')
        if result.get('Status') != 'Upload successed.':
            raise errors.Error(errmsg=f'上传文件到FastDFS失败: {result}')
        storage_ip = result.get('Storage IP')
        filename = result.get('Remote file_id')
        return {
            'filename': filename.decode(),
            'storage_ip': storage_ip.decode()
        }

    def download(self, name):
        cli = Fdfs_client(self.conf_path)
        if not isinstance(name, bytes):
            name = name.encode()
        try:
            result = cli.download_to_buffer(name)
        except FDFSError as e:
            raise errors.Error(errmsg=f'从FastDFS下载文件{name}失败:') from e
        # logger.debug(f'FastDFS download: {result}')
        content = result.get('Content')
        # remote_file_id = result.get('Remote file_id')
        # storage_ip = result.get('Storage IP')
        # size = result.get('Download size')
        return aes_decrypt(content, key=CONFIG.FILE_SECRET, a2b=False)

    def delete(self, name):
        cli = Fdfs_client(self.conf_path)
        if not isinstance(name, bytes):
            name = name.encode()
        try:
            result = cli.delete_file(name)
        except FDFSError as e:
            raise errors.Error(errmsg=f'从FastDFS删除文件{name}失败:') from e
        logger.debug(f'FastDFS delete: {result}')
        if result[0] != 'Delete file successed.':
            raise errors.Error(errmsg=f'FastDFS删除文件{name}失败: {result}')

    def get_token(self, filename, ts, secret):
        """用于生成http防盗链，目前不需要"""
        if isinstance(filename, str):
            filename = filename.encode()
        if isinstance(ts, int):
            ts = str(ts)
        if isinstance(ts, str):
            ts = ts.encode()
        if isinstance(secret, str):
            secret = secret.encode()
        s = filename + secret + ts
        return md5(s).hexdigest()


if __name__ == '__main__':
    storage = FastDFSStorage()
    filepath = './tests/申报表文件/增值税申报表.pdf'
    fio = open(filepath, 'rb')
    fname, ext = os.path.splitext(filepath)
    info = storage.upload(fio, ext_name=ext)
    filename = info.get('filename')
    storage_ip = info.get('storage_ip')
    fbuffer = storage.download(filename)
    with open('tmp.pdf', 'wb') as f:
        f.write(fbuffer)
    storage.delete(filename)
