makecert.exe -sv face2groupkey.pvk -n "CN=face2group" -len 2048 face2groupcert.cer -r
cert2spc.exe face2groupcert.cer face2groupcert.spc
pvk2pfx -pvk face2groupkey.pvk -pi jiangzx -spc face2groupcert.spc -pfx face2groupcert.pfx -po jiangzx