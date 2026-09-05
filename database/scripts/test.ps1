[CmdletBinding()]
param(
    [string]$ConnectionString = $env:PEOPLEPAY360_TEST_MIGRATION_DATABASE_URL
)

$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($ConnectionString)) {
    throw 'Set PEOPLEPAY360_TEST_MIGRATION_DATABASE_URL to the dedicated peoplepay360_test database.'
}

$env:PEOPLEPAY360_MIGRATION_DATABASE_URL = $ConnectionString
& (Join-Path $PSScriptRoot 'migrate.ps1')
if ($LASTEXITCODE -ne 0) { throw 'Migration failed before integration tests.' }

$psql = Get-Command psql -ErrorAction Stop
Get-ChildItem -LiteralPath (Join-Path $PSScriptRoot '..\tests') -Filter '*.sql' |
    Sort-Object Name |
    ForEach-Object {
        Write-Host "Testing $($_.Name)"
        & $psql.Source --no-psqlrc --set ON_ERROR_STOP=1 --dbname $ConnectionString --file $_.FullName
        if ($LASTEXITCODE -ne 0) { throw "Test $($_.Name) failed." }
    }
