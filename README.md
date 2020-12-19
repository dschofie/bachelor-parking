# Bachelor Parking
This is a small lambda handler that emits a metric to cloudwatch whenever there
are avaialable book based on `desiredDays` configureed in `lambda-handler.py`.

## AWS Lambda
You can set this up to run on AWS lambda and trigger it via a cloudwatch event
rule cron expression. The lambda role has to have `ses:SendEmail`
permissions to notify. 

## Cost
This should all be within the free tier for AWS for SES and Lambda.

TODO: handle session and actually book parking.
