from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from mirumon.application.users.auth_service import AuthUsersService
from mirumon.domain.users.scopes import UsersScopes
from mirumon.infra.api.dependencies.services import get_service
from mirumon.infra.api.dependencies.users.permissions import (
    check_user_scopes,
    get_user_in_login,
)
from mirumon.infra.api.models.http.users.users import (
    User,
    UserInCreate,
    UserInLogin,
    UserToken,
)
from mirumon.resources import strings

router = APIRouter()


@router.post(
    "",
    name="auth:register",
    summary="Create User",
    status_code=HTTP_201_CREATED,
    response_model=User,
    dependencies=[Depends(check_user_scopes([UsersScopes.write]))],
)
async def register(
    new_user: UserInCreate,
    auth_users_service: AuthUsersService = Depends(get_service(AuthUsersService)),
) -> User:
    try:
        user = await auth_users_service.register_new_user(new_user)
    except RuntimeError:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=strings.USERNAME_TAKEN,
        )

    return User.from_domain(user)


# TODO: remove scope, client_id, client_secret, gran_type
@router.post(
    "/token", name="auth:token", summary="Get User Token", response_model=UserToken
)
async def login(
    user: UserInLogin = Depends(get_user_in_login),
    users_service: AuthUsersService = Depends(get_service(AuthUsersService)),
) -> UserToken:
    try:
        return await users_service.create_access_token(user)
    except RuntimeError:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=strings.INCORRECT_LOGIN_INPUT,
        )
