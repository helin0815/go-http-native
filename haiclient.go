package main

import (
	"bufio"
	"fmt"
	"net"
	"os"
	"strconv"
)

const (
	SERVER_IP = "127.0.0.1"
	PORT      = 8085
)

func main() {
	fmt.Println("嗨客网(www.haicoder.net)")
	serverAddr := SERVER_IP + ":" + strconv.Itoa(PORT)
	conn, err := net.Dial("udp", serverAddr)
	if err != nil {
		fmt.Println("Net dial err =", err)
		os.Exit(1)
	}
	defer conn.Close()
	input := bufio.NewScanner(os.Stdin)
	for input.Scan() {
		line := input.Text()
		if _, err := conn.Write([]byte(line)); err != nil {
			fmt.Println("Wrtie err =", err)
			return
		}
		fmt.Println("Write:", line)
		msg := make([]byte, 1024)
		if _, err = conn.Read(msg); err != nil {
			fmt.Println("Read err =", err)
			return
		}
		fmt.Println("Response:", string(msg))
	}
}
