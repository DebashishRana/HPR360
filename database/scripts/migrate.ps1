[CmdletBinding()]
param(
    [string]$ConnectionString = $env:PEOPLEPAY360_MIGRATION_DATABASE_URL
)

$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($ConnectionString)) {
    throw 'Set PEOPLEPAY360_MIGRATION_DATABASE_URL to a direct PostgreSQL migration URL.'
}

$psql = Get-Command psql -ErrorAction Stop
$migrationDir = Join-Path $PSScriptRoot '..\migrations'
$migrations = Get-ChildItem -LiteralPath $migrationDir -Filter '*.sql' | Sort-Object Name

foreach ($migration in $migrations) {
    $version = [System.IO.Path]::GetFileNameWithoutExtension($migration.Name)
    $trackingTableExists = & $psql.Source --no-psqlrc --tuples-only --no-align --quiet --dbname $ConnectionString `
        --command "SELECT to_regclass('public.schema_migration') IS NOT NULL;"
    if ($LASTEXITCODE -ne 0) { throw 'Could not inspect the migration tracking table.' }
    $exists = 'f'
    if ($trackingTableExists.Trim() -eq 't') {
        $exists = & $psql.Source --no-psqlrc --tuples-only --no-align --quiet --dbname $ConnectionString `
            --command "SELECT EXISTS (SELECT 1 FROM public.schema_migration WHERE version = '$version');"
        if ($LASTEXITCODE -ne 0) { throw "Could not inspect migration state for $version." }
    }
    if ($exists.Trim() -eq 't') {
        Write-Host "Skipping $version (already applied)"
        continue
    }
    Write-Host "Applying $version"
    & $psql.Source --no-psqlrc --set ON_ERROR_STOP=1 --dbname $ConnectionString --file $migration.FullName
    if ($LASTEXITCODE -ne 0) { throw "Migration $version failed." }
}
