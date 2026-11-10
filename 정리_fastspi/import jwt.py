import jwt
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware

SECRET_KEY = "your-secret-key-change-me"  # 실제 서비스에서는 환경변수로 관리하세요.
ALGORITHM = "HS256"

app = FastAPI()


# -----------------------------------------------------------------------------
# 1. Jinja2 Context Processor 설정
# -----------------------------------------------------------------------------
def inject_user_to_templates(request: Request):
    """
    모든 Jinja2 템플릿 렌더링 시 자동으로 호출되는 함수입니다.
    미들웨어에서 request.state에 저장해둔 유저 정보를 꺼내어 'user'라는 이름으로 주입합니다.
    """
    user_data = getattr(request.state, "user", None)
    return {"user": user_data}


# Jinja2Templates를 생성할 때 context_processors 목록에 추가합니다.
templates = Jinja2Templates(
    directory="templates", context_processors=[inject_user_to_templates]
)


# -----------------------------------------------------------------------------
# 2. 인증 미들웨어 (Auth Middleware)
# -----------------------------------------------------------------------------
class AuthenticationMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        # 정적 파일(.css, .js)이나 헬스체크 등 굳이 JWT 검증이 필요 없는 경로는 패스하도록 최적화 가능
        if request.url.path.startswith("/static"):
            request.state.user = None
            return await call_next(request)

        # 1) HttpOnly, Secure 쿠키에서 토큰 추출
        token = request.cookies.get("access_token")
        user_data = None

        if token:
            try:
                # 2) JWT 토큰 디코딩 및 검증
                # 실제 환경에서는 만료일(exp) 검증 등이 포함되어야 합니다.
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                user_data = payload  # 예: {"username": "kim123", "role": "admin"}
            except jwt.PyJWTError:
                # 토큰이 만료되었거나 변조된 경우 None 처리 (또는 만료 쿠키 삭제 로직 추가 가능)
                pass

        # 3) 현재 요청(Request)의 state 객체에 안전하게 유저 정보 저장 (동시성 보장)
        request.state.user = user_data

        # 다음 단계(라우터 등)로 요청 전달
        response = await call_next(request)
        return response


# FastAPI 애플리케이션에 미들웨어 등록
app.add_middleware(AuthenticationMiddleware)


# -----------------------------------------------------------------------------
# 3. 라우터 엔드포인트 예시 (Endpoints)
# -----------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    # 💡 중요: 별도로 {"user": user}를 넘기지 않고 {"request": request}만 넘겨도
    # Context Processor 덕분에 템플릿 내부에서 user 변수를 바로 쓸 수 있습니다.
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/login")
async def login(request: Request):
    """테스트용 가짜 로그인 엔드포인트입니다."""
    # 1) 실제 유저 인증 절차 진행 (ID/PW 확인 등)
    # 2) 인증 성공 시 유저 정보로 JWT 토큰 발급
    mock_payload = {"username": "kim123", "role": "developer"}
    token = jwt.encode(mock_payload, SECRET_KEY, algorithm=ALGORITHM)

    # 3) 클라이언트에 쿠키를 구워주면서 메인 페이지로 리다이렉트
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,  # 👈 브라우저 JavaScript XSS 공격 방어
        secure=False,  # 👈 로컬 개발 환경(http)에서는 False, 상용(https) 환경에서는 True 필수
        samesite="lax",
    )
    return response


@app.get("/logout")
async def logout():
    """로그아웃 엔드포인트입니다."""
    response = RedirectResponse(url="/", status_code=303)
    # 쿠키 삭제
    response.delete_cookie(key="access_token")
    return response




<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>FastAPI + Jinja2 Auth Skeleton</title>
</head>
<body>
    <header>
        <h1>My Web Service</h1>
        <hr>
        
        <!-- Context Processor 덕분에 어떤 페이지에서든 'user' 변수를 바로 꺼내 쓸 수 있습니다. -->
        {% if user %}
            <div>
                <p>🟢 <strong>{{ user.username }}</strong>님, 환영합니다! (권한: {{ user.role }})</p>
                <a href="/logout"><button>로그아웃</button></a>
            </div>
        {% else %}
            <div>
                <p>🔴 현재 비로그인 상태입니다.</p>
                <form action="/login" method="POST" style="display: inline;">
                    <button type="submit">테스트 계정으로 로그인하기</button>
                </form>
            </div>
        {% endif %}
    </header>

    <main>
        <h3>메인 컨텐츠 영역</h3>
        <p>이 영역은 로그인 여부와 관계없이 모두에게 보이는 영역입니다.</p>
    </main>
</body>
</html>
