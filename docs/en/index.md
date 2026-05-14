# DropRaw Web

DropRaw Web converts large RAW photo folders from Dropbox, Google Drive, S3/R2, and local folders into optimized web-ready assets without downloading huge ZIP archives.

Tested on a real Dropbox shared folder with 816 Nikon NEF files. Large Dropbox folders can fail during listing or download due to transient network/SSL/SDK errors; DropRaw Web treats recoverable errors such as `ConnectionError(ProtocolError('Connection aborted.', OSError(22, 'Invalid argument')))` as retryable.

Use Python 3.11 or 3.12.
