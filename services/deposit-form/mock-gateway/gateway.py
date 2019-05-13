from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/upload', methods = ['POST'])
def upload():
    return 'working...'

@app.route('/form', methods = ['GET'])
def form():
    return jsonify(
    "banner": {
        "title": "Active Deposit Form",
        "description": "Use this form to upload your 3d models, 360 videos, and VR source code & projects",
        "instructions": "Your files will be deposited into a Library repository and published to a third-party website. You will receive a confirmation email when your deposit is processed."
    },
    "fields": [
        {
            "id": 0,
            "label":"Media Type",
            "type": "select",
            "repeatable": "false",
            "required": "true",
            "value": {},
            "options": [{"value": "model", "label": "3d Model"},
                        {"value": "video", "label": "360 Video"},
                        {"value": "vr", "label": "VR project"}],
            "dependsOn": {}
        },
        {
            "id": 1,
            "label":"Creator Name",
            "type": "text",
            "repeatable": "true",
            "required": "true",
            "value": [""],
            "placeholder": "Enter creator name",
            "dependsOn": {}
        },
        {
            "id": 2,
            "label":"Creator Status",
            "type": "select",
            "repeatable": "false",
            "required": "true",
            "value": {},
            "options": [{"value": "u", "label": "Undergraduate"}, 
                        {"value": "g", "label": "Graduate"}, 
                        {"value": "f", "label": "Faculty"}, 
                        {"value": "s", "label": "Staff"}, 
                        {"value": "o", "label": "Other"}],
            "dependsOn": {}
        },
        {
            "id": 3,
            "label":"Creator Affiliation",
            "type": "text",
            "repeatable": "true",
            "required": "false",
            "value": [""],
            "placeholder": "Enter creator's department or team affiliation",
            "dependsOn": {}
        },
        {
            "id": 4,
            "label":"Funding",
            "type": "checkbox",
            "repeatable": "true",
            "required": "false",
            "value": "false",
            "dependsOn": {}
        },
        {
            "id": 5,
            "label":"Funding Agency",
            "type": "text",
            "repeatable": "false",
            "required": "false",
            "value": [""],
            "placeholder": "Enter funding agency name",
            "dependsOn": {"id": 4, "value": "true"}
        },
        {
            "id": 6,
            "label":"Funding Number",
            "type": "text",
            "repeatable": "false",
            "required": "true",
            "value": [""],
            "placeholder": "Enter funding identification number",
            "dependsOn": {"id": 4, "value": "true"}
        }
    ]
}))


if __name__ == '__main__':
    app.run(host="0.0.0.0")

    