[English](RESULTS.md) · [한국어](RESULTS.ko.md)

# Windows 11 test results

The supplied Windows 11 session reports cover the timer, work → break → waiting transitions, effect controls, settings persistence, and lock/sleep recovery. They include automated and native GUI checks; the table distinguishes the methods. These are supplied session results, not an independent repeat of every Windows 11 scenario.

| Area | Recorded result |
| --- | --- |
| Automated checks | 202 passed: 187 recorded checks, 11 application tests and 4 DPI checks. |
| Additional real-clock effect combinations | 136 passed using Qt offscreen integration. These are not 136 manual OS pointer tests. |
| Native Windows 50/10-minute cycle | Work: 3000.158 seconds; break: 600.122 seconds. No missing or duplicate transitions were recorded. |
| 64 basic scenarios | 42 met all required conditions; 22 were partially completed or not run. |
| Additional native GUI checks | Invalid-settings recovery (F02), save failure and restored file access (F03), left-direction persistence after restart (P02), and returning the companion home in pinned/walking modes (P07). |

A Korean waiting-panel button-clipping issue was fixed by refreshing the hidden panel layout before measuring it. The added regression reproduces the sequence of a timed preview followed by an interactive waiting cue. The supplied post-fix automated receipt matches the proposed source files. The long-cycle report does not bind its run to a source hash, so it is session-level evidence rather than a confirmed repeat against this exact fixed snapshot.

The 22 incomplete scenarios are not 22 recorded functional failures. Remaining coverage includes actual tray clicks, holding a button through a transition, Alt+Tab while dragging, all native exit/forced-termination variants, portrait/minimum-resolution displays, accessibility settings, projection/taskbar changes, exclusive fullscreen, RDP, docking and hibernation. Related automated checks do not replace those manual paths or hardware conditions.

A quiet performance comparison under the same workload is also pending. Window counts stayed constant during the long cycle, but concurrent effect tests prevent treating its CPU difference as a confirmed defect or a clean performance baseline.

Known observation: after settings-file access was restored, disk writes succeeded but the save-failure warning remained visible in the running QSettings instance. Persistence recovery and warning recovery are separate outcomes; the warning behavior remains unresolved.

Raw screenshots, profiles and logs remain local. Portable build procedures are in [BUILD](BUILD.md); release notes identify the exact binary's validation. These Windows 11 source-session results do not replace a separate Windows 11 check of the frozen EXE.

[Test scenarios](TESTING.md) · [Project README](README.md)
