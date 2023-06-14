package main

import (
	"fmt"
	"net"
	"strconv"
	"strings"
)

const (
	serverIp = "127.0.0.1"
	PORT     = 8085
)

func main() {

	fmt.Println("the hai coder server starting...")
	address := serverIp + ":" + strconv.Itoa(PORT)
	addr, err := net.ResolveUDPAddr("udp", address)
	if err != nil {
		fmt.Println("create udp connecting failed...")
	}
	conn, err := net.ListenUDP("udp", addr)
	if err != nil {
		fmt.Println("create udp network failed...")
	}
	defer conn.Close()
	for {
		data := make([]byte, 1024)
		_, rAddr, err := conn.ReadFromUDP(data)
		if err != nil {
			fmt.Println("read from udp failed...:", err.Error())
			continue
		}
		strData := string(data)
		fmt.Println("received data:", strData)
		upper := strings.ToUpper(strData)
		_, err = conn.WriteToUDP([]byte(strData), rAddr)
		if err != nil {
			fmt.Println("write udp failed:", err.Error())
			continue
		}
		fmt.Println("发生数据为:", upper)

	}

}
