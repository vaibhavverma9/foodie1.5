#!/bin/bash

declare -a users=("userid=E3ZG5KyOkh0ZZxmQveapCg")

for user in "${users[@]}"
do 
 	python scrape_comments.py -u $user -c 0
	python analyze_sentiment.py -u $user
done 