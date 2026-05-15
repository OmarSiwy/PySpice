{
  description = "PySpice-rs: PySpice core rewritten in Rust";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    rust-overlay.url = "github:oxalica/rust-overlay";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, rust-overlay, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        overlays = [
          (import rust-overlay)
          (import ./nix/ngspice.nix)
        ];
        pkgs = import nixpkgs { inherit system overlays; };
        rustToolchain = pkgs.rust-bin.stable.latest.default.override {
          extensions = [ "rust-src" "rust-analyzer" ];
        };
        pythonEnv = pkgs.python312.withPackages (ps: with ps; [
          numpy
          pytest
        ]);
        openvaf = import ./nix/openvaf.nix { inherit pkgs; };
        vacask = import ./nix/vacask.nix { inherit pkgs; openvafPkg = openvaf; };
        xyce = import ./nix/xyce.nix { inherit pkgs; };
      in {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            rustToolchain
            pkgs.cargo
            pkgs.maturin
            pkgs.ngspice
            pkgs.libngspice
            pythonEnv
            pkgs.pkg-config
            openvaf
            vacask
            xyce
          ];

          shellHook = ''
            echo "PySpice-rs dev shell"
            echo "  rust: $(rustc --version)"
            echo "  python: $(python3 --version)"
            echo "  ngspice: $(ngspice --version 2>&1 | head -1)"
          '';

          RUST_SRC_PATH = "${rustToolchain}/lib/rustlib/src/rust/library";
        };

        packages = {
          default = pkgs.rustPlatform.buildRustPackage {
            pname = "pyspice-rs";
            version = "0.1.0";
            src = ./.;
            cargoLock.lockFile = ./Cargo.lock;
          };
          inherit openvaf vacask xyce;
        };
      }
    );
}
