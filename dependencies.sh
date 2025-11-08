sudo apt install build-essential git
sudo apt install libasound2-dev libx11-dev libxrandr-dev libxi-dev libgl1-mesa-dev libglu1-mesa-dev libxcursor-dev libxinerama-dev libwayland-dev libxkbcommon-dev
git clone --depth 1 https://github.com/raysan5/raylib.git raylib
# mv raylib/ ~/
cd ~/raylib/src
make clean
make PLATFORM=PLATFORM_DESKTOP -j$(nproc)
sudo make install
