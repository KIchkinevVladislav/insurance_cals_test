from environs import Env

env = Env
env.read_env()

DB_HOST=env.str("DB_HOST", default="localhost")
DB_PORT=env.str("DB_PORT", default="5432")
DB_NAME=env.str("DB_NAME", default="postgres")
DB_USER=env.str("DB_USER", default="postgres")
DB_PASS=env.str("DB_PASS", default="postgres")