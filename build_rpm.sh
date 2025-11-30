#!/bin/bash
VERSION="0.5"   # <--- Updated to match Spec
NAME="rpm-installer"
SRC_DIR="$HOME/rpmbuild/SOURCES"
TEMP_DIR="/tmp/$NAME-$VERSION"

# 1. Setup Tree
rpmdev-setuptree

# 2. Prepare Source Tarball
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"
cp rpm-installer.py "$TEMP_DIR/"
cp rpm-installer.desktop "$TEMP_DIR/"
tar -czf "$SRC_DIR/$NAME-$VERSION.tar.gz" -C /tmp "$NAME-$VERSION"

# 3. Copy Spec and Build
cp rpm-installer.spec "$HOME/rpmbuild/SPECS/"
rpmbuild -bb "$HOME/rpmbuild/SPECS/rpm-installer.spec"

echo "Build Complete: ~/rpmbuild/RPMS/noarch/$NAME-$VERSION-1.fc*.noarch.rpm"
