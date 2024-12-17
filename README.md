# Judd

Bot to host and run team-based Turf War games, which are a bit like Battleship. See `GAME.md` for more about the game itself.

## How to set up

You'll need to host Judd yourself, as it only supports one game at a time. Here is how:

* In the Discord Developer Portal, create an App as usual
* Under Installation, Set Install Link to None
* Under Bot, uncheck Public Bot
* Under Bot, check the following permissions:
  * Send Messages
  * Send Messages in Threads
  * Embed Links
  * Attach Files
  * Use External Emojis
  * Use Slash Commands
  * (The permissions integer should be `277025703936`)
* Under OAuth2, check Bot and then check the same as above.
* Make sure Integration Type is Guild Install
* Copy the generated URL and open it in your web browser
  * Follow the instructions there to invite Judd to a server

## How to run a game

### Setup

* Create `token.txt` and place the bot's token inside
* Run the bot once, which creates a config file.
  * In this file you can change some things about the game. To apply, restart the bot
* Add game managers with `/add_manager`
  * The host of the bot will always be a manager
* Add teams with `/add_team`
* Configure the game field with `/config_field`
* Configure announcements with `/config_announcements`
* Configure game logs with `/config_logs`
* Schedule the game with `/schedule`
  * The game will automatically begin at the specified time
* Open voting with `/open_voting`
  * This lets players sign up
  * Voting automatically closes when the game commences
  * Close voting prematurely with `/close_voting`

### Gameplay

* Users can sign up with `/signup` at any time until the game begins when voting is open
* At the start of each day (UTC midnight plus the configured offset), players will be DM'd a notice that game turns are open
* For the following configured amount of hours, players can use `/move` and `/throw` the configured amount of times
  * However, players that were hit by a projectile the previous day cannot make any actions
* Afterwards, the results of the day's actions will be calculated and posted in the configured channel. Players who landed or recieved hits will also be notified in DMs

### End of game

* After the final turn period concludes, the game will be finished. The results will be calculated and announced in the configured channel. Players will be DM'd statistics about their performance in the game

### Things Judd doesn't do for you

* Create in-app events
* Create channels for each team
