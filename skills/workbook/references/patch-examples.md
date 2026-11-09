# Patch examples

Five chat answers in the Patch shape. Copy the shape, not the maths.

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

## Skipped move: where did du go?

The reader asks: the line was ∫ √u du, then it is suddenly (2/3)u^(3/2). Where did du go?

Goal: turn ∫ √u du into an answer with no ∫ and no du.

The du does not turn into anything. ∫ … du is one instruction: find what has slope √u, with u as the letter. It works like ∫ x dx = x²/2, where no dx is left either.

| Power rule move | Result | Working |
|---|---|---|
| start | u^(1/2) | |
| add 1 to the power | u^(3/2) | 1/2 + 1 = 3/2 |
| divide by the new power | u^(3/2) ÷ 3/2 | |
| tidy the fraction | (2/3)u^(3/2) | 6 ÷ 3/2 = 4 = 6 × 2/3 ✓ |

Check: the slope of (2/3)u^(3/2) is (2/3)(3/2)u^(1/2) = √u ✓.

In the sheet, the integrating step gains the du sentence and the table, and every other integration in u points back to it.

## Skipped moves: an answer check in one line

The reader asks: "The answer's derivative is (2/3)·(3/2)u^(1/2)·du/dx = √u e^(−x) = √3 · 1." What is this?

Goal: show the answer is right by matching its slope to the integrand at one number.

Split the line into four steps:

1. Why it works: integrating undoes differentiating, so the answer's slope must equal the integrand.
2. The integrand at x = 0: √(4 − 1)/1 = √3.
3. The answer's slope by the chain rule, one part per line:

| Part | Slope | Why |
|---|---|---|
| outside (2/3)u^(3/2) | u^(1/2) | bring 3/2 down; (2/3)(3/2) = 1 |
| inside u = 4 − e^(−x) | e^(−x) | Step 2 |
| multiply | √u · e^(−x) | outside × inside |

4. Put in x = 0: u = 3 and e^0 = 1, so √3 · 1 = √3 ✓.

## Invalid move: outside only, then put u back

The reader asks: why must e^(−x) come back? Differentiate (2/3)u^(3/2) to get u^(1/2), then put u back.

Goal: the slope per step of x.

Putting u back only renames the letter. The outside slope is the change per step of u.

Nudge x from ln 2 by 0.001:

| What moves | By how much |
|---|---|
| x | 0.001 |
| u = 4 − e^(−x) | 0.0005 |
| answer (2/3)u^(3/2) | 0.000935 |

| Route | Slope at x = ln 2 | Matches 0.935? |
|---|---|---|
| outside only, then put u back | 1.871 | ✗ |
| outside × inside | 0.935 | ✓ |

The old check used x = 0, where e^(−x) = 1, so the missing factor hid. Test where no factor equals 1.
