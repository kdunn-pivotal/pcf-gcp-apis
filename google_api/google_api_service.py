import os

from flask import Flask, request, jsonify 
import helper_functions
from helper_functions import DEFAULT_LIMIT

app = Flask(__name__)

@app.route("/")
def main():
    return "Hello World!"

@app.route('/api', methods=['POST','OPTIONS'])
#@helper_functions.crossdomain(origin='*')
def handle_google_api_request():
    req = request.get_json(force=True)
    return jsonify(req)


@app.route('/nlp', methods=['POST','OPTIONS'])
#@helper_functions.crossdomain(origin='*')
def handle_nlp_request():
    req = request.get_json(force=True)
    first_entity_string = helper_functions.first_entity_str(req['content'])
    return jsonify({
        'first_entity_string': first_entity_string
    })


@app.route('/vision', methods=['POST','OPTIONS'])
#@helper_functions.crossdomain(origin='*')
def handle_vision_request():
    """Expecting JSON request as outlined in
    https://cloud.google.com/vision/docs/reference/rest/v1/images/annotate
    """
    req_dict = request.get_json(force=True)
    responses = []
    for req in req_dict['requests']:
        # get maxResults for LABEL_DETECTION
        label_feats = [
            feat for feat in req['features'] if feat['type'] == 'LABEL_DETECTION'
        ]
        if label_feats:
            limit = label_feats[0].get('maxResults', DEFAULT_LIMIT)
        else:
            limit = DEFAULT_LIMIT
        if 'content' in req['image']:
            labels = helper_functions.get_image_labels_from_base64(
                req['image']['content'],
                limit
            )
        # alternatives to 'content' bytes not currently implemented
        else:
            labels = []
        """
        responses.append(
            dict(labelAnnotations=list(map(entity_annotation_to_dict, labels)))
        )
        """;
    return jsonify(dict(responses=responses))

@app.route('/vision/ocr', methods=['POST','OPTIONS'])
#@helper_functions.crossdomain(origin='*')
def handle_vision_text_request():
    text_list = helper_functions.get_image_text(request.data)

    print text_list

    return jsonify(text_list)

@app.route('/vision/logos', methods=['POST','OPTIONS'])
#@helper_functions.crossdomain(origin='*')
def handle_vision_logo_request():
    logo_list = helper_functions.get_image_logos(request.data)

    return jsonify(logo_list)

@app.route('/storage/<bucket>/<blob>', methods=['GET', 'POST', 'OPTIONS'])
#@helper_functions.crossdomain(origin='*')
def handle_storage_request(bucket, blob):
    if request.method == 'POST':
        new_blob = helper_functions.create_blob(request.data, blob, bucket, 
                                                request.headers['content-type'], 
                                                create_bucket=True)
        return jsonify({
            'created': '{0} in bucket {1}'.format(blob, bucket)
        })
    elif request.method == 'GET':
        requested_blob = helper_functions.get_blob(bucket, blob)
        return jsonify(requested_blob)
    else:
        return jsonify({
            'reponse' : "{0} method not supported".format(request.method)
        })

if __name__ == "__main__":
    if os.environ.get('VCAP_SERVICES') is None: # running locally
        PORT = 5000
        DEBUG = True
        app.run(debug=DEBUG)
    else:                                       # running on CF
        PORT = int(os.getenv("PORT"))
        DEBUG = False
        app.run(host='0.0.0.0', port=PORT, debug=DEBUG)

