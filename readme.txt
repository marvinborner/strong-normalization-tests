Test suite for strong normalization
───────────────────────────────────

Languages may be tested in one of two ways:

- if the language reduces strongly, translate the tests to the language and use it to reduce the terms directly
- if not, use a higher order (or NbE) reducer to reduce the terms

Please contribute!

┌───────┐
│ Tests │
└───────┘

The tests are reconstructed from the handwritten test suite of the bruijn programming language.
Currently the suite consists of 3466 tests.
It comprises many different data structures and numeric encodings.
Some of the tests are also quite long and contain redundant terms and potential for sharing.

Each line in `tests` consists of "<bruijn term>: <term (blc)> - <nf (blc)>".
The left term is expected to be α-equivalent to the right term after strong β-reduction.

Any test reducing for more than 5s without reaching a normal form is deemed to have failed.

┌─────────┐
│ Results │
└─────────┘

┌─────────────────┬────────┬─────────┬────────┐
│ Test            │ Passed │ Timeout │ Failed │
├─────────────────┼────────┼─────────┼────────┤
│ Haskell HOAS    │ 3466   │ 0       │ 0      │
│ Optiscope       │ 3385   │ 81      │ 0      │
│ Tromp AIT/nf.c  │ 1935   │ 5       │ 1526   │
│ Your project    │ ?      │ ?       │ ?      │
└─────────────────┴────────┴─────────┴────────┘

┌─────────┐
│ Effects │
└─────────┘

- improved optiscope: https://github.com/etiamz/optiscope/issues/5
