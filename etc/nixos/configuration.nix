{ config, pkgs, lib, ... }:
let
  my-python-packages = ps: with ps; [
    pyaudio
	openai
	pyttsx3
    # other python packages
    #(
    #  buildPythonPackage rec {
    #    pname = "vosk";
    #    version = "0.3.45";
    #    format = "wheel";
    #   src = fetchPypi rec {
    #      inherit pname version format;
    #      sha256 = "4221f83287eefe5abbe54fc6f1da5774e9e3ffcbbdca1705a466b341093b072e";
    #      python = "py3";
    #      abi = "none";
    #      platform = "linux_armv7l";
    #    };
    #  }
    #)
  ];
in 
{
  system.stateVersion = "22.11";
  
  # import additional nix configurations files
  imports = [
    ./users.nix
  ];

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
   
  networking.firewall.allowedTCPPorts = [ 80 443 22 ];
  
  i18n = {
    defaultLocale = "de_DE.UTF-8";
    supportedLocales = [ "de_DE.UTF-8/UTF-8" "en_US.UTF-8/UTF-8" ];
  };  

  services.xserver = {
    layout = "de";
    # xkbOptions = "grp:win_space_toggle";
  };

}
