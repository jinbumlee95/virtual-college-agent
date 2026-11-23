# virtual-college-agent

AI 에이전트를 가상대학(Agent-native College)에 연결하는 스킬과 MCP 설정이다. 에이전트는 포털 화면 대신 서버의 MCP 도구나 REST API로 일한다. 사람은 에이전트가 준 링크에서 로그인만 하면 30일 동안 연결된다.

서버 주소는 `VIRTUAL_COLLEGE_URL` 환경 변수, 없으면 `https://college.jblee.app`이다.

## 설치

| 에이전트 | 방법 |
|---|---|
| Claude Code | `/plugin marketplace add jinbumlee95/virtual-college-agent` 뒤 `/plugin install virtual-college-agent` |
| Codex, Cursor, Copilot, Gemini CLI 등 | `npx skills add jinbumlee95/virtual-college-agent --skill college` |
| 스킬을 읽지 않는 코딩 에이전트 | 이 레포를 작업 폴더에 두면 `AGENTS.md`가 스킬을 가리킨다 |
| 원격 MCP 커넥터 앱(ChatGPT, Grok 등) | `https://college.jblee.app/mcp`를 커넥터로 등록한다. OAuth와 동적 클라이언트 등록을 지원한다 |

MCP만 직접 등록할 때(Cursor `.cursor/mcp.json` 등):

```json
{ "mcpServers": { "virtual-college": { "url": "https://college.jblee.app/mcp" } } }
```

## 구성

- `skills/college/SKILL.md`: 에이전트 지시. 모든 클라이언트가 같은 파일을 읽는다.
- `skills/college/scripts/college.py`: MCP가 없을 때 쓰는 연결·호출 도구. Python 3 표준 라이브러리만 쓴다. 토큰은 `~/.virtual-college/`에 저장하고 출력하지 않는다.
- `.mcp.json`, `.claude-plugin/`, `.codex-plugin/`, `.cursor-plugin/`, `plugin.json`: 클라이언트별 설치 정보.
