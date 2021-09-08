set -e

echo "Running SQL file: $SQL_FILE"
PSQL_CONNECT_WRITE_MODE="sslmode=verify-ca sslrootcert=/root/.postgresql/root.crt sslcert=/root/.postgresql/postgresql.crt sslkey=/root/.postgresql/postgresql.key hostaddr=$DB_HOST user=rmuser password=${DB_PASSWORD:=password} dbname=$DB_NAME"

psql "$PSQL_CONNECT_WRITE_MODE" -f "$SQL_FILE"
echo "Finished running file at $(date -u +"%FT%H-%M-%S")"
