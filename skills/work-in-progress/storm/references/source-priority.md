# Research Source Priority

Shared ranking for research-driven skills. Trace every claim to the source that **owns**
it, and find what practitioners actually ship, not what blogs recommend in the abstract.

**Rank by what the claim is about** (highest first within each row):

| Claim | Owners |
|---|---|
| API, syntax, version, config, defaults | Official documentation (`Context7` MCP, or the canonical docs site) → source code, changelog, release notes → the project's issue tracker |
| How practitioners build and run it | Big-tech engineering blogs & published design specs (Google, Meta, Amazon, Netflix, Microsoft, Apple, plus Uber, Grab, Airbnb, Stripe, etc.) → public RFCs, architecture decision records → reputable engineering newsletters |
| Empirical — X beats Y, by how much | Peer-reviewed papers and arXiv preprints (alphaXiv / arXiv) — note the sample size and whether it was peer-reviewed → vendor benchmarks, marked self-reported |
| Failures — what breaks, what was abandoned | Postmortems, incident and rollback write-ups, issue trackers |

When sources conflict, the claim's owner wins: a blog that contradicts the docs on an API
default is wrong about the default, and a vendor post is weaker than a paper on whether
its product wins.

Avoid SEO content farms, unattributed reposts, and AI-generated listicles. Cite the
source per claim.
