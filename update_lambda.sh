#!/bin/bash
zip -rj  lambda.zip src/* 
aws lambda update-function-code --function-name "todo-list" --zip-file "fileb://./lambda.zip" --region "sa-east-1" --no-cli-pager