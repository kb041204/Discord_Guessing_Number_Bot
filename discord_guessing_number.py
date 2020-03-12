import os
import random
import threading
import traceback

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
#GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()

guess_min = "null"
guess_target = "null"
guess_max = "null"
message_lock = threading.Lock()

@client.event
async def on_ready():
	#guild = discord.utils.get(client.guilds, name=GUILD)
	#print(
	#	f'{client.user} is connected to the following guild:\n'
	#	f'{guild.name}(id: {guild.id})'
	#)
	print("Bot is ready")

@client.event
async def on_message(message):
	global guess_min
	global guess_target
	global guess_max
	
	curr_chan = message.channel
	received_message = message.content.lower()
	
	#Stop executing if it is the BOT himself
	if message.author == client.user: 
		return
	
	message_lock.acquire()
	#Display help
	if received_message.startswith("/guess_num"): #(/guess_num<any>)
		
		try:
			command, first_part = received_message.split(" ", 1)
		except ValueError: #(/guess_num)
			line = "Guess number BOT v0.1 made by shun\nCommands available:\n/guess_num show: show the current game status\n/guess_num <your_guess>: guess the number in the current game\n/guess_num start <max_number>: Start a new game with range 1~max_number (both exclusive)"
			await curr_chan.send(line)
			message_lock.release()
			return
		
		if first_part.startswith("help"): #(/guess_num help<any>)
			response = "Guess number BOT v0.1 made by shun\nCommands available:\n/guess_num show: show the current game status\n/guess_num <your_guess>: guess the number in the current game\n/guess_num start <max_number>: Start a new game with range 1~max_number (both exclusive)"
		
		else: #(/guess_num <first_part>)
			if first_part.startswith("show"): #(/guess_num show<any>)
				if guess_min == "null" or guess_max == "null":
					response = "No game has started yet, start one with \"/guess_num start <max_number>\""
				else:
					response = "The current game is guess a number between " + str(guess_min) + " and " + str(guess_max) + " (both exclusive) with command /guess_num <your_guess>"
				
		
			elif first_part.startswith("start"): #(/guess_num start<any>)
				try:
					first, max_number = first_part.split(" ", 1)
				except ValueError: #(/guess_num start)
					line = "Usage: \"/guess_num start <max_number>\""
					await curr_chan.send(line)
					message_lock.release()
					return
					
				#handle wrong data type (/guess_num start <non-integer/none>)
				try: 
					new_max_number = int(max_number)
				except ValueError:
					line = message.author.name + ": \"" + str(max_number) + "\" is not an integer, please try again"
					await curr_chan.send(line)
					message_lock.release()
					return
					
				#(/guess_num start <integer>)
				#handle game already started
				if guess_min != "null" or guess_max != "null":
					response = message.author.name + ": A game has started, only one game is allowed to run at once"
				
				#handle max_number too small (/guess_num start <too small>)
				elif new_max_number <= 3:
					response = message.author.name + ": The max number \"" + str(new_max_number) + "\" is smaller than or equal to 3, please use another number"
			
				#correct command and max_number, start a game
				else:
					guess_min = 1
					guess_max = new_max_number
					random.seed()
					guess_target = random.randint(guess_min+1, guess_max-1)
					print("Log: Started a game, the target number is " + str(guess_target) + ", range: " + str(guess_min) + "~" + str(guess_max))
					response = message.author.name + " has start a game.\nGuess a number between " + str(guess_min) + " and " + str(guess_max) + " (both exclusive) with command /guess_num <your_guess>"

			else: #(/guess_num <first_part>)
				#handle wrong data type (/guess_num <non-integer/none>)
				try:
					guessing_number = int(first_part)
				except ValueError:
					line = message.author.name + "'s guess \"" + str(first_part) + "\" is not an integer, please try again"
					await curr_chan.send(line)
					message_lock.release()
					return
				
				#guess not yet stated
				if guess_min == "null" or guess_max == "null":
					response = message.author.name + " please start a game first by \"/guess_num start <max_number>\""

				#guess out of range (/guess_num <non-integer>)
				elif guessing_number <= guess_min or guessing_number >= guess_max:
					response = message.author.name + "'s guess \"" + str(guessing_number) + "\" is not between " + str(guess_min) + " and " + str(guess_max) + " (both exclusive), please try again"
				
				#correct command syntax and within range
				else:
					print("Log: " + message.author.name + " guessed " + str(guessing_number) + ", the target number is " + str(guess_target) + ", range: " + str(guess_min) + "~" + str(guess_max) + " (both exclusive)")
					if guessing_number == guess_target:
						await message.add_reaction("\U0001F4A3") #Bomb emoji
						response = message.author.name + " has guessed the correct number: " + str(guessing_number) + "! Round end"
						guess_min = "null"
						guess_target = "null"
						guess_max = "null"
						print("Log: " + message.author.name + " has guessed the correct number, data reset successful")
						
					else:
						if guessing_number > guess_min and guessing_number < guess_target:
							guess_min = guessing_number
						else:
							guess_max = guessing_number
						await message.add_reaction("\U0001F44C") #Okay emoji
						response = message.author.name + "'s guess \"" + str(guessing_number) + "\" is safe! The new range is between " + str(guess_min) + " and " + str(guess_max) + " (both exclusive)"
	try:
		await curr_chan.send(response)
	except UnboundLocalError as emsg:
		print("Log: UnboundLocalError catched!!!!")
		traceback.print_exc()
		guess_min = "null"
		guess_target = "null"
		guess_max = "null"
		await curr_chan.send("An error occured during execution, reseting all the data...")
		message_lock.release()
	message_lock.release()

client.run(TOKEN)