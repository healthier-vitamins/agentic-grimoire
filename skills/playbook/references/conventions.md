# The playbook

Convention checklist for the `playbook` skill. Each row: **Trigger** (when it applies — the false-positive gate), **Standard** (what the playbook expects), **Smell** (what the omission looks like in code), **Ref** (canonical source). Fire a row only when its Trigger matches a changed hunk.

This list is seeded, not exhaustive. When a change touches a convention not listed here that a senior would expect, flag it anyway and note it for adding to this file.

## 1. Resilience / remote calls

**Backoff has jitter**
- Trigger: a retry loop with a computed delay against a shared or remote dependency (HTTP, DB, queue, third-party API), especially when more than one instance/replica runs the code.
- Standard: full jitter — `delay = random(0, min(maxDelay, base * 2 ** attempt))`. Randomized, not deterministic.
- Smell: `base * 2 ** attempt` or `min(base * 2 ** attempt, cap)` with no `random(...)`. Deterministic delay → replicas retry in lockstep → thundering herd on the recovering server.
- Ref: https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/ ; https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/

**Retry budget is bounded**
- Trigger: any retry loop.
- Standard: a hard max-attempts cap and a max total delay; ideally a per-caller retry budget so retries can't amplify load without limit.
- Smell: unbounded loop, no max attempts, or an uncapped growing delay.
- Ref: https://docs.aws.amazon.com/wellarchitected/latest/framework/rel_mitigate_interaction_failure_limit_retries.html

**Per-call timeout**
- Trigger: a network/IO call (HTTP client, DB query, RPC, lock acquisition).
- Standard: an explicit timeout on every outbound call; never rely on the default (often infinite).
- Smell: client constructed with no timeout; `await call()` with no deadline.
- Ref: https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/

**Retries are idempotency-safe**
- Trigger: retrying a non-idempotent operation (POST that creates, charge, send, write-without-key).
- Standard: send an idempotency key, or gate the retry to idempotent operations only.
- Smell: a create/charge/send inside a retry loop with no idempotency key → duplicates on retry.
- Ref: https://stripe.com/docs/api/idempotent_requests

**Circuit breaker on a flaky dependency**
- Trigger: repeated calls to a dependency that can stay down for a sustained period.
- Standard: a circuit breaker (or equivalent) to stop hammering a failing dependency and let it recover.
- Smell: retry-forever against a hard-down dependency with no breaker.

**Failure mode is explicit (fail-open vs fail-closed)**
- Trigger: a guardrail, auth check, or safety gate that calls an external service.
- Standard: the behavior when the dependency is unavailable is a deliberate, documented choice (fail-open or fail-closed).
- Smell: a `catch` that swallows the error and silently allows (or silently blocks) with no stated intent.

## 2. Concurrency

**No check-then-act race**
- Trigger: read a value, then write based on it (counter, balance, "if not exists then create").
- Standard: atomic op, transaction, or lock around the read-modify-write.
- Smell: `get()` then `set()` with no atomicity; two callers interleave and lose an update.

**Connection pooling**
- Trigger: opening a DB/HTTP connection inside a request or loop.
- Standard: reuse a pooled connection.
- Smell: a fresh connection created per call → handshake cost and exhaustion under load.

**Debounce / throttle on high-frequency triggers**
- Trigger: a handler fired by rapid events (scroll, keypress, webhook bursts).
- Standard: debounce or throttle.
- Smell: unbounded work per event.

## 3. Data / DB

**Migrations are reversible and additive**
- Trigger: a schema migration.
- Standard: forward-only safe change; a down path or a documented reason there isn't one; no edits to already-applied migrations (new migration instead).
- Smell: editing a committed migration; a destructive change with no rollback plan.

**Multi-step writes in a transaction**
- Trigger: two or more writes that must all succeed or all fail (e.g. write + audit log).
- Standard: wrap in a transaction.
- Smell: sequential writes with no transaction → partial state on mid-failure.

**No N+1 query**
- Trigger: a query inside a loop over rows.
- Standard: batch / join / eager-load.
- Smell: one query per iteration.

**Unbounded reads are paginated**
- Trigger: a list/scan query with no limit.
- Standard: pagination or an explicit cap.
- Smell: `findAll()` on a table that grows without bound.

## 4. Security

**Input is validated at the boundary**
- Trigger: data crossing a trust boundary (request body, query param, external payload).
- Standard: validate/parse into a typed shape before use.
- Smell: raw request fields used directly.

**Authorization on every entrypoint**
- Trigger: a new route/handler/RPC that reads or mutates data.
- Standard: an authz check, not just authentication.
- Smell: a handler that assumes the caller is allowed.

**No injection**
- Trigger: building SQL, a shell command, or a template from variable input.
- Standard: parameterized queries / safe APIs / escaping.
- Smell: string interpolation into SQL, `exec`, or HTML.

**Secrets not hardcoded**
- Trigger: a key, token, password, or connection string in source.
- Standard: from env/secret store.
- Smell: a literal credential committed.

## 5. API surface

**Stable error contract**
- Trigger: a new or changed API response.
- Standard: consistent error shape and status codes matching the rest of the surface.
- Smell: ad hoc error bodies / wrong status codes.

**Pagination and rate limiting on public/list endpoints**
- Trigger: a list endpoint or a public-facing write.
- Standard: pagination on lists; rate limiting on abuse-prone endpoints.
- Smell: unbounded list response; no throttle on a public mutation.

## 6. Observability

**No silently swallowed errors**
- Trigger: a `catch`/`except` block.
- Standard: log with context, or rethrow/wrap; never an empty handler.
- Smell: `catch {}` or `except: pass`.

**Metrics on retries and latency**
- Trigger: a retry loop or a slow external call.
- Standard: emit a metric/telemetry for attempts and wait time so the behavior is observable in prod.
- Smell: retries happen invisibly with no signal.

## 7. Config

**Magic numbers are config with sane defaults**
- Trigger: a tunable constant that operations may need to change (timeout, retry count, backoff base/cap, page size, batch size).
- Standard: read from env/config with a sensible default; document the unit.
- Smell: a hardcoded `2.0` / `60` / `10` buried in code with no name or override path.
