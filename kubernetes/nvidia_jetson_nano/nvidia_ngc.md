# NVIDIA NGC


<https://docs.nvidia.com/ngc/ngc-catalog-cli-user-guide/index.html>


<https://ngc.nvidia.com/setup/installers/cli>


## Install NGC CLI

### Linux
```sh
wget -O ngccli_cat_linux.zip https://ngc.nvidia.com/downloads/ngccli_cat_linux.zip && \
unzip -o ngccli_cat_linux.zip -d ngccli && \
md5sum -c ngccli/ngc.md5 && \
chmod u+x ngccli/ngc && \
mkdir -p ~/.local/bin && \
cp ngccli/ngc ~/.local/bin/ && \
sudo cp ngccli/ngc /usr/local/bin/ && \
rm -r ngccli

ngc config set
```

The NGC CLI binary for Linux is supported on Ubuntu 16.04 and later distributions.

Click Download CLI to download the zip file that contains the binary, then transfer the zip file to a directory where you have permissions and then unzip and execute the binary. You can also download, unzip, and install from the command line by moving to a directory where you have execute permissions and then running the following command:
```sh
wget -O ngccli_cat_linux.zip https://ngc.nvidia.com/downloads/ngccli_cat_linux.zip && \
unzip -o ngccli_cat_linux.zip -d ngccli && \
cd ngccli \
chmod u+x ngc
```

Check the binary's md5 hash to ensure the file wasn't corrupted during download:
```sh
md5sum -c ngc.md5
```

Add your current directory to path:
```sh
echo "export PATH=\"\$PATH:$(pwd)\"" >> ~/.bash_profile && source ~/.bash_profile
echo "export PATH=\"\$PATH:$(pwd)\"" >> ~/.bashrc && source ~/.bashrc
echo "export PATH=\"\$PATH:$(pwd)\"" >> ~/.zshrc && source ~/.zshrc
```

You must configure NGC CLI for your use so that you can run the commands.
Enter the following command, including your API key when prompted:
```sh
ngc config set
```

* Uninstall
Remove the binary file:
```sh
rm `which ngc`
```


### Mac OS

The NGC CLI binary for macOS is supported on macOS 10.13 and later.

Click Download CLI to download the zip file that contains the binary, then transfer the zip file to a directory where you have permissions and then unzip and execute the binary. You can also download, unzip, and install from the command line by moving to a directory where you have permissions and then running the following command:
```sh
curl -O https://ngc.nvidia.com/downloads/ngccli_cat_mac.zip && unzip ngccli_cat_mac.zip && chmod u+x ngc
```

Make sure that you have set up localization to support UTF-8 by setting LC_ALL in ~/.bash_profile. For example:
```sh
export LC_ALL=en_US.UTF-8
```

Add your current directory to path:
```sh
echo "export PATH=\"\$PATH:$(pwd)\"" >> ~/.bash_profile && source ~/.bash_profile
```

You must configure NGC CLI for your use so that you can run the commands.
```sh
ngc config set
```

* Uninstall
Remove the binary file and clear the hash:
```sh
rm `which ngc` && hash -d ngc
```


