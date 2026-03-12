# secrets-broker plan

## done
- repo initialized

## in progress
- netlify broker (feature/netlify-broker branch)

## todo

### remote notification (punted)
when the container is not local, deliver the form_url via a push notification
so the user does not have to watch the terminal.
options: Ntfy (self-hosted or ntfy.sh), Pushover (one-time $5), email.
needs: SECRETS_BROKER_NOTIFY_URL env var in client, notify step in request.py.

### github actions integration
use repository_dispatch as an alternative request channel.
repo environment secrets as the secret source instead of user-typed values.

### admin UI
page listing pending requests with timestamps.

### rate limiting
prevent token flooding on /api/request.

### configurable TTL
allow per-request TTL override.
