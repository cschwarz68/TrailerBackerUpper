#An RTSP server is needed to stream video from the car camera(s) for viewing of camera feed during driving.
#The executible of this server is not kept in the repository of this project. Execute this script to install server binary.



#IMPORTANT: this script must be run from the root directory of this repository (I didn't feel like learning how to write .sh files so I hacked this together quickly).

SERVER_BINARY=mediamtx
cd src/rtsp_server
if test -f "$SERVER_BINARY"; then
    echo "Server binary already present. Not installing."
    echo "Done."
else
    echo "Server binary not found. Installing."
    cd ..
    cd ..
    wget https://github.com/bluenviron/mediamtx/releases/download/v0.23.5/mediamtx_v0.23.5_linux_arm64v8.tar.gz
    tar -xf mediamtx_v0.23.5_linux_arm64v8.tar.gz
    rm mediamtx_v0.23.5_linux_arm64v8.tar.gz
    rm mediamtx.yml
    rm LICENSE
    mv mediamtx src/rtsp_server
    echo "Success!"
fi 




