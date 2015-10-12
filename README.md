# twitter-feeder

How to run locally ?

1. Start Kafka broker locally.
2. ```
    pip3 install virtualenv
    virtualenv env
    source venv/bin/activate
    pip install -r requirements.txt
    SVC_KAFKA_KAFKA_SERVICE_HOST=localhost SVC_KAFKA_KAFKA_SERVICE_PORT=9092 SECRET_DIR=/Users/arrawatia/code/try-openshift/template/ APP_PORT=5000 python app.py
    ```
3. Make sure the secret.yaml is in the right place.

How to deploy on the server:
    ```    
      oc create -f python3.yaml
      oc secrets new app-secret template/twitter-secret.yaml
      oc secrets add --for=mount serviceaccount/default secret/app-secret
      oc new-app python3 \
          --name='twitter-feeder' \
          -p SOURCE_REPOSITORY_URL='https://github.com/quantezza/twitter-feeder' \
          -p APP_NAME='twitter-feeder' \


      oc start-build twitter-feeder
    ```
