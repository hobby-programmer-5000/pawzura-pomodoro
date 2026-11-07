[English](INSPIRATION.md) · [한국어](INSPIRATION.ko.md)

# References and inspiration

Pawzura Pomodoro's visual reminders were informed by the interaction ideas below. We consulted these public documents on November 7, 2026.

| Reference | Idea we drew from it | How it informed this app |
| --- | --- | --- |
| [Time Out, Break Controls](https://dejal.com/help/timeout/en/controls.html) | An optional end-of-break confirmation keeps the break visible until the user responds. The documentation identifies this as a supporter feature. | The completed-break screen can stay visible, and the next work interval begins when the user clicks Start work. |
| [Stretchly, official README](https://github.com/hovancik/stretchly/blob/trunk/README.md) | Fullscreen, transparency and all-display preferences provide different ways to present a break. | Each transition has its own appearance, including dim and opaque covers on every monitor. |
| [Workrave, Break windows](https://workrave.org/docs/breaks/breaks/) | Postponing closes a break window and reminds the user again later. | A completed-break reminder can be postponed for a configurable number of minutes. |
| [BreakTimer, official site](https://breaktimer.app/) | Customizable break messages and notifications with snooze choices. | Clear phase-specific messages and a visible reminder control informed the options. |
| [Pawzura pet controls](https://github.com/hobby-programmer-5000/pawzura/blob/23bd3b90435d6e5ab6c0dd510d8dc5b8897489a6/pawzura/pet.py) | Walking, drag-to-pin, reactions and placement across monitors. | The app directly reuses these MIT-licensed movement controls with its own tomato drawing. |

Product direction and feature choices came from the user. Codex implemented the Qt timer, configurable effects and original vector tomato in this checkout. The web references above informed interaction design. The implementation uses this project's Qt code and original artwork.

The app's original code and artwork follow the repository's [MIT license](LICENSE). Runtime libraries retain their own terms, recorded in the [dependency notices](THIRD-PARTY-NOTICES.md). These references document design influences alongside those component notices.
