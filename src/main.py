import sys, getopt, config

def print_usage(errcode = None):
    print ("Usage: python main.py -c <config_file_path>")
    sys.exit(errcode)

def main(argv):
    configfile = ""
    try:
        opts, args = getopt.getopt(argv,"hc:",["config="])
    except getopt.GetoptError:
        print ("[FATAL] Error in parsing command line arguments")
        print_usage(1)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_usage()
        elif opt in ("-c", "--config"):
            configfile = arg
    if my_config.mode["multi_threading"]:
        # TODO multi threading for batching
        return
    else:
        my_config = config.Config(configfile)

if __name__ == "__main__":
    main(sys.argv[1:])