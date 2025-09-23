from devtools import debug
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from fastapi import Request, Response
from firebase_admin import auth as firebase_auth
from starlette.responses import JSONResponse


class FirebaseAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.method == "OPTIONS":
            return await call_next(request)

        authorization: str = request.headers.get("Authorization")
        if not authorization:
            return JSONResponse({"detail": "Authorization header is missing"}, status_code=401)

        token = authorization.split(" ")[-1]
        try:
            decoded_token = firebase_auth.verify_id_token(token)
            request.state.user = decoded_token  # Store user information in request state
        except Exception as e:
            return JSONResponse({"detail": "Invalid or expired token"}, status_code=403)

        try:
            response = await call_next(request)
        except Exception as e:
            raise e
        return response
