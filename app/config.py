from environs import Env

env = Env()
env.read_env()

KAFKA_HOST=env.str("KAFKA_HOST", default="kafka")
KAFKA_PORT=env.str("KAFKA_PORT", default="9092")