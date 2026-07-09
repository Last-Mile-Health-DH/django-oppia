OppiaMobile - django-oppia
===========================

django-oppia is the server side component for the OppiaMobile learning platform

For documentation please visit: https://oppiamobile.readthedocs.io

For information on how to contribute, submit bug reports and feature requests,
please visit:
https://github.com/DigitalCampus/django-oppia/blob/master/CONTRIBUTING.md

For help and support, please join our OppiaMobile Community site at
https://community.oppia-mobile.org/

## Docker deployment

The stack runs via Docker Compose: `oppia` (Django app, served by gunicorn),
`db` (MySQL), `caddy` (reverse proxy - handles TLS and serves static/media
directly), and `oppia-cron` (runs `oppiacron`/`update_summaries` on a loop).

### First-time setup

1. Copy `example.env` to `.env` and fill in real values (DB credentials,
   `SECRET_KEY`, `DOMAIN`, initial admin user, etc). `.env` is gitignored -
   it holds real secrets, `example.env` is just the tracked template.
2. Copy `oppiamobile/settings_secret.py.docker-template` to
   `oppiamobile/settings_secret_docker.py`. This is the Django settings file
   actually used inside the container (bind-mounted at runtime); it reads
   its values from the environment variables set in `.env`. It's also
   gitignored, since it's specific to your deployment.
3. Build and start everything:

   ```
   docker compose -p lmhoppia up --build
   ```

   On first run this also applies migrations, compiles SCSS, collects
   static files, loads default fixtures, and creates the initial admin
   user (from `DJANGO_SUPERUSER_*` in `.env`) if it doesn't already exist.

4. Visit `https://<DOMAIN>` (`https://localhost` by default). Caddy issues
   a locally-trusted certificate automatically; browsers will show a
   certificate warning until that CA is trusted on your machine - safe to
   click through for local development.

### Notes

- Application code is not stored in a persistent volume, so
  `docker compose -p lmhoppia up --build` always runs whatever you most
  recently built - no manual volume cleanup needed to pick up code changes.
- `static`, `media`, `upload`, and the database do persist across restarts
  (named volumes), so re-running `up --build` won't lose uploaded content.

