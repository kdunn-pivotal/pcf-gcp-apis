# pcf-gcp-ml-apis
Access to Google Cloud APIs provided from endpoints in Pivotal Cloud Foundry.

## Python dependencies:

- >= google-cloud-core 0.23.0

`pip install --upgrade google-cloud`

## Cloud Foundry setup

    cf push --no-start
    cf create-service google-ml-apis default google-ml
    cf bind-service google-api-service google-ml -c '{"role": "viewer"}'
    cf start APP_NAME

## Google API credential setup

 1. Create a new service account in GCP
 2. Authorize the above service account for editor access to the desired GCP storage container
 3. Add OAuth JSON to `VCAP_SERVICES` in a field within `credentials` called `PrivateKeyData` using the output from the following command:

```
    cat <FILENAME FROM GCP>.json | base64
```

For local testing, create a file call `vcap_local.json` formatted like this:

```
{
  "google-ml-apis" :[{
    "name": "google-ml",
    "credentials": {
     "Email": "<YOUR SERVICE ACCOUNT EMAIL>",
     "Name": "pcf-binding-kdunn",
     "PrivateKeyData": "<OUTPUT FROM COMMAND ABOVE>",
     "ProjectId": "<YOUR PROJECT NAME>",
     "UniqueId": "<YOUR PROJECT ID>",
     "bucket_name": "<YOUR STORAGE BUCKET URL>"
    }
  }]
}
```

where `google-ml-apis` and `google-ml` match the global variables in `helper_functions.py` (SERVICE_NAME and SERVICE_INSTANCE_NAME respectively)

then store this data in an environment variable:

    export VCAP_SERVICES=`cat vcap_local.json`

## Test NLP with curl:

`curl --data '{"content": "New Yorkers will choose one of five finalists for residents in all five boroughs to read as part of a city program."}' http://google-api-service.apps.pcfongcp.com/nlp`

## Test Vision with curl

Note: watch out for this [bug](https://github.com/GoogleCloudPlatform/google-cloud-python/pull/2961) when using OCR.

Run from root directory of repo, because the command refers to the test JSON 
request included in the tests directory.

`curl -H "Content-Type:application/json" --data-bindary "@tests/vision_request.json" http://google-api-service.apps.pcfongcp.com/vision`
