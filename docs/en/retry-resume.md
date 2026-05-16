# Retry And Resume

RawBridge supports listing retries, download retries, exponential backoff, `.part` downloads, size checks, failed logs, retry only failed, and resume without overwriting existing outputs.

State is stored in `.rawbridge_manifest.sqlite`. Failed files are written to `rawbridge_failed.tsv`.
