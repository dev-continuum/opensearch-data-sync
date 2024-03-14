# opensearch-data-sync
Code base which supports the indexing Charging Station records in OpenSearch database.

# Tech Stack
- Python 3.9
- OpenSearch.py
- AWS Lambda

# Fast API Service.
## Run the test cases from CI.
    $export ACTIVE_ENVIRONMENT=test
    $python -m unittest discover -s tests

## How to build and run.?
    cd to '/opensearch-data-sync'  directory.
### Build electric-search image locally.
```
$docker build -t <image_name> .
$docker image ls     - you must  see image with <image_name>

Ex. $docker image -t esearch .
```

### Lambda function.

Build image locally

    $docker build -t opensearch-data-sync:latest . -f lambda.Dockerfile

Tag and Push image to ECR

    $aws configure
    # authentica ecr from local.
    $aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 683563489644.dkr.ecr.ap-south-1.amazonaws.com
    $docker tag <docker_image_name:tag> <ecr_repo_url>:<tag_name>
    $docker push <ecr_repo_url>:<tag_name>    -- tag_name must be same as above.

## Test lambda function local.

Pre-Requisite: 

    $pip install python-lambda-local

Execute ```RunLambda.sh``` file from terminal.

    $export ACTIVE_ENVIRONMENT=test
    $sh lambda_test.sh lib/ handler ./app/lambda_func.py tests/datasets/lambda_event.json

Note: Python lambda local is not supporting from debugging, 
alternatively you can pretty much write a py main method to invoke lambda handler by passing event and mock context. :)

