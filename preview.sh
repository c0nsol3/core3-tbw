#!/bin/bash
cd ~/core3-tbw/

# activate py env
source ~/.venv/tbw/bin/activate

# move unpaid into staging table which is then used to start a payout
python core/tbw.py --manualPay

# payout preview
python core/pay.py

# deactivate py env
deactivate
