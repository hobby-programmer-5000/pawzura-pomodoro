[English](BUILD.md) · [한국어](BUILD.ko.md)

# Windows 포터블 빌드

알파 릴리스는 `PawzuraPomodoro.exe`와 `_internal` 폴더가 들어 있는 Windows x64 ZIP이에요. 쓰기 가능한 폴더에 ZIP 전체를 풀고 EXE를 실행하세요. Python 설치는 필요 없어요. EXE와 폴더를 함께 유지해 주세요. 실행 파일에는 코드 서명이 없어요. 이 저장소의 Releases에서 내려받고, 서명 없는 알파 앱에 Windows 평판 안내가 나타나면 공개된 SHA256을 확인한 뒤 실행 여부를 결정하세요.

설정은 사용자별 `%APPDATA%/Pawzura/Pomodoro.ini`에 저장돼요. 새 설정은 영어, 작업 50분·휴식 10분, 걷기 켜기, 시각 효과 켜기예요. 컴패니언/트레이 메뉴에서 종료하세요. 삭제하려면 종료 후 압축을 푼 폴더를 지우면 돼요. 환경설정도 초기화하려면 설정 파일을 별도로 삭제해 주세요.

## 검토된 소스로 빌드

Windows x64와 표준 CPython 3.14를 사용하세요. Conda Qt 환경은 사용하지 않아요. 깨끗한 체크아웃에서 실행해요.

```powershell
py -3.14 -m venv .venv-standard
.\.venv-standard\Scripts\python.exe -m pip install -r requirements-build.txt
.\.venv-standard\Scripts\python.exe -m unittest discover -s tests -v
.\.venv-standard\Scripts\python.exe -m pomodoro --smoke-check --smoke-output .cache/source-smoke.json
.\.venv-standard\Scripts\python.exe scripts/build.py --dist-dir dist/0.1.0a1
```

검토한 변경을 먼저 커밋해 주세요. 빌더는 미커밋 변경이나 이미 존재하는 출력 폴더를 거부해요. 재시도마다 새 출력 이름을 사용하고 이전 증거는 보존해요. 패키징 도구는 PyInstaller 6.22.3과 hooks 2026.9에 고정하며 Qt/PySide/Shiboken은 기존 6.12.0을 유지해요. `BUILD-INFO.json`에는 실제 Python/의존성 버전, Git 커밋, 소스 해시를 기록해요. 같은 절차로 다시 만들 수 있지만 Windows 바이너리가 바이트 단위로 동일하다고 보장하지는 않아요.

빌드는 토마토 아이콘, 모니터별 DPI를 인식하는 창 모드 폴더형 실행 파일, 구성요소 고지, 파일 해시 목록, ZIP과 SHA256을 만들어요. Qt는 동적 연결을 유지하며 단일 EXE로 압축하지 않아요. 빌더는 내장 Python 코드와 커밋 소스를 비교하고 Python PATH가 없는 환경에서 임시 설정으로 EXE를 실행해요. 기본값, 두 언어, 작업/휴식/대기 전환, 일시정지/재개, 다섯 미리보기, 모든 화면의 버튼 배치, 작업 확인, 지난 콜백 무효화, 옵션, 저장을 검사해요. 진단은 시간을 가속하므로 실제 50/10분 재검사가 아니에요.

빌드 증거는 `build/<출력이름>/`에 `frozen-smoke.json`, `validation.json` 등으로 남고 Git과 릴리스에서 제외돼요. 빌드나 진단이 실패하면 게시를 중단하고 해당 오류를 확인·수정한 뒤 새 폴더에 다시 빌드하세요.

## 내려받은 압축 파일 확인

```powershell
Get-FileHash .\PawzuraPomodoro-0.1.0a1-windows-x64.zip -Algorithm SHA256
```

릴리스의 `.sha256` 파일과 비교해 주세요. 해시 일치는 파일의 동일성을 확인하며 게시자의 신뢰도를 판정하지는 않아요. 관리자는 같은 소스 체크아웃에 빌드 의존성을 설치한 뒤 `python scripts/check_distribution.py <압축을푼폴더> --embedded`로도 확인할 수 있어요.

일반 환경설정을 읽지 않고 해당 EXE를 진단하려면 실행해요.

```powershell
.\PawzuraPomodoro\PawzuraPomodoro.exe --smoke-check --smoke-output "$env:TEMP\pomodoro-smoke.json"
Get-Content "$env:TEMP\pomodoro-smoke.json"
```

보고서에 `PASS`, `frozen: true`, 버전 `0.1.0a1`이 있어야 해요. 진단 창은 잠깐 나타난 뒤 닫혀요. 트레이 OS 입력, 잠금, 절전, RDP, 모니터 연결 변경은 이 명령으로 검사하지 않아요. [결과와 제한](RESULTS.ko.md), [수동 시나리오](TESTING.ko.md)를 참고하세요. Windows 11 소스 세션 결과만으로 배포 EXE의 호환성을 확정하지 않으며 해당 바이너리를 Windows 11에서 별도로 확인해야 해요.

일반 메뉴·트레이·인스턴스 잠금을 사용하는 별도 프로필로 실행하려면 `PawzuraPomodoro.exe --settings-file <새폴더>/settings.ini`를 사용하세요. 전용 폴더를 지정해 주세요. 같은 폴더의 프로필은 잠금을 공유해요. 기본 설정 위치는 Qt가 Windows의 알려진 폴더 API로 결정하므로 APPDATA/LOCALAPPDATA 환경변수 변경에 의존하지 마세요.

## 구성요소와 교체 권리

원본 코드는 MIT를 유지해요. Qt/PySide/Shiboken은 해당 LGPLv3 선택지로 사용하며 고지와 원본 출처별 문서는 `licenses/`에 있어요. 변경하지 않은 대응 소스는 [Qt Base v6.12.0](https://github.com/qt/qtbase/archive/refs/tags/v6.12.0.tar.gz), [Qt SVG v6.12.0](https://github.com/qt/qtsvg/archive/refs/tags/v6.12.0.tar.gz), [PySide/Shiboken v6.12.0](https://github.com/pyside/pyside-setup/archive/refs/tags/v6.12.0.tar.gz)에서 받을 수 있으며 릴리스에도 제공해요. 고정된 Pawzura 소스와 MIT 고지는 [외부 구성요소 문서](THIRD-PARTY-NOTICES.ko.md)에 연결돼 있어요.

`_internal`의 호환되는 Qt/PySide/Shiboken DLL/PYD를 검사·교체하고 라이브러리 수정 디버깅에 필요한 역공학을 할 수 있어요. 아키텍처와 Python/Qt ABI를 맞추고 백업 후 진단을 다시 실행하세요. 서명이나 런처 검사가 수정 라이브러리 실행을 차단하지 않으며 선택적 해시 검사기는 변경을 보고해요. 재배포 시 고지와 대응 소스 접근을 유지하세요. 구성요소 의무는 앱의 MIT와 별개예요. [Qt LGPL 안내](https://www.qt.io/development/open-source-lgpl-obligations)와 [PyInstaller 예외](https://pyinstaller.org/en/stable/license.html)를 참고하세요.
