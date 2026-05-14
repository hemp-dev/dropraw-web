# Retry And Resume

DropRaw Web supports listing retries, download retries, exponential backoff, `.part` downloads, size checks, failed logs, retry only failed, and resume without overwriting existing outputs.

State is stored in `.dropraw_manifest.sqlite`. Failed files are written to `dropraw_failed.tsv`.
