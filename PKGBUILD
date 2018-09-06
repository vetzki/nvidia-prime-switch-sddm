pkgname="nvidia-prime-switch-sddm"
pkgver=1
pkgrel=7
pkgdesc="(! use only with sddm !) Setup nvidia and intel for optimus based laptops without bumblebee (legacy 390xx nvidia driver) (! use only with sddm !)"
license=("none")
kernelvers="$(uname -r | awk -F "." '{print $1 $2}')"
depends=('xf86-video-intel' 'python' 'sddm' "linux${kernelvers}-nvidia-390xx" 'lib32-nvidia-390xx-utils' 'nvidia-390xx-utils')
optdepends=('python-magic: better support for --info switch')
makedepends=('python')
conflicts=('nvidia-prime-switch' 'nvidia-prime-switch-lightdm')
source=('prime-switch.py' 'prime-switch-conf.json' 'intel.conf' 'nvidia.conf' 'intel-modesetting.conf' 'nvidia-prime-displaymanager.hook')
sha256sums=(
'001dd4e5c011d365a88f0095205aefe04b46cacd8cc70fda6460584ac55db5cb'
'574138661177cc5042636f237c8adc2e934a38adb7bf2851acd35d0115ca8569'
'b7e686d0f689c9d7e2d99ffa6a3b3c110730e36a911b5672f711551b3e41d6a8'
'8e0473885e05c7a3b00380db251884456a29111544f94faeabd945b442595891'
'edd5b3968e0cf46dcc13a8335f71291b19355c8fc75c8c3af597540fe548c929'
'547ca622632e234f04900a46e5652ea5c77b252595689b22c8e46f81a800173f'
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
std = getoutput("lspci | grep -e VGA -e 3D").split("\n")
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
