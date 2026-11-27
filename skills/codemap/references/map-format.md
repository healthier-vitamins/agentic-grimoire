# `map.json`: the hand-written half of a code map

`<project>/.codemap/map.json` holds only what reading the code gives. Every count, line
number, import edge and state list comes from the scan; `build.py` fills them in and checks
each citation below against the code. One problem → one line on stderr, exit 1.

```json
{
  "title": "shop",
  "areas": [
    {
      "name": "Checkout",
      "sections": [
        {
          "slug": "place-order",
          "job": "Turns a cart into an order, holds the stock and asks for payment",
          "files": ["src/shop/checkout.py", "src/shop/orders/"],
          "entry_points": ["src/shop/checkout.py::Checkout.place"],
          "statecharts": [
            {
              "name": "an order",
              "states_from": "src/shop/orders/model.py:12",
              "transitions": [
                {"from": "*", "to": "pending", "at": "src/shop/orders/store.py:40",
                 "when": "the cart is placed"},
                {"from": "pending", "to": "paid", "at": "src/shop/orders/store.py:71",
                 "when": "the payment succeeds"}
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

| Field | Rule the build checks |
|---|---|
| `slug` | Kebab-case, unique. It names the codewalk folder: `.codewalk/<slug>/page.html`. |
| `job` | One line, no closing period (the prompt adds one). Plain words, no backticks. |
| `files` | Scanned source files, or a folder ending in `/` (every scanned file under it). A file sits in at most one section. |
| `entry_points` | `path::Symbol` as `facts.json` spells it (`Class.method` for methods). The build looks up the line. |
| `statecharts` | Optional. Only where the code stores a state and moves it. |
| `states_from` | `path:line` of a state list in `facts.json` (`states` of that file): an enum, a `Literal` alias, a string union, or a SQL `CHECK (col IN ...)`. The states are taken from there. |
| `transitions[].from`, `.to` | States from that list; `from` may be `"*"` for the start. |
| `transitions[].at` | `path:line` where the move happens. That line or one of the two after it must spell `to` as a word; for a column default (`DEFAULT 'pending'`) cite the default. The page names the enclosing function itself. |
| `transitions[].when` | Optional, a few words: the condition of the move. |

A state no transition reaches renders on a last row: that is a finding, not a layout bug.
Files no section holds are printed by the build; tests usually stay out.
