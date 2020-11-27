from fastapi import APIRouter, Depends

from mirumon.domain.users.scopes import DevicesScopes
from mirumon.infra.api.dependencies.users.permissions import check_user_scopes
from mirumon.infra.api.endpoints.http import users
from mirumon.infra.api.endpoints.http.devices import (
    auth,
    detail,
    execute,
    info,
    list,
    shutdown,
)
from mirumon.infra.api.endpoints.ws.devices import ws

router = APIRouter()

DEVICES_PATH = "/devices"
DEVICES_TAG = "Devices"

USERS_PATH = "/users"
USERS_TAG = "Users"

# Users routers
router.include_router(users.router, prefix=USERS_PATH, tags=[USERS_TAG])

# Devices routers
router.include_router(
    auth.router,
    prefix=DEVICES_PATH,
    tags=[DEVICES_TAG],
)
router.include_router(
    list.router,
    prefix=DEVICES_PATH,
    tags=[DEVICES_TAG],
    dependencies=[Depends(check_user_scopes([DevicesScopes.read]))],
)
router.include_router(
    detail.router,
    prefix=DEVICES_PATH,
    tags=[DEVICES_TAG],
    dependencies=[Depends(check_user_scopes([DevicesScopes.read]))],
)
router.include_router(
    info.router,
    prefix=DEVICES_PATH,
    tags=[DEVICES_TAG],
    dependencies=[Depends(check_user_scopes([DevicesScopes.read]))],
)
router.include_router(
    shutdown.router,
    prefix=DEVICES_PATH,
    tags=[DEVICES_TAG],
    dependencies=[Depends(check_user_scopes([DevicesScopes.write]))],
)
router.include_router(
    execute.router,
    prefix=DEVICES_PATH,
    tags=[DEVICES_TAG],
    dependencies=[Depends(check_user_scopes([DevicesScopes.write]))],
)

router.include_router(ws.router, prefix=DEVICES_PATH, tags=[DEVICES_TAG])
