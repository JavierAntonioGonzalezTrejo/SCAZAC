#!/bin/bash
set -x
# For use on Cywing only
# Put this file on the home directory ~/
# =============================================================================
# Script Variables
# =============================================================================
export GETPIPFILE=get-pip.py
export GETPIPURL=https://bootstrap.pypa.io/$GETPIPFILE
export SISTEMADIR=~/sistema
export SCAZACURL=https://github.com/JavierAntonioGonzalezTrejo/SCAZAC.git
# =============================================================================
# Script Functions
# =============================================================================
setUpEnvironment(){
    wget $GETPIPURL
    python $GETPIPFILE
    pip install virtualenv
    virtualenv $SISTEMADIR
    cd $SISTEMADIR
}
cloneInstallSCAZAC(){
    cd $SISTEMADIR
    source bin/activate
    git clone $SCAZACURL
    cd $SISTEMADIR/SCAZAC
    pip install -r requirements.txt
    ./manage.py makemigrations
    ./manage.py makemigrations calidadAire investigacion
    ./manage.py migrate
    ./manage.py loaddata sites
}
# =============================================================================
# Script Main
# =============================================================================
echo "Creando el Entorno"
# setUpEnvironment
echo "Instalando SCAZAC"
cloneInstallSCAZAC
echo "./sistema/SCAZAC/updateMigrateRunScazac.sh" >> ~/.bashrc
echo "SCAZAC correctamente Instalado"
# End of File
