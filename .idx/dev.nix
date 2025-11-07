{ pkgs, ... }:

let
  pythonPackages = with pkgs.python313Packages; [
    fastapi
    uvicorn
    python-socketio
    python-multipart
    pandas
    numpy
    plotly
    aiofiles
    pyarrow
    openpyxl
    xlrd
    websockets
  ];
  pythonWithPackages = pkgs.python313.withPackages (ps: pythonPackages);
in
{
  # Using unstable channel to get Python 3.13
  channel = "unstable";

  # Use https://search.nixos.org/packages to find packages
  packages = [
    pkgs.nodejs_20
    pythonWithPackages
  ];

  # Sets environment variables in the workspace
  env = {};

  # Search for the extensions you want on https://open-vsx.org/ and use "publisher.id"
  idx.extensions = [
    "ms-python.python"
    "esbenp.prettier-vscode"
  ];

  # Enable previews and customize configuration
  idx.previews = {
    enable = true;
    previews = {
      frontend = {
        # Frontend web preview
        command = [
          "npm"
          "run"
          "dev"
          "--"
          "--port"
          "$PORT"
          "--host"
          "0.0.0.0"
        ];
        manager = "web";
        cwd = "frontend";
      };
      backend = {
        # Backend preview
        command = [
          "uvicorn"
          "app.main:app"
          "--host"
          "0.0.0.0"
          "--port"
          "8000"
        ];
        manager = "web";
        cwd = "backend";
      };
    };
  };
}
