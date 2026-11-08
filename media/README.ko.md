[English](README.md) · [한국어](README.ko.md)

# 화면 데모

한영 GIF·MP4는 각각 36초·1280 × 800·초당 12프레임(432프레임)이에요. 기존/앞치마 선택·저장, 50/10 기본값, 자동 시작 옵션, 알림 설정, 앉기·휴식·대기·일어난 뒤 걷기를 보여줘요. 캐릭터 선택 아래 라이선스 설명은 없고 별도 라이선스 버튼은 유지해요.

임시 설정과 두 예제 바탕 화면에서 실제 Qt 위젯을 캡처해요. 카운트다운은 가속하고 자세 시계는 별도로 연속 진행하며 확대 캐릭터도 같은 위젯이에요. 자동 시작은 메모리 저장소만 사용해 이 PC의 Run 항목을 바꾸지 않아요. 실제 데스크톱·하드웨어 검사는 아니에요.

기존 Qt 호환 환경과 PATH의 FFmpeg를 사용해 새 출력·작업 경로로 다시 만들 수 있어요. 인코더는 기존 파일을 덮어쓰지 않아요.

```powershell
.\.venv-standard\Scripts\python.exe -m pomodoro.tools.record_demo --language en --output-dir .cache/demo-output --work-dir .cache/demo-work-en
.\.venv-standard\Scripts\python.exe -m pomodoro.tools.record_demo --language ko --output-dir .cache/demo-output --work-dir .cache/demo-work-ko
```

네 결과물을 검토한 뒤 저장소 미디어를 교체하세요. [SHA256.json](SHA256.json)에 정확한 파일 해시가 있어요. 네 파일을 전체 디코딩해 각각 432프레임·36초를 확인하고 인코딩된 선택·자세·한영 자막을 살펴봤어요. 이전 후보·릴리스는 보존해요.

자체 데모 문구·구성과 두 캐릭터 이미지는 [MIT](../LICENSE)예요. 크레디트: hobby-programmer-5000; AI-assisted procedural vector art/media with ChatGPT/Codex. [그림 기록](../ASSET-LICENSING.ko.md) · [구성요소 고지](../THIRD-PARTY-NOTICES.ko.md). 이전 허락을 유지하며 이번 버전에서 앞치마 그림에도 MIT 허락을 제공해요.

FFmpeg 9.0.2는 제작 도구로만 사용했고 해당 설치 빌드는 GPL-3.0-or-later를 안내해요([FFmpeg 조건](https://ffmpeg.org/legal.html)). 설치된 Windows Segoe UI·Malgun Gothic 글꼴을 프레임으로 그렸으며 폰트 파일·FFmpeg 실행 파일은 배포하지 않아요([Microsoft 글꼴 FAQ](https://learn.microsoft.com/en-us/typography/fonts/font-faq)). Qt·런타임 조건은 별도예요.
