# differ
WAES assignment

## Description
Project provides http interface to compare two binary encrypted data.
Two endpoints accept binary data.
Third endpoint returns diff.
 
## Requirements
* Python language
* virtualenv is applied
* URI format for accepting data: \<host>/v1/diff/\<ID>/\<left|right>
* URI format for returning result: \<host>/v1/diff/\<ID>
* Requests use only JSON format. Binary data should be base64 encoded.
* Differences might be represented only as "equal", "different data size", offsets + length
* Tests

## Implementation details
* Flask framework to process http requests
* SQLAlchemy and sqlite for storing data
* json PUT request uses only "data" key to provide requied encoded data
* requests module is used for integration tests
* numpy module is used to quickly compare binary arrays
* DB does not store actuall data, only sha
* Actuall data is stored on file system in special tree
* Class Record links received data attributes: sha, filepath and encoded content

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

## TODO
* Add logging for application and tests
* Fix problem when data is replaced but GET request still use old cache
* Add configuration for development environment that uses sqlite base and real data
* Do not replace data on uploading with the same sha
* Extend integration tests with all other tests, only single one is available

## License
Feel free to use my code on production environments and good luck. =)
