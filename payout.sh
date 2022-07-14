#!/bin/bash
cd ~/core3-tbw/

# activate py env
source ~/.venv/tbw/bin/activate

# move unpaid into staging table which is then used to start a payout
python core/tbw.py --manualPay

# payout
python core/pay.py payout

# deactivate py env
deactivate
