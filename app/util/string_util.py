import base64
import hashlib
import secrets
import re



# 한눈에 보는 직관적인 비교 테이블

# 비교 항목	            secrets + DB 해시 저장 방식	                                itsdangerous 서명 방식
# DB 사용 여부	        필수 (발급 시 INSERT, 검증 시 SELECT/DELETE)	            없음 (서버 내부 암호화 연산만 수행)
# 토큰 만료 관리	    DB의 expires_at 컬럼으로 직접 비교	                        토큰 내부에 포함된 타임스탬프와 max_age로 자동 비교
# 즉시 취소/폐기	    가능 (DB 레코드 삭제 시 즉시 무효화)	                      불가능 (유효기간이 지나기 전까진 무조건 유효)
# 일회용(Reuse) 방지	매우 쉬움 (사용 후 DB에서 삭제)	                            추가 로직 필요 (유저 정보의 변경 시점 등과 대조)
# 추천 시나리오	        보안이 극도로 중요하여 확실한 제어와 즉시 폐기가 필요한 경우	  대규모 서비스에서 DB 부하를 줄이고 단순한 로직을 원하는 경우



# 🛠️ 핵심 기능과 사용법

# 가장 많이 쓰는 기능은 데이터를 직렬화하고 서명하는 URLSafeTimedSerializer입니다.

# 1. 안전한 서명 및 복호화 (기본)

# python
# from itsdangerous import URLSafeTimedSerializer

# # 서버만 알고 있는 비밀 키 설정
# auth_serializer = URLSafeTimedSerializer("secret-key-configured-by-server")

# # 1. 데이터 서명 (토큰 생성)
# data_to_sign = {"user_id": 5, "email": "[email protected]"}
# token = auth_serializer.dumps(data_to_sign)
# print(token) 
# # 출력: InVzZXJfaWQiOjUsImVtYWlsIjoieHh4QGV4YW1wbGUuY29tIn0.Z0N... (안전한 문자열)

# # 2. 데이터 검증 및 복구 (토큰 해석)
# # 누군가 토큰을 위조했다면 BadSignature 에러가 발생합니다.
# original_data = auth_serializer.loads(token)
# print(original_data)
# # 출력: {'user_id': 5, 'email': '[email protected]'}


def generate_urlsafe_token(_len: int = 32) -> str:
    return secrets.token_urlsafe(_len)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def str_encode(string: str) -> str:
    return base64.b64encode(string.encode()).decode()


def str_decode(string: str) -> str:
    return base64.b64decode(string.encode()).decode()


def normalize_phone_number(phone: str) -> str | None:
    """연락처 정규화"""
    if not phone:
        return None

    # 숫자만 추출
    digits = re.sub(r"\D", "", phone)

    # 10-11자리 확인
    if len(digits) == 10:
        return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11:
        return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"

    return phone  # 형식이 맞지 않으면 원본 반환
