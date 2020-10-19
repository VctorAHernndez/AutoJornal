# AutoJornal
Automatic signing/mailing system used to send clock-in/clock-out hours to our employer with our electronic signature. System is currently being run every two weeks on a Raspberry Pi with Raspbian installed.

## Usage
Clone the repository into your home folder:
```
cd ~
git clone https://github.com/VctorAHernndez/AutoJornal.git
```

Run the following lines to create a virtual environment & install the dependencies:
```
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
sudo apt install libtiff5 # if not yet installed
```

Create an environment file `.env` that contains your gmail address and its app password ([click here to know how to set it up](https://support.google.com/mail/answer/185833?hl=en)) at the root of the repository folder:
```
FROM_EMAIL=your@gmail.here
APP_PASSWORD=your-app-password-here
```

Create a cron job that will execute the AutoJornal scripts:
```
crontab -e
0 8 * * Tue /home/pi/AutoJornal/cron.sh > /home/pi/AutoJornal/out.log 2>&1
```
