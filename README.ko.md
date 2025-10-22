[日本語](README.ja.md)

# Python용 Jules Agent SDK

> **면책 조항**: 이것은 Python으로 된 Jules API SDK 래퍼의 오픈 소스 구현이며 Google과는 아무런 관련이 없습니다. 공식 API는 다음을 방문하십시오: https://developers.google.com/jules/api/

Jules API용 Python SDK. Jules 세션, 활동 및 소스 작업을 위한 간단한 인터페이스입니다.

![Jules](jules.png)

## 빠른 시작

### 설치

```bash
pip install jules-agent-sdk
```

### 기본 사용법

```python
from jules_agent_sdk import JulesClient

# API 키로 초기화
client = JulesClient(api_key="your-api-key")

# 소스 목록 가져오기
sources = client.sources.list_all()
print(f"{len(sources)}개의 소스를 찾았습니다")

# 세션 생성
session = client.sessions.create(
    prompt="인증 모듈에 오류 처리 추가",
    source=sources[0].name,
    starting_branch="main"
)

print(f"세션이 생성되었습니다: {session.id}")
print(f"다음에서 보기: {session.url}")

client.close()
```

## 구성

API 키를 환경 변수로 설정하십시오:

```bash
export JULES_API_KEY="your-api-key-here"
```

[Jules 대시보드](https://jules.google.com)에서 API 키를 받으십시오.

## 기능

### API 범위
- **세션**: 생성, 가져오기, 목록, 계획 승인, 메시지 보내기, 완료 대기
- **활동**: 자동 페이지 매김으로 가져오기, 목록
- **소스**: 자동 페이지 매김으로 가져오기, 목록


## 문서

- **[빠른 시작](docs/QUICKSTART.md)** - 시작 안내서
- **[전체 문서](docs/README.md)** - 전체 API 참조
- **[개발 안내서](docs/DEVELOPMENT.md)** - 기여자를 위해

## 사용 예

### 컨텍스트 관리자 (권장)

```python
from jules_agent_sdk import JulesClient

with JulesClient(api_key="your-api-key") as client:
    sources = client.sources.list_all()

    session = client.sessions.create(
        prompt="인증 버그 수정",
        source=sources[0].name,
        starting_branch="main"
    )

    print(f"생성됨: {session.id}")
```

### Async/Await 지원

```python
import asyncio
from jules_agent_sdk import AsyncJulesClient

async def main():
    async with AsyncJulesClient(api_key="your-api-key") as client:
        sources = await client.sources.list_all()

        session = await client.sessions.create(
            prompt="단위 테스트 추가",
            source=sources[0].name,
            starting_branch="main"
        )

        # 완료 대기
        completed = await client.sessions.wait_for_completion(session.id)
        print(f"완료: {completed.state}")

asyncio.run(main())
```

### 오류 처리

```python
from jules_agent_sdk import JulesClient
from jules_agent_sdk.exceptions import (
    JulesAuthenticationError,
    JulesNotFoundError,
    JulesValidationError,
    JulesRateLimitError
)

try:
    client = JulesClient(api_key="your-api-key")
    session = client.sessions.create(
        prompt="내 작업",
        source="sources/invalid-id"
    )
except JulesAuthenticationError:
    print("잘못된 API 키")
except JulesNotFoundError:
    print("소스를 찾을 수 없음")
except JulesValidationError as e:
    print(f"유효성 검사 오류: {e.message}")
except JulesRateLimitError as e:
    retry_after = e.response.get("retry_after_seconds", 60)
    print(f"속도 제한. {retry_after}초 후에 다시 시도하십시오")
finally:
    client.close()
```

### 사용자 지정 구성

```python
client = JulesClient(
    api_key="your-api-key",
    timeout=60,              # 요청 시간 초과(초) (기본값: 30)
    max_retries=5,           # 최대 재시도 횟수 (기본값: 3)
    retry_backoff_factor=2.0 # 백오프 승수 (기본값: 1.0)
)
```

다음에 대해 자동으로 재시도합니다:
- 네트워크 오류 (연결 문제, 시간 초과)
- 서버 오류 (5xx 상태 코드)

다음에 대해서는 재시도하지 않습니다:
- 클라이언트 오류 (4xx 상태 코드)
- 인증 오류

## API 참조

### 세션

```python
# 세션 생성
session = client.sessions.create(
    prompt="작업 설명",
    source="sources/source-id",
    starting_branch="main",
    title="선택적 제목",
    require_plan_approval=False
)

# 세션 가져오기
session = client.sessions.get("session-id")

# 세션 목록
result = client.sessions.list(page_size=10)
sessions = result["sessions"]

# 계획 승인
client.sessions.approve_plan("session-id")

# 메시지 보내기
client.sessions.send_message("session-id", "추가 지침")

# 완료 대기
completed = client.sessions.wait_for_completion(
    "session-id",
    poll_interval=5,
    timeout=600
)
```

### 활동

```python
# 활동 가져오기
activity = client.activities.get("session-id", "activity-id")

# 활동 목록 (페이지 매김)
result = client.activities.list("session-id", page_size=20)

# 모든 활동 목록 (자동 페이지 매김)
all_activities = client.activities.list_all("session-id")
```

### 소스

```python
# 소스 가져오기
source = client.sources.get("source-id")

# 소스 목록 (페이지 매김)
result = client.sources.list(page_size=10)

# 모든 소스 목록 (자동 페이지 매김)
all_sources = client.sources.list_all()
```

## 로깅

요청 세부 정보를 보려면 로깅을 활성화하십시오:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("jules_agent_sdk")
```

## 테스트

```bash
# 모든 테스트 실행
pytest

# 커버리지와 함께 실행
pytest --cov=jules_agent_sdk

# 특정 테스트 실행
pytest tests/test_client.py -v
```

## 프로젝트 구조

```
jules-api-python-sdk/
├── src/jules_agent_sdk/
│   ├── client.py              # 메인 클라이언트
│   ├── async_client.py        # 비동기 클라이언트
│   ├── base.py                # 재시도가 포함된 HTTP 클라이언트
│   ├── models.py              # 데이터 모델
│   ├── sessions.py            # 세션 API
│   ├── activities.py          # 활동 API
│   ├── sources.py             # 소스 API
│   └── exceptions.py          # 사용자 지정 예외
├── tests/                     # 테스트 스위트
├── examples/                  # 사용 예
│   ├── simple_test.py         # 빠른 시작
│   ├── interactive_demo.py    # 전체 데모
│   ├── async_example.py       # 비동기 사용법
│   └── plan_approval_example.py
├── docs/                      # 문서
└── README.md
```

## 기여

개발 설정 및 지침은 [DEVELOPMENT.md](docs/DEVELOPMENT.md)를 참조하십시오.

## 라이선스

MIT 라이선스 - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하십시오.

## 지원

- **문서**: [docs/](docs/) 폴더 참조
- **예**: [examples/](examples/) 폴더 참조
- **문제**: GitHub 문제 열기

## 다음 단계

1. `python examples/simple_test.py`를 실행하여 사용해 보십시오
2. 자세한 내용은 [docs/QUICKSTART.md](docs/QUICKSTART.md)를 읽으십시오
3. 더 많은 사용 사례는 [examples/](examples/) 폴더를 확인하십시오