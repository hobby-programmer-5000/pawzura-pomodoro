[English](RESULTS.md) · [한국어](RESULTS.ko.md)

# Windows 11 test results

These supplied records describe the alpha-1 source session with its Korean layout fix. Alpha 2 adds profile separation, startup controls and a standalone build; those changes require the separate A2 cases in [TESTING](TESTING.md) and release-specific binary checks.

The supplied Windows 11 session reports cover the timer, work → break → waiting transitions, effect controls, settings persistence, and lock/sleep recovery. They include automated and native GUI checks; the table distinguishes the methods. These are supplied session results, not an independent repeat of every Windows 11 scenario.

| Area | Recorded result |
| --- | --- |
| Automated checks | 202 passed: 187 recorded checks, 11 application tests and 4 DPI checks. |
| Additional real-clock effect combinations | 136 passed using Qt offscreen integration. These are not 136 manual OS pointer tests. |
| Native Windows 50/10-minute cycle | Work: 3000.158 seconds; break: 600.122 seconds. No missing or duplicate transitions were recorded. |
| 64 basic scenarios | 42 met all required conditions; 22 were partially completed or not run. |
| Additional native GUI checks | Invalid-settings recovery (F02), save failure and restored file access (F03), left-direction persistence after restart (P02), and returning the companion home in pinned/walking modes (P07). |

A Korean waiting-panel button-clipping issue was fixed by refreshing the hidden panel layout before measuring it. The added regression reproduces the sequence of a timed preview followed by an interactive waiting cue. The supplied post-fix automated receipt matched the archived alpha-1 layout fix and regression files. The long-cycle report does not bind its run to a source hash, so it is session-level evidence rather than a confirmed repeat against this exact fixed snapshot.

The 22 incomplete scenarios are not 22 recorded functional failures. Remaining coverage includes actual tray clicks, holding a button through a transition, Alt+Tab while dragging, all native exit/forced-termination variants, portrait/minimum-resolution displays, accessibility settings, projection/taskbar changes, exclusive fullscreen, RDP, docking and hibernation. Related automated checks do not replace those manual paths or hardware conditions.

A quiet performance comparison under the same workload is also pending. Window counts stayed constant during the long cycle, but concurrent effect tests prevent treating its CPU difference as a confirmed defect or a clean performance baseline.

Known observation: after settings-file access was restored, disk writes succeeded but the save-failure warning remained visible in the running QSettings instance. Persistence recovery and warning recovery are separate outcomes; the warning behavior remains unresolved.

Raw screenshots, profiles and logs remain local. Portable build procedures are in [BUILD](BUILD.md); release notes identify the exact binary's validation. These Windows 11 source-session results do not replace a separate Windows 11 check of the frozen EXE.

[Test scenarios](TESTING.md) · [Project README](README.md)

## Alpha 3 checks on Windows 10

The 0.1.0a3 source update was checked on native Windows 10 x64 build 19045 with standard CPython 3.14.7 and PySide6/Shiboken 6.12.0: **33 unittest tests passed with no skips**. Added coverage checks stationary sit/sleep/wait/rise, standing before travel, pause/pin/reset/rapid reversal, dragging while seated, bounded art validation and rendered eye/gait behavior. The disposable-profile native diagnostic passed in English/Korean on three connected screens, including pet/options/button renders. These are widget-driven checks, not a repeat of every manual Windows 11 or hardware case.

All four new GIF/MP4 demos passed complete decoding: 432 frames, 1280 × 800, 36 seconds each. Encoded sit/sleep/wait/rise scenes and captions were visually inspected in both languages. Wheels were inspected for exact new artwork bytes and all six license/policy files. A restricted-runner wheel cleanup failed with Windows access denied; the native build and inventory passed. The new offline document check validates links and artwork/license/media hashes.

Release-specific frozen checks are recorded with the exact release artifacts. Windows 11 frozen execution, hardware hot-plug/mixed-DPI posture transitions and live OS pointer behavior still need itemized manual evidence; historical alpha-1 results above do not establish those alpha-3 results.

The character-selection follow-up adds restart persistence, invalid-choice recovery and live switching during rest without resetting posture/timer/cue identity. Eight standing/walking/reaction renders of Classic matched alpha-2 pixels in both directions. English/Korean General options and both seated skins were inspected; the 36-second demos now show both choices. The initial switch test incorrectly measured cue identity before opening Options (which intentionally dismisses effects); the corrected fixture opens a fresh live cue first. Demo popup automation initially missed pointer movement; using the existing style-selector interaction fixed both language recordings. Earlier failed logs are retained locally.
