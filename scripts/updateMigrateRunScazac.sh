#!/bin/bash
set -x
# For use on Cywing Only
# Put the script under on the proyect directory ~/sistema/SCAZAC
# =============================================================================
# Script Variables
# =============================================================================
export SCAZACDIR=~/sistema/SCAZAC
export ACTIVATEDIR=~/sistema/bin/activate
# =============================================================================
# Script Functions
# =============================================================================
updateSCAZAC(){
    cd $SCAZACDIR
    git pull origin master
}
migrateDBSCAZAC(){
    source $ACTIVATEDIR
    cd $SCAZACDIR
    ./manage.py makemigrations
    ./manage.py makemigrations calidadAire investigacion
    ./manage.py migrate
}
runSCAZAC(){
    source $ACTIVATEDIR
    cd $SCAZACDIR
    ./manage.py runserver
}
# =============================================================================
# Script Main
# =============================================================================
updateSCAZAC
migrateDBSCAZAC
runSCAZAC
# End of File
