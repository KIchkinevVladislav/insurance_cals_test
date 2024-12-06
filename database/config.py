from environs import Env

env = Env()
env.read_env()

DB_HOST=env.str("DB_HOST", default="localhost")
DB_PORT=env.str("DB_PORT", default="5432")
DB_NAME=env.str("DB_NAME", default="postgres")
DB_USER=env.str("DB_USER", default="postgres")
DB_PASS=env.str("DB_PASS", default="postgres")

DB_TEST_HOST=env.str("DB_TEST_HOST", default="localhost")
DB_TEST_PORT=env.str("DB_TEST_PORT", default="5432")
DB_TEST_NAME=env.str("DB_TEST_NAME", default="postgres_test")
DB_TEST_USER=env.str("DB_TEST_USER", default="postgres")
DB_TEST_PASS=env.str("DB_TEST_PASS", default="postgres")
