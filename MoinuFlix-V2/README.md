# MoinuFlix V2

> Premium media management, ingestion and library interface for MoinuFlix.

---

## Project Status

**Version:** V2  
**Stage:** Foundation / Master UI V2  
**Status:** In Development

MoinuFlix V2 is a new-generation architecture being rebuilt from the verified V1 implementation.

The V2 project is being developed **step-by-step** to prevent old code, old JSON structures, UI code and data logic from becoming mixed together.

---

## V2 Development Rules

### 1. V2 Is Separate From V1

The existing V1 project remains the reference implementation.

V1 files must **not** be modified during V2 development unless explicitly requested.

V2 must be developed inside this new project folder.

---

### 2. Old Code Is Reference Only

The old `p_push.html` and other V1 files may be inspected to recover existing features and working logic.

Do not blindly copy the old implementation.

Each feature must be:

1. Audited
2. Documented
3. Improved where required
4. Implemented in V2
5. Tested
6. Marked complete in `STATUS.md`

---

### 3. Master UI First

The common UI system is the foundation of V2.

All major pages should use the same Master UI design system.

Common UI belongs in:

```text
c_core/
├── ui_style.css
├── ui_components.css
└── ui.js
