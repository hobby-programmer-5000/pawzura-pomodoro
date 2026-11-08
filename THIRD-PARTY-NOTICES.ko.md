[English](THIRD-PARTY-NOTICES.md) · [한국어](THIRD-PARTY-NOTICES.ko.md)

# 구성요소 라이선스

자체 코드와 데모 문구·구성은 [MIT](LICENSE)를 유지해요. 새 민트색 앞치마 지정 캐릭터·렌더 아이콘·alpha-3 데모의 캐릭터 부분은 보유 권리 범위에서 **CC BY-NC-SA 4.0**이며 [일반적인 유료 업무 중 앱 사용은 별도 허용](CHARACTER-POLICY.ko.md)해요. [자산 등록부·크레디트](ASSET-LICENSING.ko.md) · [수정하지 않은 CC 원문](licenses/CC-BY-NC-SA-4.0.txt). 이전 토마토·데모는 MIT 허락을 유지하며 코드·외부 자료 전체를 재허락하는 것이 아니에요.

| 구성요소 | 버전 | 라이선스와 자료 |
| --- | --- | --- |
| Pawzura | 23bd3b90435d6e5ab6c0dd510d8dc5b8897489a6 | MIT. [원본 라이선스](https://github.com/hobby-programmer-5000/pawzura/blob/23bd3b90435d6e5ab6c0dd510d8dc5b8897489a6/LICENSE). |
| PySide6 Essentials | 6.12.0 | LGPL-3.0-only, 원본의 선택지 중 사용. [패키지](https://pypi.org/project/PySide6-Essentials/6.12.0/). |
| Shiboken6 | 6.12.0 | LGPL-3.0-only, 원본의 선택지 중 사용. [패키지](https://pypi.org/project/shiboken6/6.12.0/). |
| Qt Base | 6.12.0 | 해당 LGPL-3.0 조건과 포함된 고지. [Qt licensing](https://doc.qt.io/qt-6/licensing.html). |
| CPython | 소스: 사용자 설치 3.12+; 이번 포터블 알파: 3.14.7 | Python Software Foundation 조건과 포함된 고지. [License](https://docs.python.org/3.14/license.html). |
| PyInstaller | 6.22.3 | GPL-2.0-or-later와 부트로더 배포 예외, 일부 파일 Apache-2.0. 빌드 도구이며 앱의 MIT를 바꾸지 않아요. [예외](https://pyinstaller.org/en/stable/license.html). |
| PyInstaller hooks | 2026.9 | 설치 패키지 고지에 명시된 Apache-2.0/GPL 조건과 해당 예외. 빌드 도구. [원본](https://github.com/pyinstaller/pyinstaller-hooks-contrib). |
| FFmpeg | 데모 제작에 사용한 9.0.2 | 설치된 제작용 빌드는 GPL-3.0-or-later로 안내. [License](https://ffmpeg.org/legal.html). |
| Windows fonts | Segoe UI / Malgun Gothic | 화면·영상의 비트맵 출력. [Microsoft guidance](https://learn.microsoft.com/en-us/typography/fonts/font-faq). |

Qt/PySide 바인딩은 동적으로 불러와요. 실행 파일을 배포할 때 각 패키지 고지와 호환 라이브러리 교체·재결합 권리를 유지하세요. EXE 배포를 준비할 때 실제 바이너리와 포함 구성요소를 검토하세요. [Qt LGPL 의무](https://www.qt.io/development/open-source-lgpl-obligations).

포터블 ZIP의 `licenses/`에는 검토한 원본 라이선스·출처별 고지, 설치 패키지 고지와 CPython 라이선스가 들어 있어요. [자료 목록](licenses/SOURCES.json)에 고지 파일의 원본 URL과 해시를 기록해요. ZIP의 `BUILD-INFO.json`은 실제 버전·소스 해시를, `FILE-MANIFEST.json`은 배포 파일을 식별해요. 실행 파일에 포함되지 않은 빌드 전용 도구의 고지도 함께 제공할 수 있어요. CPython/Qt 휠에서 제공한 MSVC 런타임은 수정하지 않으며, 같은 이름의 DLL 버전이 다르면 제공된 최신 버전을 일관되게 사용해요.

앱과 Pawzura 소스는 MIT를 유지해요. 모델 가중치, FFmpeg 실행 파일, Windows 글꼴 파일, 관계없는 Pawzura 프로필·에셋은 배포하지 않아요. FFmpeg/글꼴은 기존 비트맵·영상 데모 제작에만 사용했어요. 선택된 Qt 모듈은 실제 런타임과 보관된 고지를 대조하며 이 기록이 다른 모듈이나 향후 버전의 포괄적 법률 검토를 대신하지는 않아요. 대응 소스 압축 파일과 LGPL 권리는 [빌드·라이브러리 교체 안내](BUILD.ko.md)를 참고하세요.

아이디어를 참고한 경위는 [참고 및 영감](INSPIRATION.ko.md)에 기록했어요.

별도 단일 EXE는 같은 동적 런타임과 고지를 내장하고 임시로 풀어요. [BUILD](BUILD.ko.md)에 설명한 대응 앱 코드·빌드 스크립트·정확한 라이브러리 소스를 제공해 LGPL 재결합 경로를 지원하며, 폴더형 ZIP은 계속 호환 DLL을 직접 교체할 수 있어요. 두 형식 모두 **옵션 > 라이선스**에서 고지와 정확한 빌드 소스를 열어요. 원본 코드·과거 그림은 MIT를 유지하고 새 지정 그림은 자산 등록부 조건을 따라요.

`pomodoro/classic.py`는 과거 MIT 토마토 렌더러를 복원하고 앉기 동작을 MIT로 추가해요. 새 CC 지정 그림과 함께 선택할 수 있고 기존 허락은 그대로예요. 캐릭터 선택을 위해 새 라이브러리·모델·외부 그림을 추가하지 않았어요.
