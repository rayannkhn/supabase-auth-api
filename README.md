# supabase-auth-api

A FastAPI authentication API that delegates identity to **Supabase Auth** — signup, login,
token verification, and logout — instead of implementing password hashing or session
storage itself. Public routes are open; protected routes require a Supabase-issued
JWT in the `Authorization` header, verified through a single reusable dependency.

## Environment variables

Copy the template and fill in your own Supabase project's values:

```bash
cp .env.example .env
```

| Variable | Description |
|---|---|
| `SUPABASE_URL` | Your project's URL (Project Settings → API), e.g. `https://xxxx.supabase.co` |
| `SUPABASE_KEY` | The **service_role** secret key (Project Settings → API) — **not** the anon/public key. See "Why service_role, not anon" below. |
| `PORT` | Port the API listens on (default `8000`) |

`.env` is listed in `.gitignore` and is never committed; only `.env.example` (placeholders
only) is tracked.

### Why service_role, not anon

`/auth/logout` needs to revoke one specific, caller-supplied JWT — but Supabase's
non-admin `auth.sign_out()` doesn't take a token argument at all; it only signs out
whatever session happens to be cached inside the client object, which doesn't work
for a stateless backend serving many concurrent users off one shared client. The
SDK's own docstring for `sign_out()` says: *"For advanced use cases, you can revoke
all refresh tokens for a user by passing a user's JWT through to `admin.sign_out`."*
That admin call is exactly what `/auth/logout` uses (`supabase.auth.admin.sign_out(token)`
in [routes/auth.py](routes/auth.py)), and Supabase only authorizes admin calls with the
service_role key. Signup, login, and token verification all work fine with the same key.

## Running it

```bash
pip install -r requirements.txt
python main.py
```

Single command once dependencies are installed. It reads `PORT` from `.env` and starts
uvicorn. On boot you'll see `Server running and connected to Supabase` in the logs.

Interactive docs: `http://localhost:8000/docs`

## Auth dependency

All token verification lives in **one place**: `get_current_user` in
[auth/dependencies.py](auth/dependencies.py). It parses the `Authorization` header,
requires a well-formed `Bearer <token>`, calls `supabase.auth.get_user(token)`, and
raises the correct `401` on any failure. `/protected/profile`, `/protected/dashboard`,
and `/auth/logout` all depend on it — none of them parse headers or call Supabase
themselves. `/auth/logout` additionally depends on the shared `bearer_scheme` to read
the raw token string for `sign_out`; FastAPI caches dependency results per request, so
that's reading already-parsed credentials again, not duplicating any verification logic.

## API reference

| Route | Method | Auth required | Expected status codes |
|---|---|---|---|
| `/public/info` | GET | No | 200 |
| `/auth/signup` | POST | No | 201 (created), 400 (missing email/password, or Supabase signup error) |
| `/auth/login` | POST | No | 200 (success, returns `access_token` + `refresh_token`), 400 (missing fields), 401 (invalid credentials) |
| `/protected/profile` | GET | Yes (Bearer token) | 200 (returns id/email/created_at), 401 (missing/malformed header or no token), 401 (invalid/expired token) |
| `/protected/dashboard` | GET | Yes (Bearer token) | 200, 401 (same cases as above) — demo route proving the dependency is reusable |
| `/auth/logout` | POST | Yes (Bearer token) | 204 (success), 401 (missing/invalid/expired token) |

## Swagger UI

`/docs` shows a padlock next to every route that depends on `get_current_user`, because
that dependency depends on FastAPI's `HTTPBearer` security scheme, which FastAPI
automatically registers in the OpenAPI spec. Click **Authorize**, paste an access token
(no `Bearer ` prefix — Swagger adds it), and **Try it out** on `/protected/profile`.

Verified against a real Supabase project: authorized with a live access token in the
Swagger UI and executed `/protected/profile` via **Try it out** — response `200` with
the real user's `id`, `email`, and `created_at`, and the generated `curl` command showed
the `Authorization: Bearer` header being sent correctly.

**Screenshot pending** — captured the same result as structured page data instead of a
screenshot image this round. Take one yourself (Authorize → paste a token → Try it out
on `/protected/profile`), save it at `docs/swagger-screenshot.png`, and reference it here
as `![Swagger UI screenshot](docs/swagger-screenshot.png)`.

## Verification checklist

- [x] Server starts with a single documented command (`python main.py`) and logs
      `Server running and connected to Supabase`.
- [x] `.env` gitignored, `.env.example` committed with placeholders only — confirmed on
      the pushed GitHub repo (`.env` absent, `.env.example` present).
- [x] `/auth/signup` and `/auth/login` verified against a real Supabase project: signup
      returned `201` with a real user object, login returned `200` with a real
      `access_token`/`refresh_token`.
- [x] `/protected/profile` extracts and verifies the bearer token via
      `get_current_user` — verified with a real token (`200` + real user data), a
      tampered token (`401` invalid/expired), and no header (`401` access token
      required).
- [x] Status codes verified end-to-end, against a real Supabase project: `201` signup,
      `200` login/read, `204` logout, `400` missing inputs, `401` missing/malformed/
      invalid/expired token.
- [x] Auth check extracted into a single reusable dependency, applied to 3 routes
      (`/protected/profile`, `/protected/dashboard`, `/auth/logout`).
- [x] Swagger `/docs` confirmed to apply the `HTTPBearer` security scheme to exactly
      those 3 routes, and a live Authorize → Try it out run against `/protected/profile`
      succeeded with a real token.
- [x] **Logout genuinely revokes the token**, not just a 204 no-op: the same access
      token that returned `200` from `/protected/profile` before logout returned `401`
      "Invalid or expired token" after calling `/auth/logout` — confirms
      `admin.sign_out(token)` actually invalidates that specific session server-side.
- [x] Public GitHub repo with 8 clean commits (Stage 0 through Stage 6, plus one bug
      fix found during real-project testing — `load_dotenv()` was missing).
- [ ] Swagger screenshot image still needed (see above).
