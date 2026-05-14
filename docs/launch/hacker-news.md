# Launch HN

Show HN: DropRaw Web — convert large RAW photo folders without huge ZIP downloads

DropRaw Web is an open-source CLI and local UI for converting large RAW photo folders from Dropbox, Google Drive, S3/R2, and local folders into optimized WebP/AVIF/JPEG assets.

The first reliability target was a real Dropbox shared folder with 816 Nikon NEF files. Large folder listing/downloads can fail with transient network or SDK errors, so the tool is built around retries, `.part` downloads, size checks, a failed log, and resume.

It is for photographers, designers, agencies, and web developers who need practical web export workflows rather than a hosted service.
