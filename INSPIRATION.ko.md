[English](INSPIRATION.md) · [한국어](INSPIRATION.ko.md)

# 참고 및 영감

Pawzura 포모도로의 시각 알림은 아래 문서에 소개된 상호작용 방식에서 착안했어요. 공개 문서의 확인일은 2026년 11월 7일이에요.

| 참고 자료 | 착안한 아이디어 | 이 앱에 반영한 방식 |
| --- | --- | --- |
| [Time Out, Break Controls](https://dejal.com/help/timeout/en/controls.html) | 사용자가 응답할 때까지 휴식 종료 화면을 유지하는 옵션이에요. 원문에서는 후원자 기능으로 안내해요. | 휴식 종료 화면을 유지할 수 있고, 작업 시작을 누른 순간부터 다음 작업 시간을 재요. |
| [Stretchly 공식 README](https://github.com/hovancik/stretchly/blob/trunk/README.md) | 전체 화면, 투명도, 모든 모니터 표시를 각각 설정하는 방식이에요. | 전환마다 모양을 고를 수 있고, 모든 모니터에 반투명 덮개나 전체 가림을 표시해요. |
| [Workrave, Break windows](https://workrave.org/docs/breaks/breaks/) | 미루기를 선택하면 휴식 창을 닫았다가 나중에 다시 알려줘요. | 휴식 종료 안내를 설정한 시간만큼 미루고 다시 표시할 수 있어요. |
| [BreakTimer 공식 사이트](https://breaktimer.app/) | 휴식 메시지 설정과 다시 알림이 있는 안내 방식이에요. | 전환 상황을 분명히 알려주는 문구와 다시 알림 버튼을 구성할 때 참고했어요. |
| [Pawzura 컴패니언 조작 코드](https://github.com/hobby-programmer-5000/pawzura/blob/23bd3b90435d6e5ab6c0dd510d8dc5b8897489a6/pawzura/pet.py) | 걷기, 드래그 고정, 반응, 모니터 사이의 위치 처리예요. | MIT 라이선스의 이동·조작 코드를 직접 재사용하고, 토마토는 별도로 그렸어요. |

제품 방향과 기능 선택은 사용자가 정했고, Codex가 이 체크아웃의 Qt 타이머, 시각 효과 설정, 벡터 토마토를 구현했어요. 위 웹 문서는 상호작용을 설계할 때 참고한 자료예요. 구현에는 프로젝트의 Qt 코드와 직접 그린 그림을 사용했어요.

앱의 직접 작성한 코드와 그림에는 저장소의 [MIT 라이선스](LICENSE)가 적용돼요. 런타임 라이브러리는 [외부 구성요소 고지](THIRD-PARTY-NOTICES.ko.md)에 기록된 각 구성요소의 조건을 따라요. 이 문서는 해당 고지와 함께 아이디어를 참고한 경위를 기록해요.
