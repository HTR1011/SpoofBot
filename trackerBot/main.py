

from helper import *
from dotenv import load_dotenv


load_dotenv()

TELEGRAM_BOT_TOKEN = os.environ.get("TelegramBotToken")


#Start interface of Spoof Bot in Telegram

def start(update, context):
    message = """


👋 Welcome to the Spoof Monitoring Bot!

Use /add <blockchain (optional)> <address> <name> to add a new address to monitor.

Example: /add eth 0x123456789abcdef Whale Wallet

Use /remove <address> or <name> to stop monitoring an address.

Example: /remove $PEPE

Use /list <blockchain> to list all addresses being monitored for a specific blockchain.

Example: /list ETH or just /list

    """
    context.bot.send_message(chat_id=update.message.chat_id, text=message)


#telegram add command
#input: blockchain {optional}, address, name

def add(update, context):
    if len(context.args) < 2:
        context.bot.send_message(chat_id=update.message.chat_id, text="Please provide a blockchain (optional) + address + name\n->Example: /add chain (default:eth) address name")
        return


    if len(context.args[0]) > 4:
        blockchain = "eth"
        address = context.args[0]
        name = ' '.join(context.args[1:]).strip()
        type = (checkAdress(context.args[0])).lower()


    else:
        blockchain = context.args[0].lower()
        address = context.args[1]
        name = ' '.join(context.args[2:]).strip()
        type = (checkAdress(context.args[1])).lower()

    #do not need to check blockchain type and THEN format if all chains are EVM compatible
    # will have same format

    if blockchain == 'eth' or blockchain == 'bnb' or blockchain == 'arb':
        if not re.match(r'^0x[a-fA-F0-9]{40}$', address):
            context.bot.send_message(chat_id=update.message.chat_id, text=f"{address} is not a valid address.")
            return

    else:
        context.bot.send_message(chat_id=update.message.chat_id, text=f"Invalid blockchain specified: {blockchain}")
        return


    add_address(address, blockchain, name, type)

    message = f'Added {type} {name} to the list of watched {blockchain.upper()} addresses.'
    context.bot.send_message(chat_id=update.message.chat_id, text=message)


#remove command to remove an address from watched list through telegram
#input: address or name

def remove(update, context):

    address_delete = ' '.join(context.args[0:]).strip()

    with open("watched_addresses.txt", "r") as file:
        lines = file.readlines()


    for index, line in enumerate(lines):
        blockchain, address, name = line.strip().split(":")
        if address_delete == address or address_delete == name:
            message = f'Removed {address_delete} from the list of watched addresses.'
            remove_address(address_delete)
            break
        else:
            message = f'{type} {address_delete} not found.'


    context.bot.send_message(chat_id=update.message.chat_id, text=message)




#List command in telegram; outputs: addresses tracked.
#Seperates wallets and contracts

def list(update, context):

    with open("watched_addresses.txt", "r") as f:

        # creates a list of addresses by strip() each line in the file.
        #splits it into blockchain and address using the colon (:) as the separator.
        addresses = [line.strip() for line in f.readlines()]

    if addresses:
        eth_addresses = []
        bnb_addresses = []

        for i_address in addresses:
            blockchain, address, name, type = i_address.split(':')

            if blockchain == 'eth':
                eth_addresses.append((address, name,type))
            elif blockchain == 'bnb':
                bnb_addresses.append((address, name))

        message = "The following addresses are currently being monitored\n"
        message += "\n"

        if eth_addresses:
            message += "Ethereum Addresses:\n"

            #The enumerate function returns both the index i
            # and the value address, name for each element in the list.
            #Unpacks the tuple in message var
            for i, (address, name, type) in enumerate(eth_addresses):
                message += f"{i+1}. {type} {address} as {name}\n"

            message += "\n"

        if bnb_addresses:
            message += "Binance Addresses:\n"
            for i, (address, name) in enumerate(bnb_addresses):
                message += f"{i+1}. {address} as {name} \n"
        context.bot.send_message(chat_id=update.message.chat_id, text=message)

    else:
        message = "There are no addresses currently being monitored."
        context.bot.send_message(chat_id=update.message.chat_id, text=message)


# Initialization of telegram bot through telegram packages

from telegram.ext import Updater, CommandHandler

updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

start_handler = CommandHandler('start', start)
add_handler = CommandHandler('add', add)
remove_handler = CommandHandler('remove', remove)
list_handler = CommandHandler('list', list)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(add_handler)
dispatcher.add_handler(remove_handler)
dispatcher.add_handler(list_handler)

updater.start_polling()
print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Telegram bot started.")

print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Monitoring addresses...")
spoof_monitor()
