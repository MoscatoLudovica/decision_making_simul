import sys, getopt, logging
from config import Config
from environment import EnvironmentFactory

def print_usage(errcode=None):
    print("Usage: python main.py -c <config_file_path>")
    sys.exit(errcode)

def main(argv):
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    configfile = ""
    try:
        opts, args = getopt.getopt(argv, "hc:", ["config="])
    except getopt.GetoptError:
        logging.fatal("Error in parsing command line arguments")
        print_usage(1)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_usage()
        elif opt in ("-c", "--config"):
            configfile = arg
    if not configfile:
        logging.fatal("No configuration file provided")
        print_usage(1)
    try:
        my_config = Config(config_path=configfile)
        my_env = EnvironmentFactory.create_environment(my_config)
    except Exception as e:
        logging.fatal(f"Failed to create environment: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main(sys.argv[1:])