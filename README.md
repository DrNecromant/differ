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

## Implementation details
* Flask framework to process http requests
* SQLAlchemy and sqlite for storing data

## Usage and examples
* TBD

# License
Feel free to use my code on production environments and good luck. =)
