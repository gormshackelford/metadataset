# Metadataset
Metadataset (www.metadataset.com) is a collection of open data from scientific publications. These publications are about the management of agricultural and natural resources (e.g., crops, soil, water, and wildlife). The data are extracted from scientific publications, standardized, and summarized using dynamic meta-analysis.

# Reinstalling Metadataset on a new server
This README file describes the steps you could take to reinstall Metadataset on a new server. It uses the example of a virtual machine on Google Compute Engine (an `e2-small` instance, with 2 vCPUs and 2GB RAM, running Ubuntu 18.04 LTS). In this example, the name of the project on Google Compute Engine is `metadataset`, and so the path names begin with `/home/metadataset/` (but you may need to replace this with your path name). This example assumes that you have SSH access to the command line on your virtual machine, where you will enter these commands. You will need to replace variable names in square brackets with your own variable names (e.g., `[your_root_password]`).

## Installing dependencies
Enter these commands on the command line of your virtual machine (e.g., `/home/metadataset/`).
```
sudo apt update
sudo apt install mysql-server python-pip libmysqlclient-dev python3 python3-dev python3-mysqldb git virtualenv libexpat1 apache2 apache2-utils ssl-cert libapache2-mod-wsgi-py3
```

Set your `root` user and password for MySQL.
```
sudo mysql_secure_installation
sudo mysql
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '[your_root_password]';
exit
```

Set the time zone tables in MySQL.
```
mysql_tzinfo_to_sql /usr/share/zoneinfo | mysql -uroot -p mysql
```

## Installing Metadataset
Copy the code for Metadataset from GitHub to a new directory named "metadataset" (e.g., `/home/metadataset/metadataset`).
```
git clone https://github.com/gormshackelford/metadataset.git
```

Create a virtual environment for Python3.
```
cd metadataset
which python3
virtualenv -p [insert_path_from_previous_prompt] venv
source venv/bin/activate
```

Install Python dependencies.
```
pip install --upgrade pip
pip install -r requirements.txt
```

## Configuring Metadataset
Create `config.json` (e.g., in `/home/metadataset/metadataset/config.json`).
```
nano config.json
```

Copy and paste the following into `config.json` and then exit/save (`Ctrl + X`). You should add your domain name to the list of `ALLOWED_HOSTS` if you are not using `www.metadataset.com` or `dev.metadataset.com`. You should also randomly generate a new `SECRET_KEY`. See https://docs.djangoproject.com for more information on Django, the web framework that is used by Metadataset, and search for `SECRET_KEY`.
```
{
    "SECRET_KEY": "[your_secret_key]",
    "EMAIL_HOST": "[your_email_host (e.g. smtp.google.com)]",
    "EMAIL_PORT": "[your_email_port (e.g., 587)]",
    "EMAIL_HOST_USER": "[your_email_address]",
    "EMAIL_HOST_PASSWORD": "[your_email_host_password]",
    "DEFAULT_FROM_EMAIL": "[your_email_name_and_address (e.g., Metadataset <metadataset@metadataset.com>)]",
    "DB_ENGINE": "django.db.backends.mysql",
    "DB_NAME": "metadataset",
    "DB_USER": "[your_db_user]",
    "DB_PASSWORD": "[your_db_user_password]",
    "DB_HOST": "127.0.0.1",
    "ALLOWED_HOSTS": "['127.0.0.1', 'www.metadataset.com', 'dev.metadataset.com']",
    "DEBUG": "True",
    "SECURE_SSL_REDIRECT": "False"
}
```

## Configuring Apache
Create a configuration file for `Apache`.
```
cd /etc/apache2/sites-available
sudo nano 001-metadataset.conf
```

Copy and paste the following and the exit/save (`Ctrl + X`). Change `ServerName` to the domain name you are using (e.g., `dev.metadataset.com`).
```
<VirtualHost *:80>
    ServerName dev2.metadataset.com
    Alias /static/ /home/metadataset/metadataset/publications/static/
    <Directory /home/metadataset/metadataset/publications/static>
        Require all granted
    </Directory>
    WSGIScriptAlias / /home/metadataset/metadataset/metadataset/wsgi.py
    WSGIDaemonProcess metadataset user=www-data group=www-data threads=5 home=/home/metadataset/metadataset python-home=/home/metadataset/metadataset/venv
    ErrorLog "/var/log/apache2/metadataset_error_log"
    CustomLog "/var/log/apache2/metadataset_access_log" common
    <directory /home/metadataset/metadataset/>
        WSGIProcessGroup metadataset
        WSGIApplicationGroup %{GLOBAL}
        WSGIScriptReloading On
        Require all granted
    </directory>
</VirtualHost>
```

Enable this virtual host.
```
sudo a2ensite 001-metadataset.conf
sudo apache2ctl restart
```

Grant access to the `whoosh_index`.
```
cd
sudo chown -R www-data:www-data metadataset/whoosh_index
```

Collect the static files for Django. The `collectstatic` command copies the CSS files for Django (`admin`, `mptt`, and `rest_framework`) to the static directory specified in `settings.py` (`/home/metadataset/metadataset/publications/static/`), which is also specified in `001-metadataset.conf` file for Apache. Check that you are in your virtual environment, which should be indicated by "(venv)" on your command prompt, before running this command.
```
cd /home/metadataset/metadataset/
python manage.py collectstatic
```

## Configuring MySQL
Create an empty database named `metadataset` (if already exists, `drop database metadataset;` before creating it).
```
mysql -u root -p -e "CREATE DATABASE metadataset CHARACTER SET utf8;"
```

You will need a backup copy of the database. Upload this database dump to your server (e.g., upload `metadataset_backup.sql` to `/home/metadataset/metadataset_backup.sql`). Then restore the database from this database dump.
```
mysql -u root -p metadataset < /home/metadataset/metadataset/metadataset_backup.sql
```

Create the MySQL user that you specified in config.json.
```
mysql -u root -p
CREATE USER '[your_db_user]'@'localhost' IDENTIFIED BY '[your_db_password]';
GRANT ALL PRIVILEGES ON metadataset.* TO '[your_db_user]'@'localhost';
FLUSH PRIVILEGES;
exit
```

## Configuring the domain name
Forward your domain name (e.g., `dev.metadataset.com`) to the IP address of your server (e.g., `34.69.236.195`). Follow the instructions of your registrar (e.g., `domains.google.com`) to edit the DNS settings. After these changes take effect, you should see the http version of the website when you go to your domain name (e.g., `dev.metadataset.com`) in your browser.

## Restarting the server
You may need to restart Apache after making changes.
```
sudo apache2ctl restart
```

## Install an SSL certificate and enable https
Comment out the following line in `001-metadataset.conf`:
```
# WSGIDaemonProcess...
```
To prevent this error:
```
Name duplicates previous WSGI daemon definition.
```
Uncomment this line after following the instructions for installing the SSL certificate. Follow the instructions at https://letsencrypt.org/ to install an SSL certificate. For example:
```
sudo apt-get update
sudo apt-get install software-properties-common
sudo add-apt-repository universe
sudo add-apt-repository ppa:certbot/certbot
sudo apt-get update
sudo apt-get install certbot python-certbot-apache
sudo certbot --apache
```

When running `certbot`, select the option for `1: No redirect - Make no further changes to the webserver configuration.`

Uncomment the line that you commented out in `001-metadataset.conf`. Then edit the `.conf` file that was created by `certbot` (`001-metadataset-le-ssl.conf`: uncomment the line, as above, and then add the prefix `ssl-` to the name of `WSGIDaemonProcess` and `WSGIProcessGroup`. For example, if the line is `WSGIDaemonProcess metadataset`, change it to `WSGIDaemonProcess ssl-metadataset`. For example:
```
<IfModule mod_ssl.c>
<VirtualHost *:443>
    ServerName dev2.metadataset.com
    Alias /static/ /home/metadataset/metadataset/publications/static/
    <Directory /home/metadataset/metadataset/publications/static>
        Require all granted
    </Directory>
    WSGIScriptAlias / /home/metadataset/metadataset/metadataset/wsgi.py
    WSGIDaemonProcess ssl-metadataset user=www-data group=www-data threads=5 home=/home/metadataset/metadataset/ p$
    ErrorLog "/var/log/apache2/metadataset_error_log"
    CustomLog "/var/log/apache2/metadataset_access_log" common
    <directory /home/metadataset/metadataset/>
        WSGIProcessGroup ssl-metadataset
        WSGIApplicationGroup %{GLOBAL}
        WSGIScriptReloading On
        Require all granted
    </directory>
SSLCertificateFile /etc/letsencrypt/live/dev2.metadataset.com/fullchain.pem
SSLCertificateKeyFile /etc/letsencrypt/live/dev2.metadataset.com/privkey.pem
Include /etc/letsencrypt/options-ssl-apache.conf
</VirtualHost>
</IfModule>
```

Check that your server allows traffic via https on port 443 (for example, on Google Compute Engine, there is a checkbox for enabling https). Change `config.json` to redirect from http to https: "SECURE_SSL_REDIRECT": "True". Then restart Apache with `sudo apache2ctl restart`. You should now see the https version of the website when you go to your domain name in your browser (e.g., with the padlock symbol).

# Copyright
Metadataset is copyright (c) 2020 Gorm Shackelford, but it is Open Source and licensed under the MIT License. Thanks to Stefan Haselwimmer for developing the README file and server architecture for www.x-risk.net, on which this file is based.
