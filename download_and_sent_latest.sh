#!/bin/bash

source .env
source .venv/bin/activate
python3 the_economist_scraper.py \
  --latest \
  --save-path "$SAVE_PATH" \
  ${RECIPIENTS:+--recipients "$RECIPIENTS"} \
  ${KINDLE_RECIPIENTS:+--kindle-recipients "$KINDLE_RECIPIENTS"}
