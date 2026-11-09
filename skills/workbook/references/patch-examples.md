# Patch examples

Two chat answers in the Patch shape. Copy the shape, not the maths.

## Valid but unfinished move

The reader asks: from du/dx = 3x², why is dx = (1/3x²) du, not du on the bottom? They want to multiply both sides by 1/du.

Goal: the slide wants dx alone on one side.

Your way is correct. The slide skips your middle line.

Plain numbers first. 12 plays du, 2 plays dx, 6 plays 3x².

| Step | Plain numbers | Symbols |
|---|---|---|
| Start | 12/2 = 6 | du/dx = 3x² |
| 1. Multiply both sides by 1 over the top. | 1/2 = 6/12 (both 0.5 ✓) | 1/dx = 3x²/du |
| 2. Flip both sides. | 2 = 12/6 ✓ | dx = du/3x² |

The missing step is the flip. du/3x² is the same as (1/3x²) du.

## Why this substitution

The reader asks: in ∫ x² e^(x³) dx, why u = x³?

Goal: pick u so the leftover x terms cancel.

The slope of x³ is 3x². The integral already holds x², so the x² cancels.

The rival u = x² gives dx = du/2x. Then x² × 1/2x = x/2, and an x is left behind.

| Choice | dx | Leftover after cancelling | Works |
|---|---|---|---|
| u = x³ | du/3x² | 1/3 | ✓ |
| u = x² | du/2x | x/2 | ✗ |

Check the cancellation at x = 2: 4 × 1/12 = 1/3 ✓.

Rule: pick u so its slope is already in the integral. A different number in front is fine.
