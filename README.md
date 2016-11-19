# differ
WAES assignment

## Description
Project provides http interface to compare two binary files.
Two endpoints accept binary data.
Third endpoint returns diff.
 
## Requirements
* Python language
* virtualenv is applied
* URI format for accepting data: \<host>/v1/diff/\<ID>/\<left|right>
* URI format for returning result: \<host>/v1/diff/\<ID>
* Requests use only JSON format. Binary data should be base64 encoded.
* Differences might be represented only as "equal", "different file size", offsets + length
* Tests

## Implementation details
* Flask framework to process http requests
* SQLAlchemy and sqlite for storing data
* json PUT request uses "data" key to provide requied encoded data

## Server deployment/cleanup

### Install project
* pip install virtualenv
* git clone https://github.com/DrNecromant/differ
* virtualenv differ
* cd differ
* . bin/activate
* pip install -r requirements.txt

### Start application
* python app.py

### Stop application
* CTRL+C

### Exit and remove project
* deactivate
* cd ..
* rm -r differ

## Usage and examples
* TBD

## License
Feel free to use my code on production environments and good luck. =)
