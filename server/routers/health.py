from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=[""])


@router.get("")
def health():
    return {"message": "OK"}
