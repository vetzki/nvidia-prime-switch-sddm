pkgname="nvidia-prime-switch-sddm"
pkgver=1
pkgrel=4
pkgdesc="(! use only with sddm !) Setup nvidia and intel for optimus based laptops without bumblebee (! use only with sddm !)"
license=("none")
kernelvers="$(uname -r | awk -F "." '{print $1 $2}')"
depends=("linux${kernelvers}-nvidia" 'lib32-nvidia-utils' 'nvidia-utils' 'xf86-video-intel' 'python' 'sddm') # maybe add also nouveau?
makedepends=('python')
conflicts=('nvidia-prime-switch' 'nvidia-prime-switch-lightdm')
source=('prime-switch.py' 'prime-switch-conf.json' 'intel.conf' 'nvidia.conf' 'intel-modesetting.conf' 'nvidia-prime-displaymanager.hook')
sha256sums=(
'40d83133fd815b80936e4ae9579accea0beae4a119104381e295d404f64a34c0'
'92a22f6815afcd1dca60c989b92435bec0125889c8c43f36ffffc2f6af5b4794'
'b7e686d0f689c9d7e2d99ffa6a3b3c110730e36a911b5672f711551b3e41d6a8'
'847139b9d357134ed01a563e4d332a28d8c25cabd6d972db53baf4dee7c99e36'
'edd5b3968e0cf46dcc13a8335f71291b19355c8fc75c8c3af597540fe548c929'
'73a67c2ba8f77253fbb1c36194fb29dd7aa6babeff2174078a8abff87265d604'
)

arch=('x86_64')
prefix="/usr/local"
install="${pkgname}".install
backup=('etc/X11/mhwd.d/intel.conf' 'etc/X11/mhwd.d/intel-modesetting.conf' 'etc/X11/mhwd.d/nvidia.conf')


prepare() {
# xconfigs
# ensure right buisd (maybe not needed)
pcis=$(python -c '
from subprocess import getoutput
std = getoutput("/usr/bin/lspci | grep VGA").split("\n")
pci = [ i.split(" ")[0] for i in std if "intel" in i.lower() ]
pci += [ i.split(" ")[0] for i in std if "nvidia" in i.lower() ]
cids = {}
joiner = ":"
for k,v in enumerate(pci): cids[k]=[int(i) for i in v.replace(".",":").split(":")];
print("%s %s" %(joiner.join(str(x) for x in cids[0]),joiner.join(str(x) for x in cids[1])) )
')

i=$(echo ${pcis} | cut -d \  -f 1) # intel config
n=$(echo ${pcis} | cut -d \  -f 2) # nvidia config
sed -i "s/BusID \"PCI:0:2:0\"/BusID \"PCI:${i}\"/" ${srcdir}/intel.conf
sed -i "s/BusID \"PCI:0:2:0\"/BusID \"PCI:${i}\"/" ${srcdir}/intel-modesetting.conf
sed -i "s/BusID \"PCI:1:0:0\"/BusID \"PCI:${n}\"/" ${srcdir}/nvidia.conf
}


package() {
cd "${srcdir}"

install -Dm755 prime-switch.py "${pkgdir}/${prefix}/bin/prime-switch"
install -Dm644 prime-switch-conf.json "${pkgdir}/${prefix}/share/nvidia-prime-switch/prime-switch-conf.json"
# xconfigs
for i in intel.conf intel-modesetting.conf nvidia.conf
  do
    install -Dm644 ${srcdir}/$i "${pkgdir}/etc/X11/mhwd.d/$i"
done

# hooks
install -Dm644 "${srcdir}/nvidia-prime-displaymanager.hook" "${pkgdir}/usr/share/libalpm/hooks/nvidia-prime-displaymanager.hook"
}
