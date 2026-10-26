#!/bin/bash

websites=(
    "https://google.com"
    "https://facebook.com"
    "https://twitter.com"
)

log_file="website_status.log"

> "$log_file"

for website in "${websites[@]}"; do
    status_code=$(curl -L -s -o /dev/null -w "%{http_code}" --max-time 10 "$website")

    if [ "$status_code" -eq 200 ]; then
        echo "$website is UP" >> "$log_file"
    else
        echo "$website is DOWN" >> "$log_file"
    fi
done

echo "Результати перевірки записано у файл $log_file"