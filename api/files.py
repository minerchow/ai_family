import re
from uuid import uuid4

from fastapi import APIRouter, File, Request, UploadFile
from starlette.concurrency import run_in_threadpool
from starlette.responses import FileResponse

from common.exception_handler import CustomException
from common.result import Result, ResultCodeEnum
from settings import settings

router = APIRouter(prefix="/api/files", tags=["文件"])

SUFFIX_PATTERN = re.compile(r"\.[a-z0-9]{1,10}")
STORED_NAME_PATTERN = re.compile(r"[0-9a-f]{32}(\.[a-z0-9]{1,10})?")


@router.post("/upload", summary="上传文件")
async def upload(request: Request, file: UploadFile = File(...)) -> Result:
    content = await file.read(settings.max_upload_size + 1)
    await file.close()
    if not content:
        raise CustomException(ResultCodeEnum.PARAM_ERROR, "请选择需要上传的文件")
    if len(content) > settings.max_upload_size:
        raise CustomException(ResultCodeEnum.PARAM_ERROR, "文件不能超过 20 MB")

    original_name = get_original_name(file.filename)
    stored_name = uuid4().hex + get_suffix(original_name)

    settings.file_storage_path.mkdir(parents=True, exist_ok=True)
    await run_in_threadpool((settings.file_storage_path / stored_name).write_bytes, content)

    return Result.success(
        {
            "originalName": original_name,
            "storedName": stored_name,
            "size": len(content),
            "url": f"{str(request.base_url).rstrip('/')}/api/files/{stored_name}",
        }
    )


@router.get("/{file_name}", summary="下载文件")
async def download(file_name: str) -> FileResponse:
    if not STORED_NAME_PATTERN.fullmatch(file_name):
        raise CustomException(ResultCodeEnum.PARAM_ERROR, "文件名不合法")

    target = settings.file_storage_path / file_name
    if not target.is_file():
        raise CustomException(ResultCodeEnum.NOT_FOUND, "文件不存在")

    return FileResponse(target, filename=file_name, media_type="application/octet-stream")


def get_original_name(filename: str | None) -> str:
    if not filename or not filename.strip():
        return "unnamed-file"
    # 部分浏览器会带上完整路径，只保留文件名
    name = re.split(r"[\\/]", filename)[-1]
    return name if name.strip() else "unnamed-file"


def get_suffix(original_name: str) -> str:
    dot_index = original_name.rfind(".")
    if dot_index <= 0:
        return ""
    suffix = original_name[dot_index:].lower()
    return suffix if SUFFIX_PATTERN.fullmatch(suffix) else ""
