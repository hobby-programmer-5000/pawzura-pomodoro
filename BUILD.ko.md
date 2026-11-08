[English](BUILD.md) · [한국어](BUILD.ko.md)

# Windows 포터블 빌드

Windows x64 ZIP과 별도 단일 EXE 중에서 선택하세요. ZIP은 전체를 풀고 `PawzuraPomodoro.exe`를 실행하며 `_internal` 폴더를 함께 유지해요. `PawzuraPomodoro-0.1.0-windows-x64.exe` 단일 파일은 동반 폴더가 필요 없어요. 둘 다 Python 설치 없이 실행해요. 단일 파일은 실행 중 임시 폴더에 내장 런타임을 풀기 때문에 첫 시작이 더 걸릴 수 있어요. 실행 파일에는 코드 서명이 없어요. 이 저장소의 Releases에서 내려받고, 서명 없는 앱에 Windows 평판 안내가 나타나면 공개된 SHA256을 확인한 뒤 실행 여부를 결정하세요.

일반 배포본은 사용자별 고정 경로 `%APPDATA%/PawzuraPomodoro/Desktop.ini`를 공유해요. 소스 실행은 같은 폴더의 `Development.ini`를 사용해요. 이전 알파 1/소스 시험의 `%APPDATA%/Pawzura/Pomodoro.ini`는 보존하고 자동으로 가져오지 않아요. 유효한 1분 시험 값이 새 배포 앱의 기본값이 되지 않게 분리했어요. 새 배포 프로필은 영어, 작업 50분·휴식 10분, 걷기·효과 켜기예요. 이후 바꾼 값은 업데이트 후에도 유지되고 ZIP과 단일 EXE가 공유해요. 휴식 시간 옆 **50 / 10** 버튼은 현재 타이머를 중단하지 않고 다음 구간부터 기본 시간을 복원해요.

## 검토된 소스로 빌드

Windows x64와 표준 CPython 3.14를 사용하세요. Conda Qt 환경은 사용하지 않아요. 깨끗한 체크아웃에서 실행해요.

```powershell
py -3.14 -m venv .venv-standard
.\.venv-standard\Scripts\python.exe -m pip install -r requirements-build.txt
.\.venv-standard\Scripts\python.exe -m unittest discover -s tests -v
.\.venv-standard\Scripts\python.exe -m pomodoro --smoke-check --smoke-output .cache/source-smoke.json
.\.venv-standard\Scripts\python.exe scripts/build.py --dist-dir dist/0.1.0 --single-exe
```

검토한 변경을 먼저 커밋해 주세요. 빌더는 미커밋 변경이나 이미 존재하는 출력 폴더를 거부해요. 재시도마다 새 출력 이름을 사용하고 이전 증거는 보존해요. 패키징 도구는 PyInstaller 6.22.3과 hooks 2026.9에 고정하며 Qt/PySide/Shiboken은 기존 6.12.0을 유지해요. `BUILD-INFO.json`에는 실제 Python/의존성 버전, Git 커밋, 소스 해시를 기록해요. 같은 절차로 다시 만들 수 있지만 Windows 바이너리가 바이트 단위로 동일하다고 보장하지는 않아요.

빌드는 토마토 아이콘, 모니터별 DPI를 인식하는 창 모드 폴더형 실행 파일, 구성요소 고지, 파일 해시 목록, ZIP과 SHA256을 만들어요. 두 형식 모두 Qt를 동적으로 연결해요. ZIP은 라이브러리를 직접 교체할 수 있고, 단일 EXE는 같은 통합 런타임을 임시로 풀며 고지·빌드 정보·페이로드 해시를 내장해요. **옵션 > 라이선스**에서 두 형식 모두 고지와 해당 소스 링크를 열 수 있어요. 빌더는 내장 Python 코드와 커밋 소스를 비교하고 Python PATH가 없는 환경에서 임시 설정으로 EXE를 실행해요. 기본값, 두 언어, 작업/휴식/대기 전환, 일시정지/재개, 다섯 미리보기, 모든 화면의 버튼 배치, 작업 확인, 지난 콜백 무효화, 옵션, 저장을 검사해요. 진단은 시간을 가속하므로 실제 50/10분 재검사가 아니에요.

빌드 증거는 `build/<출력이름>/`에 `frozen-smoke.json`, `validation.json` 등으로 남고 Git과 릴리스에서 제외돼요. 빌드나 진단이 실패하면 게시를 중단하고 해당 오류를 확인·수정한 뒤 새 폴더에 다시 빌드하세요.

## 내려받은 압축 파일 확인

```powershell
Get-FileHash .\PawzuraPomodoro-0.1.0-windows-x64.zip -Algorithm SHA256
```

릴리스의 `.sha256` 파일과 비교해 주세요. 해시 일치는 파일의 동일성을 확인하며 게시자의 신뢰도를 판정하지는 않아요. 관리자는 같은 소스 체크아웃에 빌드 의존성을 설치한 뒤 `python scripts/check_distribution.py <압축을푼폴더> --embedded`로도 확인할 수 있어요.

일반 환경설정을 읽지 않고 해당 EXE를 진단하려면 실행해요.

```powershell
.\PawzuraPomodoro\PawzuraPomodoro.exe --smoke-check --smoke-output "$env:TEMP\pomodoro-smoke.json"
Get-Content "$env:TEMP\pomodoro-smoke.json"
```

보고서에 `PASS`, `frozen: true`, 버전 `0.1.0`이 있어야 해요. 진단 창은 잠깐 나타난 뒤 닫혀요. 트레이 OS 입력, 잠금, 절전, RDP, 모니터 연결 변경은 이 명령으로 검사하지 않아요. [결과와 제한](RESULTS.ko.md), [수동 시나리오](TESTING.ko.md)를 참고하세요. Windows 11 소스 세션 결과만으로 배포 EXE의 호환성을 확정하지 않으며 해당 바이너리를 Windows 11에서 별도로 확인해야 해요.

일반 메뉴·트레이·인스턴스 잠금을 사용하되 Windows 자동 시작 등록은 비활성화한 별도 프로필로 실행하려면 `PawzuraPomodoro.exe --settings-file <새폴더>/settings.ini`를 사용하세요. 전용 폴더를 지정해 주세요. 같은 폴더의 프로필은 잠금을 공유해요. 기본 설정 위치는 Qt가 Windows의 알려진 폴더 API로 결정하므로 APPDATA/LOCALAPPDATA 환경변수 변경에 의존하지 마세요.

## 구성요소와 교체 권리

원본 코드는 MIT를 유지해요. Qt/PySide/Shiboken은 해당 LGPLv3 선택지로 사용하며 고지와 원본 출처별 문서는 `licenses/`에 있어요. 변경하지 않은 대응 소스는 [Qt Base v6.12.0](https://github.com/qt/qtbase/archive/refs/tags/v6.12.0.tar.gz), [Qt SVG v6.12.0](https://github.com/qt/qtsvg/archive/refs/tags/v6.12.0.tar.gz), [PySide/Shiboken v6.12.0](https://github.com/pyside/pyside-setup/archive/refs/tags/v6.12.0.tar.gz)에서 받을 수 있으며 릴리스에도 제공해요. 고정된 Pawzura 소스와 MIT 고지는 [외부 구성요소 문서](THIRD-PARTY-NOTICES.ko.md)에 연결돼 있어요.

`_internal`의 호환되는 Qt/PySide/Shiboken DLL/PYD를 검사·교체하고 라이브러리 수정 디버깅에 필요한 역공학을 할 수 있어요. 아키텍처와 Python/Qt ABI를 맞추고 백업 후 진단을 다시 실행하세요. 서명이나 런처 검사가 수정 라이브러리 실행을 차단하지 않으며 선택적 해시 검사기는 변경을 보고해요. 재배포 시 고지와 대응 소스 접근을 유지하세요. 구성요소 의무는 앱의 MIT와 별개예요. [Qt LGPL 안내](https://www.qt.io/development/open-source-lgpl-obligations)와 [PyInstaller 예외](https://pyinstaller.org/en/stable/license.html)를 참고하세요.

## Windows 자동 시작

일반 배포 실행에서 **옵션 > 일반 > Windows 로그인 시 자동 시작**을 켜세요. 기본값은 꺼짐이에요. 앱의 현재 사용자 `HKCU/Software/Microsoft/Windows/CurrentVersion/Run` 값 하나만 만들며 관리자 권한은 필요 없어요. 단일 EXE도 임시 파일이 아닌 외부 EXE의 고정 경로를 따옴표로 처리하고 `--startup`을 추가해요. 중복 로그인 실행은 조용히 종료돼요. 알 수 없는 기존 값은 보존하고 접근 실패를 알려줘요.

자동 시작을 켜기 전에 EXE를 계속 사용할 폴더에 보관하세요. 이동·삭제 전에는 옵션을 끄고, 버전 이름이 다른 단일 EXE로 교체한 뒤에는 껐다 켜서 새 경로를 등록하세요. 소스 실행과 `--settings-file` 시험 프로필에서는 이 옵션이 비활성화돼요. 삭제할 때는 자동 시작을 끄고 트레이/컴패니언 메뉴로 종료한 뒤 ZIP 폴더나 단일 파일을 지우세요. 설정까지 초기화하려는 경우에만 Desktop.ini도 삭제해 주세요.

## 단일 파일의 라이브러리 재결합

단일 파일에는 동적 라이브러리가 내장돼 있어 ZIP과 교체 방법이 달라요. 해당 앱 코드·빌드 스크립트·요구사항은 릴리스 소스 압축 파일이나 **옵션 > 라이선스**의 정확한 커밋 링크에서 제공해요. LGPL 대응 라이브러리 소스는 각 릴리스의 Qt Base/SVG/PySide 압축 파일이에요. 재배포 대상에게도 고지와 같은 소스 접근을 유지하세요.

수정한 결합물을 만들려면 정확한 소스 리비전을 clone하고 위의 표준 빌드 환경을 만든 뒤, 빌드 환경의 해당 Qt/PySide/Shiboken 공유 라이브러리를 수정한 ABI 호환 6.12.0 버전으로 교체하세요. 앱/빌드 변경은 커밋하고 `python scripts/build.py --dist-dir dist/custom-name --single-exe --modified-runtime`을 실행하면 수정 런타임 여부를 기록하고 해당 라이브러리를 다시 묶어요. 재빌드 서명은 선택이며 앱이 저희 서명 키를 요구하지 않아요. 수정 라이브러리를 배포한다면 그 수정 소스와 고지도 제공하세요. 수정 디버깅에 필요한 역공학도 허용돼요. 원본 앱은 MIT를 유지하며, 단일 파일은 임시 DLL을 직접 교체할 수 있다고 주장하는 대신 LGPL의 대응 앱 코드·재결합 경로를 제공해요. [LGPL 4절](licenses/upstream/qtbase/LICENSES/LGPL-3.0-only.txt).

## 선택적 공인 서명

이번 릴리스는 결정에 따라 미서명으로 제공해요. 단일 EXE로 묶어도 SmartScreen 경고가 없어지지 않으며, 새 공인 서명도 즉시 평판을 보장하지 않아요. [Microsoft의 현재 안내](https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/smartscreen-reputation).

Windows 현재 사용자 My 저장소에 이미 발급된 공인 코드 서명 인증서가 있다면 빌드 명령에 `--signtool <Windows-SDK-SignTool.exe> --sign-thumbprint <인증서-SHA1> --signing-required`를 추가하세요. 키 제공자에 연결된 인증서도 포함해요. 도우미는 SHA256 Authenticode와 RFC3161 SHA256 타임스탬프를 요청하고 신뢰 검증이 실패하면 빌드를 중단해요. 두 EXE의 서명 후 해시와 ZIP을 확정해요. 스크립트는 비밀키 파일/암호를 읽지 않으며 인증서 파일·서비스 자격증명을 커밋하지 마세요. 서명 필수 모드에 신원이 없으면 빌드를 거부해요. 신원 구매·등록, Store 제출, OS 보호 기능 변경은 이 명령에 포함되지 않아요.

자동 진단 창은 실제 마우스 입력이 바탕 화면으로 통과하게 두고 위젯 동작을 직접 실행해요. 실제 OS 포인터 가로채기와 로그인 자동 시작은 별도 수동 검사예요.

## 알파 3 캐릭터 포함 파일

두 형식에 `pomodoro/art/sprout-tomato-v1.json`, 자산 기록·캐릭터 출처·MIT 원문이 들어 있어요. 폴더형 자원은 `_internal/pomodoro/art/`에, 단일 EXE는 같은 패키지 경로의 임시 추출 위치에 있어요. `BUILD-INFO.json`에 자원 SHA-256을 기록하고 검사기가 빌드 소스와 파일·고지를 대조해요. wheel에도 package-data로 그림을 포함해요. 두 그림과 자체 코드는 MIT이며 [그림 출처](CHARACTER-POLICY.ko.md)와 LGPL 런타임 의무도 문서에 남겨요. 새 런타임 의존성은 없어요.

## 저장소 검사와 main 보호

GitHub Actions의 `Windows checks` 작업은 깨끗한 Windows 실행기에 고정된 런타임을 설치하고 의존성 호환·회귀 검사·격리 네이티브 위젯 진단·문서 및 자산 해시를 확인해요. 저장소 읽기 권한과 15분 제한만 사용하고 빌드 게시나 앱 프로필·비밀값을 사용하지 않아요. 공식 checkout/setup-python은 확인한 v6 커밋에 고정하며 MIT인 CI 인프라로만 사용해요.

main 정책은 PR·최신 `Windows checks` 통과·대화 해결을 요구하고 관리자에게도 적용하며 강제 푸시·삭제를 막아요. 개인 관리 저장소이므로 외부 승인 리뷰 수는 요구하지 않아요. 보호 설정은 GitHub에 적용하고 다시 읽어 확인하며 Markdown 파일 자체가 강제하는 것은 아니에요. GitHub Free에서는 공개 전환 후 사용할 수 있어요. [브랜치 보호 안내](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches).

0.1.0은 알파 3 개발 스냅샷에서 검증한 36초 데모를 유지해요. 보여주는 동작·UI는 같고 영상에 버전 번호는 표시하지 않으며 파일명·해시로 출처를 보존해요. 정식 릴리스라고 해서 코드 서명이나 모든 Windows 11·하드웨어 수동 검사를 마쳤다는 뜻은 아니에요.
