# What is it?

This is web server for turn based games (e.g. board games). Idea was to make something similar to [boardgamearena](https://boardgamearena.com/) and "maybe" write some games that not exist there yet.


### List of available games:

- [Regicide](https://boardgamegeek.com/boardgame/307002/regicide)

    Regicide is a cooperative, fantasy card game for 1 to 4 players, played using a standard deck of cards.

- TicTacToe

- ...



## How to use

The simplest way to run it is to use Docker. But, before you need to add environment files to "client" and "server" (see readme).

### Docker

`docker-compose build`

`docker-compose up -d`

`docker-compose up scale backend=3`
