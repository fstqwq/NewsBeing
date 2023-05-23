from api import *


if __name__ == "__main__":
    # read config from data/config-sample.json
    with open('data/config-sample.json') as f:
        config = json.load(f)
    preprocess(config)