[English](TESTING.md) · [한국어](TESTING.ko.md)

> Alpha 2 additions: the existing 64-case source-session results do not cover these new release cases. Test the exact ZIP and standalone EXE separately and record the version/hash. For diagnostics use a new `--settings-file` directory; checking real Windows login startup requires a normal packaged run and explicit opt-in.

| New case | Procedure and expected result |
| --- | --- |
| A2-01 | Keep an old alpha-1/development profile with work=1. A new normal desktop profile starts at work=50/rest=10 and leaves the old file unchanged. |
| A2-02 | Set desktop times to 23/7, quit and reopen using the other EXE format: 23/7 remains. Press **50 / 10**: the next interval uses 50/10; an active interval is not interrupted. |
| A2-03 | Normal packaged **Start with Windows** is initially off. In a permanent EXE folder, enable it, sign out/in and confirm one companion with the same settings. A duplicate `--startup` exits quietly. Disable and confirm no login start. Restore your original state after testing. |
| A2-04 | Source and explicit test profiles disable the startup option. Move/delete a test EXE before enabling in an isolated backend: show the failure and retain the actual checkbox state. Never overwrite an unrecognized Run value. |
| A2-05 | Copy only the versioned standalone EXE into a fresh folder on a machine without Python; run, inspect **Licenses**, options, all-monitor effects and persistence. Close and reopen. Compare its exact SHA256 with the release. |
| A2-06 | Inspect **General** and **Licenses** in English/Korean, including 50/10 values, restore tooltip, startup availability/error and component/source links. Browser-download SmartScreen behavior is recorded separately; this unsigned alpha does not claim to remove its warning. |

# Windows 11 manual test scenarios

This checklist covers the current source app. Record the exact files, Windows build and display configuration you test. The previous automated/native checks ran on Windows 10. The animated demo uses synthetic desktops and a shortened clock. Windows 11 results start as NOT RUN.

There are 64 scenario IDs and 136 effect combinations across English and Korean. Keep preview results and real-transition results separate. A passing preview covers appearance and dismissal, while a real transition covers the timer and event wiring.

## Prepare the test

1. On a new Windows 11 machine, use standard CPython 3.12+ and create the Qt environment from the checkout root. The earlier checked interpreter was CPython 3.14.7. For an installed Python 3.14, run the commands below.

   ```powershell
   py -3.14 -m venv .venv-standard
   .\.venv-standard\Scripts\python.exe -m pip install -r requirements.txt
   ```

2. Check the normal [run.bat](run.bat) launch once, then quit from its tray menu. Run the remaining tests with an isolated profile using the command below in a dedicated PowerShell window. Repeat the same command for duplicate-launch and restart checks. Change `run-01` to a fresh name when you need clean defaults.

   ```powershell
   .\.venv-standard\Scripts\python.exe -c "import os; from pathlib import Path; from PySide6.QtCore import QSettings; p=Path('.cache/windows11-manual/run-01').resolve(); p.mkdir(parents=True, exist_ok=True); QSettings.setPath(QSettings.Format.IniFormat, QSettings.Scope.UserScope, str(p)); print('Test PID', os.getpid(), flush=True); from pomodoro.app import main; raise SystemExit(main())"
   ```

3. Record the PID of the process that successfully opened the app. Also record the Windows version/build from `winver`, Python/PySide versions, source hashes, screen count, arrangement, resolution, scaling, refresh rate, primary screen and laptop/dock status. Give displays neutral labels A/B/C.
4. Verify fresh defaults first. Then set work and break to **1 minute**, snooze to **1 minute**, and timed effects to **2 seconds**. Use an empty text editor and a phone stopwatch for input/time checks.
5. Record PASS, FAIL or NOT RUN for every ID and variation. Give a reason for NOT RUN. For observations, record the observed result and keep the acceptance status NOT RUN until the expected policy is agreed.
6. Save results and app-only evidence under ignored `.cache/windows11-manual/`. A failure report should include ID, language, event/style/retention/anywhere setting, screen setup, steps, expected result, actual result, reproducibility and an evidence filename.

If the app becomes unresponsive, use its visible **Turn effects off** button first. For a forced-stop test, identify only the dedicated test PID printed above. A second PowerShell window can run `Stop-Process -Id <test-PID>`. Relaunch using the same isolated profile.

Use these read-only commands to record versions and the core source hashes.

```powershell
.\.venv-standard\Scripts\python.exe -c "import sys, PySide6; print(sys.version); print(PySide6.__version__)"
Get-FileHash .\pomodoro\app.py, .\pomodoro\effects.py, .\pomodoro\options.py, .\pomodoro\surfaces.py, .\pomodoro\text.py, .\pomodoro\timer.py -Algorithm SHA256 | Select-Object @{Name='File';Expression={Split-Path $_.Path -Leaf}},Hash
```

## Current behavior to use as the reference

- Closing Options keeps the app running. Opening Options dismisses the current effect and cancels a scheduled reminder.
- Settings save immediately. New work/break durations apply to the next interval. Restarting the app restores settings and starts in Ready with a full work duration.
- A completed break waits for Start work. Dismiss and click-anywhere keep that waiting state. Start work begins a full interval and closes the old effect on every screen.
- Enabling effects while waiting displays the waiting reminder again. An explicit Preview works while automatic effects are off.
- Timed edge/bubble/banner/dim effects pass mouse input through. Cover receives mouse input even when timed. Interactive dim/cover backgrounds receive clicks. With anywhere off, the clear areas around an edge/bubble/banner allow ordinary desktop clicks.
- Effect windows keep keyboard focus in the previously active app. Use the empty text editor to check this behavior, including under an opaque cover.
- Waiting offers timed/click retention. Work and break also offer whole-interval retention. Preview closes through Close preview or its timed expiry, and leaves the timer state unchanged.

## Launch and lifecycle

| ID | Procedure | Expected result |
| --- | --- | --- |
| L01 | Launch with run.bat, then the isolated command after quitting. | Both routes show one tomato and one tray icon for that run. Record which route/profile was tested. |
| L02 | Launch a fresh isolated profile. | English, work 50/break 10, walking on, effects on, work edge 1 s, break dim 3 s, waiting dim until dismissed, snooze 2 min. |
| L03 | Run the same isolated command again while it is open. | An already-open message appears. The original countdown continues and no second companion starts. |
| L04 | Open Options through body double-click, companion right-click, tray click and tray menu. Close through Close and X. | Each route reaches the same settings. Closing Options keeps the timer, pet and tray running. |
| L05 | Quit from both menus, including while an effect is visible. | Pet, tray and every effect close. A scheduled snooze produces no later window. |
| L06 | Change settings, quit and relaunch the same profile. | Language, durations, effect presets, snooze, walking/direction and pinned position persist. The timer starts Ready with the full configured work duration. |

## Settings and languages

| ID | Procedure | Expected result |
| --- | --- | --- |
| S01 | Switch EN ↔ KO in Options, companion Language submenu and tray Language submenu. | All controls, menu check marks, tooltips, timer labels and current effect update. |
| S02 | Try work/break 1 and 180, then type 0, 181, a negative value and letters. Commit with Tab. | Valid bounds save. Invalid text is rejected or restored to a valid value. The app remains usable. |
| S03 | Try effect seconds 1/60 and snooze 1/30, plus out-of-range and text input. | Values stay within 1–60 seconds and 1–30 minutes. |
| S04 | Give work, break and waiting three visibly different presets. Switch the event selector repeatedly. | Each event retains its own appearance, retention, duration and anywhere setting. |
| S05 | Change work/rest during work, then during paused work and paused break. | The current interval keeps its original duration/remaining time. Each next interval uses the updated value. |
| S06 | Switch timed/click/interval retention and each style. | Seconds is editable for timed retention. Waiting has two retention choices. Anywhere is editable for interactive effects, including timed Cover. |
| S07 | Edit a spin box using keyboard, commit with Tab, then close Options with X and restart. | The committed value is saved. Closing X keeps committed settings. |
| S08 | Inspect both tabs, menus, overlays and badge in both languages; use Tab/Shift+Tab in Options and enlarged Windows text. | Options controls remain reachable and readable. Time digits remain visible. A shortened badge label has its complete tooltip. Record overlay keyboard accessibility, contrast themes and available touch/pen input as observations. |

## Timer transitions

Use work 1/break 1 unless stated otherwise. For a foreground stopwatch check, use ±2 seconds as a manual comparison tolerance for a one-minute interval. This is a test criterion for this pass.

| ID | Procedure | Expected result |
| --- | --- | --- |
| T01 | Click the badge to start. Repeat after reset several times. | It begins at 01:00 and counts downward. It never begins at 01:01. |
| T02 | Start, pause and resume through Options, companion menu and tray menu. | Each route controls the same interval and label. |
| T03 | Pause work and break for 15 seconds, then resume. | Displayed remaining time stays fixed while paused and resumes from the saved time. |
| T04 | Let work expire. | Break begins automatically once, with its own preset and full break duration. |
| T05 | Let break expire, then wait another 30 seconds. | Waiting remains until explicit start. The next work countdown stays full. |
| T06 | Click Start work on a secondary monitor's waiting effect. | All old effects close together. One full work interval starts, followed by its configured start effect. |
| T07 | Dismiss waiting via its button, then via click-anywhere. | Effects close on all displays. The app keeps waiting and the next work time stays full. |
| T08 | Reset from work, paused work, break, paused break and waiting. | Ready shows the full configured work time. Old effects and pending snoozes are cancelled. |
| T09 | Complete three 1/1 cycles, then a genuine 50/10 cycle. | Ordering stays work → break → waiting → explicit work. Record stopwatch differences and any repeated, missing or late transition. Use ±5 seconds as the manual 50-minute comparison tolerance. |

## Effects and interaction

| ID | Procedure | Expected result |
| --- | --- | --- |
| E01 | Complete the effect matrix below in both languages. | Every selected combination matches its appearance and enabled controls. |
| E02 | Use timed retention with 1, 2 and 60 seconds. | The effect expires approximately at its configured duration on every screen. |
| E03 | Use click retention, wait longer than the seconds field, then dismiss. | It remains until acknowledgement and all displays close together. |
| E04 | Use interval retention for work and break. Pause, resume, then allow expiry. | It remains during the interval and pause. The next phase replaces it once. |
| E05 | With anywhere off, click outside buttons on dim/cover and in a clear area beside a bubble/banner/edge. | Dim/cover stay visible. Clear areas beside bubble/banner/edge pass desktop clicks. Buttons remain usable. |
| E06 | With anywhere on, click the background on every screen, including timed Cover. | All copies dismiss. Waiting stays waiting. Background acknowledgement never starts work. |
| E07 | In a scratch text editor, keep typing/clicking through timed edge/bubble/banner/dim. Repeat under Cover. | Timed clear effects preserve normal interaction. Cover receives mouse clicks. Existing keyboard focus remains with the editor; verify its contents after dismissing. |
| E08 | Turn effects off while one is visible, through the overlay button and each menu. Turn it back on in work and waiting. | Every display clears immediately. Menu/Options state agrees. Work continues; enabling while waiting shows its reminder. |
| E09 | Preview every event during Ready, work, paused work and waiting, including automatic effects off. | Preview leaves the timer state/countdown unchanged apart from normal elapsed running time. Close preview has no start/snooze side effect. |
| E10 | With a preview visible near work expiry, hold its Close preview button down until the next real phase appears, then release. | The stale release does not dismiss or trigger a button in the new phase. Test with the new break preset kept until clicked. |

## Snooze and cancellation

For cancellation cases, set the next work duration to 2 minutes and snooze to 1 minute before starting the cycle.

| ID | Procedure | Expected result |
| --- | --- | --- |
| R01 | On waiting, choose Remind in 1 min. | All effects close, work stays waiting and the reminder returns once after about one minute. |
| R02 | Snooze again when it returns. | A new one-minute wait starts, with no duplicate window. |
| R03 | Repeat snooze separately followed by Start work, Reset, Dismiss this effect and Turn effects off. Wait beyond its due time. | The old waiting reminder stays cancelled. Ordinary new-phase effects follow the timer's own schedule. |
| R04 | Snooze, then open Options before the reminder is due. | Opening Options cancels that scheduled reminder. |
| R05 | Snooze, change language using a Language submenu without opening Options, then wait. | The reminder returns in the new language with the saved settings. |

## Companion controls

| ID | Procedure | Expected result |
| --- | --- | --- |
| P01 | Let it walk across each connected screen and the outer edges. | It uses current display floors, continues through the display order and wraps without becoming permanently lost. |
| P02 | Choose Left and Right in Options. | Walking direction changes. Restart preserves the preference. |
| P03 | Hover, move away, single-click the body and double-click the body. | Hover stops walking; leaving resumes it. Click reacts; double-click opens Options. The badge controls the timer. |
| P04 | Drag within a display and onto each other display. | Release pins at the new position and unchecks walking in both menus/Options. |
| P05 | Drag near screen corners, taskbar and gaps between displays. | It fits into an available work area and remains recoverable. |
| P06 | Interrupt a drag with Alt+Tab, release, then drag again. | It does not remain stuck in a held gesture. |
| P07 | Toggle walking off/on and use Bring companion back, both while pinned and walking. | Walking resumes at a display floor. Recovery returns the companion to the primary display. |

## Displays and Windows integration

Repeat core appearance/input checks on the display configurations you can access. Record unavailable hardware/configurations as NOT RUN.

| ID | Procedure | Expected result |
| --- | --- | --- |
| M01 | Single display, then extended displays. | One correctly placed effect per extended display, with readable buttons. |
| M02 | Put a secondary display left of the primary, then above it, including a gap. | Effects fill each actual display and controls remain on its own work area. |
| M03 | Mix 100/125/150/200% scaling; try portrait and the smallest supported resolution. Move the pet and Options between displays. | Size, hit targets and text stay usable, with no cumulative growth, missing time digits or unreachable close control. |
| M04 | Change the primary display while running. | Recovery and later placement use the new primary. Timer state survives. |
| M05 | Disconnect/reconnect a display while walking and while pinned there. | The pet becomes reachable on remaining displays; reconnecting leaves one usable companion. |
| M06 | Disconnect/reconnect while a persistent effect or preview is visible. | Removed-display surfaces disappear. Current displays have the active effect and one action dismisses all. |
| M07 | Use Win+P to test Extend, Duplicate, PC screen only and Second screen only. | Remaining physical screens show the expected content. Duplicate mirrors the logical display. No unreachable leftover surface remains. |
| M08 | Try taskbar auto-hide, taskbar on multiple monitors and work-area changes. | Pet/panels adapt to usable work areas. Full-screen covers span the entire screen, including taskbar space, with their own controls accessible. |

Windows display arrangement/scaling is under Settings > System > Display. Win+P selects display mode. [Microsoft display guide](https://support.microsoft.com/en-gb/windows/hardware/display-graphics/how-to-use-multiple-monitors-in-windows).

## Session and recovery

| ID | Procedure | Expected result |
| --- | --- | --- |
| W01 | Use Alt+Tab, Win+D, Snap and ordinary window movement while the timer runs. | Countdown continues. Returning leaves a usable companion and controls. |
| W02 | Try borderless/full-screen apps, a second virtual desktop and Do Not Disturb/Focus. Where available, connect/disconnect Remote Desktop. | Record visibility and dismissal behavior separately for each configuration. Exclusive full-screen, all-virtual-desktop visibility and remote-session behavior are observations awaiting a defined compatibility claim. |
| W03 | With work 1/break 1, lock using Win+L for over two minutes while the PC stays awake, then unlock. | The running app reaches waiting, and its configured waiting reminder remains usable. |
| W04 | Pause, sleep for at least one minute, then resume Windows. | The paused time is retained and all controls still work. |
| W05 | Sleep/hibernate while working, breaking and waiting; repeat with a dock/monitor change. | Record before/after phase, remaining time and wall-clock gap. Current code starts a newly reached break when its callback is processed. It can therefore show a fresh break after a suspended work interval. Require usable recovery and record timing behavior for policy review. |
| W06 | Quit/relaunch from work, paused break and waiting, and exit while a preview is visible. | The app restores settings into Ready, with no old preview/reminder or orphan overlay. |
| W07 | Repeat preview/style/language changes 20 times and run one normal 50/10 session. Observe Task Manager before/after. | No accumulating windows, crashes, stuck input or continuing unexplained CPU/memory growth. Record measurements without inventing a fixed performance target. |

Locking keeps apps open in the background. Sleep/hibernate availability depends on the device. [Microsoft account guide](https://support.microsoft.com/en-us/accounts-billing/security/user-account-access-in-windows), [Microsoft sleep guide](https://support.microsoft.com/en-us/windows/experience/power-battery/shut-down-sleep-or-hibernate-your-pc). The current Windows clock implementation is based on a counter that includes sleep time. [Microsoft timing documentation](https://learn.microsoft.com/en-us/windows/win32/sysinfo/acquiring-high-resolution-time-stamps).

The source uses Python's monotonic clock, whose documented Windows implementation uses that counter. [Python clock documentation](https://docs.python.org/3/library/time.html#time.monotonic).

## Setup failures and saved data

Use disposable copies/profiles for these cases.

| ID | Procedure | Expected result |
| --- | --- | --- |
| F01 | Try run.bat in a disposable copy with its expected virtual environment absent. Separately run the terminal command if dependencies are missing. | The missing-environment launcher gives its setup instruction. Record dependency errors from the terminal and verify the documented install procedure resolves them. |
| F02 | Close the isolated app and put invalid language, work/rest, cue style/retention/seconds and snooze values into its test-only INI using QSettings or a text editor. | Safe defaults load: English, 50/10, default event presets and snooze 2. The app remains operable. Keep the invalid sample as local evidence. |
| F03 | If you can safely control permissions on the disposable profile, deny settings writes after launch, change a setting, then restore access. Also try a startup profile that cannot be written. | An in-session save failure is shown in Options while the setting works for that session. An unwritable startup folder produces a storage message. Record recovered disk values after access is restored. |
| F04 | Force-stop only the printed test PID, then relaunch the same profile. | The old lock recovers, the app starts once and saved settings remain readable. Partial saves recover or produce a reproducible failure report. |

## Full effect matrix

For each language, test these eight event/retention pairs against all five styles.

| Event | Retention pairs |
| --- | --- |
| Work starts | timed, until dismissed, whole interval |
| Break starts | timed, until dismissed, whole interval |
| Break ends / waiting | timed, until dismissed |

For each pair, use Edge glow, Companion bubble, Top banner, Dim screen and Cover screen. This gives 40 cases per language. Keep anywhere off as the base case.

Repeat each interactive case with anywhere on. Interactive cases are all click/interval cases plus timed Cover. That adds 28 cases per language, for **68 per language and 136 total**.

For every row, record a preview result and a real-transition result. To exercise the real transition, set the event's preset, close Options and reach that event through the real timer. Configure several upcoming event rows in one cycle where possible. Preview alone does not verify interval expiry, the waiting state or snooze.

Use IDs `V-EN-001` through `V-EN-068` and `V-KO-001` through `V-KO-068`, ordered by event, style, retention and anywhere off/on. Use the columns below to record every combination in an ignored local results sheet.

| ID | Language | Event | Style | Retention | Anywhere | Preview | Real transition | Notes/evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| V-EN-001 | en | work | edge | timed | unavailable | NOT RUN | NOT RUN | |

## Completion and report

Every scenario ID and variation has a status and evidence or a reason it could not run. Keep unresolved observations and unavailable display configurations explicit. A useful report is `T06 / ko / waiting-cover-click / secondary 150% / Start work left one cover visible / reproduced 2 of 3 / screenshot filename`.

Mark a scenario PASS after all the states, input values and routes listed in that row have been checked. Record the language and screen configuration used for each run.

Test results apply to the recorded source hashes and environment. A later fix invalidates affected checks and should be rerun on that changed snapshot.

## Alpha 3 posture cases (A3)

Run both languages with disposable settings and effects on/off. Record exact version, display arrangement and results separately from historical alpha-1/2 evidence.

| ID | Procedure and acceptance |
| --- | --- |
| A3-01 | Reach break while walking: stop at the same position, animate sitting down, then close eyes. No autonomous walk/hop during rest or paused rest. |
| A3-02 | Reach waiting, dismiss/snooze/preview reminders: remain seated with eyes open; no work starts until confirmed. |
| A3-03 | Start work from badge or reminder: stand in place before walking resumes; a pinned companion remains pinned. |
| A3-04 | Reset during sitting/rising, then change phase rapidly: continuous posture, no stale completion or jump. |
| A3-05 | Drag while seated, recover home, change monitor geometry: remain reachable and seated; dragging still saves pinning. Test negative origins/mixed DPI on suitable hardware. |
| A3-06 | Open Options > Licenses in both EXEs: new art/register, supplemental work-use permission and CC text accessible; defaults 50/10, startup off. |
| A3-07 | In both languages choose Classic/Mint apron under General > Character during ready, work, rest and waiting. The picture, tray and reminder skin update immediately; phase/deadline/posture/pinning stay intact. Restart preserves the choice. Unknown stored choices safely fall back to Mint apron. There is no license explanation below the character picker; the separate Licenses button still opens component notices. |
