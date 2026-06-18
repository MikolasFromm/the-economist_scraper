# The Economist EPUB Downloader

A minimal Python scraper that downloads weekly issues of [The Economist](https://www.economist.com) as EPUB files from the community repository [evanbio/The_Economist](https://github.com/evanbio/The_Economist) and optionally emails them (including to Kindle).

## Features

- Download the latest weekly issue (no account required)
- Send the downloaded EPUB to any number of email recipients
- Kindle delivery support (one address per send)

## Requirements

- Python 3.9+

Install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

All credentials and settings are read from a `.env` file in the project directory (gitignored). Create it before running:

```bash
cat > .env <<'EOF'
export SENDER_EMAIL='sender@example.com'
export SENDER_EMAIL_PASSWORD='yourpassword'
export RECIPIENTS='alice@example.com;bob@example.com'
export KINDLE_RECIPIENTS='yourkindle@kindle.com'
export SAVE_PATH='./epubs'
EOF
```

| Variable | Required | Description |
|---|---|---|
| `SENDER_EMAIL` | for email | The address emails are sent from |
| `SENDER_EMAIL_PASSWORD` | for email | SMTP password for the sender account |
| `RECIPIENTS` | no | Semicolon-separated email recipients |
| `KINDLE_RECIPIENTS` | no | Semicolon-separated Kindle addresses |
| `SAVE_PATH` | no | Where to store downloaded files (default: `./epubs`) |
| `SMTP_SERVER` | no | SMTP host (default: `smtp.gmail.com`) |
| `SMTP_PORT` | no | SMTP port for SSL (default: `465`) |

## Usage

### Download the latest issue

```bash
python3 the_economist_scraper.py --latest
```

### Download and email the latest issue

```bash
python3 the_economist_scraper.py \
  --latest \
  --recipients 'alice@example.com;bob@example.com'
```

### Send to Kindle

```bash
python3 the_economist_scraper.py \
  --latest \
  --kindle-recipients 'yourkindle@kindle.com'
```

### Custom save directory

Pass `--save-path` to any command:

```bash
python3 the_economist_scraper.py --latest --save-path /path/to/my/epubs
```

EPUBs are saved under `<save-path>/<year>/` with names like `TE-2026-06-13.epub`.

## Shell helper scripts

| Script | Purpose |
|---|---|
| `download_and_sent_latest.sh` | Download the newest issue and email it |
| `setup_cron.sh` | Install the Monday morning cron job |

Both scripts source `.env` and `.venv` automatically — just run them from the project directory.

### Automating with cron

Run `setup_cron.sh` to install a cron job that fires every Monday at 07:00:

```bash
bash setup_cron.sh
```

It logs to `~/.the_economist.log`.

## License

Apache 2.0
