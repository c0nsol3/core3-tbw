#!/usr/bin/env python
from config.configure import Configure
from network.network import Network
from modules.allocate import Allocate
from modules.blocks import Blocks
from modules.initialize import Initialize
from modules.stage import Stage
from modules.voters import Voters
from utility.database import Database
from utility.dynamic import Dynamic
from utility.sql import Sql
from utility.utility import Utility
import sys
import time


def update_voter_share(sql, config):
    old_rate = float(input("Enter old share rate in the following format (80): "))
    sql.open_connection()
    voters = sql.all_voters().fetchall()
    
    for i in voters:
        if i[3] == old_rate:
            sql.update_voter_share(i[0], config.voter_share)
    
    sql.close_connection()
    quit()


def update_custom_share():
    pass


def force_manual_pay():
    pass



def interval_check(block_count, interval):
    if block_count % interval == 0:
        print("Payout interval reached")
        sql.open_connection()
        voter_balances = sql.voters().fetchall()
        delegate_balances = sql.rewards().fetchall()
        sql.close_connection()
        
        voter_unpaid = {i[0]:i[2] for i in voter_balances}
        delegate_unpaid = {i[0]:i[1] for i in delegate_balances}
        
        # check if there is a positive unpaid balance
        if sum(voter_unpaid.values()) > 0:
            stage = True
        else:
            stage = False
    else:
        stage = False
        voter_unpaid = {}
        delegate_unpaid = {}
    
    return stage, voter_unpaid, delegate_unpaid

if __name__ == '__main__':
    print("Start Script")
    # get configuration
    config = Configure()
    
    # load network
    network = Network(config.network)
    
    # load utility and dynamic
    utility = Utility(network)
    dynamic = Dynamic(utility, config)
    
    # connect to core and tbw script database
    database = Database(config, network)
    sql = Sql()
    
    # check if initialized
    Initialize(config, database, sql)
    
    # update all voter share
    if config.update_share == "Y":
        update_voter_share(sql, config)
    
    # check if manual pay flag is set
    
    # check if custom share flag is set
    
    # MAIN FUNCTION LOOP SHOULD START HERE
    while True:
        # get blocks
        block = Blocks(config, database, sql)
    
        # get last block to start
        last_block = block.get_last_block()
    
        # use last block timestamp to get all new blocks
        new_blocks = block.get_new_blocks(last_block)
    
        # store all new blocks
        block.store_new_blocks(new_blocks)
    
        # get unprocessed blocks
        unprocessed_blocks = block.return_unprocessed_blocks()
    
        # allocate block rewards
        allocate = Allocate(database, config, sql)
        voter_options = Voters(config, sql)
    
        for unprocessed in unprocessed_blocks:
            print(unprocessed)
            block_timestamp = unprocessed[1]
            # get vote and unvote transactions
            vote, unvote = allocate.get_vote_transactions(block_timestamp)
            # create voter_roll
            voter_roll = allocate.create_voter_roll(vote, unvote)
            # get voter_balances
            voter_balances = allocate.get_voter_balance(unprocessed, voter_roll)
            print("\noriginal voter_balances")
            for k, v in voter_balances.items():
                print(k,v)
            # run voters through various vote_options
            if config.whitelist == 'Y':
                voter_balances = voter_options.process_whitelist(voter_balances)
            if config.whitelist == 'N' and config.blacklist =='Y':
                voter_balances = voter_options.process_blacklist(voter_balances)
            print("\n voter_balances post whitelist or blacklist")
            for k, v in voter_balances.items():
                print(k,v / config.atomic)
            
            voter_balances = voter_options.process_voter_cap(voter_balances)
            print("\n voter_balances post voter cap")
            for k, v in voter_balances.items():
                print(k,v / config.atomic)
 
            voter_balances = voter_options.process_voter_min(voter_balances)
            print("\n voter_balances post voter min")
            for k, v in voter_balances.items():
                print(k,v / config.atomic)
 
            voter_balances = voter_options.process_anti_dilution(voter_balances)
            print("\n voter_balances post anti_dulite")
            for k, v in voter_balances.items():
                print(k,v / config.atomic)
        
            # allocate block rewards
            allocate.block_allocations(unprocessed, voter_balances)
            # get block count
            block_count = block.block_counter()
            print(f"\nCurrent block count : {block_count}")
        
            # check interval for payout
            stage, unpaid_voters, unpaid_delegate = interval_check(block_count, config.interval)
        
            # check if true to stage payments
            if stage == True and sum(unpaid_voters.values()) > 0:
                print("Staging payments")
                s = Stage(config, dynamic, sql, unpaid_voters, unpaid_delegate)
        
            # pause betweeen blocks
            time.sleep(5)
 
    print("End Script - Looping")
    time.sleep(600)
