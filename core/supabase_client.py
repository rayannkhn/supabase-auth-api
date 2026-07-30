import os

from supabase import Client, create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError(
        "SUPABASE_URL and SUPABASE_KEY must be set (check your .env file)."
    )

# Must be the service_role key, not the anon key: /auth/logout revokes an
# arbitrary caller-supplied token via supabase.auth.admin.sign_out(token),
# which Supabase only allows for the service role.
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
