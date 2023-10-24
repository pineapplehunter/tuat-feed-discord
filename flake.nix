{
  description = "A very basic flake";

  inputs.poetry2nix.url = "github:nix-community/poetry2nix";

  outputs = { self, nixpkgs, poetry2nix }:
    let
      inherit (poetry2nix.legacyPackages.x86_64-linux) mkPoetryApplication mkPoetryEnv;
    in
    {
      packages.x86_64-linux = {
        tuat-feed-discord = mkPoetryApplication {
          projectDir = ./.;
          preferWheels = true;
        };
        default = self.packages.x86_64-linux.tuat-feed-discord;
      };

      devShells.x86_64-linux.default = mkPoetryEnv {
          projectDir = ./.;
          preferWheels = true;
        };

      formatter.x86_64-linux = nixpkgs.legacyPackages.x86_64-linux.nixpkgs-fmt;
    };
}
