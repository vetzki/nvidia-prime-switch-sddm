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
    parser.add_argument(
        "--current",
        const=True,
        action="store_const",
        help="Show current used driver"
    )
    return(parser.parse_args())
        

def return_curdrivers():
        cmd = 'lspci -D|grep VGA'
        std = subprocess.getstatusoutput(cmd)
        if std[0] == 0:
            gpus = ([k,v.split(" ")] for k,v in enumerate(std[1].split("\n")))
            gpu = {}
            for k,v in gpus:
                gpu[k]={ "pcislot":v[0], "name": " ".join(v[1:len(v)]) }
                with open("/sys/bus/pci/devices/"+v[0]+"/uevent") as f:
                    gpu[k]["status"] = f.read()
            return(gpu)
        else:
            print("Errorcode %i: Error %s" %(std[0],std[1]))


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


    #
    # switchDriver function:
    # par1=conf to symlink
    # par2=target symlink (default /etc/X11/xorg.conf.d/90-mhwd.conf)
    # par3=modules to load (list)
    # par4=modules to blacklist (list)
    # par5=modules to disable (list)
    # par6=modules options (list)
    #
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
    FMT = { "red":"\033[31m","green":"\033[32m","default":"\033[0m" }
    
    if args.current is True:
        gpus = return_curdrivers()
        c = 0
        for i in range(0,len(gpus)):
            print("GPU%i: %s\n%s" %(c,gpus[i]["name"],gpus[i]["status"]))
            c+=1
        exit(0)
        
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
        print("Possible drivers: %s" %(" or ".join(drivers)))
        exit(2)
