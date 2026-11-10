https://www.youtube.com/watch?v=hj81HI2AsG4&t=203s
FastAPI Full Course | Build Production-Ready Backend (Part 2)
By Asadullah AI / part1: 10:26 part2: 09:12

shoppingmall\_

            13485
            경기 성남시 분당구 판교로 20

insert into addresses(name, recipient, phone, zipcode, address1, address2, is_default, user_id)
values('박선호', '문지향', '010-5211-8936', '13485', '경기 성남시 분당구 판교로 20', '401호', true, 46);

insert into addresses(name, recipient, phone, zipcode, address1, address2, is_default, user_id)
values('박선호', '박다온', '010-5211-8936', '07956', '서울시 양천구 목동중앙남로16다길5 영동빌라', '401호', false, 46);

https://text.ibetter.kr/fastapi-vol1/part-00-%EB%93%A4%EC%96%B4%EA%B0%80%EA%B8%B0
https://text.ibetter.kr/fastapi-vol2/part-00-%EB%93%A4%EC%96%B4%EA%B0%80%EA%B8%B0

https://text.ibetter.kr/fastapi-vol3/part-00-%EB%93%A4%EC%96%B4%EA%B0%80%EA%B8%B0

iBetter Books
https://github.com/sung2ne/textbook-fastapi-vol2
https://github.com/sung2ne/textbook-fastapi-vol3

## fastapi html guide

https://blakecrosley.com/guides/fastapi-htmx

https://medium.com/@bhagyarana80/async-without-tears-10-patterns-for-asyncpg-sqlmodel-72c68aa68f0d
Async Without Tears: 10 Patterns for asyncpg + SQLModel
from medium

https://www.youtube.com/watch?v=-2YpvLCT5F8&list=PLcXyemr8ZeoR82N8uZuG9xVrFIfdnLd72
BJ.11 스택과 큐 설명! 참 쉽죠~~? 기술 문서 읽다가 큐 만났을 때 팁과 스택/큐와 관련된 에러들 그리고 해결책도 설명드려요!!
By 쉬운코드

# https://www.youtube.com/watch?v=CG4WyImo72s

Complete FastAPI Course 2027 | Learn FastAPI to Build Scalable Backend (Beginner to Advanced)
Asadullah AI / 10:26:09 / 2026-10

# https://www.youtube.com/watch?v=PzIF1IAxzaw

Complete FastAPI in 5 Hours — Full CRUD, MySQL Database, Auth & Docker (Beginner to Advanced)
By Genalytiq / 4:33:36

```Python
update_data = post_data.model_dump(exclude_unset=True)
for field, value in update_data.items():
    setattr(post, field, value)
```

# https://www.youtube.com/watch?v=8-5othzDPPQ&list=PL4ZAMI75RNjD1lZhMRbwNpLWzQc4TJpP1&index=3

Authentication & Authorization in FastAPI 🔐 | JWT, OAuth2 & Role-Based Access Explained
By Genalytiq

# https://www.youtube.com/watch?v=hFNnNVawHhk

Redis Full Course 2026 | Caching, Rate Limiting, Pub/Sub
By Sangam Mukherjee

# https://www.youtube.com/watch?v=1BDV1PpByG8

Django vs FastAPI 차이점 | CGI부터 WSGI, ASGI까지
By 코딩하는 초롱

## asyncio.run(run_async_migrations(), loop_factory=asyncio.SelectorEventLoop)

# -------------

## Postgresql 18 in Windows 11

Windows 11 환경에서 PostgreSQL 18의 Windows 서비스를 완전히 제거하고,
개발자가 원할 때만 명령 프롬프트(CMD)를 통해 직접 수동으로 실행하는 방법입니다.

1단계: 기존 PostgreSQL 18 서비스 중지 및 제거

1. 명령 프롬프트(CMD)를 관리자 권한으로 실행합니다.
   (시작 메뉴에서 cmd 검색 후 우클릭 -> '관리자 권한으로 실행')

2. 현재 실행 중인 PostgreSQL 서비스를 중지합니다.

`$> net stop postgresql-x64-18`

3. 윈도우 등록 서비스 목록에서 PostgreSQL 18 서비스를 제거합니다.

`$> sc delete postgresql-x64-18`

2단계: PostgreSQL 직접(수동) 실행하기

서비스를 지웠기 때문에 이제 백그라운드에서 자동 실행되지 않습니다.
대신 PostgreSQL 정식 문서에 명시된 내장 제어 도구인 pg_ctl을 사용하여 직접 실행하고 종료해야 합니다.

① 데이터 디렉터리 경로 파악

일반적인 Windows 18 버전 설치 경로를 기준으로 아래 두 경로가 필요합니다.
본인의 실제 설치 경로에 맞게 확인해 주세요.
• 프로그램(바이너리) 경로: C:\Program Files\PostgreSQL\18\bin
• 데이터(Data) 경로: C:\Program Files\PostgreSQL\18\data

# ② 데이터베스 서버 시작 (Start)

명령 프롬프트를 열고 아래 명령어를 실행하면
PostgreSQL 서버가 독립된 프로세스로 실행됩니다.
Log 파일 생성을 원치 않는다면 -l 옵션 부분을 제외해도 됩니다.

"C:\Program Files\PostgreSQL\18\bin\pg_ctl.exe" start -D "C:\Program Files\PostgreSQL\18\data" -l "C:\Program Files\PostgreSQL\18\data\logfile"

③ 데이터베이스 서버 종료 (Stop)

작업이 끝난 후 안전하게 서버를 종료하려면 아래 명령어를 입력합니다.
-m fast 옵션을 주면 안전하고 빠르게 세션을 종료하고 서버를 닫습니다.

"C:\Program Files\PostgreSQL\18\bin\pg_ctl.exe" stop -D "C:\Program Files\PostgreSQL\18\data" -m fast

# sqlmodel 사용에 관한 좋은 자료나 internet 상의 글 또는 책 추천해줘.

SQLModel은 FastAPI의 제작자(tiangolo)가 만든 라이브러리로, 데이터 검증을 위한 Pydantic과 데이터베이스 매핑을 위한 SQLAlchemy를 하나로 결합한 혁신적인 ORM입니다. 비교적 최신 기술에 속하기 때문에 SQLModel 단독으로 다루는 독립된 종이책보다는 공식 문서, 해외 커뮤니티 아티클, 그리고 FastAPI 중심의 도서를 참고하시는 것이 가장 정확하고 좋습니다.
학습과 실무에 가장 도움되는 유용한 자료들을 추천해 드립니다.

1. 0순위로 봐야 하는 최고의 바이블 (인터넷 공식 문서)

SQLModel은 공식 문서가 워낙 쉽고, 단계별(Tutorial)로 빌드업하는 과정이 매우 훌륭합니다. 책을 사기 전에 반드시 공식 가이드를 정독하는 것을 추천합니다.
• SQLModel 공식 튜토리얼 (영문)
• 특징: 데이터베이스의 기초 개념부터 복잡한 다대다(Many-to-Many) 관계 설정, 상속 구조를 활용한 데이터 모델 분리(HeroCreate, HeroRead 등)까지 소설 읽듯 따라갈 수 있게 구성되어 있습니다.
• 팁: 브라우저 번역 기능을 이용해도 코드 가독성이 좋아 이해하기 매우 쉽습니다.
• FastAPI 공식 문서 내 SQLModel 가이드
• FastAPI 앱 안에서 SQLModel을 사용해 Depends를 통한 비동기 Session 주입 방식이나 의존성 주입 구조(SessionDep)를 관리하는 실제 웹 패턴을 가장 표준적으로 배울 수 있습니다.

2. 추천 서적 (FastAPI와 함께 배우는 에코시스템)

국내외를 막론하고 SQLModel만 단독으로 다루는 책은 드물지만, 현대적인 FastAPI 개발을 다루는 핵심 도서들에서 SQLModel을 비중 있게 채택하고 있습니다.
• 해외 도서: 《FastAPI Development Essentials》 (Katri Peltonen 저, 2026)
• 특징: 최신 아키텍처 패턴을 반영하여 FastAPI 환경에서 Pydantic 데이터 검증과 비동기(Async) 패턴을 포함한 SQLModel 연동 방식을 직관적이고 깊이 있게 다룹니다.
• 해외 도서: 《Building Python Web APIs with FastAPI》 (Abdulazeez 저, Packt)
• 특징: FastAPI로 실제 프로덕션 수준의 API를 개발하는 과정을 담은 책으로, 모던 데이터베이스 연동 장(Chapter)에서 SQLModel을 다루어 실무 아키텍처를 잡는 데 유용합니다.

3. 실무자들의 생생한 팁이 담긴 블로그 및 아티클 추천

실무에서 겪는 한계나 베스트 프랙티스를 파악하는 데는 기술 블로그 글이 유용합니다.
• Medium 아티클: Build a Book Review API with FastAPI and SQLModel
• 비동기 세션 생성, 테이블 초기화, 가벼운 CRUD를 레이어별로 깔끔하게 정리해 둔 입문용 해외 아티클입니다.
• Reddit 커뮤니티 논쟁: r/FastAPI - "Is SQLModel Overrated?"
• 필독 추천: 무조건적인 찬사보다 실무 관점의 비판과 팁을 얻기 좋습니다. SQLModel이 결국 SQLAlchemy와 Pydantic의 얇은 추상화 레이어이기 때문에 발생하는 한계(예: 복잡한 집계 쿼리에서의 제약, table=True일 때 검증 작동 방식 등)와 이를 극복하는 개발자들의 우회 방법들이 잘 정리되어 있습니다.

💡 효과적인 SQLModel 학습을 위한 조언

SQLModel을 깊게 쓰다 보면 결국 내부 기반 기술인 SQLAlchemy(2.0 버전 이상) 문법과 Pydantic(v2)의 특징을 마주하게 됩니다.
따라서 SQLModel을 공부하시다가 복잡한 조인(Join), 서브쿼리, 오늘 질문하신 exec()나 scalar() 같은 실행 메서드의 세부 동작이 막힐 때는 SQLAlchemy 2.0 공식 문서를 검색해 보시는 것이 해결의 가장 빠른 지름길이 될 것입니다.
혹시 지금 개발 중이신 프로젝트가 FastAPI 웹 서버 기반인가요, 혹은 간단한 데이터 가공 스크립트인가요? 프로젝트의 성격에 맞춰 추가로 참고하기 좋은 오픈소스 예제(Boilerplate) 저장소를 추천해 드릴 수도 있습니다!
AI responses may include mistakes. Learn more
•
Reddit·r/FastAPI
SQLModel 너무 과대평가된 거 아님? : r/FastAPI - Reddit
•
GitHub
README.md - fastapi/sqlmodel
•
pythonology
Build a Book Review API with FastAPI and SQLModel
Show all

현재 개발중인 웹앱은 python 3.14, fastapi, sqlmodel, postgresql 18, uv, async mode 기반으로 개발 중이야. 프로젝트의 성격에 맞춰 추가로 참고하기 좋은 오픈소스 예제(Boilerplate) 저장소를 추천해 줘.

독보적으로 트렌디하고 효율적인 모던 스택(Python 3.14, FastAPI, SQLModel, PostgreSQL 18, uv, Async)을 채택하셨네요! 이 최신 아키텍처 환경에서 구조적 설계, 비동기 세션 관리, 패키지 가속 기술을 참고하기 가장 좋은 오픈소스 보일러플레이트 저장소들을 추천해 드립니다.

1. 최적의 아키텍처와 폴더 구조 참고

• tiangolo / full-stack-fastapi-template
• 설명: FastAPI와 SQLModel의 창시자인 tiangolo가 직접 관리하는 공식 풀스택 템플릿입니다.
• 추천 이유: 비록 이 레포지토리 전체는 프론트엔드(가령 React)까지 포함하고 있지만, backend/ 폴더 내부의 구조는 SQLModel 아키텍처의 교과서입니다. 데이터 생성/조회 레이어를 깔끔하게 격리하는 crud.py, 역할별(Request, Response, DB 테이블) 모델을 상속 구조로 설계하는 models.py 관리법 등 다중 환경 배포 구조를 파악할 때 가장 먼저 표준으로 삼아야 할 가이드라인입니다. 최근 uv 생태계로 전면 전환을 완료하여 pyproject.toml과 uv workspace 설계 방식도 참고하기 매우 좋습니다.

2. 순수 Async 모드와 고급 DB 쿼리 패턴 참고

• benavlabs / SQLModel-boilerplate
• 설명: SQLModel 기반으로 완벽한 비동기(Fully Async) 프로덕션 API를 구축하는 데 초점을 맞춘 완성도 높은 저장소입니다.
• 추천 이유: SQLModel은 공식 가이드가 아직 동기(Sync) 위주로 서술되어 있어 비동기 실무 적용 시 헷갈리는 경우가 많은데, 이 보일러플레이트는 ext.asyncio 엔진 구성, 비동기 컨텍스트 세션 주입 방식을 디테일하게 구현해 두었습니다. 특히 복잡한 비동기 페이지네이션(Cursor & Offset)이나 효율적인 비동기 쿼리를 구현하기 위한 fastcrud 계열의 유틸리티 연동 레이어가 훌륭하게 설계되어 있어, 현재 프로젝트의 DB 조회 아키텍처를 잡을 때 큰 힌트를 얻을 수 있습니다.

Python 3.14, FastAPI, SQLModel, PostgreSQL 18, uv, 비동기(Async) 모드의 조합은 현재 파이썬 생태계에서 구성할 수 있는 가장 모던하고 강력한 최첨단 백엔드 스택입니다. 특히 uv를 패키지/프로젝트 관리자로 사용하고 비동기 SQLModel을 PostgreSQL 18과 연동하는 구조에 딱 맞는 최고의 오픈소스 보일러플레이트와 레퍼런스 저장소들을 추천해 드립니다.

1. 공식 최고 존엄 레퍼런스: Full Stack FastAPI Template

FastAPI와 SQLModel의 제작자인 tiangolo가 직접 관리하는 공식 프로덕션 템플릿입니다.
• 저장소 이름: tiangolo/full-stack-fastapi-template
• 왜 봐야 할까요?
• SQLModel의 정석 패턴: 대규모 프로젝트에서 SQLModel을 어떻게 구조화하는지(HeroBase, HeroCreate, HeroUpdate, HeroPublic 등 데이터 검증과 DB 모델의 분리) 보여주는 가장 완벽한 교과서입니다.
• 강력한 레퍼런스: 공식 템플릿인 만큼 최신 모던 파이썬 표준과 의존성 주입(Dependency Injection) 패턴을 가장 정확하게 구현하고 있습니다.

2. 최첨단 스택 마이그레이션 참고: FastAPI-Alembic-Docker

모던 툴체인(uv, 비동기)과 데이터베이스 고도화에 초점을 맞춘 프로덕션용 보일러플레이트입니다.
• 저장소 이름: zhanymkanov/fastapi-alembic-docker (또는 유사한 모던 비동기 SQLModel 템플릿들)
• 왜 봐야 할까요?
• uv 패키지 관리 완벽 지원: uv pip sync 및 pyproject.toml을 기반으로 한 초고속 빌드 및 가상환경 격리 구조를 참고하기 좋습니다.
• 비동기(Async) SQLModel과 Alembic의 결합: PostgreSQL 환경에서 비동기 세션(AsyncSession)을 다룰 때 발생하는 이 마이그레이션 툴(Alembic)과의 연동 에러를 해결해 둔 구조입니다. PostgreSQL 18의 논리적 복제나 고급 인덱스를 Alembic과 사용할 때 큰 도움이 됩니다.

3. 아키텍처 고도화 참고: FastAPI + SQLModel 비동기 특화 저장소

프로젝트 규모가 커질 때 컴포넌트를 분리하는 클린 아키텍처/레포지토리 패턴 지향 템플릿입니다.
• 키워드로 검색 가능한 GitHub 레포지토리: fastapi-sqlmodel-async-boilerplate
• 왜 봐야 할까요?
• Strict Async 모드: 라우터(@router.get)부터 서비스 레이어, 데이터베이스 실행부(await session.exec())까지 단 하나의 블로킹 I/O도 허용하지 않는 완벽한 비동기 파이프라인을 보여줍니다.
• PostgreSQL 성능 최적화: 커넥션 풀링(AsyncConnectionPool) 설정과 복잡한 관계형 조인 성능을 극대화하는 예제가 포함되어 있습니다.

💡 Python 3.14 + PostgreSQL 18 환경을 위한 꿀팁

• Python 3.14 성능 이점 극대화: 3.14 버전은 인터프리터 수준에서 비동기 루프 성능이 대폭 개선되었습니다. SQLModel 모델 내부에서 타입 힌팅을 작성할 때 최신 Pep 표준(예: | 연산자를 활용한 Union 처리, Deferred Type Evaluation 등)을 적극 반영하여 코드를 간결하게 유지하세요.
• PostgreSQL 18 비동기 드라이버: 반드시 asyncpg 드라이버를 기반으로 SQLModel 엔진을 생성해야 합니다. (postgresql+asyncpg://...) PostgreSQL 18에서 향상된 동시성 처리 성능을 asyncpg가 온전히 리소스를 낭비하지 않고 비동기로 받아쳐 줄 수 있습니다.
혹시 이 저장소들을 참고하면서 Alembic을 활용한 비동기 마이그레이션 파일 설정이나, uv 환경에서 도커(Docker) 멀티 스테이지 빌드를 구성하는 데 어려움이 있으시다면 언제든 말씀해 주세요. 관련 설정 코드를 바로 짜드릴 수 있습니다!

# toss payments 가입

sunho.charm@gmail.com daonpark21c@A

# 주문서형·결제창형 연동 키 - 주문서형·결제창형 결제를 연동할 때 사용해요

TOSS_CLIENT_KEY=test_gck_docs_Ovk5rk1EwkEbP0W43n07xlzm # for frontend
TOSS_SECRET_KEY=test_gsk_docs_OaPz8L5KdmQXkzRz3y47BMw6 # for backend
