@echo off
cd /d e:\workspace\project\net-manager\dist\client
echo 正在运行客户端程序...
echo.
echo 程序启动时间: %date% %time% > client_output.log
echo. >> client_output.log
net-manager-client.exe >> client_output.log 2>&1
echo. >> client_output.log
echo 程序结束时间: %date% %time% >> client_output.log
echo.
echo 程序运行完成，输出已保存到 client_output.log
echo.
type client_output.log
echo.
pause