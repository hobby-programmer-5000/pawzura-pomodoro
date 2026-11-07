[English](README.md) · [한국어](README.ko.md)

# 화면 데모

영문·한글 GIF와 MP4는 각각 22초, 1280 × 800픽셀, 초당 12프레임이에요. 걷기, 알림 설정, 말풍선과 배너 미리보기, 휴식, 유지되는 전체 가림, 두 번째 모니터에서 새 작업을 시작하는 흐름을 보여줘요.

실제 앱의 Qt 화면을 캡처해 두 개의 예제 바탕 화면 위에 배치했어요. 임시 설정을 사용하고, 대기 시간을 단축했으며, 조작을 알아보기 쉽게 커서 표시를 더했어요. 화면 배치는 앱의 다중 모니터 동작을 설명하기 위한 구성이에요. 실제 Windows 환경의 검증 결과는 프로젝트 체크포인트에 따로 기록했어요.

각 언어의 프로젝트 README에서 GIF를 표시하고 MP4를 연결해요. GitHub는 GIF 이미지 표시를 지원해요. [GitHub 이미지 문서](https://docs.github.com/en/repositories/working-with-files/using-files/working-with-non-code-files).

Windows에서 다시 만들려면 기존 Qt 호환 환경과 PATH에 등록된 FFmpeg를 사용하세요. 체크아웃 루트에서 새 출력 폴더와 작업 폴더를 지정해 실행해요.

```powershell
.\.venv-standard\Scripts\python.exe -m pomodoro.tools.record_demo --language en --output-dir .cache/demo-output --work-dir .cache/demo-work-en
.\.venv-standard\Scripts\python.exe -m pomodoro.tools.record_demo --language ko --output-dir .cache/demo-output --work-dir .cache/demo-work-ko
```

결과를 검토한 뒤 GIF·MP4 네 파일을 이 폴더에 복사하세요. 스크립트는 기존 결과를 보존하도록 새 경로를 요구해요.

이 데모는 FFmpeg 9.0.2로 인코딩했어요. 사용한 제작용 빌드는 GPL-3.0-or-later로 안내해요. [FFmpeg 라이선스 안내](https://ffmpeg.org/legal.html).

직접 작성한 데모 문구, 화면 구성, 토마토 그림에는 저장소의 [MIT 라이선스](../LICENSE)가 적용돼요. Qt/PySide 런타임은 기존 [외부 구성요소 고지](../THIRD-PARTY-NOTICES.ko.md)를 따라요. 로컬 Windows 글꼴을 비트맵 프레임에 그리는 방식은 Microsoft의 이미지·영상 출력 안내를 참고했어요. [Microsoft 글꼴 FAQ](https://learn.microsoft.com/en-us/typography/fonts/font-faq).
