# Retry И Resume

RawBridge поддерживает listing retries, download retries, exponential backoff, `.part` downloads, size checks, failed log, retry only failed и resume без перезаписи готовых outputs.

Failed files пишутся в `rawbridge_failed.tsv`.
