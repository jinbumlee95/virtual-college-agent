# virtual-college-agent

가상대학 Agent-native College용 MCP 설정과 에이전트 스킬이다. 서버는 `https://college.jblee.app`이다. `VIRTUAL_COLLEGE_URL` 환경 변수로 바꿀 수 있다.

## 설치

에이전트에게 아래 문장을 보낸다.

```text
https://github.com/jinbumlee95/virtual-college-agent README의 "에이전트 설치 절차"대로 MCP 서버 등록과 스킬 설치를 해줘.
```

## 에이전트 설치 절차

설치하는 에이전트가 아래 절차를 따른다. 사람은 마지막 로그인만 한다.

### Claude Code

1. 아래 명령을 실행한다. 플러그인이 MCP 서버 `virtual-college`와 스킬 `college`를 함께 설치한다.

   ```sh
   claude plugin marketplace add jinbumlee95/virtual-college-agent
   claude plugin install virtual-college-agent@virtual-college-agent
   ```

2. `claude mcp list`를 실행한다. 플러그인 서버는 `plugin:virtual-college-agent:virtual-college`로 나온다.
   - 주소가 `https://college.jblee.app/mcp`가 아니면 `VIRTUAL_COLLEGE_URL` 환경 변수가 설정된 것이다. 사람에게 알린다.
   - `claude mcp add`로 따로 등록한 `virtual-college`가 있으면 같은 서버가 두 번 등록된 것이다. 사람에게 알리고 `claude mcp remove virtual-college -s user`로 하나를 지운다.
3. 2번에서 환경 변수를 바꾸거나 지웠다면 사람에게 Claude Code와 터미널을 모두 닫고 새 터미널에서 `claude`를 실행하라고 안내한다. 이미 열린 터미널은 이전 값을 유지한다. 그다음 `/mcp`를 입력하고, `plugin:virtual-college-agent:virtual-college`를 골라 Authenticate를 누르라고 안내한다. 브라우저에서 로그인하면 30일 동안 연결된다.
4. 사람이 로그인했다고 하면 `calendar_now` 도구를 호출한다. `ok=true`면 설치가 끝난 것이다.

### 그 밖의 에이전트

1. 스킬을 설치한다.

   ```sh
   npx skills add jinbumlee95/virtual-college-agent --skill college
   ```

2. 그 에이전트의 MCP 설정에 원격 HTTP 서버 `https://college.jblee.app/mcp`를 `virtual-college`라는 이름으로 추가한다. Cursor는 `.cursor/mcp.json`에 아래 내용을 넣는다.

   ```json
   { "mcpServers": { "virtual-college": { "url": "https://college.jblee.app/mcp" } } }
   ```

3. 사람에게 그 에이전트의 MCP 인증 화면에서 로그인하라고 안내한다. 서버는 OAuth와 동적 클라이언트 등록을 지원한다.
4. `calendar_now` 도구를 호출해 `ok=true`인지 확인한다.

MCP를 쓸 수 없는 에이전트는 2번부터 대신 `python skills/college/scripts/college.py login`을 실행하고, 출력된 링크를 사람에게 준다. 이 스크립트는 REST API를 호출한다.

### ChatGPT, Grok 같은 커넥터 앱

사람이 `https://college.jblee.app/mcp`를 커넥터로 등록하고 로그인한다.

## 파일

- `skills/college/SKILL.md`: 에이전트 작업 지시
- `skills/college/scripts/college.py`: MCP 없이 로그인하고 REST API를 호출하는 스크립트. Python 3 표준 라이브러리만 쓰고, 토큰은 `~/.virtual-college/`에 저장한다.
- `.mcp.json`, `.claude-plugin/`, `.codex-plugin/`, `.cursor-plugin/`, `plugin.json`: 클라이언트별 설치 정보
