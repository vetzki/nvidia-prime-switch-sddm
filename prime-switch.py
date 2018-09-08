#!/usr/bin/python3
# -*- coding_utf-8 -*-

import os,subprocess,re
import argparse
import json


def create_parser():
    defconf = "/usr/local/share/nvidia-prime-switch/prime-switch-conf.json"
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d", "--driver",
        help="Switch to this driver (e.g. intel or nvidia)"
    )
    parser.add_argument(
        "-c", "--config",
        default=defconf,
        help="Path to config file"
    )
    parser.add_argument(
        "-s", "--show-config",
        nargs='?',
        const=True,
        metavar="Filename",
        help="Dumps default config to stdout or filename if specified"
    )
    return(parser.parse_args())


class Util:
    def _file_writer(self,key,li,f,keyend=None,addtoprint=None):
        if keyend is None:
            _gen = (key+" "+i if key is not None else ""+i for i in li if len(li) > 0 )
        else:
            _gen = (key+" "+i+" "+keyend for i in li if len(li) > 0)
        for i in _gen:
            f.write(i+"\n")
            print("%s %s" %(addtoprint,i) if addtoprint is not None else "%s" %(i) )
        return

    def _changeModules(self,load,blacklist,disable,options):
        with open(config["modules_load_file"],"w") as f1:# start with empty file
            self._file_writer(None,load,f1,None,"load")

        with open(config["modules_modprobe_file"],"w") as f2:# start with empty file
            self._file_writer("blacklist",blacklist,f2)
            self._file_writer("install",disable,f2,"/bin/false")
            self._file_writer("options",options,f2)

    def switchDriver(self,src, trg, mload, mblacklist, mdisable, moptions):
        try:
            os.unlink(trg)
        except FileNotFoundError:
            # file dont exist, continue without unlink
            pass

        os.symlink(src,trg)
        print("Symlink %s -> %s" %(src,trg))

        try:
            self._changeModules(mload,mblacklist,mdisable,moptions)
            return(True)
        except Exception as e:
            return(str(e))


if __name__ == "__main__":
    args = create_parser()
    FMT = { "red":"\x1b[31m","green":"\x1b[32m","bold":"\x1b[1m","cyan":"\x1b[36m","default":"\x1b[0m" }
        
    with open(args.config,"r") as f:
        config = json.loads(f.read())

    if args.show_config is True:
        print(json.dumps(config, indent=4, separators=(',', ': ')))
        exit(0)
    elif isinstance(args.show_config,str): # filename specified
        print("dump config to file %s" %args.show_config)
        with open(args.show_config,"w") as f:
            f.write(json.dumps(config, indent=4, separators=(',', ': ')))
        exit(0)

    drivers = list(config["driver"].keys())

    if args.driver in drivers:
        if os.getuid() != 0:
            # not root user
            print("please start with root privileges")
            exit(3)

        res = Util().switchDriver(
                  src=config["driver"][args.driver]["xorg_file"],
                  trg=config["mhwd_symlink_target"],
                  mload=config["driver"][args.driver]["modules_load"],
                  mblacklist=config["driver"][args.driver]["modules_blacklist"],
                  mdisable=config["driver"][args.driver]["modules_disable"],
                  moptions=config["driver"][args.driver]["modules_options"])

        if res is True:
            print(FMT["green"]+"please relogin/reboot"+FMT["default"])
            exit(0)
        else:
            print("%sError\n%s%s" %(FMT["red"],res,FMT["default"]))
            exit(1)
    else:
        # driver not found or none specified
        print("possible drivers:")
        for i in drivers:
            driver = FMT["bold"]+i+FMT["default"]
            try:
                comment = config["driver"][i]["comment"] if config["driver"][i]["comment"] is not False else None
            except KeyError:
                comment = None
            print("%s (%s)" %(driver,comment) if comment is not None else "%s" %(driver))
        exit(2)
