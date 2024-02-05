#!/usr/bin/env sh
echo "unloading multipass daemon"
sudo launchctl unload /Library/LaunchDaemons/com.canonical.multipassd.plist
# Figure out which instances exist
for dir in `sudo ls /var/root/Library/Application\ Support/multipassd/qemu/vault/instances`;
    do
    # Figure out which images exist
    for img in `sudo ls /var/root/Library/Application\ Support/multipassd/qemu/vault/instances/$dir/`;
        do
        # knock out the ISOs
        ext="img"
        if [[ "$img" =~ "$ext" ]]
        then
            # Suspend and clean discovered images
            echo "suspending the $dir $img image"
            sudo /Library/Application\ Support/com.canonical.multipass/bin/qemu-img snapshot -d suspend /var/root/Library/Application\ Support/multipassd/qemu/vault/instances/$dir/$img
            echo "trying to clean the $dir $img image"
            sudo /Library/Application\ Support/com.canonical.multipass/bin/qemu-img check -r all /var/root/Library/Application\ Support/multipassd/qemu/vault/instances/$dir/$img
            fi
        done
    done
echo "reloading multipass daemon"
sudo launchctl load -w /Library/LaunchDaemons/com.canonical.multipassd.plist
echo "killing the UI"
pkill -SIGSTOP Multipass
echo "restarting the UI"
/Library/Application\ Support/com.canonical.multipass/bin/multipass.gui.app/Contents/MacOS/multipass.gui
