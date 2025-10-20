# Database Migrations

This directory contains SQL schema snapshots that document the database structure at different points in time.

## Overview

This project uses **Alembic** for database migrations. The SQL files in this directory are for documentation purposes - they show the complete database schema after each major migration.

## How Migrations Work

### For New Developers

When you clone this repository:

1. Set up your `.env` file with your `DATABASE_URL`
2. Run migrations to create all tables:
   ```bash
   alembic upgrade head
   ```

That's it! Alembic will create all tables automatically based on the migration history.

### Viewing Schema

To see the current database schema, check the latest numbered SQL file in this directory (e.g., `001.sql`).

### Making Schema Changes

When you need to modify the database schema:

1. **Update the models** in `app/db_models.py`

2. **Generate a migration**:
   ```bash
   alembic revision --autogenerate -m "Description of changes"
   ```

3. **Review the migration** in `alembic/versions/[hash]_description.py`

4. **Apply the migration**:
   ```bash
   alembic upgrade head
   ```

5. **Document the changes** (optional but recommended):
   - Create a new SQL snapshot (e.g., `002.sql`) if the change is significant

### Creating SQL Snapshots

To create a new SQL snapshot after a migration:

```bash
# Copy and modify the previous snapshot
cp migrations/001.sql migrations/002.sql

# Or manually document the changes based on your db_models.py
```

Update the file header with:
- Date of the migration
- Description of changes
- Alembic revision ID

## Migration History

### 001.sql (2025-10-15) - Initial Schema
**Alembic Revision:** `57fe7a40e8b6`

- Created base schema for Klara application
- Added `users` table with email authentication and first_name field
- Added `tasks`, `shopping_items`, and `calendar_events` tables
- Set up CASCADE delete constraints for data integrity
- Added indexes on foreign keys for query performance

## Useful Alembic Commands

```bash
# Show current migration version
alembic current

# Show migration history
alembic history --verbose

# Upgrade to latest migration
alembic upgrade head

# Upgrade to specific revision
alembic upgrade <revision_id>

# Rollback last migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>

# Generate SQL without executing (dry run)
alembic upgrade head --sql
```

## Troubleshooting

### "Target database is not up to date"
Run `alembic upgrade head` to apply pending migrations.

### "Can't locate revision"
Ensure all migration files in `alembic/versions/` are present. Pull latest changes from git.

### Database connection issues
- Verify `DATABASE_URL` in `.env`
- For Supabase: use the direct connection string (not pooler URL)
- Check that your IP is whitelisted in Supabase settings

## Best Practices

1. **Always review** auto-generated migrations before applying them
2. **Test migrations** on a development database first
3. **Commit migration files** to version control
4. **Document significant changes** by creating new SQL snapshots
5. **Use descriptive migration messages** that explain the "why" not just the "what"
6. **Never edit applied migrations** - create a new migration to fix issues

## Supabase Integration

This project uses Supabase as the PostgreSQL database. Migrations are applied directly to the Supabase database using the connection string in your `.env` file.

To view your database in Supabase:
1. Go to your Supabase Dashboard
2. Navigate to "Table Editor" to see all tables
3. Navigate to "Database" > "Migrations" to see the Alembic version tracking

Alembic manages the schema, while Supabase provides the hosting, authentication, and real-time features.
