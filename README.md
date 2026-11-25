# virtual-college-agent

이 레포는 AI 에이전트를 가상대학 Agent-native College에 연결하는 스킬과 MCP 설정이다. 에이전트는 포털 화면을 쓰지 않고 서버의 MCP 도구나 REST API를 호출한다. 사람은 에이전트가 준 링크에서 한 번 로그인하고, 연결은 30일 동안 유지된다.

서버 주소는 `VIRTUAL_COLLEGE_URL` 환경 변수의 값이다. 값이 없으면 `https://college.jblee.app`을 쓴다.

## 1. MCP 서버 등록

먼저 MCP 서버를 등록한다. MCP 클라이언트는 세션을 유지하므로 조회 한 번에 0.3~0.5초가 걸린다. MCP 없이 `college.py`로 호출하면 호출마다 Python을 새로 실행하고 TLS 연결을 새로 맺어서 1.1~1.4초가 걸린다.

Claude Code에서는 아래 명령으로 등록한다.

```sh
claude mcp add --transport http -s user virtual-college https://college.jblee.app/mcp
```

등록한 뒤 Claude Code에서 `/mcp`를 입력하고, `virtual-college`를 고르고, Authenticate를 누른다. 열린 브라우저에서 로그인하면 연결된다. `claude mcp get virtual-college`가 `✓ Connected`를 출력하면 등록이 끝난 것이다.

다른 클라이언트는 아래처럼 등록한다.

| 클라이언트 | 방법 |
|---|---|
| Cursor처럼 JSON 파일로 설정하는 클라이언트 | `.cursor/mcp.json` 같은 설정 파일에 `{ "mcpServers": { "virtual-college": { "url": "https://college.jblee.app/mcp" } } }`를 넣는다 |
| ChatGPT, Grok 같은 원격 MCP 커넥터 앱 | `https://college.jblee.app/mcp`를 커넥터로 등록한다. 서버는 OAuth와 동적 클라이언트 등록을 지원한다 |

## 2. 스킬 설치

스킬은 에이전트가 따를 작업 순서를 담고 있다. 에이전트는 가이드를 읽고, 학사 시각을 확인하고, 변경을 미리보기로 검사한 다음에 실행한다.

| 에이전트 | 방법 |
|---|---|
| Claude Code | `/plugin marketplace add jinbumlee95/virtual-college-agent`를 실행한 뒤 `/plugin install virtual-college-agent`를 실행한다. 플러그인은 MCP 서버도 함께 등록한다 |
| Codex, Cursor, Copilot, Gemini CLI 등 | `npx skills add jinbumlee95/virtual-college-agent --skill college` |
| 스킬을 읽지 않는 코딩 에이전트 | 이 레포를 작업 폴더에 둔다. `AGENTS.md`가 스킬 파일을 가리킨다 |

MCP를 쓸 수 없는 환경에서는 스킬의 `scripts/college.py`가 REST API로 서버를 호출한다.

## 구성

- `skills/college/SKILL.md`는 에이전트가 읽는 지시 파일이다. 모든 클라이언트가 이 파일 하나를 읽는다.
- `skills/college/scripts/college.py`는 MCP가 없을 때 로그인하고 API를 호출하는 스크립트다. Python 3 표준 라이브러리만 쓴다. 토큰은 `~/.virtual-college/`에 저장하고 화면에 출력하지 않는다.
- `.mcp.json`, `.claude-plugin/`, `.codex-plugin/`, `.cursor-plugin/`, `plugin.json`은 클라이언트별 설치 정보다.
