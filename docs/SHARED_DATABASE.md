# Shared database for Streamlit Cloud

The dashboard can use a shared Postgres database so listings scanned by one user
are visible to every visitor of the Streamlit app.

## Configure Streamlit Cloud

1. Create a Postgres database, for example Supabase, Neon, Railway, or Render.
2. Copy the database connection string.
3. In Streamlit Community Cloud, open the app settings.
4. Add this secret:

```toml
DATABASE_URL = "postgresql://USER:PASSWORD@HOST:PORT/DATABASE"
```

`postgres://...` URLs are also accepted and normalized automatically.

## Behavior

- If `DATABASE_URL` is configured, the app reads and writes listings in the shared
  cloud database.
- If `DATABASE_URL` is not configured, the app falls back to local
  `rental_listings.db`.
- The dashboard's "增量上新" button only merges newly scanned or changed listings.
  It does not clear saved listings.
- Local SQLite storage is useful for development, but it should not be treated as
  permanent storage on Streamlit Community Cloud.
