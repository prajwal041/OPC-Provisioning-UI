#!/bin/bash

NAME="provui" # Name of the application
DJANGODIR=/home/opc/provui # Django project directory
SOCKFILE=/var/run/gunicorn.sock # we will communicte using this unix socket
USER=apache # the user to run as
GROUP=apache # the group to run as
NUM_WORKERS=3 # how many worker processes should Gunicorn spawn
DJANGO_SETTINGS_MODULE=provui.settings # which settings file should Django use
DJANGO_WSGI_MODULE=provui.wsgi # WSGI module name
LOG_FILE=/home/opc/provui/gunicorn.log

echo "Starting $NAME as `whoami`"

# Activate the virtual environment
cd $DJANGODIR
#source activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH


# Create the run directory if it doesn't exist
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR



# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
echo "about to exec exec is" $DJANGO_WSGI_MODULE
exec /usr/local/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
--name $NAME \
--workers $NUM_WORKERS \
--user=$USER --group=$GROUP \
--log-level=debug \
--access-logfile $LOG_FILE \
--error-logfile $LOG_FILE \
--bind=unix:$SOCKFILE


