{ config, pkgs, lib, ... }:
{

  # users
  services.openssh = {
    enable = true;
    permitRootLogin = "yes";	
    passwordAuthentication = false;
  };
  
  users.users = {
  
    raspi = {
      isNormalUser = true;
      home = "/home/raspi";
	  description = "Raspi";
      extraGroups = ["wheel"];
      openssh.authorizedKeys = {
	    keys = [
          "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEAg2st6LtwRQVQHimkHYOfftw8U9mXz1dMYigN+VvHOhVdrvPxnywB4bciZKJgVuDbzg6eKXiojOuJje3VJKVa1YCL1OCh+ox0udm43OqQeo8FDJhxXzLVDKSOsxAajFBB8WsHb9zOJE0FXkCMK5Ez4UXdQwM31aYkOqMwUt1+CLKGIj/w3SRqQI97ovIuxMQtUoYtSd9tFIl5SjfO3mH68u7ENaBvHxfBJV62vuJJHx8ZZvRQelHJg1K0inGY1hPQqzV2UV7tbQnQHc64ZStoBNprkHkv6WQgq7dEuEXZOkY6TnNkkdXaKKfwYcO6C0t+s0nl0rytQ1Io9+FPmcAcVQ== root"
        ];

    };

    root = {
      openssh.authorizedKeys = {
	    keys = [
          "ssh-rsa AAAAB3NzaC1yc2EAAAABJQAAAQEAg2st6LtwRQVQHimkHYOfftw8U9mXz1dMYigN+VvHOhVdrvPxnywB4bciZKJgVuDbzg6eKXiojOuJje3VJKVa1YCL1OCh+ox0udm43OqQeo8FDJhxXzLVDKSOsxAajFBB8WsHb9zOJE0FXkCMK5Ez4UXdQwM31aYkOqMwUt1+CLKGIj/w3SRqQI97ovIuxMQtUoYtSd9tFIl5SjfO3mH68u7ENaBvHxfBJV62vuJJHx8ZZvRQelHJg1K0inGY1hPQqzV2UV7tbQnQHc64ZStoBNprkHkv6WQgq7dEuEXZOkY6TnNkkdXaKKfwYcO6C0t+s0nl0rytQ1Io9+FPmcAcVQ== root"
        ];
        keyFiles = [ ./3d197d7caf75ae14eeb45c1dc1fa6356_public_2023-05-07.pub ];
      };
    };
  };
}
