[English](THIRD-PARTY-NOTICES.md) · [한국어](THIRD-PARTY-NOTICES.ko.md)

# 구성요소 라이선스

직접 작성한 앱 코드, 토마토 그림, 데모 구성에는 저장소의 MIT 라이선스가 적용돼요. [MIT](LICENSE).

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
