# AutoJornal
Automatic signing/mailing system used to send clock-in/clock-out hours to our employer with our electronic signature.

## Requirements
Run the following lines to create a virtual environment & install the dependencies:
```
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
sudo apt install libtiff5
```

## Usage
Create an environment file `.env` that contains your gmail address and its password at the root of the repository folder:
```
FROM_EMAIL=your@gmail.here
FROM_PASSWORD=your-password-here
```

Then run the following line:
```
python main.py
```
