# cups-filters-1.x
VCS cups-filters repository for https://copr.fedorainfracloud.org/coprs/dkosovic/printing-el8/

This respository started of as a git clone of the f37 branch of cups-filters
from Fedora Package Sources:
*  https://src.fedoraproject.org/rpms/cups-filters/tree/f37

Fedora 37 is the last version of Fedora to use cups-filters-1.x.

This repository has been updated to cups-filters 1.28.17, includes a
number of patches and will attempt to use Adobe Reader for pdtops filter
or fallback to pdtops filter's hybrid option if /usr/bin/acroread is not
installed.

### Building on Fedora Copr

Select **Custom** for the source type.

Copy and paste the following script into the custom script text box:

```sh
#! /bin/sh

set -x # verbose output
set -e # fail the whole script if some command fails
                 
git clone https://github.com/eait-cups-printing/cups-filters-1.x.git
cp -p cups-filters-1.x/* .

version=`grep Version: cups-filters.spec | awk '{ print $2 }'`
source=`grep Source0: cups-filters.spec | awk '{print $2}' | sed "s/%{version}/$version/g"`

curl -OL $source
```

Copy and paste the following into the build dependencies field:
```
autoconf
automake
gettext-devel
libtool
gcc
gcc-c++
git-core
make
pkgconf-pkg-config
cups-devel
pkgconfig(libqpdf)
poppler-utils
ghostscript
libjpeg-turbo-devel
libtiff-devel
pkgconfig(dbus-1)
pkgconfig(fontconfig)
pkgconfig(freetype2)
pkgconfig(lcms2)
pkgconfig(libexif)
pkgconfig(libpng)
pkgconfig(poppler-cpp)
pkgconfig(zlib)
avahi-devel
pkgconfig(avahi-glib)
pkgconfig(glib-2.0)
systemd
python3-cups
dejavu-sans-fonts
systemd-rpm-macros
```
