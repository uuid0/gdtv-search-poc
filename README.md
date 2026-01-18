# GDTV search prototype

This is a proof of concept / prototype for a process which extracts and indexes information from videos.

You will need about 2GB of disk space. All will be placed in `data/`, so you can delete the folder after you're done.

This is completely untweaked and not optimized for anything.
To get consistency in the keywords, one would probably give preferred keywords to into the context.

## Setup

### ffmpeg

https://ffmpeg.org/

### Pixi

Install pixi (or just python3 and install the requirements according to pyproject.toml).

https://pixi.prefix.dev/latest/

After installation run `pixi install`.

### Whisper

Run `./development/get_whisper.sh`. This will download and compile whisper.cpp. This is currently only tested on MacOS aarch64.

### Docker OR elasticsearch

Run `docker compose up` in the root directory OR install and run elasticsearch locally and adjust the settings in the notebook accordingly.

### OpenAI key

Set the environment variable `OPENAI_API_KEY` to your OpenAI key or place it in `data/openai_key.txt`.
`data/` is ignored by git.

## Jupyter Notebook

See `notebooks/example.ipynb`.

You can go cell by cell.
It will download a sample video, a model and then process the video.
