#!/usr/local/bin/bash
# MAKE dmg, hash, sign and verify

echo "Creating dmg..."
echo "$(appdmg bleico_appdmg.json bleico_img.dmg)"
echo "Hashing..."
echo "$(shasum -a 256 bleico_img.dmg > SHA256)"
echo "$(shasum -c SHA256)"
echo "Signing with gpg key..."
echo "$(gpg -a --detach-sign bleico_img.dmg)"
echo "$(gpg --verify bleico_img.dmg.asc)"
echo "Done!"
