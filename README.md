# CloudFaceRecognitionApplication

CloudFaceRecognitionApplication is a cloud-based face recognition service built with Python and Flask. It provides APIs for image identification and integrates with cloud infrastructure for scalable workflows.

## Features

- **Face Recognition API:**  
  Upload an image file via HTTP POST and receive name predictions.
- **Cloud Integration:**  
  App-tier handles cloud processing using AWS S3 and SQS.  
  Processes images from S3, runs recognition, sends results back and manages queues.
- **CSV Dataset:**  
  `Face_Dataset.csv` provides a mapping of image names to recognized identities.

## Directory Structure

```
CloudFaceRecognitionApplication/
├── app.py              # Flask API for web-tier image recognition
├── Face_Dataset.csv    # Ground truth/lookup table for faces
├── app-tier/           # Cloud processing Python (SQS, S3, face matching)
│   └── app.py
├── web-tier/           # (Reserved for web assets or UI)
```

## API Usage

### Web-tier (Flask)

#### URL
```
POST /
```
#### Parameters
- `inputFile` (form-data): Image file to identify

#### Response
- `200 OK` : `filename:Prediction`
- `404 Not Found` : `filename:Unknown`

### App-tier (AWS service)

- Receives SQS messages containing S3 image URLs.
- Downloads images, runs face matching (`face_recognition.face_match`), uploads result to S3, notifies via SQS.

## Setup & Requirements

- Python 3, Flask, pandas
- AWS credentials for app-tier (with permissions for S3 and SQS)
- Install dependencies:  
  ```
  pip install flask pandas boto3 requests
  ```
- Place images and CSV in proper locations as referenced by code.

## Running the Project

### Web-tier API

```bash
python app.py
# Default: runs at http://localhost:80
```

### App-tier Service

```bash
cd app-tier
python app.py
# Requires AWS access and SQS/S3 preconfiguration
```

## Face Dataset

Sample of `Face_Dataset.csv`:
```csv name=Face_Dataset.csv url=https://github.com/dhanushsanand/CloudFaceRecognitionApplication/blob/main/Face_Dataset.csv#L1-L12
Image,Results
test_000,Paul
test_001,Emily
test_002,Bob
test_003,German
test_004,Emily
test_005,Gerry
test_006,Gerry
test_007,Ranil
test_008,Bill
test_009,Wang
```

## Author

- [dhanushsanand](https://github.com/dhanushsanand)

## License

*No explicit license found. Please add a LICENSE file if distribution is intended.*

## Contributing

Feel free to fork or submit pull requests for improvements or fixes.
