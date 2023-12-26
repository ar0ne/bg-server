# Game server

This is web server for turn based games, build on top of [Tornado](https://github.com/tornadoweb/tornado) + [Tortoise-ORM](https://github.com/tortoise/tortoise-orm).

## Run locally

```
cd server

virtualenv venv

source venv/bin/activate

pip install -r requirements.txt

aerich upgrade

python main.py
```

*Note*: You need to `.env.example` as `.env` and update variables accordingly.
