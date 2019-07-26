# 3deposit - Vimeo Service

This service interacts with the [Vimeo API](https://developer.vimeo.com/api/guides/start) to upload 360 videos to [Vimeo](https://vimeo.com/), retrieve video data from it, and deletes uploads and/or their comments.

## Installation

- Python 3.5
- Flask
- PyVimeo
- requests
- unpack

## JSON Data

Use the JSON data below to make API calls. Replace the values if necessary.

```
{
    "config": {
        "auth": {
            "access_token": "{access_token}",
            "api": "https://api.vimeo.com",
            "client_id": "{client_id}",
            "client_secret": "{client_secret}"
        }
    },
    "data": {
        "comments": {"anybody", "contacts", "nobody"},
        "description": "{video_description}",
        "embed": {"private", "public"},
        "filename": "{local_filename}",
        "license": {"by", "by-nc", "by-nc-nd", "by-nc-sa", "by-nd", "by-sa", "cc0"},
        "name": "{video_title}",
        "projection": {"cubical", "cylindrical", "dome", "equirectangular", "pyramid"},
        "stereo_format": {"left-right", "mono", "top-bottom"},
        "view": {"anybody", "contacts", "nobody"}
    },
    "file": "{file_path}"
}
```

## Resources

- [Vimeo API](https://developer.vimeo.com/api/guides/start)
