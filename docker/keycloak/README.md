# Keycloak infrastructure

Open Forms supports OpenID Connect as an authentication protocol. Keycloak is
an example of an Identity Provider that supports OIDC

We include a compose stack for development and CI purposes. This is **NOT** suitable
for production usage.

## docker-compose

Start a Keycloak instance in your local environment from the parent directory:

```bash
docker-compose -f docker-compose.keycloak.yml up -d
```

This brings up Keycloak, the admin interface is accessible at http://localhost:8080/.
You can log in with `demo:demo`.

## Load fixtures

Before the DigiD login via OIDC can be tested, two fixtures need to be loaded.
Assuming the docker containers specified in `docker-compose.yml` in the root directory
are running, run the following commands:

```bash
cat keycloak/fixtures/oidc_form.json | docker exec -i <openforms_container_name> src/manage.py loaddata --format=json -
cat keycloak/fixtures/oidc.json | docker exec -i <openforms_container_name> src/manage.py loaddata --format=json -
```

This loads an example form configured to use DigiD via OIDC for authentication and
it loads a configuration to connect to our Keycloak instance.

## Test login flow

To test the login flow, navigate to `http://127.0.0.1:8000/digid-oidc/`
(not `localhost`, because this domain is not on the allowlist in the Keycloak config).

Click `Inloggen met DigiD` and fill in `testuser` for both username and password
in the Keycloak login screen. If everything succeeded, you are now redirected back to the form.
