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

**Expensive objects are built once, not per request**
- Trigger: constructing a compile-, parse-, or connect-heavy framework object inside a request handler or a per-item loop (compiled graph or pipeline, HTTP/DB client, schema validator, template environment, loaded model).
- Standard: build once at module/app scope, or memoize keyed on the static config alone; per-request inputs (tenant, model, effort) travel through invocation arguments, not the constructor.
- Smell: `.compile()` / `new Client()` / `Factory(...)` on the hot path → compile cost and per-item retention on every record.

**Hoisting to shared scope audits baked-in state**
- Trigger: moving a per-request object to module, singleton, or cached (`lru_cache`, DI singleton) scope — including as part of a build-once fix.
- Standard: enumerate everything the constructor bakes in — concurrency primitives, mutable buffers or accumulators, deadlines, tenant/auth context — and confirm each is either genuinely static config (and therefore part of the cache key) or moved to invocation state.
- Smell: a cached object holding a `Semaphore(n)` → an n-per-request bound silently becomes n-global; or a cache key that omits a config field, pinning stale config past a reload.

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

Security rows carry a sharper false-positive risk than the rest of the playbook, because
most security defects are defects of *absence* — a missing authz check has no syntax to
match on. Two gates apply to every row below:

- **Fire on evidence in the hunk.** A visible token (`verify=False`, `Math.random()`,
  `@v3`) is decidable from the diff. "No authz check anywhere" is a property of the whole
  program — check the middleware and route registration before flagging it.
- **Scope to the component that terminates the request.** TLS termination, security
  headers, and rate limiting often live in a proxy, gateway, or CDN. Absence in
  application code is not a violation when the edge owns it.

`Ref` cites CWE numbers because they are stable; OWASP category numbers are renumbered
between editions (the 2025 edition folded SSRF into A01 and added supply chain at A03).

### 4a. Input and data handling

**Input is validated at the boundary**
- Trigger: data crossing a trust boundary (request body, query param, external payload).
- Standard: validate/parse into a typed shape before use.
- Smell: raw request fields used directly.

**No injection**
- Trigger: building SQL, a shell command, or a template from variable input.
- Standard: parameterized queries / safe APIs / escaping.
- Smell: string interpolation into SQL, `exec`, or HTML.

**Paths from input are confined to a base directory**
- Trigger: a path segment, upload filename, or archive entry that came from outside.
- Standard: join, resolve to absolute, then assert the result is still under the base dir.
- Smell: `path.join(base, input)` with no containment check after resolving; archive
  extraction that trusts entry names (zip-slip). Traversal reads or overwrites files
  outside the intended directory.
- Ref: https://cwe.mitre.org/data/definitions/22.html

**Untrusted bytes are never deserialized into objects**
- Trigger: deserializing input that crossed a trust boundary.
- Standard: a data-only format (JSON) with a schema; never an object-graph deserializer.
- Smell: `pickle.loads(request.data)`, `yaml.load` without `SafeLoader`, Java native
  deserialization, `unserialize` — each reaches arbitrary code execution, not just bad data.
- Ref: https://cwe.mitre.org/data/definitions/502.html

**Model fields are allowlisted, not spread**
- Trigger: constructing or updating a record from a request body.
- Standard: name the writable fields explicitly.
- Smell: `User(**body)` / `Object.assign(user, req.body)` → the client supplies `role` or
  `isAdmin` and escalates privilege through a field nobody meant to expose.
- Ref: https://cwe.mitre.org/data/definitions/915.html

### 4b. Identity and access

**Authorization on every entrypoint**
- Trigger: a new route/handler/RPC that reads or mutates data.
- Standard: an authz check, not just authentication.
- Smell: a handler that assumes the caller is allowed.

### 4c. Crypto and secrets

**Security values come from a CSPRNG**
- Trigger: generating a token, session ID, password-reset code, salt, or nonce.
- Standard: a cryptographic RNG (`secrets`, `crypto.randomBytes`,
  `crypto.getRandomValues`) with at least 128 bits of entropy.
- Smell: `Math.random()`, `random.randint`, `uuid1`, or a timestamp-derived value used as
  a secret → predictable, so guessable offline.
- Ref: https://cwe.mitre.org/data/definitions/338.html

**Secret comparison is constant-time**
- Trigger: comparing a token, HMAC, signature, or API key.
- Standard: `hmac.compare_digest` / `crypto.timingSafeEqual`.
- Smell: `==` on a secret. Short-circuit comparison leaks the matching prefix length
  through timing, letting an attacker recover the value byte by byte.
- Ref: https://cwe.mitre.org/data/definitions/208.html

**Passwords use a memory-hard KDF**
- Trigger: storing or verifying a user password.
- Standard: argon2id (or bcrypt/scrypt) with a stated, tuned cost parameter.
- Smell: `sha256(password)`, `md5`, any bare hash, or a library default cost with no
  chosen number → GPU-cheap to crack in bulk after a dump.
- Ref: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html

**AEAD nonce/IV is unique per key**
- Trigger: encrypting with AES-GCM or ChaCha20-Poly1305.
- Standard: a fresh random 96-bit nonce (or a strict counter) per message, plus a bound on
  messages per key — randomly generated 96-bit nonces collide at roughly 2^32 messages.
- Smell: a constant or module-level IV, an IV derived from stable data (user ID, filename),
  or a reused buffer. Reuse repeats the keystream (leaking the XOR of plaintexts) *and*
  allows recovery of the authentication subkey, which permits forging valid tags for
  arbitrary messages — integrity fails, not just confidentiality.
- Ref: https://cwe.mitre.org/data/definitions/323.html ; https://eprint.iacr.org/2015/477.pdf

**TLS verification stays on**
- Trigger: constructing an HTTP/TLS client or a database connection.
- Standard: verify certificate chain and hostname; pin a CA bundle if the default store
  is wrong for the environment.
- Smell: `verify=False`, `rejectUnauthorized: false`, `InsecureSkipVerify: true`, `curl -k`,
  `NODE_TLS_REJECT_UNAUTHORIZED=0` — usually added to silence a local dev error and shipped.
- Ref: https://cwe.mitre.org/data/definitions/295.html

**Secrets not hardcoded**
- Trigger: a key, token, password, or connection string in source.
- Standard: **rotate the exposed credential first**, then read it from env/secret store.
  Removing the line does not remediate: the value persists in git history, in every fork
  and clone, and in CI logs.
- Smell: a literal credential committed; or a "fix" commit that moves the value to env
  without revoking it.
- Ref: https://cwe.mitre.org/data/definitions/798.html

### 4d. Supply chain

**Dependencies and CI actions are pinned**
- Trigger: adding or bumping a dependency, or a workflow step using a third-party action.
- Standard: a committed lockfile installed with a frozen resolver (`npm ci`,
  `uv sync --frozen`); third-party actions pinned to a full-length commit SHA; workflow
  `permissions:` set to least privilege.
- Smell: `uses: org/action@v3` (a mutable tag the upstream owner can repoint), a short SHA
  (forkable to a colliding commit), `npm install` in CI, a missing lockfile, or no
  `permissions:` block — a compromised action reads every secret in the repo.
- Ref: https://docs.github.com/en/actions/reference/security/secure-use

### 4e. Error and log hygiene

These two are one convention with two faces: detail goes to the log, redacted; a
correlation ID goes to the caller. Read alongside "No silently swallowed errors" in §6.

**Error responses carry no internals**
- Trigger: an error path that crosses a trust boundary.
- Standard: a generic message plus a correlation ID out; the detail stays in the log.
- Smell: a stack trace, SQL fragment, hostname, or file path in a 5xx body; a debug flag
  reachable in production → free reconnaissance for an attacker.
- Ref: https://cwe.mitre.org/data/definitions/209.html

**Logs exclude credentials and PII**
- Trigger: a new log or telemetry statement on an auth, payment, or personal-data path.
- Standard: log identifiers, not payloads; redact tokens, passwords, `Authorization`
  headers, and full personal identifiers.
- Smell: `log.info(request.headers)` or logging a whole request body → the secret is now
  in a log store with much broader read access than the secret store it came from.
- Ref: https://cwe.mitre.org/data/definitions/532.html

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
- Standard: log with context, or rethrow/wrap; never an empty handler. "With context" means
  identifiers and state, not the raw payload — see §4e for what must be redacted and for
  what may cross back to the caller.
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

## 8. Portability

**Runtime assumptions match supported environments**
- Trigger: changed code relies on behavior that varies by OS, shell, runtime, filesystem, or tool version and materially differs between supported Linux and macOS environments.
- Standard: verify the smallest relevant check on the least-capable supported environment (or equivalent version). Do not require an unconditional OS matrix, Windows coverage, or new CI scaffolding.
- Smell: empty-array handling works on a newer Bash but fails under macOS Bash 3.2 with `set -u`, or validation covers only a newer developer environment.
