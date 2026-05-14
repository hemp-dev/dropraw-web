# Reddit Post

I built DropRaw Web, an open-source CLI + local UI for converting large RAW photo folders into optimized web images.

It supports local folders, Dropbox shared folders, Google Drive, and S3/R2. The Dropbox path avoids downloading a huge ZIP; it lists files and downloads RAW files one by one with retries, `.part` files, failed logs, and resume.

The reliability work came from a real Dropbox folder with 816 Nikon NEF files where transient network errors made simple batch scripts unreliable.

Useful for photographers, designers, agencies, and developers preparing web galleries or CMS assets.
