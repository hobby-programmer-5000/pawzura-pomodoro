[English](README.md) · [한국어](README.ko.md)

# 화면 데모

영문·한글 GIF와 MP4는 각각 30초, 1280 × 800픽셀, 초당 12프레임이에요. 알파 3은 걷기·50/10·Windows 자동 시작·효과 설정과 미리보기, 휴식 시작 시 멈춰 앉고 눈 감기, 두 번째 모니터에서 효과를 닫은 뒤에도 앉아서 대기하기, 타이머 배지로 작업을 시작해 일어난 뒤 걷는 흐름을 보여줘요. 별도 확대 캐릭터도 알림이 화면을 덮는 동안을 포함해 같은 실제 위젯을 캡처해요.

실제 앱의 Qt 화면을 캡처해 두 개의 예제 바탕 화면 위에 배치했어요. 임시 설정을 사용하고, 대기 시간을 단축했으며, 조작을 알아보기 쉽게 커서 표시를 더했어요. 화면 배치는 앱의 다중 모니터 동작을 설명하기 위한 구성이에요. 실제 Windows 환경의 검증 결과는 프로젝트 체크포인트에 따로 기록했어요.

각 언어의 프로젝트 README에서 GIF를 표시하고 MP4를 연결해요. GitHub는 GIF 이미지 표시를 지원해요. [GitHub 이미지 문서](https://docs.github.com/en/repositories/working-with-files/using-files/working-with-non-code-files).

Windows에서 다시 만들려면 기존 Qt 호환 환경과 PATH에 등록된 FFmpeg를 사용하세요. 체크아웃 루트에서 새 출력 폴더와 작업 폴더를 지정해 실행해요.

```powershell
.\.venv-standard\Scripts\python.exe -m pomodoro.tools.record_demo --language en --output-dir .cache/demo-output --work-dir .cache/demo-work-en
.\.venv-standard\Scripts\python.exe -m pomodoro.tools.record_demo --language ko --output-dir .cache/demo-output --work-dir .cache/demo-work-ko
```

결과를 검토한 뒤 GIF·MP4 네 파일을 이 폴더에 복사하세요. 스크립트는 기존 결과를 보존하도록 새 경로를 요구해요.

이 데모는 FFmpeg 9.0.2로 인코딩했어요. 사용한 제작용 빌드는 GPL-3.0-or-later로 안내해요. [FFmpeg 라이선스 안내](https://ffmpeg.org/legal.html).

자체 데모 문구·구성은 [MIT](../LICENSE)를 유지해요. `pomodoro-demo-0.1.0a3-en.gif`, `pomodoro-demo-0.1.0a3-en.mp4`, `pomodoro-demo-0.1.0a3-ko.gif`, `pomodoro-demo-0.1.0a3-ko.mp4`의 새 캐릭터 부분은 지정 자산 **Sprout Tomato — mint apron edition v1**을 재현하며, 이용허락자가 허락할 수 있는 권리에 **CC BY-NC-SA 4.0**을 적용해요. 크레디트: hobby-programmer-5000; AI-assisted vector artwork with ChatGPT/Codex. [자산 등록부](../ASSET-LICENSING.ko.md) · [수정하지 않은 CC 원문](../licenses/CC-BY-NC-SA-4.0.txt) · [일반 유료 업무 중 앱 사용 추가 허용](../CHARACTER-POLICY.ko.md). 완성 데모를 공유할 때 이 고지와 캐릭터 조건을 지키고 MIT 부분·외부 자료의 해당 조건도 유지하세요. 과거 알파 1·2 미디어는 MIT 허락을 유지해요. Qt/PySide 런타임은 기존 [외부 구성요소 고지](../THIRD-PARTY-NOTICES.ko.md)를 따라요. 로컬 Windows 글꼴을 비트맵 프레임에 그리는 방식은 Microsoft의 이미지·영상 출력 안내를 참고했어요. [Microsoft 글꼴 FAQ](https://learn.microsoft.com/en-us/typography/fonts/font-faq).

알파 3 녹화는 일반 옵션의 50/10 값과 Windows 자동 시작, 시각 효과와 명시적 재시작을 보여줘요. 마지막 자막은 ZIP/단일 EXE 선택을 안내해요. 녹화의 자동 시작 조작은 이 PC의 Run 레지스트리 대신 메모리 저장소를 사용해요. 실제 UI와 이벤트 처리기를 사용하지만 로그인·재부팅 동작은 별도 확인 대상이에요. 버전·언어가 들어간 파일 이름을 사용하고 인코더는 기존 파일 덮어쓰기를 거부해요.

정확한 파일 해시는 [SHA256.json](SHA256.json)에 있어요. 첫 버전: 0.1.0a3, 2026-11-08. 자세 시계는 가속 카운트다운과 별도이며 프레임별 단언으로 휴식·대기·일어서기 중 위치 유지를 확인해요. 인코딩된 네 파일을 전체 디코딩해 각각 360프레임·1280 × 800·30초를 확인하고 두 언어의 자세·자막 장면도 살펴봤어요. 이전 릴리스 자산은 그대로이며 과거 소스 미디어는 Git 기록에 남아 있어요.
