# Retry И Resume

DropRaw Web поддерживает listing retries, download retries, exponential backoff, `.part` downloads, size checks, failed log, retry only failed и resume без перезаписи готовых outputs.

Failed files пишутся в `dropraw_failed.tsv`.
