import pytest
from fastapi import HTTPException
from dependencies import check_ownership

def test_check_ownership_passes():
    check_ownership(1, 1)

def test_check_owenership_fails():
    with pytest.raises(HTTPException) as exc_info:
        check_ownership(1, 2)
    assert exc_info.value.status_code == 403