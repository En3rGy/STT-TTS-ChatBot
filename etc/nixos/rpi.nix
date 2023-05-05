{ config, pkgs, lib, ... }:

let
  my-python-packages = ps: with ps; [
    pyaudio
    # other python packages
    (
      buildPythonPackage rec {
        pname = "charset-normalizer";
        version = "3.1.0";
        src = fetchPypi {
          inherit pname version;
          sha256 = "34e0a2f9c370eb95597aae63bf85eb5e96826d81e3dcf88b8886012906f509b5";
        };
      }
    )
    (
      buildPythonPackage rec {
        pname = "tqdm";
        version = "4.65.0";
        format = "wheel";
        src = fetchPypi rec {
          inherit pname version format;
          sha256 = "c4f53a17fe37e132815abceec022631be8ffe1b9381c2e6e30aa70edc99e9671";
          python = "py3";
          abi = "none";
          platform = "any";
        };
      }
    )
   (
      buildPythonPackage rec {
        pname = "requests";
        version = "2.30.0";
        src = fetchPypi {
          inherit pname version;
          sha256 = "239d7d4458afcb28a692cdd298d87542235f4ca8d36d03a15bfc128a6559a2f4";
        };
		# buildInputs = [ charset-normalizer ];
      }
    )	
    (
      buildPythonPackage rec {
        pname = "openai";
        version = "0.27.6";
        format = "wheel";
        src = fetchPypi rec {
          inherit pname version format;
          sha256 = "1f07ed06f1cfc6c25126107193726fe4cf476edcc4e1485cd9eb708f068f2606";
          python = "py3";
          abi = "none";
          platform = "any";
        };
        buildInputs = [ tqdm requests ];
      }
    )
    (
      buildPythonPackage rec {
        pname = "pyttsx3";
        version = "2.90";
		format = "wheel";
        src = fetchPypi rec {
          inherit pname version format;
          sha256 = "a585b6d8cffc19bd92db1e0ccbd8aa9c6528dd2baa5a47045d6fed542a44aa19";
          python = "py3";
		  abi = "none";
		  platform = "any";
        };
      }
    )
    (
      buildPythonPackage rec {
        pname = "vosk";
        version = "0.3.45";
        format = "wheel";
        src = fetchPypi rec {
          inherit pname version format;
          sha256 = "4221f83287eefe5abbe54fc6f1da5774e9e3ffcbbdca1705a466b341093b072e";
          python = "py3";
          abi = "none";
          platform = "manylinux_2_12_x86_64.manylinux2010_x86_64";
        };
      }
    )
  ];  
in 
{
  # NixOS wants to enable GRUB by default
  boot.loader.grub.enable = false;

  # if you have a Raspberry Pi 2 or 3, pick this:
  # boot.kernelPackages = pkgs.linuxPackages_latest;
  boot.kernelPackages = pkgs.linuxPackages_5_4;

  # A bunch of boot parameters needed for optimal runtime on RPi 3b+
  boot.kernelParams = ["cma=256M"];
  boot.loader.raspberryPi.enable = true;
  boot.loader.raspberryPi.version = 3;
  boot.loader.raspberryPi.uboot.enable = true;
  boot.loader.raspberryPi.firmwareConfig = ''
    gpu_mem=256
    dtparam=audio=on
  '';
  
  environment.systemPackages = with pkgs; [
    libraspberrypi nano python3 git espeak
    (pkgs.python3.withPackages my-python-packages)
  ];
  
  # File systems configuration for using the installer's partition layout
  fileSystems = {
    "/" = {
      device = "/dev/disk/by-label/NIXOS_SD";
      fsType = "ext4";
    };
  };

  time.timeZone = "Europe/Berlin";
  services.timesyncd = {
    enable = true;
    servers = [ "pool.ntp.org" ];
  };

  # Preserve space by sacrificing documentation and history
  documentation.nixos.enable = false;
  nix.gc.automatic = true;
  nix.gc.options = "--delete-older-than 30d";
  boot.cleanTmpDir = true;

  # Use 1GB of additional swap memory in order to not run out of memory
  # when installing lots of things while running other things at the same time.
  swapDevices = [ { device = "/swapfile"; size = 1024; } ];
  
  # audio
  sound.enable = true;
  hardware.pulseaudio.enable = true;
  
  # users
  services.openssh = {
    enable = true;
    permitRootLogin = "yes";	
    passwordAuthentication = false;
  };

  # Ensure the user exists on the system
  users.users."raspi" = {
    isNormalUser = true;
  };

  users.users."root" = {
    openssh.authorizedKeys.keys = [
      "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEAg2st6LtwRQVQHimkHYOfftw8U9mXz1dMYigN+VvHOhVdrvPxnywB4bciZKJgVuDbzg6eKXiojOuJje3VJKVa1YCL1OCh+ox0udm43OqQeo8FDJhxXzLVDKSOsxAajFBB8WsHb9zOJE0FXkCMK5Ez4UXdQwM31aYkOqMwUt1+CLKGIj/w3SRqQI97ovIuxMQtUoYtSd9tFIl5SjfO3mH68u7ENaBvHxfBJV62vuJJHx8ZZvRQelHJg1K0inGY1hPQqzV2UV7tbQnQHc64ZStoBNprkHkv6WQgq7dEuEXZOkY6TnNkkdXaKKfwYcO6C0t+s0nl0rytQ1Io9+FPmcAcVQ== en3rgy@localhost"
    ];
  };
}
