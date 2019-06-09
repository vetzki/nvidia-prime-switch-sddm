#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
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
        help="Dumps config to stdout or filename if specified"
    )
    return(parser.parse_args())

# remove in the future
def _compat_helper(conf,f,FMT):
    try:
        return(conf["symlink_target"])
    except KeyError:
        print("%smhwd_symlink_target is deprecated. please change mhwd_symlink_target to symlink_target in your custom config file ( %s )%s" %(FMT["red"],os.path.realpath(f),FMT["default"]))
        return(conf["mhwd_symlink_target"])

class Util:
    def __init__(self,src, trg, mload, mblacklist, mdisable, moptions):
        self.src = src
        self.trg = trg
        self.ml = mload
        self.mbl = mblacklist
        self.mdis = mdisable
        self.mopts = moptions
        self.modules_load_file = config["modules_load_file"]
        self.modules_modprobe_file = config["modules_modprobe_file"]

    def __enter__(self):
        return(self)

    def _file_writer(self,key,li,f,keyend=None):
        if keyend is None:
            _gen = (key+" "+i if key is not None else ""+i for i in li if len(li) > 0 )
        else:
            _gen = (key+" "+i+" "+keyend for i in li if len(li) > 0)
        for i in _gen:
            f.write(i+"\n")
        return

    def _changeModules(self):
        with open(self.modules_load_file,"w") as f1:# start with empty file
            self._file_writer(None, self.ml, f1, None)

        with open(self.modules_modprobe_file,"w") as f2:# start with empty file
            self._file_writer("blacklist", self.mbl, f2)
            self._file_writer("install", self.mdis, f2, "/bin/false")
            self._file_writer("options", self.mopts, f2)

    def switch_driver(self):
        try:
            os.unlink(self.trg)
        except FileNotFoundError:
            # file dont exist, continue without unlink
            pass
        # handle other unlink exceptions
        except Exception as e:
            self.res = "unlink exception!\n"+str(e)
            return
        try:
            os.symlink(self.src,self.trg)
        # handle symlink exception
        except Exception as e:
            self.res = "symlink exception!\n"+str(e)
            return
        try:
            self._changeModules()
            self.res = True
        # handle module change exception
        except Exception as e:
            self.res = "change module exception!\n"+str(e)

    def __exit__(self,t,i,tb):
        self.res = ""


if __name__ == "__main__":
    args = create_parser()
    FMT = { "red":"\x1b[31m","green":"\x1b[32m","bold":"\x1b[1m","cyan":"\x1b[36m","default":"\x1b[0m" }
        
    with open(args.config,"r") as f:
        config = json.loads(f.read())
        # remove in the future
        symlink_trg = (lambda : _compat_helper(config,args.config,FMT))()

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

        with Util(
                src=config["driver"][args.driver]["xorg_file"],
                trg=symlink_trg,
                mload=config["driver"][args.driver]["modules_load"],
                mblacklist=config["driver"][args.driver]["modules_blacklist"],
                mdisable=config["driver"][args.driver]["modules_disable"],
                moptions=config["driver"][args.driver]["modules_options"]
                ) as res:

            res.switch_driver()
            print("modules-load file: %s\nmodprobe file: %s\nSymlink %s -> %s" %(
                res.modules_load_file,res.modules_modprobe_file,
                res.src,res.trg
                ))
            for v in (["loaded: %s" %i for i in res.ml]+
                      ["blacklisted: %s" %i for i in res.mbl]+
                      ["disabled: %s" %i for i in res.mdis]+
                      ["options: %s" %i for i in res.mopts]):
                print(v)

            if res.res is True:
                print(FMT["green"]+"please relogin/reboot"+FMT["default"])
                exit(0)
            else:
                print("%sError\n%s%s" %(FMT["red"],res.res,FMT["default"]))
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
