from pathlib import Path
import json

# path for datafolder
data_folder = Path("/Users/mattrobins/rareskills_projects/week1/data")
# path for input file
inputPath = Path("/Users/mattrobins/rareskills_projects/week1/input.txt")

count = 1  # the current block number


def main(inputFile):
    global count
    global data_folder


# BLOCK CREATION
    with open(inputFile, 'r') as input:  # convert the input into list
        inputs = input.readlines()

    i = 0
    blockItems = []  # list for block with transfers
    for i in range(0, len(inputs)):
        if inputs[i].split('|')[0].strip() == 'coinbase':

            name = 'block'+str(count)+'.txt'  # name of block using count
            file_to_open = data_folder/name

            if not blockItems:  # if there are no transfers in this block
                with open(file_to_open, 'w') as block:
                    block.write(inputs[i])
                count += 1

            if blockItems:  # if there are transfers in this block
                transferContents = []  # transferContents with broken up transactions
                for transaction in blockItems:
                    # split input line between '|' to separate items (NESTED LIST)
                    transferContents.append(transaction.split('|'))

                n = len(transferContents)  # length of

                for k in range(n - 1):
                    flag = 0

                    # bubble sort to organize the 'transferContents' but also the original order of input lines in the block
                    for j in range(n - 1):

                        if float(transferContents[j][4].replace("\n", '').strip()) < float(transferContents[j+1][4].replace("\n", '').strip()):
                            tmp = transferContents[j]
                            tmp2 = blockItems[j]
                            transferContents[j] = transferContents[j+1]
                            blockItems[j] = blockItems[j+1]
                            transferContents[j+1] = tmp
                            blockItems[j+1] = tmp2
                            flag = 1

                    if flag == 0:
                        break

                # writing *sorted* input lines to the block'count'.txt file
                with open(file_to_open, 'w') as block:
                    for transacation in blockItems:
                        block.write(transacation)
                    block.write(inputs[i])
                blockItems = []  # clearing blockItems for next block
                count += 1  # next block id

        # adding transfer input line to blockItems
        if inputs[i].split('|')[0].strip() == 'transfer':
            blockItems.append(inputs[i])

# STATE CREATION
    stateFileName = 'state.json'
    with open(data_folder/stateFileName, 'w') as state:  # opening json file to write to later
        stateDictionary = {}  # initializing dictionary
        fees = 0  # initializing fees
        for i in range(1, count):  # looping through all the blocks
            blockFileName = 'block'+str(i)+'.txt'
            with open(data_folder/blockFileName, 'r') as block:
                blockLines = block.readlines()  # adding block content to blockLines list

                # initializing list of transfers (does the same as the blockContents in block creation)
                blockContents = []

                for j in range(0, len(blockLines)):
                    currentLine = blockLines[j]  # current line in block
                    # making a list of items in the line separated by '|'
                    transaction = currentLine.split('|')

                    if transaction[0].strip() == 'coinbase':  # if input line is 'coinbase'
                        if not blockContents:  # if there are no transfers in this block
                            adress = transaction[1].strip()
                            # add the adress + balance of 5 to the dictionary (ADDING THE BLOCK TO THE CHAIN)
                            stateDictionary.update({adress: {'balance': 5}})

                        if blockContents:  # if there are transfers in this block
                            for transfer in blockContents:
                                keys = transfer.split('|')
                                fromAdress = keys[1].strip()  # from adress
                                toAdress = keys[2].strip()  # to adress
                                amount = float(keys[3].strip())  # amount
                                fee = float(keys[4].strip())  # fee
                                # add the fee to the total fees for this block (what the miner receives )
                                fees += fee

                                if fromAdress in stateDictionary:  # if this adress is 'on the chain'
                                    currentBalance = stateDictionary[fromAdress]['balance']
                                    # subtract the fees and the amount from the balance to get the new balance
                                    newBalance = currentBalance-amount-fee

                                    if newBalance < 0:
                                        print(
                                            'ERROR: ' + transfer + 'INSUFFECIENT FUNDS IN: ' + fromAdress)
                                        quit()  # if there isn't suffecient funds in the from adress the code stops and prints an error message
                                    else:
                                        # update the existing adress and balance on the chain (round the amount to 1 decimal place)
                                        stateDictionary.update(
                                            {fromAdress: {'balance': round(newBalance, 1)}})

                                else:  # if there is no from adress on the chain
                                    print('ERROR: ' + transfer +
                                          'NO ADRESS: ' + fromAdress)
                                    quit()  # if the from adress is not on the chain the code stops and prints an error message

                                if toAdress in stateDictionary:  # if the to adress is already on the chain
                                    currentBalance = stateDictionary[toAdress]['balance']
                                    newBalance = currentBalance+amount  # add the amount to the current balance

                                    # update the balance on the chain
                                    stateDictionary.update(
                                        {toAdress: {'balance': round(newBalance, 1)}})

                                else:  # if the adress is not already on the chain
                                    # add the adress and the new balance onto the chain
                                    stateDictionary.update(
                                        {toAdress: {'balance': round(amount, 1)}})

                            # payout to the miner
                            adress = transaction[1].strip()

                            if adress in stateDictionary:  # if the adress is alreay on the chain
                                currentBalance = stateDictionary[adress]['balance']
                                # add the reward of 5 eth and the fees from the transactions in the block
                                amount = currentBalance + 5 + fees
                                # update the balance on the chain
                                stateDictionary.update(
                                    {adress: {'balance': round(amount, 1)}})

                            else:  # if the adress is not on the chain
                                amount = 5 + fees  # add the fees to the 5 eth reward
                                # add the adress and the balance to the chain
                                stateDictionary.update(
                                    {adress: {'balance': round(amount, 1)}})

                            fees = 0  # reset the fees for the next block since the block has been added to the chain and the miner recived the fees

                    if transaction[0].strip() == 'transfer':
                        # add the transfer input line to the blockContents (same as block creation)
                        blockContents.append(currentLine)

        # dump the dictionary to the stat.json file and format it
        json.dump(stateDictionary, state, indent=2)


main(inputPath)  # run the code
