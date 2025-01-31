# Judd

Discord bot to host and run team-based Turf War games, which are an interesting cross between Battleship and Splatoon Turf War.

\-- [Jump to "How to set up"](#how-to-set-up) --

## About the game

Turf War games are played in two or more teams, and are designed for lots of players. Game rounds are played one per day, where players can move to new locations and throw projectiles. Thrown projectiles claim turf in your team's colour - stepping on the colour of an enemy team will reveal your location and make you lose your turn the next day.

The objective is to claim as much turf as possible over the game period. At the end, the team with the most claimed in their name wins. Strategize with your teammates to keep opponents frozen and stop them contesting you!

The design of the game was created by makotomori.

## How to set up

You'll need to host Judd yourself, as it only supports one game at a time. Generally, Judd is intended to be "disposable" - a fresh install is the easiest way to start a new game. Here is how to do it:

* In the Discord Developer Portal, create an App as usual
* Under Installation, Set Install Link to None
* Under Bot, uncheck Public Bot
* Under Bot, check the following permissions:
  * Manage Roles
  * Send Messages
  * Send Messages in Threads
  * Embed Links
  * Attach Files
  * Use Slash Commands
  * (The permissions integer should be `277293877248`)
* Under OAuth2, check Bot and then check the same as above
* Make sure Integration Type is Guild Install
* Copy the generated URL and open it in your web browser
  * Follow the instructions there to invite Judd to a server
  * Make sure to allow all the requested permissions or Judd may not work

## How to run a game

### Setup

* Create `token.txt` and place the bot's token inside
* Run the bot once, which creates a config file `config.json`
  * In this file you can change some things about the game. To apply, restart the bot
* Add game managers with `/add_manager`
  * Game managers can run priveliged commands to set up and run the game
  * The host of the bot will always be a manager
* Configure the game field with `/setup_map`
* Add teams with `/add_team`
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
* At the start of each day (UTC midnight plus the configured offset), turns will be opened
* For the following configured amount of hours, players can use `/move` and `/throw` the configured amount of times
  * However, players that were on enemy territory (that is, they moved there, or a snowball landed there) the previous day cannot make any actions
  * When a player is unfrozen, they'll need to move out of enemy territory or they will be frozen again the next turn
* Afterwards, the results of the day's actions will be calculated and posted in the configured channel
  * The positions of players frozen this day are revealed
* Anyone can see the map with `/map` and a detailed view with `/location`
  * However, player positions are not visible. If you're participating in the game, you can see your teammates if you want

### End of game

* After the final turn period concludes, the game will be finished. The results will be calculated and announced in the configured channel.
* The players who performed the best will be given a special mention! This includes turfing, attacking, and best accuracy

### Things Judd doesn't do for you

* Create in-app events
* Create channels for each team
  * It *does* create roles for each time and assign them automatically
  * Therefore, you can configure team channels based on these roles
